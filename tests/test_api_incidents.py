
import importlib
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient

api_module = importlib.import_module("ran_intelligence.api.app")


class FakeIncidentService:
    def __init__(self):
        self.started_incident = None
        self.review_args = None

    def start(self, incident):
        self.started_incident = incident
        return {
            "thread_id": str(incident.incident_id),
            "incident_id": str(incident.incident_id),
            "current_step": "awaiting_human_review",
            "investigation_status": "completed",
            "pending_review": True,
            "review_approved": None,
            "human_feedback": None,
            "completed_tools": ["kpi", "anomaly"],
            "errors": [],
            "report": {"summary": "Mock investigation report"},
            "review_request": {"message": "Please review this report"},
        }

    def get(self, thread_id):
        if thread_id == "unknown":
            raise KeyError(f"Unknown investigation: {thread_id}")
        return {
            "thread_id": thread_id,
            "current_step": "awaiting_human_review",
            "pending_review": True,
        }

    def review(self, thread_id, approved, feedback):
        if thread_id == "unknown":
            raise KeyError(f"Unknown investigation: {thread_id}")
        if thread_id == "already-reviewed":
            raise ValueError("Investigation is not awaiting review.")
        self.review_args = (thread_id, approved, feedback)
        return {
            "thread_id": thread_id,
            "current_step": "approved" if approved else "review_rejected",
            "pending_review": False,
            "review_approved": approved,
            "human_feedback": feedback,
        }


@pytest.fixture
def client_and_service(monkeypatch):
    service = FakeIncidentService()
    monkeypatch.setattr(
        api_module,
        "get_incident_service",
        lambda request: service,
    )
    with TestClient(api_module.create_app()) as client:
        yield client, service


def valid_payload():
    end = datetime.now(UTC)
    start = end - timedelta(minutes=10)
    return {
        "description": "Investigate potential NR radio-quality degradation.",
        "session_id": "yaw315",
        "start_time": start.isoformat(),
        "end_time": end.isoformat(),
        "severity": "medium",
        "suspected_kpis": ["nr_sinr_db", "nr_rsrp_dbm"],
    }


def test_submit_incident(client_and_service):
    client, service = client_and_service

    response = client.post("/api/v1/incidents", json=valid_payload())

    assert response.status_code == 200
    payload = response.json()
    assert payload["current_step"] == "awaiting_human_review"
    assert payload["pending_review"] is True
    assert payload["report"]["summary"] == "Mock investigation report"
    assert service.started_incident is not None
    assert service.started_incident.session_id == "yaw315"


def test_submit_incident_rejects_invalid_time_window(client_and_service):
    client, _ = client_and_service
    payload = valid_payload()
    payload["end_time"] = payload["start_time"]

    response = client.post("/api/v1/incidents", json=payload)

    assert response.status_code == 422


def test_get_incident_state(client_and_service):
    client, _ = client_and_service

    response = client.get("/api/v1/incidents/test-thread")

    assert response.status_code == 200
    assert response.json()["thread_id"] == "test-thread"
    assert response.json()["pending_review"] is True


def test_get_unknown_incident_returns_404(client_and_service):
    client, _ = client_and_service

    response = client.get("/api/v1/incidents/unknown")

    assert response.status_code == 404


@pytest.mark.parametrize(
    ("approved", "expected_step"),
    [
        (True, "approved"),
        (False, "review_rejected"),
    ],
)
def test_submit_human_review(
    client_and_service,
    approved,
    expected_step,
):
    client, service = client_and_service
    feedback = "Reviewed by an engineer."

    response = client.post(
        "/api/v1/incidents/test-thread/review",
        json={"approved": approved, "feedback": feedback},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["pending_review"] is False
    assert payload["review_approved"] is approved
    assert payload["current_step"] == expected_step
    assert payload["human_feedback"] == feedback
    assert service.review_args == ("test-thread", approved, feedback)


def test_review_unknown_incident_returns_404(client_and_service):
    client, _ = client_and_service

    response = client.post(
        "/api/v1/incidents/unknown/review",
        json={"approved": True},
    )

    assert response.status_code == 404


def test_review_already_reviewed_incident_returns_409(client_and_service):
    client, _ = client_and_service

    response = client.post(
        "/api/v1/incidents/already-reviewed/review",
        json={"approved": True},
    )

    assert response.status_code == 409


def test_incident_routes_are_documented(client_and_service):
    client, _ = client_and_service
    schema = client.get("/openapi.json").json()
    paths = schema["paths"]

    assert "/api/v1/incidents" in paths
    assert "/api/v1/incidents/{thread_id}" in paths
    assert "/api/v1/incidents/{thread_id}/review" in paths
