
from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from ran_intelligence.agents.schemas import (
    EvidenceItem,
    IncidentHypothesis,
    IncidentReport,
    IncidentRequest,
)


@pytest.fixture
def incident():
    start = datetime(2026, 11, 18, 10, tzinfo=UTC)

    return IncidentRequest(
        description="Unexpected throughput degradation",
        session_id="yaw315",
        cell_id="cell_001",
        start_time=start,
        end_time=start + timedelta(minutes=10),
        severity="high",
        suspected_kpis=["throughput", "sinr"],
    )


def test_incident_request_creation(incident):
    assert incident.description == "Unexpected throughput degradation"
    assert incident.severity == "high"
    assert incident.incident_id


def test_incident_rejects_invalid_severity():
    start = datetime.now(UTC)

    with pytest.raises(ValidationError):
        IncidentRequest(
            description="Throughput degradation",
            start_time=start,
            end_time=start + timedelta(minutes=5),
            severity="extreme",
        )


def test_evidence_item_creation():
    evidence = EvidenceItem(
        evidence_type="kpi",
        description="Mean SINR decreased by 2.1 dB",
        source="kpi_analytics",
        observed_value="-2.1 dB",
    )

    assert evidence.evidence_id
    assert evidence.evidence_type == "kpi"


def test_hypothesis_confidence_is_bounded():
    with pytest.raises(ValidationError):
        IncidentHypothesis(
            title="Possible interference",
            explanation="SINR degradation may indicate increased interference.",
            confidence=1.5,
        )


def test_hypothesis_tracks_supporting_and_contradicting_evidence():
    hypothesis = IncidentHypothesis(
        title="Possible interference",
        explanation="Increased interference may explain the SINR degradation.",
        confidence=0.65,
        supporting_evidence_ids=["evidence-1"],
        contradicting_evidence_ids=["evidence-2"],
        status="plausible",
    )

    assert hypothesis.supporting_evidence_ids == ["evidence-1"]
    assert hypothesis.contradicting_evidence_ids == ["evidence-2"]


def test_report_requires_human_review(incident):
    report = IncidentReport(
        incident_id=incident.incident_id,
        summary="Throughput degradation was observed.",
        limitations=["Available measurements are limited."],
    )

    assert report.requires_human_review is True
    assert report.investigation_status == "completed"


def test_report_can_mark_insufficient_evidence(incident):
    report = IncidentReport(
        incident_id=incident.incident_id,
        summary="Available evidence is insufficient to determine a cause.",
        investigation_status="insufficient_evidence",
    )

    assert report.investigation_status == "insufficient_evidence"
    assert report.hypotheses == []