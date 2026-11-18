"""API request and response schemas."""

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from ran_intelligence.agents.schemas import IncidentRequest


class APIModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class HealthResponse(BaseModel):
    status: Literal["ok", "degraded"]
    app_name: str
    environment: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ErrorResponse(BaseModel):
    error: str
    message: str
    details: dict = Field(default_factory=dict)


class KpiTimeseriesRequest(APIModel):
    session_id: str = Field(min_length=1)
    metric: str = Field(min_length=1)
    interval: str = "1min"
    aggregation: Literal["mean", "median", "min", "max"] = "median"


class AnomalyRequest(APIModel):
    metrics: list[str] | None = None
    threshold: float = Field(default=3.5, gt=0, le=10)
    min_samples: int = Field(default=20, ge=5, le=1000)
    max_gap_seconds: float = Field(default=2.0, ge=0, le=60)
    limit: int = Field(default=100, ge=1, le=500)


class ForecastRequest(APIModel):
    session_id: str = Field(min_length=1)
    metric: str = Field(min_length=1)
    frequency: str = "1s"
    max_forward_fill: int = Field(default=2, ge=0, le=10)
    horizon_steps: int = Field(default=5, ge=1, le=60)
    test_fraction: float = Field(default=0.2, gt=0.05, lt=0.5)
    gap_steps: int = Field(default=5, ge=0, le=60)
    n_estimators: int = Field(default=100, ge=10, le=500)
    min_samples_leaf: int = Field(default=3, ge=1, le=50)
    limit: int = Field(default=100, ge=1, le=500)



class RAGSearchRequest(APIModel):
    query: str = Field(min_length=3, max_length=2000)
    top_k: int = Field(default=5, ge=1, le=10)
    candidate_k: int = Field(default=30, ge=5, le=100)
    rrf_k: int = Field(default=60, ge=1, le=200)




class IncidentSubmissionRequest(IncidentRequest):
    """Incident submission requiring a session for measurement filtering."""

    session_id: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_time_window(self):
        if self.end_time <= self.start_time:
            raise ValueError("end_time must be later than start_time.")
        return self


class IncidentReviewRequest(APIModel):
    """Human decision submitted for a pending investigation."""

    approved: bool
    feedback: str | None = Field(default=None, max_length=2000)
