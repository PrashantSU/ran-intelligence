
"""Structured observability and audit traces for RAN investigations."""

from __future__ import annotations

import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


def _get(value: Any, key: str, default: Any = None) -> Any:
    if isinstance(value, dict):
        return value.get(key, default)
    return getattr(value, key, default)


def _json_safe(value: Any) -> Any:
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if hasattr(value, "value"):
        return value.value
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


class TraceRecorder:
    """Collect structured investigation events and persist them as JSONL."""

    def __init__(self, incident_id: str | None = None):
        self.incident_id = str(incident_id) if incident_id else None
        self.events: list[dict[str, Any]] = []

    def _record(self, event_type: str, details: dict[str, Any]) -> dict[str, Any]:
        event = {
            "event_id": str(uuid4()),
            "timestamp": datetime.now(UTC).isoformat(),
            "incident_id": self.incident_id,
            "event_type": event_type,
            "details": _json_safe(details),
        }
        self.events.append(event)
        return event

    def record_tool_result(
        self,
        tool_name: str,
        result: Any,
    ) -> dict[str, Any]:
        """Record execution metadata without copying raw tool output."""
        evidence = _get(result, "evidence", []) or []
        return self._record(
            "tool_execution",
            {
                "tool_name": tool_name,
                "status": _get(result, "status", "unknown"),
                "latency_ms": float(_get(result, "latency_ms", 0.0) or 0.0),
                "evidence_count": len(evidence),
                "error": _get(result, "error"),
            },
        )

    def record_workflow_state(self, state: Any) -> dict[str, Any]:
        """Record the final workflow and human-review state."""
        incident = _get(state, "incident")
        incident_id = _get(incident, "incident_id")
        if incident_id is not None:
            self.incident_id = str(incident_id)

        evidence = _get(state, "evidence", []) or []
        completed_tools = _get(state, "completed_tools", []) or []
        errors = _get(state, "errors", []) or []
        report = _get(state, "report")

        return self._record(
            "workflow_completed",
            {
                "investigation_status": _get(
                    state, "investigation_status", "unknown"
                ),
                "completed_tools": list(completed_tools),
                "evidence_count": len(evidence),
                "report_generated": report is not None,
                "pending_review": bool(_get(state, "pending_review", False)),
                "review_approved": _get(state, "review_approved"),
                "current_step": _get(state, "current_step"),
                "error_count": len(errors),
            },
        )

    def record_investigation(self, state: Any) -> list[dict[str, Any]]:
        """Record all tool results followed by the final workflow state."""
        tool_results = _get(state, "tool_results", {}) or {}
        for tool_name, result in tool_results.items():
            self.record_tool_result(tool_name, result)
        self.record_workflow_state(state)
        return self.events

    def summary(self) -> dict[str, Any]:
        tool_events = [
            event for event in self.events
            if event["event_type"] == "tool_execution"
        ]
        statuses = Counter(
            event["details"]["status"] for event in tool_events
        )
        latencies = [
            event["details"]["latency_ms"] for event in tool_events
        ]
        return {
            "incident_id": self.incident_id,
            "event_count": len(self.events),
            "tool_count": len(tool_events),
            "status_counts": dict(statuses),
            "total_latency_ms": sum(latencies),
            "mean_latency_ms": (
                sum(latencies) / len(latencies) if latencies else 0.0
            ),
            "failed_tools": [
                event["details"]["tool_name"]
                for event in tool_events
                if event["details"]["status"] != "success"
            ],
        }

    def save_jsonl(self, path: str | Path) -> Path:
        """Write one JSON event per line and return the saved path."""
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as file:
            for event in self.events:
                file.write(
                    json.dumps(event, ensure_ascii=False, allow_nan=False)
                    + chr(10)
                )
        return output_path
