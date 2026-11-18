from datetime import UTC, datetime, timedelta

import pandas as pd
import pytest

from ran_intelligence.agents.schemas import (
    EvidenceItem,
    IncidentRequest,
)
from ran_intelligence.agents.tools import InvestigationToolbox


@pytest.fixture
def incident():
    start = datetime(2026, 11, 18, 10, tzinfo=UTC)

    return IncidentRequest(
        description="Unexpected throughput degradation",
        session_id="yaw315",
        cell_id="cell_001",
        start_time=start,
        end_time=start + timedelta(minutes=10),
        severity="high",
    )


def test_available_tools():
    toolbox = InvestigationToolbox({
        "kpi": lambda incident: {"mean_sinr_db": 8.2},
        "anomaly": lambda incident: {"anomaly_count": 3},
    })

    assert toolbox.available_tools == ["anomaly", "kpi"]


def test_tool_output_becomes_structured_evidence(incident):
    toolbox = InvestigationToolbox({
        "kpi": lambda incident: {
            "mean_sinr_db": 8.2,
            "mean_throughput_mbps": 12.5,
        }
    })

    result = toolbox.run("kpi", incident)

    assert result.status == "success"
    assert len(result.evidence) == 1
    assert result.evidence[0].evidence_type == "kpi"
    assert result.evidence[0].source == "kpi"
    assert "mean_sinr_db" in result.evidence[0].description


def test_dataframe_output_is_supported(incident):
    frame = pd.DataFrame({
        "kpi": ["SINR", "throughput"],
        "value": [8.2, 12.5],
    })

    toolbox = InvestigationToolbox({
        "kpi": lambda incident: frame,
    })

    result = toolbox.run("kpi", incident)

    assert result.status == "success"
    assert result.evidence[0].metadata["row_count"] == 2
    assert len(result.evidence[0].metadata["records"]) == 2


def test_existing_evidence_item_is_preserved(incident):
    evidence = EvidenceItem(
        evidence_type="rag",
        description="3GPP reference describes the relevant procedure.",
        source="3gpp-ts-38-300",
    )

    toolbox = InvestigationToolbox({
        "rag": lambda incident: evidence,
    })

    result = toolbox.run("rag", incident)

    assert result.status == "success"
    assert result.evidence[0].evidence_id == evidence.evidence_id


def test_list_of_evidence_items_is_supported(incident):
    toolbox = InvestigationToolbox({
        "anomaly": lambda incident: [
            {"event": "SINR anomaly"},
            {"event": "Throughput anomaly"},
        ],
    })

    result = toolbox.run("anomaly", incident)

    assert result.status == "success"
    assert len(result.evidence) == 2


def test_missing_handler_returns_unavailable(incident):
    toolbox = InvestigationToolbox()

    result = toolbox.run("rag", incident)

    assert result.status == "unavailable"
    assert result.evidence == []
    assert result.error is not None


def test_handler_failure_is_captured(incident):
    def failing_handler(incident):
        raise RuntimeError("Index unavailable")

    toolbox = InvestigationToolbox({
        "rag": failing_handler,
    })

    result = toolbox.run("rag", incident)

    assert result.status == "failed"
    assert "Index unavailable" in result.error


def test_unknown_handler_is_rejected():
    with pytest.raises(ValueError, match="Unsupported investigation tools"):
        InvestigationToolbox({
            "unknown": lambda incident: {},
        })


def test_unknown_tool_execution_is_rejected(incident):
    toolbox = InvestigationToolbox()

    with pytest.raises(ValueError, match="Unknown investigation tool"):
        toolbox.run("unknown", incident)


def test_run_all_executes_configured_tools(incident):
    calls = []

    def handler(name):
        def execute(request):
            calls.append((name, request.incident_id))
            return {"tool": name}
        return execute

    toolbox = InvestigationToolbox({
        "kpi": handler("kpi"),
        "anomaly": handler("anomaly"),
        "rag": handler("rag"),
    })

    results = toolbox.run_all(incident)

    assert [result.tool_name for result in results] == [
        "anomaly", "kpi", "rag"
    ]
    assert len(calls) == 3
    assert all(result.status == "success" for result in results)


def test_dataframe_timestamps_are_json_safe():
    frame = pd.DataFrame({
        "timestamp": [pd.Timestamp("2026-11-18 10:00:00")],
        "value": [12.5],
    })

    converted = InvestigationToolbox._json_safe(frame)
    timestamp = converted["records"][0]["timestamp"]

    assert isinstance(timestamp, str)
    assert timestamp == "2026-11-18T10:00:00"


def test_nested_timestamps_are_json_safe():
    value = {
        "items": [
            {"timestamp": pd.Timestamp("2026-11-18 10:00:00")}
        ]
    }

    converted = InvestigationToolbox._json_safe(value)

    assert isinstance(converted["items"][0]["timestamp"], str)
