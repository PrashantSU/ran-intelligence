import pandas as pd
import pytest

from ran_intelligence.analytics.visualization import (
    plot_anomaly_detection,
)


def make_visualization_data():
    measurements = pd.DataFrame(
        {
            "session_id": ["s1"] * 4,
            "timestamp": pd.date_range("2025-01-01", periods=4, freq="s"),
            "lte_sinr_db": [20.0, 21.0, 19.0, 40.0],
        }
    )

    anomalies = pd.DataFrame(
        {
            "session_id": ["s1", "s1"],
            "kpi": ["lte_sinr_db", "lte_sinr_db"],
            "timestamp": [
                pd.Timestamp("2025-01-01 00:00:03"),
                pd.Timestamp("2025-01-01 00:00:02"),
            ],
            "value": [40.0, 19.0],
            "robust_z_score": [5.2, 0.5],
            "is_anomaly": [True, False],
        }
    )

    return measurements, anomalies


def test_anomaly_chart_shows_measurements_and_flagged_points():
    measurements, anomalies = make_visualization_data()

    fig = plot_anomaly_detection(measurements, anomalies, "s1", "lte_sinr_db")

    assert len(fig.data) == 2
    assert len(fig.data[0].x) == 4
    assert len(fig.data[1].x) == 1
    assert list(fig.data[1].y) == [40.0]


def test_anomaly_chart_rejects_unknown_metric():
    measurements, anomalies = make_visualization_data()

    with pytest.raises(ValueError, match="Measurements missing columns"):
        plot_anomaly_detection(measurements, anomalies, "s1", "unknown_metric")


def test_anomaly_chart_rejects_unknown_session():
    measurements, anomalies = make_visualization_data()

    with pytest.raises(ValueError, match="No measurements found"):
        plot_anomaly_detection(measurements, anomalies, "missing", "lte_sinr_db")
