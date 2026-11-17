from typing import Any

from ran_intelligence.rag.generation import generate_grounded_answer
from ran_intelligence.rag.retrieval import (
    search_telecom_documents,
    search_telecom_documents_reranked,
)


def answer_telecom_question(
    index: dict[str, Any],
    query: str,
    tokenizer: Any,
    model: Any,
    reranker: Any = None,
    top_k: int = 5,
    candidate_k: int = 30,
    device: str | None = None,
    max_input_tokens: int = 512,
    max_new_tokens: int = 360,
    max_context_chars: int = 5000,
    context_window: int = 1,
) -> dict[str, Any]:
    """Retrieve telecom evidence, expand context and generate a cited answer."""
    from ran_intelligence.rag.retrieval import expand_adjacent_chunks

    if not query or not query.strip():
        raise ValueError("query must not be empty")

    if top_k < 1 or candidate_k < 1:
        raise ValueError("top_k and candidate_k must be positive")

    if context_window < 0:
        raise ValueError("context_window must be non-negative")

    if reranker is None:
        documents = search_telecom_documents(
            index=index,
            query=query,
            top_k=top_k,
            candidate_k=candidate_k,
        )
        retrieval_method = "hybrid"
    else:
        documents = search_telecom_documents_reranked(
            index=index,
            query=query,
            reranker=reranker,
            top_k=top_k,
            candidate_k=candidate_k,
        )
        retrieval_method = "hybrid_reranked"

    if not documents:
        return {
            "question": query,
            "answer": (
                "I could not find relevant evidence in the available "
                "telecom documents to answer this question."
            ),
            "sources": [],
            "citations": {
                "valid": False,
                "used": [],
                "invalid": [],
                "uncited": True,
            },
            "status": "insufficient_evidence",
            "retrieval_method": retrieval_method,
            "retrieved_count": 0,
            "context_count": 0,
            "model": None,
        }

    expanded_documents = expand_adjacent_chunks(
        documents=documents,
        all_documents=index["documents"],
        window=context_window,
    )

    # Preserve original retrieval ranking before adding neighbouring passages.
    expanded_documents.sort(
        key=lambda document: (
            document.get("retrieval_rank") is None,
            document.get("retrieval_rank") or float("inf"),
            str(document.get("metadata", {}).get("source", "")),
            int(document.get("metadata", {}).get("page", 0)),
            int(document.get("metadata", {}).get("chunk_index", 0)),
        )
    )

    result = generate_grounded_answer(
        query=query,
        documents=expanded_documents,
        tokenizer=tokenizer,
        model=model,
        device=device,
        max_input_tokens=max_input_tokens,
        max_new_tokens=max_new_tokens,
        max_context_chars=max_context_chars,
    )

    result["status"] = _classify_qa_status(
        result.get("answer", ""),
        result.get("citations", {}),
    )
    result["retrieval_method"] = retrieval_method
    result["retrieved_count"] = len(documents)
    result["context_count"] = len(expanded_documents)

    return result


def _classify_qa_status(answer: str, citations: dict) -> str:
    """Classify answer completeness using citation validity and explicit abstention."""
    if not isinstance(citations, dict):
        citations = {}

    invalid_sources = citations.get("invalid_sources", [])
    used_sources = citations.get("used_sources", [])

    if invalid_sources:
        return "invalid_citations"
    if not used_sources:
        return "uncited"

    text = (answer or "").strip().lower()
    text = text.lstrip("-*# ").strip()

    abstention_openers = (
        "insufficient evidence",
        "there is insufficient evidence",
        "the provided evidence is insufficient",
        "the available evidence is insufficient",
        "i cannot determine",
        "i cannot answer",
        "the evidence does not establish",
        "the provided context does not establish",
        "the provided context does not explicitly define",
        "the retrieved evidence does not explicitly define",
        "the available context does not explicitly define",
    )

    if text.startswith(abstention_openers):
        return "insufficient_evidence"

    return "answered"
