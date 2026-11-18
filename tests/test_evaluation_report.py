
from ran_intelligence.evaluation.report import evaluate_incident_report


def make_report():
    return {
        "summary": "Investigation collected evidence.",
        "evidence": [
            {"evidence_id": "e1"},
            {"evidence_id": "e2"},
        ],
        "hypotheses": [
            {
                "supporting_evidence_ids": ["e1"],
                "contradicting_evidence_ids": ["e2"],
            }
        ],
        "limitations": ["Evidence does not confirm root cause."],
        "recommended_actions": ["Review telemetry."],
        "requires_human_review": True,
        "investigation_status": "completed",
    }


def test_complete_report_passes():
    report = make_report()
    result = evaluate_incident_report(report)

    assert result["passed"] is True
    assert result["score"] == 1.0
    assert result["invalid_evidence_references"] == []


def test_invalid_hypothesis_evidence_reference_fails():
    report = make_report()
    report["hypotheses"][0]["supporting_evidence_ids"] = ["missing"]

    result = evaluate_incident_report(report)

    assert result["passed"] is False
    assert result["checks"]["hypothesis_references_valid"] is False
    assert result["invalid_evidence_references"] == ["missing"]


def test_missing_human_review_fails():
    report = make_report()
    report["requires_human_review"] = False

    result = evaluate_incident_report(report)

    assert result["checks"]["human_review_required"] is False


def test_duplicate_evidence_ids_fail():
    report = make_report()
    report["evidence"].append({"evidence_id": "e1"})

    result = evaluate_incident_report(report)

    assert result["checks"]["evidence_ids_unique"] is False


def test_missing_report_returns_failure():
    result = evaluate_incident_report(None)

    assert result["passed"] is False
    assert result["score"] == 0.0


def test_workflow_consistency_is_checked():
    report = make_report()
    state = {
        "investigation_status": "completed",
        "evidence": report["evidence"],
    }

    result = evaluate_incident_report(
        report,
        investigation_state=state,
    )

    assert result["passed"] is True
    assert result["checks"]["workflow_report_status_consistent"]
    assert result["checks"]["workflow_evidence_consistent"]


def test_workflow_status_mismatch_fails():
    report = make_report()
    state = {
        "investigation_status": "failed",
        "evidence": report["evidence"],
    }

    result = evaluate_incident_report(
        report,
        investigation_state=state,
    )

    assert result["checks"]["workflow_report_status_consistent"] is False
