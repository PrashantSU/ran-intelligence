"""Reusable AERPAW data processing pipeline."""

import json
from datetime import UTC, datetime
from pathlib import Path

from ran_intelligence.core.exceptions import DataValidationError
from ran_intelligence.data.aerpaw_loader import load_aerpaw_dataset
from ran_intelligence.data.validation import validate_measurement_dataframe


def run_aerpaw_pipeline(
    raw_data_dir: str | Path,
    output_dir: str | Path,
    sessions: list[str] | None = None,
    tolerance_ms: int = 250,
) -> dict:
    """Load, validate and persist the AERPAW dataset."""

    raw_data_dir = Path(raw_data_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load raw measurements and unmatched throughput.
    measurements, unmatched = load_aerpaw_dataset(
        data_dir=raw_data_dir,
        sessions=sessions,
        tolerance_ms=tolerance_ms,
    )

    # 2. Validate the unified measurement dataset.
    validation_report = validate_measurement_dataframe(measurements)

    if not validation_report["valid"]:
        raise DataValidationError(
            "AERPAW dataset validation failed.",
            details=validation_report,
        )

    if validation_report["warnings"]:
        raise DataValidationError(
            "AERPAW dataset contains validation warnings.",
            details=validation_report,
        )

    # 3. Persist processed datasets.
    measurements_path = output_dir / "aerpaw_measurements.parquet"
    unmatched_path = output_dir / "aerpaw_unmatched_throughput.parquet"
    report_path = output_dir / "aerpaw_quality_report.json"

    measurements.to_parquet(measurements_path, index=False)
    unmatched.to_parquet(unmatched_path, index=False)

    # 4. Create a reproducible quality summary.
    quality_summary = {
        "pipeline": "aerpaw",
        "processed_at_utc": datetime.now(UTC).isoformat(),
        "sessions": sorted(measurements["session_id"].unique().tolist()),
        "measurement_rows": int(len(measurements)),
        "unmatched_throughput_rows": int(len(unmatched)),
        "matched_throughput_rows": int(measurements["throughput_raw"].notna().sum()),
        "missing_values": {
            column: int(count) for column, count in measurements.isna().sum().items()
        },
        "validation": validation_report,
        "outputs": {
            "measurements": measurements_path.name,
            "unmatched_throughput": unmatched_path.name,
        },
    }

    report_path.write_text(
        json.dumps(quality_summary, indent=2, default=str),
        encoding="utf-8",
    )

    return {
        "measurements": measurements,
        "unmatched_throughput": unmatched,
        "quality_summary": quality_summary,
        "output_paths": {
            "measurements": measurements_path,
            "unmatched_throughput": unmatched_path,
            "quality_report": report_path,
        },
    }
