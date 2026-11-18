import pytest

from ran_intelligence.evaluation.retrieval import (
    evaluate_retrieval,
    evaluate_retrieval_batch,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
)


def test_precision_recall_and_mrr():
    retrieved = ["a", "x", "b", "c"]
    relevant = {"a", "b", "c"}

    assert precision_at_k(retrieved, relevant, 3) == pytest.approx(2 / 3)
    assert recall_at_k(retrieved, relevant, 3) == pytest.approx(2 / 3)
    assert reciprocal_rank(retrieved, relevant) == 1.0


def test_reciprocal_rank_uses_first_relevant_result():
    assert reciprocal_rank(
        ["x", "y", "b", "a"], {"a", "b"}
    ) == pytest.approx(1 / 3)


def test_ndcg_perfect_ranking():
    assert ndcg_at_k(["a", "b", "x"], {"a", "b"}, 3) == 1.0


def test_ndcg_penalises_lower_relevant_rank():
    ideal = ndcg_at_k(["a", "b", "x"], {"a", "b"}, 3)
    lower = ndcg_at_k(["x", "a", "b"], {"a", "b"}, 3)

    assert lower < ideal


def test_duplicate_retrieval_ids_do_not_inflate_metrics():
    assert precision_at_k(["a", "a", "b"], {"a", "b"}, 3) == pytest.approx(
        2 / 3
    )
    assert recall_at_k(["a", "a"], {"a", "b"}, 2) == pytest.approx(0.5)


def test_empty_relevance_set_returns_zero():
    metrics = evaluate_retrieval(["a", "b"], set())

    assert all(value == 0.0 for value in metrics.values())


def test_invalid_k_is_rejected():
    with pytest.raises(ValueError):
        precision_at_k(["a"], {"a"}, 0)


def test_batch_evaluation_returns_macro_metrics():
    result = evaluate_retrieval_batch(
        {
            "q1": ["a", "x"],
            "q2": ["x", "b"],
        },
        {
            "q1": {"a"},
            "q2": {"b"},
        },
        ks=(1, 2),
    )

    assert result["query_count"] == 2
    assert result["macro_metrics"]["recall@2"] == 1.0
    assert result["macro_metrics"]["mrr"] == pytest.approx(0.75)
    assert len(result["per_query"]) == 2


def test_batch_requires_relevance_judgments():
    with pytest.raises(ValueError, match="Missing relevance"):
        evaluate_retrieval_batch({"q1": ["a"]}, {})


def test_batch_rejects_empty_queries():
    with pytest.raises(ValueError, match="At least one"):
        evaluate_retrieval_batch({}, {})
