
"""Structured data contracts for incident investigation."""

from datetime import datetime
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field


class IncidentRequest(BaseModel):
    """Input submitted by an engineer for investigation."""

    incident_id: str = Field(
        default_factory=lambda: str(uuid4())
    )
    description: str = Field(min_length=5)
    session_id: str | None = None
    cell_id: str | None = None
    start_time: datetime
    end_time: datetime
    severity: Literal["low", "medium", "high", "critical"] = "medium"
    suspected_kpis: list[str] = Field(default_factory=list)

    class Config:
        extra = "forbid"


class EvidenceItem(BaseModel):
    """A traceable observation collected during investigation."""

    evidence_id: str = Field(
        default_factory=lambda: str(uuid4())
    )
    evidence_type: Literal[
        "kpi",
        "anomaly",
        "forecast",
        "rag",
        "simulation",
        "historical",
    ]
    description: str = Field(min_length=1)
    source: str = Field(min_length=1)
    observed_value: str | None = None
    timestamp: datetime | None = None
    supports_hypothesis: bool | None = None
    metadata: dict = Field(default_factory=dict)

    class Config:
        extra = "forbid"


class IncidentHypothesis(BaseModel):
    """A possible explanation, explicitly separated from evidence."""

    hypothesis_id: str = Field(
        default_factory=lambda: str(uuid4())
    )
    title: str = Field(min_length=3)
    explanation: str = Field(min_length=5)
    confidence: float = Field(ge=0.0, le=1.0)
    supporting_evidence_ids: list[str] = Field(default_factory=list)
    contradicting_evidence_ids: list[str] = Field(default_factory=list)
    status: Literal[
        "plausible",
        "weakly_supported",
        "strongly_supported",
        "unresolved",
    ] = "unresolved"

    class Config:
        extra = "forbid"


class IncidentReport(BaseModel):
    """Human-reviewable result of an investigation."""

    incident_id: str
    summary: str = Field(min_length=1)
    evidence: list[EvidenceItem] = Field(default_factory=list)
    hypotheses: list[IncidentHypothesis] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    requires_human_review: bool = True
    investigation_status: Literal[
        "completed",
        "insufficient_evidence",
        "failed",
    ] = "completed"

    class Config:
        extra = "forbid"