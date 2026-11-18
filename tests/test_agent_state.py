"""Tests for the incident investigation state contract."""

from ran_intelligence.agents.schemas import IncidentRequest
from ran_intelligence.agents.state import (
    InvestigationState,
    create_initial_state,
)


def test_initial_state_contains_incident():
    incident = IncidentRequest(
        description="SINR degradation",
        session_id="session_a",
        cell_id="1",
        start_time="2026-11-18T10:00:00Z",
        end_time="2026-11-18T10:05:00Z",
        severity="high",
        suspected_kpis=["lte_sinr_db"],
    )

    state = create_initial_state(incident)

    assert state["incident"] == incident
    assert state["investigation_status"] == "running"
    assert state["current_step"] == "initialised"


def test_initial_state_starts_with_empty_collections():
    incident = IncidentRequest(
        description="Test incident",
        session_id="session_a",
        cell_id="1",
        start_time="2026-11-18T10:00:00Z",
        end_time="2026-11-18T10:05:00Z",
        severity="medium",
    )

    state = create_initial_state(incident)

    assert state["evidence"] == []
    assert state["tool_results"] == {}
    assert state["completed_tools"] == []
    assert state["hypotheses"] == []
    assert state["errors"] == []


def test_initial_state_has_no_report_or_review_decision():
    incident = IncidentRequest(
        description="Test incident",
        session_id="session_a",
        cell_id="1",
        start_time="2026-11-18T10:00:00Z",
        end_time="2026-11-18T10:05:00Z",
        severity="low",
    )

    state = create_initial_state(incident)

    assert state["report"] is None
    assert state["pending_review"] is False
    assert state["review_approved"] is None
    assert state["human_feedback"] is None


def test_state_is_a_typed_dict():
    assert InvestigationState.__total__ is False
    assert "incident" in InvestigationState.__annotations__
    assert "evidence" in InvestigationState.__annotations__
    assert "hypotheses" in InvestigationState.__annotations__
    assert "report" in InvestigationState.__annotations__
