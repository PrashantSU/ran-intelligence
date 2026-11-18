"""Retrieval quality metrics for RAG evaluation."""

from collections.abc import Iterable, Mapping, Sequence
from math import log2


def _validate_k(k: int) -> None:
    if isinstance(k, bool) or not isinstance(k, int) or k < 1:
        raise ValueError("k must be a positive integer")


def _unique(items: Iterable[str]) -> list[str]:
    return list(dict.fromkeys(items))


def precision_at_k(
    retrieved_ids: Sequence[str],
    relevant_ids: Iterable[str],
    k: int = 5,
) -> float:
    """Fraction of the top-k retrieved documents that are relevant."""
    _validate_k(k)
    relevant = set(relevant_ids)
    retrieved = _unique(retrieved_ids)[:k]

    return sum(item in relevant for item in retrieved) / k


def recall_at_k(
    retrieved_ids: Sequence[str],
    relevant_ids: Iterable[str],
    k: int = 5,
) -> float:
    """Fraction of all relevant documents found in the top-k results."""
    _validate_k(k)
    relevant = set(relevant_ids)

    if not relevant:
        return 0.0

    retrieved = _unique(retrieved_ids)[:k]
    return sum(item in relevant for item in retrieved) / len(relevant)


def reciprocal_rank(
    retrieved_ids: Sequence[str],
    relevant_ids: Iterable[str],
) -> float:
    """Reciprocal rank of the first relevant retrieved document."""
    relevant = set(relevant_ids)

    for rank, item in enumerate(_unique(retrieved_ids), start=1):
        if item in relevant:
            return 1.0 / rank

    return 0.0


def ndcg_at_k(
    retrieved_ids: Sequence[str],
    relevant_ids: Iterable[str],
    k: int = 5,
) -> float:
    """Normalized discounted cumulative gain with binary relevance."""
    _validate_k(k)
    relevant = set(relevant_ids)

    if not relevant:
        return 0.0

    retrieved = _unique(retrieved_ids)[:k]
    dcg = sum(
        1.0 / log2(rank + 1)
        for rank, item in enumerate(retrieved, start=1)
        if item in relevant
    )

    ideal_count = min(k, len(relevant))
    idcg = sum(
        1.0 / log2(rank + 1)
        for rank in range(1, ideal_count + 1)
    )

    return dcg / idcg


def evaluate_retrieval(
    retrieved_ids: Sequence[str],
    relevant_ids: Iterable[str],
    ks: Sequence[int] = (1, 3, 5),
) -> dict[str, float]:
    """Calculate standard ranking metrics for one retrieval query."""
    if not ks:
        raise ValueError("ks must contain at least one value")

    relevant = set(relevant_ids)
    results = {"mrr": reciprocal_rank(retrieved_ids, relevant)}

    for k in ks:
        _validate_k(k)
        results[f"precision@{k}"] = precision_at_k(
            retrieved_ids, relevant, k
        )
        results[f"recall@{k}"] = recall_at_k(
            retrieved_ids, relevant, k
        )
        results[f"ndcg@{k}"] = ndcg_at_k(
            retrieved_ids, relevant, k
        )

    return results


def evaluate_retrieval_batch(
    retrieved_by_query: Mapping[str, Sequence[str]],
    relevant_by_query: Mapping[str, Iterable[str]],
    ks: Sequence[int] = (1, 3, 5),
) -> dict:
    """Evaluate multiple queries and return per-query and macro metrics."""
    if not retrieved_by_query:
        raise ValueError("At least one retrieval query is required")

    missing = set(retrieved_by_query) - set(relevant_by_query)
    if missing:
        raise ValueError(
            f"Missing relevance judgments for queries: {sorted(missing)}"
        )

    per_query = {
        query_id: evaluate_retrieval(
            retrieved,
            relevant_by_query[query_id],
            ks,
        )
        for query_id, retrieved in retrieved_by_query.items()
    }

    metric_names = next(iter(per_query.values()))
    macro = {
        metric: sum(values[metric] for values in per_query.values())
        / len(per_query)
        for metric in metric_names
    }

    return {
        "query_count": len(per_query),
        "macro_metrics": macro,
        "per_query": per_query,
    }
