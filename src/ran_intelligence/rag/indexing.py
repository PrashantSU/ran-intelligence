"""Semantic, keyword and hybrid retrieval for telecom documents."""

import re
from typing import Any

import faiss
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

DEFAULT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def _tokenize(text: str) -> list[str]:
    """Tokenize text while preserving technical identifiers."""
    return re.findall(r"[a-zA-Z0-9]+(?:[-_.][a-zA-Z0-9]+)*", text.lower())


def _chunk_id(chunk: dict[str, Any]) -> str:
    """Build a stable identifier for a chunk."""
    metadata = chunk.get("metadata", {})
    return str(
        chunk.get("chunk_id")
        or metadata.get("chunk_id")
        or (
            f"{metadata.get('source', 'unknown')}:"
            f"{metadata.get('page', 'unknown')}:"
            f"{metadata.get('chunk_index', 0)}"
        )
    )


def build_retrieval_index(
    chunks: list[dict[str, Any]],
    model_name: str = DEFAULT_MODEL,
    batch_size: int = 32,
) -> dict[str, Any]:
    """Build normalized FAISS and BM25 indexes from document chunks."""
    if not chunks:
        raise ValueError("chunks must not be empty")

    if batch_size < 1:
        raise ValueError("batch_size must be positive")

    documents = []
    seen_ids = set()

    for chunk in chunks:
        text = str(chunk.get("text", "")).strip()
        if not text:
            continue

        chunk_id = _chunk_id(chunk)
        if chunk_id in seen_ids:
            raise ValueError(f"Duplicate chunk ID: {chunk_id}")

        seen_ids.add(chunk_id)
        documents.append({
            "chunk_id": chunk_id,
            "text": text,
            "metadata": dict(chunk.get("metadata", {})),
        })

    if not documents:
        raise ValueError("No non-empty chunks found")

    model = SentenceTransformer(model_name)

    embeddings = model.encode(
        [doc["text"] for doc in documents],
        batch_size=batch_size,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    embeddings = np.asarray(embeddings, dtype=np.float32)

    if embeddings.ndim != 2 or not np.isfinite(embeddings).all():
        raise ValueError("Invalid embedding matrix")

    vector_index = faiss.IndexFlatIP(embeddings.shape[1])
    vector_index.add(embeddings)

    tokenized_documents = [_tokenize(doc["text"]) for doc in documents]
    bm25_index = BM25Okapi(tokenized_documents)

    return {
        "model_name": model_name,
        "model": model,
        "vector_index": vector_index,
        "bm25_index": bm25_index,
        "documents": documents,
        "embedding_dimension": embeddings.shape[1],
        "document_count": len(documents),
    }


def hybrid_search(
    index: dict[str, Any],
    query: str,
    top_k: int = 5,
    candidate_k: int = 20,
    rrf_k: int = 60,
) -> list[dict[str, Any]]:
    """Combine vector and BM25 rankings using Reciprocal Rank Fusion."""
    if not query or not query.strip():
        raise ValueError("query must not be empty")

    if top_k < 1 or candidate_k < 1 or rrf_k < 1:
        raise ValueError("top_k, candidate_k and rrf_k must be positive")

    documents = index["documents"]
    candidate_count = min(candidate_k, len(documents))

    query_embedding = index["model"].encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    query_embedding = np.asarray(query_embedding, dtype=np.float32)

    vector_scores, vector_ids = index["vector_index"].search(
        query_embedding, candidate_count
    )

    bm25_scores = index["bm25_index"].get_scores(_tokenize(query))
    bm25_ids = np.argsort(bm25_scores)[::-1][:candidate_count]

    fused_scores: dict[int, float] = {}
    vector_ranks: dict[int, int] = {}
    bm25_ranks: dict[int, int] = {}

    for rank, doc_id in enumerate(vector_ids[0], start=1):
        if doc_id >= 0:
            doc_id = int(doc_id)
            vector_ranks[doc_id] = rank
            fused_scores[doc_id] = fused_scores.get(doc_id, 0.0) + (
                1.0 / (rrf_k + rank)
            )

    for rank, doc_id in enumerate(bm25_ids, start=1):
        doc_id = int(doc_id)
        bm25_ranks[doc_id] = rank
        fused_scores[doc_id] = fused_scores.get(doc_id, 0.0) + (
            1.0 / (rrf_k + rank)
        )

    ranked_ids = sorted(
        fused_scores,
        key=lambda doc_id: fused_scores[doc_id],
        reverse=True,
    )[:top_k]

    results = []
    for doc_id in ranked_ids:
        document = documents[doc_id]
        results.append({
            **document,
            "rrf_score": fused_scores[doc_id],
            "vector_rank": vector_ranks.get(doc_id),
            "bm25_rank": bm25_ranks.get(doc_id),
        })

    return results
