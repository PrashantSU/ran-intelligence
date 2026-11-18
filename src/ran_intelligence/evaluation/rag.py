"""End-to-end evaluation of the hybrid telecom RAG retriever."""

from collections.abc import Mapping
from statistics import mean
from time import perf_counter
from typing import Any

from ran_intelligence.evaluation.retrieval import evaluate_retrieval
from ran_intelligence.rag.retrieval import search_telecom_documents


def evaluate_rag_retriever(
    index: dict[str, Any],
    queries: Mapping[str, Mapping[str, Any]],
    top_k: int = 5,
    candidate_k: int = 30,
) -> dict[str, Any]:
    """Evaluate real retrieval against explicitly judged relevant chunk IDs.

    Each query entry must contain:
        query: natural-language search query
        relevant_chunk_ids: collection of judged relevant chunk IDs
    """
    if not queries:
        raise ValueError("At least one evaluation query is required")

    if top_k < 1 or candidate_k < 1:
        raise ValueError("top_k and candidate_k must be positive")

    per_query = {}
    latencies = []

    for query_id, item in queries.items():
        query = item.get("query")
        relevant_ids = item.get("relevant_chunk_ids")

        if not isinstance(query, str) or not query.strip():
            raise ValueError(f"Query {query_id!r} must have a non-empty query")

        if not isinstance(relevant_ids, (list, tuple, set)) or not relevant_ids:
            raise ValueError(
                f"Query {query_id!r} must have non-empty relevance judgments"
            )

        start = perf_counter()
        passages = search_telecom_documents(
            index=index,
            query=query,
            top_k=top_k,
            candidate_k=candidate_k,
        )
        latency_ms = (perf_counter() - start) * 1000
        latencies.append(latency_ms)

        retrieved_ids = [
            passage["chunk_id"]
            for passage in passages
            if passage.get("chunk_id")
        ]

        metrics = evaluate_retrieval(
            retrieved_ids=retrieved_ids,
            relevant_ids=relevant_ids,
            ks=(1, 3, 5),
        )

        per_query[query_id] = {
            "query": query,
            "metrics": metrics,
            "latency_ms": latency_ms,
            "retrieved_count": len(retrieved_ids),
            "retrieved_chunk_ids": retrieved_ids,
            "passages": [
                {
                    "chunk_id": passage.get("chunk_id"),
                    "source": passage.get("metadata", {}).get("source"),
                    "page": passage.get("metadata", {}).get("page"),
                    "rrf_score": passage.get("rrf_score"),
                }
                for passage in passages
            ],
        }

    metric_names = next(iter(per_query.values()))["metrics"]

    macro_metrics = {
        metric: mean(
            result["metrics"][metric]
            for result in per_query.values()
        )
        for metric in metric_names
    }

    return {
        "query_count": len(per_query),
        "top_k": top_k,
        "candidate_k": candidate_k,
        "macro_metrics": macro_metrics,
        "mean_latency_ms": mean(latencies),
        "per_query": per_query,
    }
