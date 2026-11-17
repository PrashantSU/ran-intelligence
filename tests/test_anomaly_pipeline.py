from pathlib import Path

import pandas as pd

from ran_intelligence.ml.anomaly_pipeline import run_anomaly_pipeline


def make_measurements():
    return pd.DataFrame(
        {
            "session_id": ["s1"] * 30,
            "measurement_id": range(30),
            "timestamp": pd.date_range("2025-01-01", periods=30, freq="s"),
            "lte_sinr_db": [20.0] * 29 + [40.0],
        }
    )


def test_pipeline_persists_observations_and_events(tmp_path):
    result = run_anomaly_pipeline(
        make_measurements(),
        output_dir=tmp_path,
        metrics=["lte_sinr_db"],
        min_samples=20,
    )

    observations_path = Path(result["observations_file"])
    events_path = Path(result["events_file"])

    assert observations_path.exists()
    assert events_path.exists()

    observations = pd.read_parquet(observations_path)
    events = pd.read_parquet(events_path)

    assert len(observations) == 30
    assert int(observations["is_anomaly"].sum()) == 1
    assert len(events) == 1
    assert events.iloc[0]["observation_count"] == 1


def test_pipeline_returns_consistent_summary(tmp_path):
    result = run_anomaly_pipeline(
        make_measurements(),
        output_dir=tmp_path,
        metrics=["lte_sinr_db"],
        min_samples=20,
    )

    assert result["input_rows"] == 30
    assert result["analysed_observations"] == 30
    assert result["flagged_observations"] == 1
    assert result["event_count"] == 1
    assert result["sessions"] == ["s1"]
    assert result["metrics"] == ["lte_sinr_db"]
