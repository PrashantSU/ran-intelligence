"""Small HTTP client for the RAN Intelligence API."""

import os

import requests


def _get_base_url() -> str:
    """Get API URL from environment variables or Streamlit secrets."""
    base_url = os.getenv("RAN_API_BASE_URL")

    if not base_url:
        try:
            import streamlit as st
            base_url = st.secrets.get("RAN_API_BASE_URL")
        except Exception:
            base_url = None

    return (base_url or "http://127.0.0.1:8000").rstrip("/")


def api_request(method: str, path: str, payload: dict | None = None):
    """Call the configured API and return its JSON response."""
    base_url = _get_base_url()
    url = f"{base_url}/{path.lstrip('/')}"

    try:
        response = requests.request(
            method=method.upper(),
            url=url,
            json=payload,
            timeout=180,
        )
        response.raise_for_status()
    except requests.HTTPError as exc:
        try:
            detail = response.json()
        except ValueError:
            detail = response.text
        raise RuntimeError(
            f"API returned HTTP {response.status_code}: {detail}"
        ) from exc
    except requests.RequestException as exc:
        raise RuntimeError(
            f"Could not reach the RAN API at {base_url}. "
            "Check that the API server is running."
        ) from exc

    if not response.content:
        return {}

    return response.json()
