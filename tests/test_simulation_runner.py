
import json

import pandas as pd

from ran_intelligence.simulation.runner import (
    run_scenario_suite,
    save_scenario_suite,
)


def test_runner_executes_all_scenarios():
    suite = run_scenario_suite()

    assert set(suite["results"]) == {
        "baseline",
        "higher_power",
        "cell_outage",
        "higher_interference",
        "ue_movement",
    }


def test_runner_returns_comparison_table():
    suite = run_scenario_suite()
    comparison = suite["comparison"]

    assert len(comparison) == 5
    assert "throughput_change_mbps" in comparison.columns
    assert "sinr_change_db" in comparison.columns


def test_baseline_changes_are_zero():
    suite = run_scenario_suite()
    baseline = suite["comparison"].set_index("scenario").loc["baseline"]

    assert baseline["throughput_change_mbps"] == 0
    assert baseline["sinr_change_db"] == 0


def test_cell_outage_has_two_active_cells():
    suite = run_scenario_suite()
    summary = suite["results"]["cell_outage"]["summary"]

    assert summary["active_cells"] == 2


def test_scenario_results_contain_ue_and_cell_metrics():
    suite = run_scenario_suite()

    for result in suite["results"].values():
        assert isinstance(result["ue_metrics"], pd.DataFrame)
        assert isinstance(result["cell_metrics"], pd.DataFrame)
        assert len(result["ue_metrics"]) == 10


def test_results_are_saved(tmp_path):
    suite = run_scenario_suite()
    paths = save_scenario_suite(suite, tmp_path)

    assert (tmp_path / "scenario_comparison.csv").exists()
    assert (tmp_path / "scenario_summaries.json").exists()
    assert (tmp_path / "baseline_ue_metrics.csv").exists()
    assert (tmp_path / "baseline_cell_metrics.csv").exists()

    saved = json.loads((tmp_path / "scenario_summaries.json").read_text())
    assert "baseline" in saved
    assert paths["output_directory"] == str(tmp_path)
