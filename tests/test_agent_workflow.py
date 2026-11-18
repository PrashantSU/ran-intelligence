"""Tests for the LangGraph incident investigation workflow."""

import pytest
from langgraph.types import Command

from ran_intelligence.agents.schemas import (
    EvidenceItem,
    IncidentRequest,
)
from ran_intelligence.agents.state import create_initial_state
from ran_intelligence.agents.tools import ToolExecutionResult
from ran_intelligence.agents.workflow import build_investigation_graph


class FakeToolbox:
    def __init__(self, evidence_by_tool):
        self.evidence_by_tool = evidence_by_tool
        self.calls = []

    def run(self, tool_name, incident):
        self.calls.append(tool_name)
        evidence = self.evidence_by_tool.get(tool_name, [])
        return ToolExecutionResult(
            tool_name=tool_name,
            status="success" if evidence else "failed",
            evidence=evidence,
            error=None if evidence else "No evidence available",
        )


def make_incident():
    return IncidentRequest(
        description="SINR degradation",
        session_id="session_a",
        cell_id="1",
        start_time="2026-11-18T10:00:00Z",
        end_time="2026-11-18T10:05:00Z",
        severity="high",
        suspected_kpis=["lte_sinr_db"],
    )


def make_evidence():
    return EvidenceItem(
        evidence_id="ev-001",
        evidence_type="anomaly",
        description="Low LTE SINR observed in the incident window.",
        source="anomaly_detector",
        observed_value="2 dB",
        supports_hypothesis=None,
        metadata={"kpi": "lte_sinr_db"},
    )


def make_config(thread_id="test-investigation"):
    return {"configurable": {"thread_id": thread_id}}


def pause_for_review(graph, incident=None, thread_id="test-investigation"):
    config = make_config(thread_id)
    result = graph.invoke(
        create_initial_state(incident or make_incident()),
        config=config,
    )
    assert result["pending_review"] is True
    assert result["review_approved"] is None
    assert result["current_step"] == "awaiting_human_review"
    assert graph.get_state(config).next == ("human_review",)
    return result, config


def test_workflow_runs_tools_and_collects_evidence():
    evidence = make_evidence()
    toolbox = FakeToolbox({"kpi": [evidence], "anomaly": [evidence]})
    graph = build_investigation_graph(
        toolbox,
        tool_names=("kpi", "anomaly"),
    )

    result, config = pause_for_review(graph)

    assert toolbox.calls == ["kpi", "anomaly"]
    assert len(result["evidence"]) == 2
    assert result["completed_tools"] == ["kpi", "anomaly"]
    assert result["investigation_status"] == "completed"

    final = graph.invoke(
        Command(resume={"approved": True, "feedback": "Evidence reviewed."}),
        config=config,
    )

    assert final["review_approved"] is True
    assert final["human_feedback"] == "Evidence reviewed."
    assert final["pending_review"] is False
    assert final["current_step"] == "review_approved"
    assert toolbox.calls == ["kpi", "anomaly"]


def test_workflow_pauses_with_report_for_human_review():
    toolbox = FakeToolbox({"kpi": [make_evidence()]})
    graph = build_investigation_graph(
        toolbox,
        tool_names=("kpi",),
    )

    result, config = pause_for_review(graph)

    assert result["report"] is not None
    assert result["report"].requires_human_review is True

    snapshot = graph.get_state(config)
    assert snapshot.tasks[0].interrupts
    payload = snapshot.tasks[0].interrupts[0].value
    assert payload["type"] == "human_review"
    assert payload["report"]["summary"] == result["report"].summary


def test_workflow_accepts_human_rejection_and_feedback():
    toolbox = FakeToolbox({"kpi": [make_evidence()]})
    graph = build_investigation_graph(toolbox, tool_names=("kpi",))

    _, config = pause_for_review(graph, thread_id="rejection-test")

    final = graph.invoke(
        Command(resume={
            "approved": False,
            "feedback": "Insufficient evidence for this conclusion.",
        }),
        config=config,
    )

    assert final["review_approved"] is False
    assert final["human_feedback"] == (
        "Insufficient evidence for this conclusion."
    )
    assert final["pending_review"] is False
    assert final["current_step"] == "review_rejected"


def test_workflow_marks_empty_investigation_as_insufficient():
    toolbox = FakeToolbox({})
    graph = build_investigation_graph(
        toolbox,
        tool_names=("kpi",),
    )

    result, config = pause_for_review(graph, thread_id="empty-test")

    assert result["evidence"] == []
    assert result["investigation_status"] == "insufficient_evidence"
    assert result["report"].investigation_status == "insufficient_evidence"
    assert result["pending_review"] is True

    final = graph.invoke(
        Command(resume={"approved": True}),
        config=config,
    )
    assert final["review_approved"] is True


def test_workflow_records_tool_failures():
    toolbox = FakeToolbox({})
    graph = build_investigation_graph(
        toolbox,
        tool_names=("kpi", "anomaly"),
    )

    result, _ = pause_for_review(graph, thread_id="failures-test")

    assert len(result["errors"]) == 2
    assert "kpi: No evidence available" in result["errors"]
    assert "anomaly: No evidence available" in result["errors"]


def test_workflow_rejects_empty_tool_configuration():
    toolbox = FakeToolbox({})

    with pytest.raises(ValueError, match="At least one"):
        build_investigation_graph(toolbox, tool_names=())


def test_workflow_rejects_invalid_review_decision():
    toolbox = FakeToolbox({"kpi": [make_evidence()]})
    graph = build_investigation_graph(toolbox, tool_names=("kpi",))

    _, config = pause_for_review(graph, thread_id="invalid-review-test")

    with pytest.raises(ValueError, match="boolean"):
        graph.invoke(
            Command(resume={"approved": "yes"}),
            config=config,
        )
