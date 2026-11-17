
"""Hybrid retrieval and cross-encoder reranking for telecom documents."""

import re
from typing import Any

from ran_intelligence.rag.indexing import hybrid_search
from ran_intelligence.rag.reranking import rerank_documents


def is_boilerplate(result: dict[str, Any]) -> bool:
    """Identify cover pages, repeated headers and reference-list chunks."""
    text = re.sub(r"\s+", " ", result.get("text", "")).strip()
    if not text:
        return True

    upper = text.upper()
    has_document_id = bool(
        re.search(r"(?:ETSI\s+)?TS\s+138\s+\d+", upper)
        or re.search(r"3GPP\s+TS\s+38\.\d+", upper)
    )
    has_version = bool(re.search(r"V\d+\.\d+\.\d+", upper))
    has_specification_label = any(
        label in upper
        for label in (
            "TECHNICAL SPECIFICATION",
            "PHYSICAL CHANNELS AND MODULATION",
            "RADIO RESOURCE CONTROL (RRC)",
        )
    )

    if (
        len(text) < 500
        and has_document_id
        and has_version
        and has_specification_label
    ):
        return True

    if len(text) < 200 and has_document_id and "ETSI" in upper and "3GPP" in upper:
        return True

    reference_entries = re.findall(
        r"\[\d+\]\s*(?:3GPP|ETSI|ATIS|ITU|IETF|IEEE)\b",
        text,
        re.I,
    )
    starts_with_reference = bool(
        re.match(
            r"^[\s.]*\[\d+\]\s*(?:3GPP|ETSI|ATIS|ITU|IETF|IEEE)\b",
            text,
            re.I,
        )
    )

    return len(reference_entries) >= 5 and starts_with_reference


def search_telecom_documents(
    index: dict[str, Any],
    query: str,
    top_k: int = 5,
    candidate_k: int = 30,
) -> list[dict[str, Any]]:
    """Retrieve telecom passages using hybrid search and boilerplate filtering."""
    if not query or not query.strip():
        raise ValueError("query must not be empty")
    if top_k < 1 or candidate_k < 1:
        raise ValueError("top_k and candidate_k must be positive")

    total = index["document_count"]
    candidate_limit = min(candidate_k, total)

    candidates = hybrid_search(
        index=index,
        query=query,
        top_k=candidate_limit,
        candidate_k=min(candidate_limit * 3, total),
    )

    return [
        result for result in candidates if not is_boilerplate(result)
    ][:top_k]


def search_telecom_documents_reranked(
    index: dict[str, Any],
    query: str,
    reranker: Any,
    top_k: int = 5,
    candidate_k: int = 100,
) -> list[dict[str, Any]]:
    """Retrieve a broad hybrid candidate set, filter and rerank it."""
    if not query or not query.strip():
        raise ValueError("query must not be empty")
    if top_k < 1 or candidate_k < 1:
        raise ValueError("top_k and candidate_k must be positive")

    candidates = search_telecom_documents(
        index=index,
        query=query,
        top_k=min(candidate_k, index["document_count"]),
        candidate_k=candidate_k,
    )

    return rerank_documents(
        query=query,
        documents=candidates,
        reranker=reranker,
        top_k=top_k,
    )

def expand_adjacent_chunks(
    documents: list[dict[str, Any]],
    all_documents: list[dict[str, Any]],
    window: int = 1,
) -> list[dict[str, Any]]:
    """Expand retrieved passages and retain their parent retrieval ranks."""
    if window < 0:
        raise ValueError("window must be non-negative")
    if not documents:
        return []
    if not all_documents:
        raise ValueError("all_documents must not be empty")

    def ordering_key(document):
        metadata = document.get("metadata", {})
        try:
            page = int(metadata.get("page", 0))
            chunk_index = int(metadata.get("chunk_index", 0))
        except (TypeError, ValueError) as exc:
            raise ValueError(
                "Page and chunk_index must be numeric"
            ) from exc
        return (
            str(metadata.get("source", "unknown")),
            page,
            chunk_index,
        )

    source_chunks = {}
    for document in all_documents:
        source = ordering_key(document)[0]
        source_chunks.setdefault(source, []).append(document)

    positions = {}
    for chunks in source_chunks.values():
        chunks.sort(key=ordering_key)
        for position, chunk in enumerate(chunks):
            chunk_id = chunk.get("chunk_id")
            if chunk_id is None:
                raise ValueError("Every chunk must have a chunk_id")
            positions[chunk_id] = (chunks, position)

    selected = {}

    for rank, document in enumerate(documents, start=1):
        chunk_id = document.get("chunk_id")
        if chunk_id not in positions:
            raise ValueError(
                f"Retrieved chunk {chunk_id!r} is not in all_documents"
            )

        chunks, position = positions[chunk_id]
        start_position = max(0, position - window)
        end_position = min(len(chunks), position + window + 1)

        for neighbour in chunks[start_position:end_position]:
            neighbour_id = neighbour["chunk_id"]
            is_seed = neighbour_id == chunk_id

            candidate = {
                **neighbour,
                "retrieval_rank": rank if is_seed else None,
                "context_group_rank": rank,
                "is_context_expansion": not is_seed,
            }

            existing = selected.get(neighbour_id)

            # If a chunk belongs to multiple neighbourhoods, retain
            # its highest-priority parent group.
            if (
                existing is None
                or rank < existing["context_group_rank"]
            ):
                selected[neighbour_id] = candidate

    return sorted(selected.values(), key=ordering_key)
