
import pytest

from ran_intelligence.agents.schemas import IncidentRequest
from ran_intelligence.agents.tools import InvestigationToolbox
from ran_intelligence.evaluation.agent import evaluate_agent_run


@pytest.fixture
def incident():
    return IncidentRequest(
        description="Throughput degradation",
        session_id="yaw315",
        cell_id="1",
        start_time="2026-01-15T10:00:00",
        end_time="2026-01-15T10:15:00",
        severity="high",
    )


def test_tool_execution_records_latency(incident):
    toolbox = InvestigationToolbox({
        "kpi": lambda _: {"mean_throughput": 120.0},
    })
    result = toolbox.run("kpi", incident)

    assert result.status == "success"
    assert result.latency_ms >= 0
    assert result.raw_output["mean_throughput"] == 120.0


def test_failed_tool_records_latency(incident):
    def fail(_):
        raise RuntimeError("Test failure")

    result = InvestigationToolbox({"kpi": fail}).run("kpi", incident)

    assert result.status == "failed"
    assert "RuntimeError" in result.error
    assert result.latency_ms >= 0


def test_unavailable_tool_records_latency(incident):
    result = InvestigationToolbox({}).run("kpi", incident)

    assert result.status == "unavailable"
    assert result.latency_ms >= 0


def test_agent_evaluation_counts_results(incident):
    toolbox = InvestigationToolbox({
        "kpi": lambda _: {"value": 10},
        "anomaly": lambda _: (_ for _ in ()).throw(
            RuntimeError("Failure")
        ),
    })

    results = toolbox.run_all(incident)
    result_map = {item.tool_name: item for item in results}

    metrics = evaluate_agent_run(result_map)

    assert metrics["tool_count"] == 2
    assert metrics["status_counts"]["success"] == 1
    assert metrics["status_counts"]["failed"] == 1
    assert metrics["success_rate"] == 0.5
    assert metrics["evidence_count"] == 1
    assert metrics["latency"]["total_ms"] >= 0


def test_agent_evaluation_handles_empty_results():
    metrics = evaluate_agent_run({})

    assert metrics["tool_count"] == 0
    assert metrics["success_rate"] == 0
    assert metrics["latency"]["mean_ms"] == 0
    assert len(metrics["missing_tools"]) == 5


def test_agent_evaluation_includes_review_state(incident):
    result = InvestigationToolbox({
        "kpi": lambda _: {"value": 10},
    }).run("kpi", incident)

    metrics = evaluate_agent_run(
        {"kpi": result},
        {
            "completed_tools": ["kpi"],
            "pending_review": True,
            "review_approved": None,
            "investigation_status": "completed",
        },
    )

    assert metrics["investigation_status"] == "completed"
    assert metrics["human_review"]["pending"] is True
    assert metrics["human_review"]["approved"] is None


def test_negative_latency_rejected(incident):
    result = InvestigationToolbox({
        "kpi": lambda _: {"value": 10},
    }).run("kpi", incident)

    result.latency_ms = -1

    with pytest.raises(ValueError, match="negative"):
        evaluate_agent_run({"kpi": result})
