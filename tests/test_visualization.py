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
