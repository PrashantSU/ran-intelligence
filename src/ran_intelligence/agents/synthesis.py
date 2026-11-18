"""Evidence-grounded hypothesis synthesis for RAN incidents."""

import json
from collections.abc import Callable
from typing import Any

from ran_intelligence.agents.schemas import (
    IncidentHypothesis,
)
from ran_intelligence.agents.state import InvestigationState


def build_hypothesis_prompt(state: InvestigationState) -> str:
    """Build a prompt containing only evidence collected in this investigation."""
    incident = state["incident"]
    evidence = state.get("evidence", [])

    evidence_payload = [
        {
            "evidence_id": item.evidence_id,
            "evidence_type": item.evidence_type,
            "description": item.description,
            "source": item.source,
            "observed_value": item.observed_value,
            "timestamp": (
                item.timestamp.isoformat()
                if item.timestamp is not None
                else None
            ),
            "metadata": item.metadata,
        }
        for item in evidence
    ]

    return f"""You are assisting a human engineer with a RAN incident investigation.

INCIDENT
Description: {incident.description}
Session: {incident.session_id}
Cell: {incident.cell_id}
Severity: {incident.severity}
Suspected KPIs: {incident.suspected_kpis}

COLLECTED EVIDENCE
{json.dumps(evidence_payload, indent=2, default=str)}

TASK
Generate a concise list of plausible root-cause hypotheses supported by the
provided evidence. Do not assume that a suspected KPI is the root cause.

RULES
1. Use only the supplied evidence. Do not invent measurements, events, or facts.
2. Every evidence ID must exactly match an ID in COLLECTED EVIDENCE.
3. Separate supporting evidence from contradicting evidence.
4. Do not treat correlation as proof of causation.
5. Use confidence between 0 and 1 as an uncertainty estimate, not a probability
   calibrated by a statistical model.
6. Use status "plausible", "weakly_supported", "strongly_supported", or
   "unresolved". Never claim a cause is confirmed.
7. If evidence is insufficient, return an empty hypotheses list.
8. Keep explanations concise and identify important uncertainty.

Return valid JSON only, with this structure:
{{
  "hypotheses": [
    {{
      "hypothesis_id": "hyp-001",
      "title": "Short hypothesis title",
      "explanation": "Evidence-based explanation and uncertainty",
      "confidence": 0.5,
      "supporting_evidence_ids": ["existing-evidence-id"],
      "contradicting_evidence_ids": [],
      "status": "plausible"
    }}
  ]
}}
"""


def parse_grounded_hypotheses(
    payload: dict[str, Any] | str,
    evidence: list,
) -> list[IncidentHypothesis]:
    """Parse hypotheses and reject unsupported or fabricated evidence references."""
    if isinstance(payload, str):
        payload = json.loads(payload)

    if not isinstance(payload, dict):
        raise ValueError("Synthesis output must be a JSON object.")

    raw_hypotheses = payload.get("hypotheses")
    if not isinstance(raw_hypotheses, list):
        raise ValueError("'hypotheses' must be a list.")

    known_ids = {item.evidence_id for item in evidence}
    parsed: list[IncidentHypothesis] = []

    for raw in raw_hypotheses:
        hypothesis = IncidentHypothesis.model_validate(raw)

        supporting = set(hypothesis.supporting_evidence_ids)
        contradicting = set(hypothesis.contradicting_evidence_ids)
        referenced = supporting | contradicting

        unknown = referenced - known_ids
        if unknown:
            raise ValueError(
                "Hypothesis references unknown evidence IDs: "
                f"{sorted(unknown)}"
            )

        if not referenced:
            raise ValueError(
                f"Hypothesis {hypothesis.hypothesis_id} has no evidence references."
            )

        if supporting & contradicting:
            raise ValueError(
                f"Hypothesis {hypothesis.hypothesis_id} uses the same evidence "
                "as both supporting and contradicting."
            )

        parsed.append(hypothesis)

    return parsed


def generate_grounded_hypotheses(
    state: InvestigationState,
    structured_generator: Callable[[str], dict[str, Any] | str],
) -> list[IncidentHypothesis]:
    """Generate and validate hypotheses using an injected structured-output model."""
    evidence = state.get("evidence", [])

    if not evidence:
        return []

    prompt = build_hypothesis_prompt(state)
    response = structured_generator(prompt)

    return parse_grounded_hypotheses(response, evidence)
