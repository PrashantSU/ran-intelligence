"""Shared state contract for incident investigation workflows."""

from typing import Literal, TypedDict

from ran_intelligence.agents.schemas import (
    EvidenceItem,
    IncidentHypothesis,
    IncidentReport,
    IncidentRequest,
)
from ran_intelligence.agents.tools import ToolExecutionResult


class InvestigationState(TypedDict, total=False):
    """Data shared between nodes in an incident investigation graph."""

    incident: IncidentRequest
    evidence: list[EvidenceItem]
    tool_results: dict[str, ToolExecutionResult]
    completed_tools: list[str]
    hypotheses: list[IncidentHypothesis]
    report: IncidentReport | None
    errors: list[str]
    investigation_status: Literal[
        "running",
        "completed",
        "insufficient_evidence",
        "failed",
    ]
    pending_review: bool
    review_approved: bool | None
    human_feedback: str | None
    current_step: str


def create_initial_state(
    incident: IncidentRequest,
) -> InvestigationState:
    """Create a clean initial state for a new investigation."""
    return {
        "incident": incident,
        "evidence": [],
        "tool_results": {},
        "completed_tools": [],
        "hypotheses": [],
        "report": None,
        "errors": [],
        "investigation_status": "running",
        "pending_review": False,
        "review_approved": None,
        "human_feedback": None,
        "current_step": "initialised",
    }
