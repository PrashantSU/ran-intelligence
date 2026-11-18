import pytest

from ran_intelligence.evaluation import rag


@pytest.fixture
def fake_index():
    return {"document_count": 3}


@pytest.fixture
def fake_queries():
    return {
        "q1": {
            "query": "5G NR physical channels",
            "relevant_chunk_ids": ["a", "b"],
        },
        "q2": {
            "query": "5G NR radio resource management",
            "relevant_chunk_ids": ["c"],
        },
    }


def test_evaluate_rag_retriever(fake_index, fake_queries, monkeypatch):
    results = {
        "5G NR physical channels": [
            {"chunk_id": "a", "metadata": {"source": "spec.pdf", "page": 2},
             "rrf_score": 0.03},
            {"chunk_id": "x", "metadata": {"source": "spec.pdf", "page": 3},
             "rrf_score": 0.02},
        ],
        "5G NR radio resource management": [
            {"chunk_id": "c", "metadata": {"source": "spec.pdf", "page": 4},
             "rrf_score": 0.04},
        ],
    }

    def fake_search(index, query, top_k, candidate_k):
        assert index is fake_index
        return results[query][:top_k]

    monkeypatch.setattr(rag, "search_telecom_documents", fake_search)

    output = rag.evaluate_rag_retriever(
        fake_index, fake_queries, top_k=3
    )

    assert output["query_count"] == 2
    assert output["macro_metrics"]["recall@3"] == pytest.approx(0.75)
    assert output["macro_metrics"]["mrr"] == pytest.approx(1.0)
    assert output["mean_latency_ms"] >= 0
    assert output["per_query"]["q1"]["retrieved_chunk_ids"] == ["a", "x"]


def test_empty_query_dataset_rejected(fake_index):
    with pytest.raises(ValueError, match="At least one"):
        rag.evaluate_rag_retriever(fake_index, {})


def test_missing_relevance_judgments_rejected(fake_index):
    with pytest.raises(ValueError, match="relevance judgments"):
        rag.evaluate_rag_retriever(
            fake_index,
            {"q1": {"query": "5G NR", "relevant_chunk_ids": []}},
        )


def test_empty_query_text_rejected(fake_index):
    with pytest.raises(ValueError, match="non-empty query"):
        rag.evaluate_rag_retriever(
            fake_index,
            {"q1": {"query": " ", "relevant_chunk_ids": ["a"]}},
        )


def test_invalid_top_k_rejected(fake_index, fake_queries):
    with pytest.raises(ValueError, match="positive"):
        rag.evaluate_rag_retriever(fake_index, fake_queries, top_k=0)
