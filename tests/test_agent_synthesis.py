"""Tests for evidence-grounded hypothesis synthesis."""

import json

import pytest

from ran_intelligence.agents.schemas import EvidenceItem, IncidentRequest
from ran_intelligence.agents.state import create_initial_state
from ran_intelligence.agents.synthesis import (
    build_hypothesis_prompt,
    generate_grounded_hypotheses,
    parse_grounded_hypotheses,
)


@pytest.fixture
def incident():
    return IncidentRequest(
        description="SINR degradation",
        session_id="session_a",
        cell_id="1",
        start_time="2026-11-18T10:00:00Z",
        end_time="2026-11-18T10:05:00Z",
        severity="high",
        suspected_kpis=["lte_sinr_db"],
    )


@pytest.fixture
def evidence():
    return [
        EvidenceItem(
            evidence_id="ev-001",
            evidence_type="anomaly",
            description="LTE SINR dropped during the incident window.",
            source="anomaly_detector",
            observed_value="2 dB",
            metadata={"kpi": "lte_sinr_db"},
        ),
        EvidenceItem(
            evidence_id="ev-002",
            evidence_type="kpi",
            description="LTE RSRP remained stable.",
            source="kpi_analytics",
            observed_value="-80 dBm",
            metadata={"kpi": "lte_rsrp_dbm"},
        ),
    ]


def valid_payload():
    return {
        "hypotheses": [
            {
                "hypothesis_id": "hyp-001",
                "title": "Possible radio interference",
                "explanation": (
                    "SINR degradation with stable RSRP may be consistent "
                    "with increased interference, but does not prove it."
                ),
                "confidence": 0.55,
                "supporting_evidence_ids": ["ev-001", "ev-002"],
                "contradicting_evidence_ids": [],
                "status": "plausible",
            }
        ]
    }


def test_prompt_includes_incident_and_evidence(incident, evidence):
    state = create_initial_state(incident)
    state["evidence"] = evidence

    prompt = build_hypothesis_prompt(state)

    assert "SINR degradation" in prompt
    assert "ev-001" in prompt
    assert "ev-002" in prompt
    assert "Do not invent" in prompt


def test_parser_accepts_grounded_hypothesis(evidence):
    result = parse_grounded_hypotheses(valid_payload(), evidence)

    assert len(result) == 1
    assert result[0].hypothesis_id == "hyp-001"
    assert result[0].supporting_evidence_ids == ["ev-001", "ev-002"]


def test_parser_accepts_json_string(evidence):
    result = parse_grounded_hypotheses(
        json.dumps(valid_payload()),
        evidence,
    )

    assert len(result) == 1


def test_parser_rejects_unknown_evidence_reference(evidence):
    payload = valid_payload()
    payload["hypotheses"][0]["supporting_evidence_ids"] = ["fabricated-id"]

    with pytest.raises(ValueError, match="unknown evidence IDs"):
        parse_grounded_hypotheses(payload, evidence)


def test_parser_rejects_hypothesis_without_evidence(evidence):
    payload = valid_payload()
    payload["hypotheses"][0]["supporting_evidence_ids"] = []

    with pytest.raises(ValueError, match="no evidence references"):
        parse_grounded_hypotheses(payload, evidence)


def test_parser_rejects_evidence_used_on_both_sides(evidence):
    payload = valid_payload()
    payload["hypotheses"][0]["contradicting_evidence_ids"] = ["ev-001"]

    with pytest.raises(ValueError, match="both supporting and contradicting"):
        parse_grounded_hypotheses(payload, evidence)


def test_empty_evidence_skips_model_call(incident):
    state = create_initial_state(incident)

    def unexpected_call(prompt):
        raise AssertionError("Model should not be called without evidence.")

    assert generate_grounded_hypotheses(state, unexpected_call) == []


def test_generator_uses_injected_model(incident, evidence):
    state = create_initial_state(incident)
    state["evidence"] = evidence
    captured = {}

    def fake_generator(prompt):
        captured["prompt"] = prompt
        return valid_payload()

    result = generate_grounded_hypotheses(state, fake_generator)

    assert len(result) == 1
    assert "ev-001" in captured["prompt"]
