"""LangGraph workflow for structured RAN incident investigation."""

from collections.abc import Callable
from typing import Any

from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

from ran_intelligence.agents.schemas import (
    IncidentHypothesis,
    IncidentReport,
)
from ran_intelligence.agents.state import InvestigationState

HypothesisGenerator = Callable[
    [InvestigationState],
    list[IncidentHypothesis],
]


def build_investigation_graph(
    toolbox: Any,
    tool_names: tuple[str, ...] = ("kpi", "anomaly", "forecast"),
    hypothesis_generator: HypothesisGenerator | None = None,
    checkpointer: Any | None = None,
):
    """Build an evidence-first investigation graph with resumable human review."""

    if not tool_names:
        raise ValueError("At least one investigation tool must be configured.")

    def make_tool_node(tool_name: str):
        def run_tool(state: InvestigationState) -> dict[str, Any]:
            incident = state["incident"]
            result = toolbox.run(tool_name, incident)

            tool_results = dict(state.get("tool_results", {}))
            tool_results[tool_name] = result

            evidence = list(state.get("evidence", []))
            evidence.extend(result.evidence)

            errors = list(state.get("errors", []))
            if result.status != "success" and result.error:
                errors.append(f"{tool_name}: {result.error}")

            completed_tools = list(state.get("completed_tools", []))
            completed_tools.append(tool_name)

            return {
                "tool_results": tool_results,
                "evidence": evidence,
                "errors": errors,
                "completed_tools": completed_tools,
                "current_step": f"{tool_name}_completed",
            }

        return run_tool

    def synthesise(state: InvestigationState) -> dict[str, Any]:
        evidence = state.get("evidence", [])
        hypotheses = (
            hypothesis_generator(state)
            if hypothesis_generator is not None
            else []
        )

        status = "completed" if evidence else "insufficient_evidence"

        summary = (
            f"Investigation of incident {state['incident'].incident_id} "
            f"collected {len(evidence)} evidence item(s) from "
            f"{len(state.get('completed_tools', []))} tool(s)."
        )

        limitations = [
            "This report is advisory and requires review by a human engineer.",
            "Collected evidence does not by itself establish a confirmed root cause.",
        ]

        if state.get("errors"):
            limitations.append(
                "One or more investigation tools failed; see the recorded errors."
            )

        if not evidence:
            limitations.append(
                "No evidence was collected. Root-cause assessment is unavailable."
            )

        report = IncidentReport(
            incident_id=state["incident"].incident_id,
            summary=summary,
            evidence=evidence,
            hypotheses=hypotheses,
            limitations=limitations,
            recommended_actions=[
                "Review the collected evidence and its source data.",
                "Validate plausible explanations against network telemetry.",
                "Do not make network configuration changes based solely on this report.",
            ],
            requires_human_review=True,
            investigation_status=status,
        )

        return {
            "hypotheses": hypotheses,
            "report": report,
            "investigation_status": status,
            "current_step": "synthesis_completed",
        }

    def prepare_human_review(
        state: InvestigationState,
    ) -> dict[str, Any]:
        return {
            "pending_review": True,
            "review_approved": None,
            "human_feedback": None,
            "current_step": "awaiting_human_review",
        }

    def human_review(state: InvestigationState) -> dict[str, Any]:
        """Pause execution until a human submits a review decision."""
        report = state["report"]

        review = interrupt({
            "type": "human_review",
            "incident_id": str(state["incident"].incident_id),
            "summary": report.summary,
            "report": report.model_dump(mode="json"),
            "instructions": (
                "Resume with {'approved': true/false, "
                "'feedback': 'optional engineer feedback'}."
            ),
        })

        if not isinstance(review, dict):
            raise ValueError("Human review must be supplied as a dictionary.")

        approved = review.get("approved")
        if not isinstance(approved, bool):
            raise ValueError("Human review must contain a boolean 'approved' field.")

        feedback = review.get("feedback")
        if feedback is not None and not isinstance(feedback, str):
            raise ValueError("Human review feedback must be a string or None.")

        return {
            "pending_review": False,
            "review_approved": approved,
            "human_feedback": feedback,
            "current_step": (
                "review_approved" if approved else "review_rejected"
            ),
        }

    builder = StateGraph(InvestigationState)

    builder.add_node("synthesise", synthesise)
    builder.add_node("prepare_human_review", prepare_human_review)
    builder.add_node("human_review", human_review)

    for tool_name in tool_names:
        builder.add_node(f"run_{tool_name}", make_tool_node(tool_name))

    builder.add_edge(START, f"run_{tool_names[0]}")

    for current, following in zip(tool_names, tool_names[1:]):
        builder.add_edge(f"run_{current}", f"run_{following}")

    builder.add_edge(f"run_{tool_names[-1]}", "synthesise")
    builder.add_edge("synthesise", "prepare_human_review")
    builder.add_edge("prepare_human_review", "human_review")
    builder.add_edge("human_review", END)

    if checkpointer is not None:
        active_checkpointer = checkpointer
    else:
        serializer = JsonPlusSerializer(
            allowed_msgpack_modules=[
                ("ran_intelligence.agents.schemas", "IncidentRequest"),
                ("ran_intelligence.agents.schemas", "EvidenceItem"),
                ("ran_intelligence.agents.schemas", "IncidentHypothesis"),
                ("ran_intelligence.agents.schemas", "IncidentReport"),
                ("ran_intelligence.agents.tools", "ToolExecutionResult"),
            ]
        )
        active_checkpointer = MemorySaver(serde=serializer)

    return builder.compile(checkpointer=active_checkpointer)
