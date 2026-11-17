
import pytest

from ran_intelligence.rag.reranking import rerank_documents


class FakeReranker:
    def predict(self, pairs, batch_size, show_progress_bar):
        return [0.2, 0.9, 0.5]


@pytest.fixture
def documents():
    return [
        {"chunk_id": "a", "text": "Unrelated passage"},
        {"chunk_id": "b", "text": "Relevant NR physical channel passage"},
        {"chunk_id": "c", "text": "Partially relevant passage"},
    ]


def test_reranking_orders_by_score(documents):
    results = rerank_documents(
        query="NR physical channels",
        documents=documents,
        reranker=FakeReranker(),
        top_k=3,
    )

    assert [item["chunk_id"] for item in results] == ["b", "c", "a"]
    assert results[0]["rerank_score"] == pytest.approx(0.9)
    assert results[0]["rerank_rank"] == 1


def test_reranking_preserves_original_fields(documents):
    results = rerank_documents(
        query="NR physical channels",
        documents=documents,
        reranker=FakeReranker(),
    )

    assert results[0]["text"] == documents[1]["text"]
    assert results[0]["chunk_id"] == "b"


def test_reranking_limits_top_k(documents):
    results = rerank_documents(
        query="NR physical channels",
        documents=documents,
        reranker=FakeReranker(),
        top_k=2,
    )

    assert len(results) == 2


def test_empty_documents():
    assert rerank_documents(
        query="NR physical channels",
        documents=[],
        reranker=FakeReranker(),
    ) == []


@pytest.mark.parametrize(
    "query,top_k",
    [
        ("", 5),
        ("NR channels", 0),
    ],
)
def test_invalid_inputs(documents, query, top_k):
    with pytest.raises(ValueError):
        rerank_documents(
            query=query,
            documents=documents,
            reranker=FakeReranker(),
            top_k=top_k,
        )
