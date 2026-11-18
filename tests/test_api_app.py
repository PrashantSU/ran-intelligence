"""Tests for the FastAPI application foundation."""

from fastapi.testclient import TestClient

from ran_intelligence.api.app import create_app


def test_health_endpoint():
    app = create_app()

    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["app_name"]
    assert payload["environment"]
    assert payload["timestamp"]


def test_openapi_documentation_available():
    app = create_app()

    with TestClient(app) as client:
        response = client.get("/openapi.json")

    assert response.status_code == 200

    schema = response.json()
    assert schema["info"]["title"]
    assert "/health" in schema["paths"]


def test_application_does_not_load_heavy_services_on_startup():
    app = create_app()

    with TestClient(app):
        assert app.state.services == {}
        assert app.state.started_at is not None
