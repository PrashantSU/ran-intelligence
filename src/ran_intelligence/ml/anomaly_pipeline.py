"""Persistence pipeline for KPI anomaly detection."""

from pathlib import Path

import pandas as pd

from ran_intelligence.ml.anomaly import detect_kpi_anomalies
from ran_intelligence.ml.anomaly_events import group_anomaly_events


def run_anomaly_pipeline(
    df: pd.DataFrame,
    output_dir: str | Path,
    metrics: list[str] | None = None,
    threshold: float = 3.5,
    min_samples: int = 20,
    max_gap_seconds: float = 2.0,
) -> dict:
    """Detect KPI anomalies, group events, and persist both datasets."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    observations = detect_kpi_anomalies(
        df,
        metrics=metrics,
        threshold=threshold,
        min_samples=min_samples,
    )

    events = group_anomaly_events(
        observations,
        max_gap_seconds=max_gap_seconds,
    )

    observations_file = output_path / "anomaly_observations.parquet"
    events_file = output_path / "anomaly_events.parquet"

    observations.to_parquet(observations_file, index=False)
    events.to_parquet(events_file, index=False)

    flagged = observations.loc[observations["is_anomaly"]]

    return {
        "input_rows": len(df),
        "analysed_observations": len(observations),
        "flagged_observations": len(flagged),
        "event_count": len(events),
        "sessions": sorted(df["session_id"].dropna().astype(str).unique().tolist()),
        "metrics": sorted(observations["kpi"].unique().tolist()),
        "observations_file": str(observations_file),
        "events_file": str(events_file),
        "observations": observations,
        "events": events,
    }
