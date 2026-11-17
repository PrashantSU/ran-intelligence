"""Reusable KPI analytics for LTE and NR measurements."""

import pandas as pd

KPI_DEFINITIONS = {
    "lte_rsrp_dbm": {"label": "LTE RSRP", "unit": "dBm"},
    "lte_sinr_db": {"label": "LTE SINR", "unit": "dB"},
    "nr_rsrp_dbm": {"label": "NR RSRP", "unit": "dBm"},
    "nr_sinr_db": {"label": "NR SINR", "unit": "dB"},
    "nr_cqi": {"label": "NR CQI", "unit": "index"},
    "nr_mcs": {"label": "NR MCS", "unit": "index"},
    "nr_rank_indicator": {"label": "NR Rank Indicator", "unit": "rank"},
    "throughput_raw": {
        "label": "Throughput",
        "unit": "source units (unverified)",
    },
}


def _validate_input(df: pd.DataFrame) -> None:
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")
    if df.empty:
        raise ValueError("Input DataFrame is empty.")


def get_available_kpis() -> list[dict]:
    """Return the supported KPI names, labels and units."""
    return [{"column": column, **definition} for column, definition in KPI_DEFINITIONS.items()]


def compute_kpi_summary(
    df: pd.DataFrame,
    group_by: tuple[str, ...] = ("session_id",),
) -> pd.DataFrame:
    """Calculate descriptive statistics and missingness for each KPI."""
    _validate_input(df)

    group_columns = list(group_by)
    required = group_columns + list(KPI_DEFINITIONS)
    missing_columns = [column for column in required if column not in df.columns]

    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    if len(group_columns) != len(set(group_columns)):
        raise ValueError("group_by contains duplicate columns.")

    working = df.copy()
    for column in KPI_DEFINITIONS:
        working[column] = pd.to_numeric(working[column], errors="coerce")

    if group_columns:
        grouped = working.groupby(group_columns, dropna=False, sort=True)
        groups = ((key if isinstance(key, tuple) else (key,), group) for key, group in grouped)
    else:
        groups = [((), working)]

    rows = []
    for group_key, group in groups:
        group_values = dict(zip(group_columns, group_key))

        for column, definition in KPI_DEFINITIONS.items():
            values = group[column].dropna()
            row = {
                **group_values,
                "kpi": column,
                "label": definition["label"],
                "unit": definition["unit"],
                "total_observations": len(group),
                "valid_observations": int(values.count()),
                "missing_observations": int(group[column].isna().sum()),
                "mean": values.mean(),
                "median": values.median(),
                "std": values.std(),
                "min": values.min(),
                "q25": values.quantile(0.25),
                "q75": values.quantile(0.75),
                "max": values.max(),
            }
            rows.append(row)

    return pd.DataFrame(rows)


def compute_session_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Summarise measurement volume, time coverage and throughput coverage."""
    _validate_input(df)

    required = {"session_id", "measurement_id", "timestamp", "throughput_raw"}
    missing_columns = sorted(required - set(df.columns))
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    working = df.copy()
    working["timestamp"] = pd.to_datetime(working["timestamp"], errors="coerce")

    rows = []
    for session_id, group in working.groupby("session_id", dropna=False, sort=True):
        timestamps = group["timestamp"].dropna()
        start = timestamps.min() if not timestamps.empty else pd.NaT
        end = timestamps.max() if not timestamps.empty else pd.NaT
        duration = (end - start).total_seconds() / 60 if not timestamps.empty else float("nan")

        throughput_count = int(group["throughput_raw"].notna().sum())
        total_count = len(group)

        rows.append(
            {
                "session_id": session_id,
                "total_observations": total_count,
                "unique_measurements": int(group["measurement_id"].nunique()),
                "start_time": start,
                "end_time": end,
                "duration_minutes": duration,
                "throughput_observations": throughput_count,
                "throughput_coverage_pct": (
                    100 * throughput_count / total_count if total_count else 0
                ),
            }
        )

    return pd.DataFrame(rows)


def build_kpi_timeseries(
    df: pd.DataFrame,
    session_id: str,
    metric: str,
    interval: str = "1min",
    aggregation: str = "median",
) -> pd.DataFrame:
    """Aggregate a KPI into time intervals for plotting and monitoring."""
    _validate_input(df)

    if metric not in KPI_DEFINITIONS:
        raise ValueError(f"Unsupported KPI: {metric}")

    if not {"session_id", "timestamp", metric}.issubset(df.columns):
        raise ValueError("Input must contain session_id, timestamp and metric.")

    allowed_aggregations = {"mean", "median", "min", "max", "sum"}
    if aggregation not in allowed_aggregations:
        raise ValueError(f"Unsupported aggregation. Choose from {sorted(allowed_aggregations)}")

    subset = df.loc[df["session_id"] == session_id, ["timestamp", metric]].copy()
    if subset.empty:
        raise ValueError(f"No observations found for session: {session_id}")

    subset["timestamp"] = pd.to_datetime(subset["timestamp"], errors="coerce")
    subset[metric] = pd.to_numeric(subset[metric], errors="coerce")
    subset = subset.dropna(subset=["timestamp", metric])

    if subset.empty:
        raise ValueError(f"No valid {metric} observations for {session_id}.")

    grouped = subset.set_index("timestamp")[metric].resample(interval)

    result = pd.concat(
        [
            getattr(grouped, aggregation)().rename("value"),
            grouped.count().rename("sample_count"),
        ],
        axis=1,
    ).dropna(subset=["value"])

    return result.reset_index()
