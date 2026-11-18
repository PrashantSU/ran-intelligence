"""Evaluation metrics for incident investigation agent executions."""

from collections import Counter
from collections.abc import Mapping
from statistics import mean
from typing import Any

DEFAULT_TOOLS = ("kpi", "anomaly", "forecast", "rag", "simulation")


def evaluate_agent_run(
    tool_results: Mapping[str, Any],
    investigation_state: Mapping[str, Any] | None = None,
    expected_tools: tuple[str, ...] = DEFAULT_TOOLS,
) -> dict[str, Any]:
    """Evaluate tool execution, evidence production and investigation outcome."""
    if isinstance(tool_results, Mapping):
        results = list(tool_results.values())
    elif isinstance(tool_results, (list, tuple)):
        results = list(tool_results)
    else:
        raise TypeError(
            "tool_results must be a mapping or a list/tuple of ToolExecutionResult objects"
        )
    statuses = Counter(result.status for result in results)

    invalid_statuses = set(statuses) - {"success", "failed", "unavailable"}
    if invalid_statuses:
        raise ValueError(f"Unsupported tool statuses: {sorted(invalid_statuses)}")

    latencies = [float(result.latency_ms) for result in results]
    if any(value < 0 for value in latencies):
        raise ValueError("Tool latency cannot be negative")

    evidence_counts = {
        result.tool_name: len(result.evidence)
        for result in results
    }

    attempted = len(results)
    successful = statuses["success"]
    failed = statuses["failed"]
    unavailable = statuses["unavailable"]

    state = investigation_state or {}
    completed_tools = state.get("completed_tools", [])
    expected = set(expected_tools)
    observed = {result.tool_name for result in results}

    report = state.get("report")
    report_status = (
        report.investigation_status
        if report is not None
        else state.get("investigation_status")
    )

    return {
        "tool_count": attempted,
        "status_counts": {
            "success": successful,
            "failed": failed,
            "unavailable": unavailable,
        },
        "success_rate": successful / attempted if attempted else 0.0,
        "failure_rate": failed / attempted if attempted else 0.0,
        "unavailable_rate": unavailable / attempted if attempted else 0.0,
        "evidence_count": sum(evidence_counts.values()),
        "evidence_by_tool": evidence_counts,
        "tools_without_evidence": [
            name for name, count in evidence_counts.items() if count == 0
        ],
        "expected_tools": sorted(expected),
        "missing_tools": sorted(expected - observed),
        "completed_tools": list(completed_tools),
        "latency": {
            "total_ms": sum(latencies),
            "mean_ms": mean(latencies) if latencies else 0.0,
            "max_ms": max(latencies, default=0.0),
            "per_tool_ms": {
                result.tool_name: float(result.latency_ms)
                for result in results
            },
        },
        "investigation_status": report_status,
        "human_review": {
            "pending": state.get("pending_review", False),
            "approved": state.get("review_approved"),
        },
    }
