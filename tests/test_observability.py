
import json

from ran_intelligence.evaluation.observability import TraceRecorder


def test_records_tool_execution_metadata_without_raw_output():
    recorder = TraceRecorder("incident-1")
    result = {
        "status": "success",
        "latency_ms": 12.5,
        "evidence": [{"evidence_id": "e1"}],
        "raw_output": {"large": "payload"},
    }

    event = recorder.record_tool_result("kpi", result)

    assert event["event_type"] == "tool_execution"
    assert event["incident_id"] == "incident-1"
    assert event["details"]["tool_name"] == "kpi"
    assert event["details"]["evidence_count"] == 1
    assert event["details"]["latency_ms"] == 12.5
    assert "raw_output" not in event["details"]


def test_records_final_workflow_and_review_state():
    recorder = TraceRecorder()
    state = {
        "incident": {"incident_id": "incident-2"},
        "evidence": [{"evidence_id": "e1"}],
        "completed_tools": ["kpi", "rag"],
        "tool_results": {},
        "report": {"summary": "Test report"},
        "investigation_status": "completed",
        "pending_review": False,
        "review_approved": True,
        "current_step": "review_approved",
        "errors": [],
    }

    event = recorder.record_workflow_state(state)

    assert recorder.incident_id == "incident-2"
    assert event["details"]["report_generated"] is True
    assert event["details"]["review_approved"] is True
    assert event["details"]["completed_tools"] == ["kpi", "rag"]


def test_records_full_investigation():
    recorder = TraceRecorder()
    state = {
        "incident": {"incident_id": "incident-3"},
        "tool_results": {
            "kpi": {
                "status": "success",
                "latency_ms": 10,
                "evidence": [{}],
            },
            "rag": {
                "status": "failed",
                "latency_ms": 20,
                "evidence": [],
                "error": "Unavailable",
            },
        },
        "evidence": [{}],
        "completed_tools": ["kpi", "rag"],
        "report": {"summary": "Report"},
        "investigation_status": "completed",
        "pending_review": False,
        "review_approved": True,
        "current_step": "review_approved",
        "errors": ["rag: Unavailable"],
    }

    events = recorder.record_investigation(state)

    assert len(events) == 3
    assert events[-1]["event_type"] == "workflow_completed"
    assert recorder.summary()["tool_count"] == 2
    assert recorder.summary()["status_counts"] == {
        "success": 1,
        "failed": 1,
    }
    assert recorder.summary()["total_latency_ms"] == 30
    assert recorder.summary()["failed_tools"] == ["rag"]


def test_saves_jsonl_and_reads_back(tmp_path):
    recorder = TraceRecorder("incident-4")
    recorder.record_tool_result(
        "forecast",
        {"status": "success", "latency_ms": 5, "evidence": [{}]},
    )
    recorder.record_workflow_state({
        "investigation_status": "completed",
        "completed_tools": ["forecast"],
        "evidence": [{}],
        "report": {"summary": "Report"},
        "pending_review": False,
        "review_approved": True,
        "current_step": "review_approved",
        "errors": [],
    })

    output = recorder.save_jsonl(tmp_path / "traces" / "run.jsonl")
    rows = [json.loads(line) for line in output.read_text().splitlines()]

    assert output.exists()
    assert len(rows) == 2
    assert rows[0]["event_type"] == "tool_execution"
    assert rows[1]["event_type"] == "workflow_completed"


def test_empty_recorder_summary():
    summary = TraceRecorder().summary()

    assert summary["event_count"] == 0
    assert summary["tool_count"] == 0
    assert summary["mean_latency_ms"] == 0.0
    assert summary["failed_tools"] == []
