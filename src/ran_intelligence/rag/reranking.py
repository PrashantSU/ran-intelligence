
"""Cross-encoder reranking for telecom document retrieval."""

from typing import Any

from sentence_transformers import CrossEncoder

DEFAULT_RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


def load_reranker(
    model_name: str = DEFAULT_RERANKER_MODEL,
    max_length: int = 512,
) -> CrossEncoder:
    """Load a cross-encoder model for query-passage relevance scoring."""
    if not model_name or not model_name.strip():
        raise ValueError("model_name must not be empty")
    if max_length < 1:
        raise ValueError("max_length must be positive")

    return CrossEncoder(model_name, max_length=max_length)


def rerank_documents(
    query: str,
    documents: list[dict[str, Any]],
    reranker: CrossEncoder,
    top_k: int = 5,
    batch_size: int = 16,
) -> list[dict[str, Any]]:
    """Rerank retrieved passages using cross-encoder relevance scores."""
    if not query or not query.strip():
        raise ValueError("query must not be empty")
    if top_k < 1:
        raise ValueError("top_k must be positive")
    if batch_size < 1:
        raise ValueError("batch_size must be positive")
    if not documents:
        return []

    pairs = [
        (query, document["text"])
        for document in documents
    ]

    scores = reranker.predict(
        pairs,
        batch_size=batch_size,
        show_progress_bar=False,
    )

    ranked_documents = []

    for document, score in zip(documents, scores):
        result = document.copy()
        result["rerank_score"] = float(score)
        ranked_documents.append(result)

    ranked_documents.sort(
        key=lambda item: item["rerank_score"],
        reverse=True,
    )

    for rank, document in enumerate(ranked_documents, start=1):
        document["rerank_rank"] = rank

    return ranked_documents[:top_k]
