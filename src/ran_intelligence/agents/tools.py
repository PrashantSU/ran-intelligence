"""Controlled tool interface for incident investigations."""

import json
from collections.abc import Callable
from typing import Any, Literal

from pydantic import BaseModel, Field

from ran_intelligence.agents.schemas import (
    EvidenceItem,
    IncidentRequest,
)

ToolName = Literal[
    "kpi",
    "anomaly",
    "forecast",
    "rag",
    "simulation",
]


class ToolExecutionResult(BaseModel):
    """Outcome of one investigation tool invocation."""

    tool_name: str
    status: Literal["success", "failed", "unavailable"]
    evidence: list[EvidenceItem] = Field(default_factory=list)
    error: str | None = None


class InvestigationToolbox:
    """Expose approved investigation capabilities through one interface.

    Each handler accepts an IncidentRequest and returns structured data.
    Existing analytics and retrieval functions can be adapted to this
    interface without duplicating their implementation.
    """

    EVIDENCE_TYPES = {
        "kpi": "kpi",
        "anomaly": "anomaly",
        "forecast": "forecast",
        "rag": "rag",
        "simulation": "simulation",
    }

    def __init__(
        self,
        handlers: dict[str, Callable[[IncidentRequest], Any]] | None = None,
    ) -> None:
        self.handlers = handlers or {}

        unknown = set(self.handlers) - set(self.EVIDENCE_TYPES)
        if unknown:
            raise ValueError(f"Unsupported investigation tools: {sorted(unknown)}")

        for name, handler in self.handlers.items():
            if not callable(handler):
                raise TypeError(f"Handler for '{name}' must be callable.")

    @property
    def available_tools(self) -> list[str]:
        """Return the names of configured tools."""
        return sorted(self.handlers)

    @staticmethod
    def _json_safe(value: Any) -> Any:
        """Convert common analytical outputs into JSON-compatible values."""
        if hasattr(value, "to_dict") and hasattr(value, "columns"):
            return {
                "columns": list(value.columns),
                "row_count": len(value),
                "records": value.head(10).to_dict(orient="records"),
            }

        if hasattr(value, "model_dump"):
            return value.model_dump(mode="json")

        if hasattr(value, "item"):
            try:
                return value.item()
            except (ValueError, TypeError):
                pass

        if isinstance(value, dict):
            return {
                str(key): InvestigationToolbox._json_safe(item)
                for key, item in value.items()
            }

        if isinstance(value, (list, tuple)):
            return [
                InvestigationToolbox._json_safe(item)
                for item in value
            ]

        if value is None or isinstance(value, (str, int, float, bool)):
            return value

        return str(value)

    def _to_evidence(
        self,
        tool_name: str,
        output: Any,
    ) -> list[EvidenceItem]:
        """Convert a tool's output into traceable evidence records."""
        if output is None:
            return []

        if isinstance(output, EvidenceItem):
            return [output]

        if isinstance(output, (list, tuple)):
            evidence = []
            for item in output:
                evidence.extend(self._to_evidence(tool_name, item))
            return evidence

        if isinstance(output, dict) and "evidence" in output:
            return self._to_evidence(tool_name, output["evidence"])

        safe_output = self._json_safe(output)

        if isinstance(safe_output, dict):
            description = json.dumps(
                safe_output,
                ensure_ascii=False,
                default=str,
            )
            metadata = safe_output
        else:
            description = str(safe_output)
            metadata = {"result": safe_output}

        return [
            EvidenceItem(
                evidence_type=self.EVIDENCE_TYPES[tool_name],
                description=f"{tool_name.upper()} tool result: {description}",
                source=tool_name,
                metadata=metadata,
            )
        ]

    def run(
        self,
        tool_name: str,
        incident: IncidentRequest,
    ) -> ToolExecutionResult:
        """Execute one configured tool for an incident."""
        if tool_name not in self.EVIDENCE_TYPES:
            raise ValueError(f"Unknown investigation tool: {tool_name}")

        handler = self.handlers.get(tool_name)
        if handler is None:
            return ToolExecutionResult(
                tool_name=tool_name,
                status="unavailable",
                error=f"No handler configured for '{tool_name}'.",
            )

        try:
            output = handler(incident)
            evidence = self._to_evidence(tool_name, output)

            return ToolExecutionResult(
                tool_name=tool_name,
                status="success",
                evidence=evidence,
            )
        except Exception as exc:
            return ToolExecutionResult(
                tool_name=tool_name,
                status="failed",
                error=f"{type(exc).__name__}: {exc}",
            )

    def run_all(
        self,
        incident: IncidentRequest,
    ) -> list[ToolExecutionResult]:
        """Execute all configured tools in a deterministic order."""
        return [
            self.run(tool_name, incident)
            for tool_name in self.available_tools
        ]
