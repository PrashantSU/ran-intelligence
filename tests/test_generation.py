
import pytest

from ran_intelligence.rag.generation import (
    build_evidence_context,
    build_generation_prompt,
    generate_grounded_answer,
    validate_answer_citations,
)


@pytest.fixture
def documents():
    return [
        {
            "text": "PDSCH carries downlink user data.",
            "metadata": {
                "source": "3gpp-ts-38-211.pdf",
                "page": 118,
            },
        },
        {
            "text": "PDCCH carries downlink control information.",
            "metadata": {
                "source": "3gpp-ts-38-211.pdf",
                "page": 119,
            },
        },
    ]


def test_context_preserves_source_pages(documents):
    context, sources = build_evidence_context(documents)

    assert "[S1: 3gpp-ts-38-211.pdf, page 118]" in context
    assert "[S2: 3gpp-ts-38-211.pdf, page 119]" in context
    assert len(sources) == 2
    assert sources[0]["page"] == 118
    assert sources[1]["page"] == 119


def test_context_respects_character_limit(documents):
    context, _ = build_evidence_context(
        documents,
        max_context_chars=150,
    )
    assert len(context) <= 150


def test_empty_documents_are_rejected():
    with pytest.raises(ValueError, match="must not be empty"):
        build_evidence_context([])


def test_empty_document_text_is_rejected():
    with pytest.raises(ValueError, match="No usable text"):
        build_evidence_context([{"text": " ", "metadata": {}}])


def test_prompt_contains_question_and_evidence():
    prompt = build_generation_prompt(
        "What does PDSCH carry?",
        "[S1: specification.pdf, page 10]\nPDSCH carries downlink data.",
    )
    assert "What does PDSCH carry?" in prompt
    assert "PDSCH carries downlink data." in prompt
    assert "Do not add facts" in prompt


def test_empty_query_is_rejected():
    with pytest.raises(ValueError, match="query must not be empty"):
        build_generation_prompt("", "Some evidence")


def test_valid_citations_are_accepted():
    sources = [{"id": "S1"}, {"id": "S2"}]

    result = validate_answer_citations(
        "PDSCH carries data [S1]. PDCCH carries control [S2].",
        sources,
    )

    assert result["valid"] is True
    assert result["invalid"] == []
    assert result["used"] == ["S1", "S2"]


def test_unknown_citations_are_rejected():
    result = validate_answer_citations(
        "The channel carries data [S9].",
        [{"id": "S1"}],
    )

    assert result["valid"] is False
    assert result["invalid"] == ["S9"]


def test_missing_citations_are_detected():
    result = validate_answer_citations(
        "The channel carries data.",
        [{"id": "S1"}],
    )

    assert result["uncited"] is True
    assert result["valid"] is False


def test_generation_uses_model_and_returns_sources(documents):
    class FakeTensor:
        shape = (1, 20)

        def to(self, device):
            return self

    class FakeTokenizer:
        def __call__(self, prompt, **kwargs):
            assert "PDSCH" in prompt
            assert kwargs["truncation"] is False
            return {"input_ids": FakeTensor()}

        def decode(self, output, skip_special_tokens=True):
            return "PDSCH carries downlink user data. [S1]"

    class FakeModel:
        name_or_path = "fake-model"

        def eval(self):
            return self

        def generate(self, **kwargs):
            assert "input_ids" in kwargs
            return [[1, 2, 3]]

    result = generate_grounded_answer(
        query="What does PDSCH carry?",
        documents=documents,
        tokenizer=FakeTokenizer(),
        model=FakeModel(),
    )

    assert result["status"] == "answered"
    assert result["answer"].startswith("PDSCH carries")
    assert result["sources"][0]["page"] == 118
    assert result["model"] == "fake-model"
    assert result["input_tokens"] == 20


def test_generation_rejects_overlong_input(documents):
    class FakeTensor:
        shape = (1, 600)

    class FakeTokenizer:
        def __call__(self, prompt, **kwargs):
            assert kwargs["truncation"] is False
            return {"input_ids": FakeTensor()}

    class FakeModel:
        def eval(self):
            raise AssertionError("Model must not run for overlong input")

    with pytest.raises(ValueError, match="exceeding"):
        generate_grounded_answer(
            query="What does PDSCH carry?",
            documents=documents,
            tokenizer=FakeTokenizer(),
            model=FakeModel(),
            max_input_tokens=512,
        )
