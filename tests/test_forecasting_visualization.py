
import pandas as pd
import pytest

from ran_intelligence.analytics.forecasting_visualization import (
    plot_forecast_comparison,
    plot_forecast_metric_comparison,
    plot_forecast_residuals,
    plot_gru_seed_stability,
)


@pytest.fixture
def predictions():
    return pd.DataFrame({
        "session_id": ["yaw315"] * 3,
        "origin_timestamp": pd.date_range("2026-01-01", periods=3, freq="1s"),
        "target_timestamp": pd.date_range("2026-01-01 00:00:05", periods=3, freq="1s"),
        "actual": [20.0, 21.0, 22.0],
        "persistence_prediction": [19.0, 20.0, 21.0],
        "random_forest_prediction": [19.5, 20.5, 21.5],
        "gru_prediction": [20.1, 20.8, 22.1],
    })


def test_forecast_comparison_returns_figure(predictions):
    fig = plot_forecast_comparison(predictions, "yaw315")
    assert len(fig.data) == 4


def test_metric_comparison_returns_figure():
    metrics = pd.DataFrame({
        "session_id": ["yaw315", "yaw315", "yaw45"],
        "model": ["persistence", "gru", "persistence"],
        "mae": [2.9, 2.6, 3.1],
    })

    fig = plot_forecast_metric_comparison(metrics)
    assert len(fig.data) == 2


def test_residual_plot_returns_figure(predictions):
    fig = plot_forecast_residuals(predictions, "yaw315")
    assert len(fig.data) == 6


def test_gru_seed_stability_returns_figure():
    seeds = pd.DataFrame({
        "session_id": ["yaw315"] * 3 + ["yaw45"] * 3,
        "seed": [21, 42, 63, 21, 42, 63],
        "mae": [2.7, 2.6, 2.8, 3.1, 3.2, 3.0],
    })

    fig = plot_gru_seed_stability(seeds)
    assert len(fig.data) == 2


def test_forecast_comparison_rejects_missing_columns():
    with pytest.raises(ValueError, match="Missing required columns"):
        plot_forecast_comparison(
            pd.DataFrame({"actual": [1.0]}),
            "yaw315",
        )


def test_gru_seed_plot_rejects_missing_columns():
    with pytest.raises(ValueError, match="Missing required columns"):
        plot_gru_seed_stability(
            pd.DataFrame({"session_id": ["yaw315"]})
        )
