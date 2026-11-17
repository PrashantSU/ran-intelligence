"""Tests for RAN anomaly detection and episode grouping."""

import pandas as pd
import pytest

from ran_intelligence.ml.anomaly import detect_kpi_anomalies
from ran_intelligence.ml.anomaly_events import group_anomaly_events


def test_anomaly_detection_identifies_extreme_value():
    df = pd.DataFrame(
        {
            "session_id": ["s1"] * 30,
            "measurement_id": range(30),
            "timestamp": pd.date_range("2025-01-01", periods=30, freq="s"),
            "lte_sinr_db": [20.0] * 29 + [40.0],
        }
    )

    result = detect_kpi_anomalies(
        df,
        metrics=["lte_sinr_db"],
        min_samples=20,
    )

    flagged = result[result["is_anomaly"]]

    assert len(flagged) == 1
    assert flagged.iloc[0]["measurement_id"] == 29


def test_anomaly_detection_preserves_missing_values():
    df = pd.DataFrame(
        {
            "session_id": ["s1"] * 30,
            "measurement_id": range(30),
            "timestamp": pd.date_range("2025-01-01", periods=30, freq="s"),
            "lte_sinr_db": [20.0] * 29 + [None],
        }
    )

    result = detect_kpi_anomalies(
        df,
        metrics=["lte_sinr_db"],
    )

    assert len(result) == 29


def test_episode_grouping_merges_close_anomalies():
    df = pd.DataFrame(
        {
            "session_id": ["s1"] * 3,
            "kpi": ["lte_sinr_db"] * 3,
            "timestamp": pd.to_datetime(
                [
                    "2025-01-01 00:00:00",
                    "2025-01-01 00:00:01",
                    "2025-01-01 00:00:02",
                ]
            ),
            "value": [10.0, 11.0, 12.0],
            "robust_z_score": [4.0, 4.5, 5.0],
            "is_anomaly": [True, True, True],
        }
    )

    events = group_anomaly_events(df, max_gap_seconds=2.0)

    assert len(events) == 1
    assert events.iloc[0]["observation_count"] == 3
    assert events.iloc[0]["duration_seconds"] == 2.0


def test_episode_grouping_splits_large_time_gaps():
    df = pd.DataFrame(
        {
            "session_id": ["s1"] * 3,
            "kpi": ["lte_sinr_db"] * 3,
            "timestamp": pd.to_datetime(
                [
                    "2025-01-01 00:00:00",
                    "2025-01-01 00:00:01",
                    "2025-01-01 00:00:10",
                ]
            ),
            "value": [10.0, 11.0, 12.0],
            "robust_z_score": [4.0, 4.5, 5.0],
            "is_anomaly": [True, True, True],
        }
    )

    events = group_anomaly_events(df, max_gap_seconds=2.0)

    assert len(events) == 2
    assert sorted(events["observation_count"].tolist()) == [1, 2]


def test_episode_grouping_ignores_normal_observations():
    df = pd.DataFrame(
        {
            "session_id": ["s1"] * 3,
            "kpi": ["lte_sinr_db"] * 3,
            "timestamp": pd.to_datetime(
                [
                    "2025-01-01 00:00:00",
                    "2025-01-01 00:00:01",
                    "2025-01-01 00:00:02",
                ]
            ),
            "value": [10.0, 11.0, 12.0],
            "robust_z_score": [4.0, 1.0, 5.0],
            "is_anomaly": [True, False, True],
        }
    )

    events = group_anomaly_events(df, max_gap_seconds=2.0)

    assert len(events) == 1
    assert events.iloc[0]["observation_count"] == 2


def test_episode_grouping_rejects_negative_gap():
    df = pd.DataFrame(
        {
            "session_id": ["s1"],
            "kpi": ["lte_sinr_db"],
            "timestamp": pd.to_datetime(["2025-01-01"]),
            "value": [10.0],
            "robust_z_score": [4.0],
            "is_anomaly": [True],
        }
    )

    with pytest.raises(ValueError):
        group_anomaly_events(df, max_gap_seconds=-1)
