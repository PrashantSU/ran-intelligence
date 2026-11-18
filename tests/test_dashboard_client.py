"""Tests for the Streamlit dashboard API client."""

import pytest
import requests

from ran_intelligence.dashboard.client import api_request


class FakeResponse:
    def __init__(self, payload=None, status_code=200, content=b"data"):
        self.payload = payload or {}
        self.status_code = status_code
        self.content = content
        self.text = "request failed"

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError("HTTP error")

    def json(self):
        return self.payload


def test_api_request_uses_configured_base_url(monkeypatch):
    monkeypatch.setenv("RAN_API_BASE_URL", "http://localhost:8000/")
    calls = {}

    def fake_request(**kwargs):
        calls.update(kwargs)
        return FakeResponse({"status": "ok"})

    monkeypatch.setattr(requests, "request", fake_request)

    result = api_request("get", "/health")

    assert result == {"status": "ok"}
    assert calls["url"] == "http://localhost:8000/health"
    assert calls["method"] == "GET"


def test_api_request_sends_json_payload(monkeypatch):
    calls = {}

    def fake_request(**kwargs):
        calls.update(kwargs)
        return FakeResponse({"accepted": True})

    monkeypatch.setattr(requests, "request", fake_request)

    payload = {"query": "5G NR"}
    result = api_request("post", "/api/v1/rag/search", payload)

    assert result == {"accepted": True}
    assert calls["json"] == payload


def test_api_request_reports_http_errors(monkeypatch):
    def fake_request(**kwargs):
        return FakeResponse(
            {"detail": "Invalid request"},
            status_code=422,
        )

    monkeypatch.setattr(requests, "request", fake_request)

    with pytest.raises(RuntimeError, match="HTTP 422"):
        api_request("post", "/api/v1/rag/search", {})


def test_api_request_reports_connection_errors(monkeypatch):
    def fake_request(**kwargs):
        raise requests.ConnectionError("offline")

    monkeypatch.setattr(requests, "request", fake_request)

    with pytest.raises(RuntimeError, match="Could not reach"):
        api_request("get", "/health")
