"""Services used by the FastAPI application."""

from functools import cached_property
from pathlib import Path

import pandas as pd

from ran_intelligence.analytics.kpi import (
    build_kpi_timeseries,
    compute_kpi_summary,
    compute_session_summary,
    get_available_kpis,
)


class DataService:
    """Loads and analyses the processed network measurements."""

    def __init__(self, data_path: Path):
        self.data_path = Path(data_path)

    @cached_property
    def measurements(self) -> pd.DataFrame:
        if not self.data_path.exists():
            raise FileNotFoundError(
                f"Processed measurements not found: {self.data_path}"
            )
        return pd.read_parquet(self.data_path)

    def dataset_summary(self) -> dict:
        df = self.measurements
        return {
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": df.columns.tolist(),
            "sessions": sorted(df["session_id"].dropna().unique().tolist()),
            "missing_values": {
                str(k): int(v)
                for k, v in df.isna().sum().items()
                if v > 0
            },
            "data_path": str(self.data_path),
        }

    def available_kpis(self) -> list[dict]:
        return get_available_kpis()

    def kpi_summary(self) -> pd.DataFrame:
        return compute_kpi_summary(self.measurements)

    def session_summary(self) -> pd.DataFrame:
        return compute_session_summary(self.measurements)

    def kpi_timeseries(
        self,
        session_id: str,
        metric: str,
        interval: str = "1min",
        aggregation: str = "median",
    ) -> pd.DataFrame:
        available_sessions = set(
            self.measurements["session_id"].dropna().astype(str)
        )
        if session_id not in available_sessions:
            raise ValueError(f"Unknown session_id: {session_id}")

        return build_kpi_timeseries(
            self.measurements,
            session_id=session_id,
            metric=metric,
            interval=interval,
            aggregation=aggregation,
        )


class RAGService:
    """Lazily loads and searches the persisted telecom RAG index."""

    def __init__(self, index_path: Path):
        self.index_path = Path(index_path)
        self._index = None
        self._manifest = None

    def load(self) -> dict:
        if self._index is not None:
            return self._index

        import json
        import pickle

        import faiss
        from sentence_transformers import SentenceTransformer

        required_files = [
            "manifest.json",
            "documents.json",
            "faiss.index",
            "bm25.pkl",
        ]

        missing = [
            name for name in required_files
            if not (self.index_path / name).is_file()
        ]
        if missing:
            raise FileNotFoundError(
                f"RAG index files missing in {self.index_path}: {missing}"
            )

        manifest = json.loads(
            (self.index_path / "manifest.json").read_text(
                encoding="utf-8"
            )
        )

        with (self.index_path / "documents.json").open(
            encoding="utf-8"
        ) as file:
            documents = json.load(file)

        vector_index = faiss.read_index(
            str(self.index_path / "faiss.index")
        )

        # This pickle must come from a trusted, locally stored index.
        with (self.index_path / "bm25.pkl").open("rb") as file:
            bm25_index = pickle.load(file)

        if len(documents) != manifest["document_count"]:
            raise ValueError("RAG document count does not match manifest.")

        if vector_index.ntotal != len(documents):
            raise ValueError("FAISS vector count does not match documents.")

        if vector_index.d != manifest["embedding_dimension"]:
            raise ValueError("FAISS dimension does not match manifest.")

        model_name = manifest["model_name"]
        model = SentenceTransformer(model_name)

        self._manifest = manifest
        self._index = {
            "model_name": model_name,
            "model": model,
            "vector_index": vector_index,
            "bm25_index": bm25_index,
            "documents": documents,
            "embedding_dimension": vector_index.d,
            "document_count": len(documents),
        }

        return self._index

    def search(
        self,
        query: str,
        top_k: int = 5,
        candidate_k: int = 30,
        rrf_k: int = 60,
    ) -> dict:
        from ran_intelligence.rag.indexing import hybrid_search

        index = self.load()

        results = hybrid_search(
            index=index,
            query=query,
            top_k=top_k,
            candidate_k=candidate_k,
            rrf_k=rrf_k,
        )

        chunks = []
        for rank, result in enumerate(results, start=1):
            metadata = result.get("metadata", {})

            chunks.append({
                "rank": rank,
                "chunk_id": result["chunk_id"],
                "text": result["text"],
                "source": metadata.get("source"),
                "title": metadata.get("title"),
                "page": metadata.get("page"),
                "total_pages": metadata.get("total_pages"),
                "chunk_index": metadata.get("chunk_index"),
                "rrf_score": result["rrf_score"],
                "vector_rank": result["vector_rank"],
                "bm25_rank": result["bm25_rank"],
            })

        return {
            "query": query,
            "result_count": len(chunks),
            "index_document_count": index["document_count"],
            "retrieval_method": self._manifest["retrieval_method"],
            "results": chunks,
        }



class IncidentService:
    """Manage resumable incident investigations."""

    def __init__(
        self,
        measurements: pd.DataFrame,
        rag_handler=None,
    ):
        from ran_intelligence.agents.adapters import (
            create_investigation_toolbox,
        )
        from ran_intelligence.agents.workflow import (
            build_investigation_graph,
        )

        self.toolbox = create_investigation_toolbox(
            measurements=measurements,
            rag_handler=rag_handler,
            include_simulation=True,
        )
        self.graph = build_investigation_graph(
            toolbox=self.toolbox,
            tool_names=tuple(self.toolbox.available_tools),
        )
        self._active_threads: set[str] = set()

    @staticmethod
    def _config(thread_id: str) -> dict:
        return {"configurable": {"thread_id": thread_id}}

    @staticmethod
    def _report_dict(report):
        if report is None:
            return None
        return report.model_dump(mode="json")

    def _format_state(self, snapshot, thread_id: str) -> dict:
        values = snapshot.values or {}
        report = values.get("report")

        review_request = None
        for task in snapshot.tasks:
            for interrupt_item in getattr(task, "interrupts", ()):
                review_request = getattr(
                    interrupt_item,
                    "value",
                    None,
                )

        incident = values.get("incident")

        return {
            "thread_id": thread_id,
            "incident_id": (
                str(incident.incident_id) if incident else thread_id
            ),
            "current_step": values.get("current_step", "unknown"),
            "investigation_status": values.get(
                "investigation_status",
                "running",
            ),
            "pending_review": values.get("pending_review", False),
            "review_approved": values.get("review_approved"),
            "human_feedback": values.get("human_feedback"),
            "completed_tools": values.get("completed_tools", []),
            "errors": values.get("errors", []),
            "report": self._report_dict(report),
            "review_request": review_request,
        }

    def start(self, incident) -> dict:
        """Run an investigation until its human-review interrupt."""
        from ran_intelligence.agents.state import create_initial_state

        thread_id = str(incident.incident_id)

        if thread_id in self._active_threads:
            raise ValueError(
                f"Investigation already exists: {thread_id}"
            )

        config = self._config(thread_id)

        try:
            self.graph.invoke(
                create_initial_state(incident),
                config=config,
            )
            self._active_threads.add(thread_id)
            snapshot = self.graph.get_state(config)
            return self._format_state(snapshot, thread_id)
        except Exception:
            self._active_threads.discard(thread_id)
            raise

    def get(self, thread_id: str) -> dict:
        """Return the latest checkpointed investigation state."""
        if thread_id not in self._active_threads:
            raise KeyError(f"Unknown investigation: {thread_id}")

        snapshot = self.graph.get_state(self._config(thread_id))
        return self._format_state(snapshot, thread_id)

    def review(
        self,
        thread_id: str,
        approved: bool,
        feedback: str | None = None,
    ) -> dict:
        """Resume a paused investigation with a human decision."""
        from langgraph.types import Command

        if thread_id not in self._active_threads:
            raise KeyError(f"Unknown investigation: {thread_id}")

        current = self.get(thread_id)
        if not current["pending_review"]:
            raise ValueError(
                "This investigation is not waiting for human review."
            )

        self.graph.invoke(
            Command(
                resume={
                    "approved": approved,
                    "feedback": feedback,
                }
            ),
            config=self._config(thread_id),
        )

        return self.get(thread_id)
