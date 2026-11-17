"""Group individual KPI anomalies into time-based episodes."""

import pandas as pd


def group_anomaly_events(
    anomalies: pd.DataFrame,
    max_gap_seconds: float = 2.0,
) -> pd.DataFrame:
    """Group consecutive anomalous observations into episodes.

    Observations are grouped independently by session and KPI.
    A new episode starts when the time gap between consecutive
    anomalous observations exceeds max_gap_seconds.
    """

    if not isinstance(anomalies, pd.DataFrame):
        raise TypeError("anomalies must be a pandas DataFrame.")

    if anomalies.empty:
        return pd.DataFrame(
            columns=[
                "session_id",
                "kpi",
                "start_time",
                "end_time",
                "duration_seconds",
                "observation_count",
                "max_abs_score",
                "mean_abs_score",
                "min_value",
                "max_value",
            ]
        )

    if max_gap_seconds < 0:
        raise ValueError("max_gap_seconds cannot be negative.")

    required = {
        "session_id",
        "kpi",
        "timestamp",
        "value",
        "robust_z_score",
        "is_anomaly",
    }

    missing = required - set(anomalies.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}")

    flagged = anomalies.loc[anomalies["is_anomaly"].fillna(False)].copy()

    if flagged.empty:
        return pd.DataFrame(
            columns=[
                "session_id",
                "kpi",
                "start_time",
                "end_time",
                "duration_seconds",
                "observation_count",
                "max_abs_score",
                "mean_abs_score",
                "min_value",
                "max_value",
            ]
        )

    flagged["timestamp"] = pd.to_datetime(
        flagged["timestamp"],
        errors="coerce",
    )

    flagged = flagged.dropna(subset=["timestamp", "value"])

    flagged = flagged.sort_values(["session_id", "kpi", "timestamp"])

    gap = flagged.groupby(["session_id", "kpi"])["timestamp"].diff().dt.total_seconds()

    new_episode = gap.isna() | (gap > max_gap_seconds)

    flagged["episode_number"] = (
        new_episode.groupby([flagged["session_id"], flagged["kpi"]]).cumsum().astype(int)
    )

    records = []

    for (session_id, kpi, episode_number), group in flagged.groupby(
        ["session_id", "kpi", "episode_number"],
        sort=False,
    ):
        start = group["timestamp"].min()
        end = group["timestamp"].max()
        absolute_scores = group["robust_z_score"].abs()

        records.append(
            {
                "session_id": session_id,
                "kpi": kpi,
                "episode_number": episode_number,
                "start_time": start,
                "end_time": end,
                "duration_seconds": (end - start).total_seconds(),
                "observation_count": len(group),
                "max_abs_score": absolute_scores.max(),
                "mean_abs_score": absolute_scores.mean(),
                "min_value": group["value"].min(),
                "max_value": group["value"].max(),
            }
        )

    return pd.DataFrame(records)
