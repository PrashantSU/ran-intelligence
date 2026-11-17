"""Robust statistical anomaly detection for RAN measurements."""

import numpy as np
import pandas as pd

from ran_intelligence.analytics.kpi import KPI_DEFINITIONS

DEFAULT_METRICS = [
    "lte_rsrp_dbm",
    "lte_sinr_db",
    "nr_rsrp_dbm",
    "nr_sinr_db",
    "nr_cqi",
    "nr_mcs",
]


def detect_kpi_anomalies(
    df: pd.DataFrame,
    metrics: list[str] | None = None,
    group_by: tuple[str, ...] = ("session_id",),
    threshold: float = 3.5,
    min_samples: int = 20,
) -> pd.DataFrame:
    """Detect KPI outliers using a robust modified Z-score.

    Each KPI is evaluated independently within each group.
    Missing KPI values are excluded from detection.

    Returns one row per valid measurement and KPI, including
    the baseline median, robust score and anomaly flag.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame.")

    if df.empty:
        raise ValueError("df cannot be empty.")

    if threshold <= 0:
        raise ValueError("threshold must be positive.")

    if min_samples < 2:
        raise ValueError("min_samples must be at least 2.")

    metrics = metrics or DEFAULT_METRICS

    if not metrics:
        raise ValueError("At least one KPI metric is required.")

    unknown = set(metrics) - set(KPI_DEFINITIONS)
    if unknown:
        raise ValueError(f"Unknown KPI metrics: {sorted(unknown)}")

    required = {"measurement_id", "timestamp", *group_by}
    missing_columns = required - set(df.columns)

    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    missing_metrics = set(metrics) - set(df.columns)
    if missing_metrics:
        raise ValueError(f"Missing KPI columns: {sorted(missing_metrics)}")

    records = []

    grouped = df.groupby(
        list(group_by),
        dropna=False,
        sort=False,
    )

    for group_key, group in grouped:
        if len(group_by) == 1:
            group_values = {group_by[0]: group_key[0]}
        else:
            group_values = dict(zip(group_by, group_key))

        for metric in metrics:
            values = pd.to_numeric(
                group[metric],
                errors="coerce",
            )

            valid = values.notna() & np.isfinite(values)
            observed = values.loc[valid]

            if len(observed) < min_samples:
                continue

            median = float(observed.median())
            mad = float((observed - median).abs().median())

            if mad > 0:
                scale = 1.4826 * mad
            else:
                q1 = float(observed.quantile(0.25))
                q3 = float(observed.quantile(0.75))
                iqr = q3 - q1

                if iqr > 0:
                    scale = iqr / 1.349
                else:
                    # Degenerate baseline: fall back to standard deviation.
                    scale = float(observed.std(ddof=0))

            if scale > 0:
                scores = (observed - median) / scale
                flags = scores.abs() > threshold
            else:
                scores = pd.Series(
                    0.0,
                    index=observed.index,
                )
                flags = pd.Series(
                    False,
                    index=observed.index,
                )

            for index, value in observed.items():
                source_row = group.loc[index]

                record = {
                    **group_values,
                    "measurement_id": source_row["measurement_id"],
                    "timestamp": source_row["timestamp"],
                    "kpi": metric,
                    "value": float(value),
                    "baseline_median": median,
                    "robust_z_score": float(scores.loc[index]),
                    "is_anomaly": bool(flags.loc[index]),
                }

                records.append(record)

    columns = [
        *group_by,
        "measurement_id",
        "timestamp",
        "kpi",
        "value",
        "baseline_median",
        "robust_z_score",
        "is_anomaly",
    ]

    return pd.DataFrame(records, columns=columns)
