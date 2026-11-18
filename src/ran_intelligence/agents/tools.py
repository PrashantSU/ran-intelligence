"""Controlled tool interface for incident investigations."""

import json
from collections.abc import Callable
from datetime import datetime
from time import perf_counter
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
    raw_output: Any = None
    latency_ms: float = 0.0


class InvestigationToolbox:
    """Expose approved investigation capabilities through one interface."""

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
        return sorted(self.handlers)

    @staticmethod
    def _json_safe(value: Any) -> Any:
        """Convert analytical outputs into JSON-compatible values."""
        if hasattr(value, "to_dict") and hasattr(value, "columns"):
            records = value.head(10).to_dict(orient="records")
            return {
                "columns": list(value.columns),
                "row_count": len(value),
                "records": [
                    InvestigationToolbox._json_safe(record)
                    for record in records
                ],
            }

        if hasattr(value, "model_dump"):
            return value.model_dump(mode="json")

        # pandas.Timestamp is a datetime subclass; convert it before .item().
        if isinstance(value, datetime):
            return value.isoformat()

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

    @staticmethod
    def _compact_table(
        table: Any,
        max_records: int = 5,
    ) -> Any:
        """Keep table structure and a limited number of representative rows."""
        if not isinstance(table, dict):
            return table

        return {
            "columns": table.get("columns", []),
            "row_count": table.get("row_count", 0),
            "records": table.get("records", [])[:max_records],
        }

    @classmethod
    def _compact_output(
        cls,
        tool_name: str,
        output: Any,
    ) -> dict[str, Any]:
        """Build concise human-facing evidence without discarding raw output."""
        if not isinstance(output, dict):
            return {"result": output}

        if tool_name == "kpi":
            # Preserve generic KPI dictionaries and standalone DataFrame outputs.
            if "kpi_summary" not in output:
                return output

            compact = {
                key: value
                for key, value in output.items()
                if key != "kpi_summary"
            }
            compact["kpi_summary"] = cls._compact_table(
                output["kpi_summary"],
                max_records=10,
            )
            return compact

        if tool_name == "anomaly":
            compact = {
                key: output[key]
                for key in (
                    "measurement_count",
                    "evaluated_observation_count",
                    "anomaly_count",
                    "metrics",
                )
                if key in output
            }
            if "anomaly_samples" in output:
                compact["anomaly_samples"] = cls._compact_table(
                    output["anomaly_samples"],
                    max_records=5,
                )
            return compact

        if tool_name == "forecast":
            compact = {
                key: output[key]
                for key in (
                    "metric",
                    "forecast_example_count",
                    "train_count",
                    "test_count",
                    "interpretation",
                )
                if key in output
            }
            for key in ("model_evaluation", "prediction_samples"):
                if key in output:
                    compact[key] = cls._compact_table(
                        output[key],
                        max_records=5 if key == "model_evaluation" else 3,
                    )
            return compact

        if tool_name == "rag":
            compact = {
                key: output[key]
                for key in (
                    "status",
                    "evidence_type",
                    "query",
                    "retrieved_count",
                    "interpretation",
                )
                if key in output
            }

            passages = output.get("passages", [])
            compact["passages"] = [
                {
                    key: passage[key]
                    for key in (
                        "chunk_id",
                        "citation",
                        "source",
                        "page",
                        "title",
                        "rrf_score",
                    )
                    if key in passage
                }
                for passage in passages[:3]
                if isinstance(passage, dict)
            ]
            return compact

        if tool_name == "simulation":
            suite = output.get("scenario_suite", {})
            compact_suite = {}

            if isinstance(suite, dict):
                scenarios = suite.get("scenarios", {})
                if isinstance(scenarios, dict):
                    compact_suite["scenario_names"] = list(scenarios.keys())

                comparison = suite.get("comparison")
                if isinstance(comparison, dict):
                    compact_suite["comparison"] = cls._compact_table(
                        comparison,
                        max_records=10,
                    )
                elif comparison is not None:
                    compact_suite["comparison"] = comparison

                results = suite.get("results")
                if isinstance(results, dict):
                    compact_results = {}
                    for name, result in results.items():
                        if isinstance(result, dict):
                            compact_results[name] = {
                                key: value
                                for key, value in result.items()
                                if value is None or isinstance(
                                    value, (str, int, float, bool)
                                )
                            }
                        else:
                            compact_results[name] = str(result)[:250]
                    compact_suite["results"] = compact_results

            return {
                "scope": output.get("scope"),
                "scenario_suite": compact_suite,
            }

        return output

    def _to_evidence(
        self,
        tool_name: str,
        output: Any,
    ) -> list[EvidenceItem]:
        """Convert tool output into concise, traceable evidence."""
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
        compact_output = self._compact_output(tool_name, safe_output)

        description = json.dumps(
            compact_output,
            ensure_ascii=False,
            default=str,
        )

        return [
            EvidenceItem(
                evidence_type=self.EVIDENCE_TYPES[tool_name],
                description=f"{tool_name.upper()} findings: {description}",
                source=tool_name,
                metadata=compact_output,
            )
        ]

    def run(
        self,
        tool_name: str,
        incident: IncidentRequest,
    ) -> ToolExecutionResult:
        """Execute one configured investigation tool and record latency."""
        if tool_name not in self.EVIDENCE_TYPES:
            raise ValueError(f"Unknown investigation tool: {tool_name}")

        start = perf_counter()
        handler = self.handlers.get(tool_name)

        if handler is None:
            return ToolExecutionResult(
                tool_name=tool_name,
                status="unavailable",
                error=f"No handler configured for '{tool_name}'.",
                latency_ms=(perf_counter() - start) * 1000,
            )

        try:
            output = handler(incident)
            safe_output = self._json_safe(output)
            evidence = self._to_evidence(tool_name, output)

            return ToolExecutionResult(
                tool_name=tool_name,
                status="success",
                evidence=evidence,
                raw_output=safe_output,
                latency_ms=(perf_counter() - start) * 1000,
            )
        except Exception as exc:
            return ToolExecutionResult(
                tool_name=tool_name,
                status="failed",
                error=f"{type(exc).__name__}: {exc}",
                latency_ms=(perf_counter() - start) * 1000,
            )

    def run_all(
        self,
        incident: IncidentRequest,
    ) -> list[ToolExecutionResult]:
        return [
            self.run(tool_name, incident)
            for tool_name in self.available_tools
        ]
