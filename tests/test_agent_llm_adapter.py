"""Tests for the Hugging Face structured-output adapter."""

import pytest

from ran_intelligence.agents.llm_adapter import _extract_json


def test_extracts_valid_json():
    result = _extract_json('{"hypotheses": []}')
    assert result == {"hypotheses": []}


def test_extracts_json_from_markdown_fence():
    result = _extract_json(
        '```json\n{"hypotheses": []}\n```'
    )
    assert result == {"hypotheses": []}


def test_extracts_json_surrounded_by_text():
    result = _extract_json(
        'Here is the result:\n{"hypotheses": []}\nFinished.'
    )
    assert result == {"hypotheses": []}


def test_rejects_missing_json():
    with pytest.raises(ValueError, match="did not return"):
        _extract_json("No structured response.")


def test_rejects_invalid_json():
    with pytest.raises(ValueError, match="invalid JSON"):
        _extract_json('{"hypotheses": }')


def test_rejects_non_object_json():
    with pytest.raises(ValueError, match="JSON object"):
        _extract_json('["not", "an", "object"]')
