
import pandas as pd
import pytest

from ran_intelligence.simulation.visualization import (
    plot_scenario_comparison,
    save_scenario_visualization,
)


@pytest.fixture
def comparison():
    return pd.DataFrame({
        "scenario": ["baseline", "cell_outage"],
        "total_throughput_mbps": [143.741, 95.123],
        "demand_satisfaction": [0.799, 0.528],
        "mean_sinr_db": [8.216, 8.337],
    })


def test_plot_contains_three_metrics(comparison):
    figure = plot_scenario_comparison(comparison)

    assert len(figure.data) == 3
    assert figure.layout.title.text.startswith("RAN Digital Twin")


def test_plot_rejects_missing_columns():
    with pytest.raises(ValueError, match="Missing required columns"):
        plot_scenario_comparison(pd.DataFrame({"scenario": ["baseline"]}))


def test_plot_rejects_empty_dataframe():
    empty = pd.DataFrame(columns=[
        "scenario",
        "total_throughput_mbps",
        "demand_satisfaction",
        "mean_sinr_db",
    ])

    with pytest.raises(ValueError, match="cannot be empty"):
        plot_scenario_comparison(empty)


def test_visualization_is_saved(comparison, tmp_path):
    output = tmp_path / "scenario_comparison.html"

    saved_path = save_scenario_visualization(comparison, output)

    assert output.exists()
    assert saved_path == str(output)
    assert "plotly" in output.read_text(encoding="utf-8").lower()
