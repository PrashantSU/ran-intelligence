"""AERPAW dataset ingestion and measurement alignment."""

from pathlib import Path

import pandas as pd

from ran_intelligence.core.exceptions import DataError

# Source CSV filename: (actual source column, internal column name)
METRIC_FILES = {
    "inputf1_cellid_with_header.csv": ("LTE Cell ID", "lte_cell_id"),
    "inputf1_rsrp_with_header.csv": ("LTE RSRP", "lte_rsrp_dbm"),
    "inputf1_sinr_with_header.csv": ("LTE SINR", "lte_sinr_db"),
    "inputf2_cellid_with_header.csv": ("NR Cell ID", "nr_cell_id"),
    "inputf2_rsrp_with_header.csv": ("NR RSRP", "nr_rsrp_dbm"),
    "inputf2_sinr_with_header.csv": ("NR SINR", "nr_sinr_db"),
    "inputf2_cqi_with_header.csv": ("NR CQI", "nr_cqi"),
    "inputf2_mcs_with_header.csv": ("NR MCS", "nr_mcs"),
    "inputf2_ri_with_header.csv": ("NR RI", "nr_rank_indicator"),
}

THROUGHPUT_FILE = "input_throughput_with_header.csv"

IDENTIFIER_COLUMNS = [
    "ID",
    "Time and date",
    "Longitude",
    "Latitude",
    "Altitude",
]


def _read_measurement_csv(
    path: Path,
    source_metric: str,
    canonical_metric: str,
) -> pd.DataFrame:
    """Read one CSV and standardise its column names."""

    try:
        df = pd.read_csv(path, encoding="utf-8")
    except UnicodeDecodeError:
        df = pd.read_csv(path, encoding="latin-1")

    required = IDENTIFIER_COLUMNS + [source_metric]
    missing = [col for col in required if col not in df.columns]

    if missing:
        raise DataError(f"Missing columns in {path.name}: {missing}")

    df = df[required].copy()

    df = df.rename(
        columns={
            "ID": "measurement_id",
            "Time and date": "timestamp",
            "Longitude": "longitude",
            "Latitude": "latitude",
            "Altitude": "altitude_m",
            source_metric: canonical_metric,
        }
    )

    df["measurement_id"] = pd.to_numeric(df["measurement_id"], errors="coerce")

    df["timestamp"] = pd.to_datetime(df["timestamp"], format="mixed", errors="coerce")

    numeric_columns = [
        "longitude",
        "latitude",
        "altitude_m",
        canonical_metric,
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    if df["measurement_id"].isna().any():
        raise DataError(f"Missing or invalid measurement IDs in {path.name}")

    if df["measurement_id"].duplicated().any():
        raise DataError(f"Duplicate measurement IDs in {path.name}")

    df["measurement_id"] = df["measurement_id"].astype("int64")

    return df


def _load_throughput(session_dir: Path) -> pd.DataFrame:
    """Load throughput observations independently."""

    return _read_measurement_csv(
        session_dir / THROUGHPUT_FILE,
        "Throughput",
        "throughput_raw",
    ).rename(
        columns={
            "measurement_id": "throughput_id",
            "timestamp": "throughput_timestamp",
            "longitude": "throughput_longitude",
            "latitude": "throughput_latitude",
            "altitude_m": "throughput_altitude_m",
        }
    )


def load_aerpaw_session(
    session_dir: str | Path,
    session_id: str | None = None,
    tolerance_ms: int = 250,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load and align one AERPAW session.

    Returns:
        Unified radio measurements with matched throughput.
        Throughput observations that could not be matched.
    """

    session_dir = Path(session_dir)

    if not session_dir.exists():
        raise DataError(f"Session directory does not exist: {session_dir}")

    if tolerance_ms < 0:
        raise ValueError("tolerance_ms cannot be negative.")

    session_id = session_id or session_dir.name

    merged = None
    reference_ids = None
    timestamp_diagnostics = {}

    for filename, (source_metric, canonical_metric) in METRIC_FILES.items():
        path = session_dir / filename

        if not path.exists():
            raise DataError(f"Required file not found: {path}")

        df = _read_measurement_csv(path, source_metric, canonical_metric)

        current_ids = set(df["measurement_id"])

        if reference_ids is None:
            reference_ids = current_ids
            merged = df[
                [
                    "measurement_id",
                    "timestamp",
                    "longitude",
                    "latitude",
                    "altitude_m",
                    canonical_metric,
                ]
            ].copy()
            continue

        if current_ids != reference_ids:
            raise DataError(
                f"Measurement IDs differ in {filename}. "
                "Inspect the source streams before combining them."
            )

        # Compare timestamps but retain the reference stream timestamp.
        comparison = merged[["measurement_id", "timestamp"]].merge(
            df[["measurement_id", "timestamp"]],
            on="measurement_id",
            suffixes=("_reference", "_stream"),
            validate="one_to_one",
        )

        differences = (comparison["timestamp_reference"] - comparison["timestamp_stream"]).abs()

        timestamp_diagnostics[canonical_metric] = (
            differences.max().total_seconds() if differences.notna().any() else None
        )

        merged = merged.merge(
            df[["measurement_id", canonical_metric]],
            on="measurement_id",
            how="left",
            validate="one_to_one",
        )

    if merged is None:
        raise DataError("No radio measurement files were loaded.")

    merged["session_id"] = session_id

    if merged["timestamp"].isna().any():
        raise DataError("Reference radio stream contains invalid timestamps.")

    throughput = _load_throughput(session_dir)

    # Separate invalid timestamps so merge_asof can process valid rows.
    invalid_time = throughput[throughput["throughput_timestamp"].isna()].copy()

    valid_time = throughput[throughput["throughput_timestamp"].notna()].copy()

    radio_sorted = merged.sort_values("timestamp")
    throughput_sorted = valid_time.sort_values("throughput_timestamp")

    matched_candidates = pd.merge_asof(
        throughput_sorted,
        radio_sorted,
        left_on="throughput_timestamp",
        right_on="timestamp",
        direction="nearest",
        tolerance=pd.Timedelta(milliseconds=tolerance_ms),
    )

    matched = matched_candidates[matched_candidates["measurement_id"].notna()].copy()

    unmatched_valid = matched_candidates[matched_candidates["measurement_id"].isna()].copy()

    unmatched_throughput = pd.concat(
        [unmatched_valid, invalid_time],
        ignore_index=True,
        sort=False,
    )

    matched["measurement_id"] = matched["measurement_id"].astype("int64")

    if matched["measurement_id"].duplicated().any():
        raise DataError("A radio observation was matched to multiple throughput observations.")

    matched["throughput_time_diff_ms"] = (
        matched["throughput_timestamp"] - matched["timestamp"]
    ).abs().dt.total_seconds() * 1000

    measurements = merged.merge(
        matched[
            [
                "measurement_id",
                "throughput_raw",
                "throughput_timestamp",
                "throughput_time_diff_ms",
            ]
        ],
        on="measurement_id",
        how="left",
        validate="one_to_one",
    )

    measurements["session_id"] = session_id

    print(f"SESSION: {session_id}")
    print(f"Radio observations: {len(merged)}")
    print(f"Throughput observations: {len(throughput)}")
    print(f"Matched throughput: {len(matched)}")
    print(f"Unmatched throughput: {len(unmatched_throughput)}")
    print(
        "Radio observations without throughput:",
        len(merged) - len(matched),
    )

    print("Maximum radio-stream timestamp differences:")
    for metric, difference in timestamp_diagnostics.items():
        print(f"  {metric}: {difference} seconds")

    if not matched.empty:
        print(
            "Maximum throughput matching difference:",
            round(matched["throughput_time_diff_ms"].max(), 3),
            "ms",
        )

    return measurements, unmatched_throughput


def load_aerpaw_dataset(
    data_dir: str | Path,
    sessions: list[str] | None = None,
    tolerance_ms: int = 250,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Load and combine multiple AERPAW sessions."""

    data_dir = Path(data_dir)
    sessions = sessions or ["yaw315", "yaw45"]

    measurements_list = []
    unmatched_list = []

    for session in sessions:
        measurements, unmatched = load_aerpaw_session(
            data_dir / "Dryad" / session,
            session_id=session,
            tolerance_ms=tolerance_ms,
        )

        measurements_list.append(measurements)
        unmatched_list.append(unmatched)

    return (
        pd.concat(measurements_list, ignore_index=True),
        pd.concat(unmatched_list, ignore_index=True),
    )
