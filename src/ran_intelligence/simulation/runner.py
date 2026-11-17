
"""Unified execution and persistence for RAN simulation scenarios."""

import json
from pathlib import Path
from typing import Any

import pandas as pd

from ran_intelligence.simulation.digital_twin import simulate_network
from ran_intelligence.simulation.scenarios import (
    change_interference,
    change_transmit_power,
    create_reference_scenario,
    move_user,
    simulate_cell_outage,
)


def run_scenario_suite() -> dict[str, Any]:
    """Execute a baseline and a set of representative what-if scenarios."""
    baseline = create_reference_scenario()

    scenarios = {
        "baseline": baseline,
        "higher_power": change_transmit_power(
            baseline, "cell_001", 50.0
        ),
        "cell_outage": simulate_cell_outage(
            baseline, "cell_001"
        ),
        "higher_interference": change_interference(
            baseline, "cell_002", 2.0
        ),
        "ue_movement": move_user(
            baseline, "ue_001", 300.0, 300.0
        ),
    }

    results = {
        name: simulate_network(scenario)
        for name, scenario in scenarios.items()
    }

    baseline_summary = results["baseline"]["summary"]
    comparison_rows = []

    for name, result in results.items():
        summary = result["summary"]
        comparison_rows.append({
            "scenario": name,
            **summary,
            "throughput_change_mbps": (
                summary["total_throughput_mbps"]
                - baseline_summary["total_throughput_mbps"]
            ),
            "sinr_change_db": (
                summary["mean_sinr_db"]
                - baseline_summary["mean_sinr_db"]
            ),
        })

    return {
        "scenarios": scenarios,
        "results": results,
        "comparison": pd.DataFrame(comparison_rows),
    }


def save_scenario_suite(
    suite: dict[str, Any],
    output_dir: str | Path,
) -> dict[str, str]:
    """Save scenario summaries and per-UE/per-cell results."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    comparison_path = output_path / "scenario_comparison.csv"
    suite["comparison"].to_csv(comparison_path, index=False)

    summary_path = output_path / "scenario_summaries.json"
    summaries = {
        name: result["summary"]
        for name, result in suite["results"].items()
    }
    summary_path.write_text(
        json.dumps(summaries, indent=2),
        encoding="utf-8",
    )

    for name, result in suite["results"].items():
        result["ue_metrics"].to_csv(
            output_path / f"{name}_ue_metrics.csv",
            index=False,
        )
        result["cell_metrics"].to_csv(
            output_path / f"{name}_cell_metrics.csv",
            index=False,
        )

    return {
        "comparison": str(comparison_path),
        "summaries": str(summary_path),
        "output_directory": str(output_path),
    }
