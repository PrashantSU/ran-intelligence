"""Tests for RAN KPI visualizations."""

import pandas as pd
import plotly.graph_objects as go
import pytest

from ran_intelligence.analytics.visualization import (
    plot_kpi_missingness,
    plot_kpi_timeseries,
    plot_session_kpi_comparison,
)


@pytest.fixture
def sample_timeseries():
    return pd.DataFrame(
        {
            "session_id": ["yaw315", "yaw315", "yaw45"],
            "kpi": ["nr_sinr_db", "nr_sinr_db", "nr_sinr_db"],
            "timestamp": pd.to_datetime(
                [
                    "2023-09-15 11:32:00",
                    "2023-09-15 11:33:00",
                    "2023-10-26 12:26:00",
                ]
            ),
            "value": [24.0, 26.0, 25.0],
            "sample_count": [10, 12, 11],
        }
    )


@pytest.fixture
def sample_summary():
    return pd.DataFrame(
        {
            "session_id": ["yaw315", "yaw45"],
            "kpi": ["nr_sinr_db", "nr_sinr_db"],
            "median": [25.0, 26.0],
            "valid_observations": [2794, 2824],
            "total_observations": [2898, 2949],
            "missing_observations": [104, 125],
        }
    )


def test_kpi_timeseries_returns_plotly_figure(sample_timeseries):
    fig = plot_kpi_timeseries(sample_timeseries, "yaw315", "nr_sinr_db")

    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert list(fig.data[0].y) == [24.0, 26.0]
    assert fig.layout.xaxis.title.text == "Time"


def test_kpi_timeseries_rejects_unknown_metric(sample_timeseries):
    with pytest.raises(ValueError):
        plot_kpi_timeseries(sample_timeseries, "yaw315", "unknown_metric")


def test_session_comparison_returns_expected_values(sample_summary):
    fig = plot_session_kpi_comparison(sample_summary, "nr_sinr_db")

    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert list(fig.data[0].y) == [25.0, 26.0]


def test_missingness_chart_calculates_percentages(sample_summary):
    fig = plot_kpi_missingness(sample_summary)

    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 2

    expected_yaw315 = 104 / 2898 * 100
    expected_yaw45 = 125 / 2949 * 100

    assert fig.data[0].name == "yaw315"
    assert fig.data[1].name == "yaw45"
    assert fig.data[0].y[0] == pytest.approx(expected_yaw315)
    assert fig.data[1].y[0] == pytest.approx(expected_yaw45)


def test_plot_forecast_predictions():
    import pandas as pd

    from ran_intelligence.analytics.visualization import (
        plot_forecast_predictions,
    )

    predictions = pd.DataFrame(
        {
            "origin_timestamp": pd.date_range("2023-01-01", periods=3, freq="s"),
            "target_timestamp": pd.date_range("2023-01-01 00:00:05", periods=3, freq="s"),
            "actual": [20.0, 21.0, 19.0],
            "persistence_prediction": [20.0, 20.0, 20.0],
            "random_forest_prediction": [20.5, 20.8, 19.5],
        }
    )

    fig = plot_forecast_predictions(
        predictions,
        session_id="yaw315",
        metric="nr_sinr_db",
    )

    assert len(fig.data) == 3
    assert list(fig.data[0].y) == [20.0, 21.0, 19.0]
    assert fig.data[0].name == "Actual"
    assert fig.data[1].name == "Persistence baseline"
    assert fig.data[2].name == "Random Forest"


def test_plot_forecast_predictions_rejects_missing_columns():
    import pandas as pd
    import pytest

    from ran_intelligence.analytics.visualization import (
        plot_forecast_predictions,
    )

    predictions = pd.DataFrame({"actual": [20.0]})

    with pytest.raises(ValueError, match="Missing prediction columns"):
        plot_forecast_predictions(
            predictions,
            session_id="yaw315",
            metric="nr_sinr_db",
        )


def test_plot_forecast_predictions_rejects_empty_data():
    import pandas as pd
    import pytest

    from ran_intelligence.analytics.visualization import (
        plot_forecast_predictions,
    )

    predictions = pd.DataFrame(
        columns=[
            "origin_timestamp",
            "target_timestamp",
            "actual",
            "persistence_prediction",
            "random_forest_prediction",
        ]
    )

    with pytest.raises(ValueError, match="cannot be empty"):
        plot_forecast_predictions(
            predictions,
            session_id="yaw315",
            metric="nr_sinr_db",
        )
