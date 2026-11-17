
import pytest

from ran_intelligence.rag import qa


@pytest.fixture
def documents():
    return [
        {
            "text": "PDSCH carries downlink user data.",
            "metadata": {
                "source": "3gpp-ts-38-211.pdf",
                "page": 118,
            },
        }
    ]


def test_pipeline_uses_hybrid_retrieval(monkeypatch, documents):
    calls = {}

    def fake_search(**kwargs):
        calls.update(kwargs)
        return documents

    def fake_generate(**kwargs):
        return {
            "question": kwargs["query"],
            "answer": "PDSCH carries downlink data. [S1]",
            "sources": [{"id": "S1", "page": 118}],
            "citations": {"valid": True, "used": ["S1"]},
            "status": "answered",
            "model": "fake-model",
        }

    monkeypatch.setattr(qa, "search_telecom_documents", fake_search)
    monkeypatch.setattr(qa, "generate_grounded_answer", fake_generate)

    result = qa.answer_telecom_question(
        index={"document_count": 1},
        query="What does PDSCH carry?",
        tokenizer=object(),
        model=object(),
    )

    assert result["status"] == "answered"
    assert result["retrieval_method"] == "hybrid"
    assert result["retrieved_count"] == 1
    assert calls["query"] == "What does PDSCH carry?"


def test_pipeline_uses_reranking_when_provided(monkeypatch, documents):
    calls = {}

    def fake_search(**kwargs):
        calls.update(kwargs)
        return documents

    def fake_generate(**kwargs):
        return {
            "question": kwargs["query"],
            "answer": "PDSCH carries downlink data. [S1]",
            "sources": [{"id": "S1", "page": 118}],
            "citations": {"valid": True, "used": ["S1"]},
            "status": "answered",
            "model": "fake-model",
        }

    monkeypatch.setattr(
        qa,
        "search_telecom_documents_reranked",
        fake_search,
    )
    monkeypatch.setattr(qa, "generate_grounded_answer", fake_generate)

    reranker = object()

    result = qa.answer_telecom_question(
        index={"document_count": 1},
        query="What does PDSCH carry?",
        tokenizer=object(),
        model=object(),
        reranker=reranker,
    )

    assert result["retrieval_method"] == "hybrid_reranked"
    assert calls["reranker"] is reranker


def test_pipeline_handles_no_retrieved_documents(monkeypatch):
    monkeypatch.setattr(
        qa,
        "search_telecom_documents",
        lambda **kwargs: [],
    )

    def unexpected_generation(**kwargs):
        raise AssertionError("Generation must not run without evidence")

    monkeypatch.setattr(
        qa,
        "generate_grounded_answer",
        unexpected_generation,
    )

    result = qa.answer_telecom_question(
        index={"document_count": 1},
        query="Question with no evidence",
        tokenizer=object(),
        model=object(),
    )

    assert result["status"] == "insufficient_evidence"
    assert result["sources"] == []
    assert result["retrieved_count"] == 0


def test_pipeline_rejects_empty_question():
    with pytest.raises(ValueError, match="query must not be empty"):
        qa.answer_telecom_question(
            index={},
            query=" ",
            tokenizer=object(),
            model=object(),
        )


def test_pipeline_rejects_invalid_retrieval_limits():
    with pytest.raises(ValueError, match="must be positive"):
        qa.answer_telecom_question(
            index={},
            query="What is PDSCH?",
            tokenizer=object(),
            model=object(),
            top_k=0,
        )
