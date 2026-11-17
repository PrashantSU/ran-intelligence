"""Data quality validation for standardised RAN measurements."""

import pandas as pd

from ran_intelligence.data.schemas import ALL_COLUMNS, REQUIRED_COLUMNS

# Additional metadata generated during dataset ingestion.
ALLOWED_METADATA_COLUMNS = [
    "throughput_timestamp",
    "throughput_time_diff_ms",
]


def validate_measurement_dataframe(df: pd.DataFrame) -> dict:
    """Validate a standardised RAN measurement DataFrame.

    Returns a report without modifying or dropping any observations.
    """

    errors = []
    warnings = []

    report = {
        "valid": True,
        "row_count": len(df),
        "errors": errors,
        "warnings": warnings,
    }

    if df.empty:
        warnings.append("The DataFrame contains no observations.")

    # 1. Check required columns.
    missing_columns = [column for column in REQUIRED_COLUMNS if column not in df.columns]

    if missing_columns:
        errors.append(f"Missing required columns: {missing_columns}")
        report["valid"] = False
        return report

    # 2. Report unexpected columns.
    allowed_columns = set(ALL_COLUMNS + ALLOWED_METADATA_COLUMNS)

    unexpected_columns = [column for column in df.columns if column not in allowed_columns]

    if unexpected_columns:
        warnings.append(f"Unexpected columns: {unexpected_columns}")

    # 3. Check missing values in required columns.
    for column in REQUIRED_COLUMNS:
        missing_count = int(df[column].isna().sum())

        if missing_count:
            errors.append(f"{column}: {missing_count} missing values.")

    # 4. Check duplicate measurement identifiers.
    duplicate_count = int(df.duplicated(subset=["session_id", "measurement_id"]).sum())

    if duplicate_count:
        warnings.append(f"{duplicate_count} duplicate session/measurement IDs.")

    # 5. Validate coordinates.
    longitude = pd.to_numeric(df["longitude"], errors="coerce")
    latitude = pd.to_numeric(df["latitude"], errors="coerce")

    invalid_longitude = longitude.notna() & ~longitude.between(-180, 180)
    invalid_latitude = latitude.notna() & ~latitude.between(-90, 90)

    if invalid_longitude.any():
        errors.append(f"{int(invalid_longitude.sum())} invalid longitude values.")

    if invalid_latitude.any():
        errors.append(f"{int(invalid_latitude.sum())} invalid latitude values.")

    # 6. Validate timestamp values.
    parsed_timestamps = pd.to_datetime(
        df["timestamp"],
        format="mixed",
        errors="coerce",
    )

    invalid_timestamps = int(parsed_timestamps.isna().sum())

    if invalid_timestamps:
        errors.append(f"{invalid_timestamps} invalid timestamp values.")

    report["valid"] = len(errors) == 0

    return report
