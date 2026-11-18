"""RAG evidence retrieval for incident investigations."""

from collections.abc import Callable
from typing import Any

from ran_intelligence.agents.schemas import IncidentRequest
from ran_intelligence.rag.retrieval import search_telecom_documents


def build_incident_rag_query(incident: IncidentRequest) -> str:
    """Build a focused telecom documentation query from an incident."""
    parts = [
        incident.description,
        "Relevant technical standards, procedures and possible mechanisms:",
        " ".join(incident.suspected_kpis),
    ]
    return " ".join(part.strip() for part in parts if part and part.strip())


def create_rag_handler(
    index: dict[str, Any],
    top_k: int = 5,
    candidate_k: int = 30,
    max_passage_chars: int = 1200,
    search_fn: Callable[..., list[dict[str, Any]]] | None = None,
) -> Callable[[IncidentRequest], dict[str, Any]]:
    """Create an incident handler backed by the hybrid telecom RAG index."""
    if top_k < 1 or candidate_k < 1 or max_passage_chars < 1:
        raise ValueError("Retrieval limits must be positive.")

    retrieve = search_fn or search_telecom_documents

    def rag_handler(incident: IncidentRequest) -> dict[str, Any]:
        query = build_incident_rag_query(incident)

        results = retrieve(
            index=index,
            query=query,
            top_k=top_k,
            candidate_k=candidate_k,
        )

        passages = []
        for result in results:
            metadata = result.get("metadata", {})
            source = str(metadata.get("source", "Unknown source"))
            page = metadata.get("page", "Unknown")
            title = str(metadata.get("title", source))
            chunk_id = str(result.get("chunk_id", "unknown"))

            passages.append({
                "chunk_id": chunk_id,
                "citation": f"{source}, page {page}",
                "source": source,
                "page": page,
                "title": title,
                "text": str(result.get("text", ""))[:max_passage_chars],
                "rrf_score": float(result.get("rrf_score", 0.0)),
            })

        return {
            "status": "retrieved" if passages else "no_results",
            "evidence_type": "technical_reference",
            "query": query,
            "retrieved_count": len(passages),
            "passages": passages,
            "interpretation": (
                "Retrieved standards and technical documentation provide "
                "reference context. They do not independently establish "
                "the cause of this incident."
            ),
        }

    return rag_handler
