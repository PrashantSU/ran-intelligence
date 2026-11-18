
"""Deterministic quality and evidence-integrity checks for incident reports."""

from __future__ import annotations

from typing import Any


def _get(value: Any, key: str, default: Any = None) -> Any:
    if isinstance(value, dict):
        return value.get(key, default)
    return getattr(value, key, default)


def evaluate_incident_report(
    report: Any,
    evidence: list[Any] | None = None,
    investigation_state: Any | None = None,
) -> dict[str, Any]:
    """Evaluate report completeness, evidence references and review controls."""

    if report is None:
        return {
            "passed": False,
            "score": 0.0,
            "checks": {},
            "warnings": ["No incident report was provided."],
            "invalid_evidence_references": [],
        }

    report_evidence = _get(report, "evidence", []) or []
    evidence_items = evidence if evidence is not None else report_evidence
    hypotheses = _get(report, "hypotheses", []) or []

    evidence_ids = [
        str(value)
        for item in evidence_items
        if (value := _get(item, "evidence_id")) is not None
    ]
    evidence_id_set = set(evidence_ids)

    referenced_ids: list[str] = []
    for hypothesis in hypotheses:
        referenced_ids.extend(
            str(value)
            for value in (
                _get(hypothesis, "supporting_evidence_ids", []) or []
            )
        )
        referenced_ids.extend(
            str(value)
            for value in (
                _get(hypothesis, "contradicting_evidence_ids", []) or []
            )
        )

    invalid_references = sorted(
        set(referenced_ids) - evidence_id_set
    )

    duplicate_evidence_ids = (
        len(evidence_ids) != len(evidence_id_set)
    )

    summary = _get(report, "summary")
    limitations = _get(report, "limitations", []) or []
    recommendations = _get(report, "recommended_actions", []) or []
    requires_review = _get(report, "requires_human_review", False)
    status = _get(report, "investigation_status")

    checks = {
        "summary_present": bool(summary and str(summary).strip()),
        "evidence_present": len(evidence_items) > 0,
        "limitations_present": len(limitations) > 0,
        "recommendations_present": len(recommendations) > 0,
        "human_review_required": requires_review is True,
        "evidence_ids_unique": not duplicate_evidence_ids,
        "hypothesis_references_valid": not invalid_references,
        "investigation_status_valid": status in {
            "completed", "insufficient_evidence"
        },
    }

    if investigation_state is not None:
        state_status = _get(
            investigation_state, "investigation_status"
        )
        report_status_consistent = (
            state_status is None or state_status == status
        )
        checks["workflow_report_status_consistent"] = (
            report_status_consistent
        )

        state_evidence = _get(
            investigation_state, "evidence", []
        ) or []
        checks["workflow_evidence_consistent"] = (
            len(state_evidence) == len(report_evidence)
        )

    passed_count = sum(checks.values())
    score = passed_count / len(checks) if checks else 0.0

    warnings = []
    if duplicate_evidence_ids:
        warnings.append("Duplicate evidence IDs were found.")
    if invalid_references:
        warnings.append(
            "One or more hypotheses reference evidence IDs not present "
            "in the supplied evidence."
        )
    if not evidence_items:
        warnings.append("The report has no evidence items.")
    if requires_review is not True:
        warnings.append("Human review is not explicitly required.")
    if status == "completed" and not evidence_items:
        warnings.append(
            "Investigation is marked completed despite having no evidence."
        )

    return {
        "passed": all(checks.values()),
        "score": round(score, 4),
        "checks": checks,
        "passed_checks": passed_count,
        "total_checks": len(checks),
        "evidence_count": len(evidence_items),
        "hypothesis_count": len(hypotheses),
        "hypothesis_evidence_reference_count": len(referenced_ids),
        "invalid_evidence_references": invalid_references,
        "warnings": warnings,
    }
