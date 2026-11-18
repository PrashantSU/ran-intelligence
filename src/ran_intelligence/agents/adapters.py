"""Adapters connecting existing RAN capabilities to incident tools."""

from collections.abc import Callable
from typing import Any

import pandas as pd

from ran_intelligence.agents.schemas import IncidentRequest
from ran_intelligence.agents.tools import InvestigationToolbox
from ran_intelligence.analytics.kpi import compute_kpi_summary
from ran_intelligence.ml.anomaly import detect_kpi_anomalies
from ran_intelligence.ml.forecasting import (
    build_gap_aware_dataset,
    chronological_split,
    evaluate_forecasters,
    prepare_forecasting_series,
)
from ran_intelligence.simulation.runner import run_scenario_suite

SUPPORTED_KPIS = {
    "lte_rsrp_dbm",
    "lte_sinr_db",
    "nr_rsrp_dbm",
    "nr_sinr_db",
    "nr_cqi",
    "nr_mcs",
    "nr_rank_indicator",
    "throughput_raw",
}

COLUMN_ALIASES = {
    "LTE_RSRP_dBm": "lte_rsrp_dbm",
    "LTE_SINR_dB": "lte_sinr_db",
    "NR_RSRP_dBm": "nr_rsrp_dbm",
    "NR_SINR_dB": "nr_sinr_db",
    "NR_CQI": "nr_cqi",
    "NR_MCS": "nr_mcs",
    "NR_Rank_Indicator": "nr_rank_indicator",
    "LTE_cell_id": "lte_cell_id",
    "NR_cell_id": "nr_cell_id",
}


def _normalise_columns(frame: pd.DataFrame) -> pd.DataFrame:
    """Convert recognised source aliases to canonical column names."""
    rename = {
        old: new
        for old, new in COLUMN_ALIASES.items()
        if old in frame.columns and new not in frame.columns
    }
    return frame.rename(columns=rename)


def filter_incident_measurements(
    measurements: pd.DataFrame,
    incident: IncidentRequest,
) -> pd.DataFrame:
    """Select measurements matching the incident session and time window."""
    frame = _normalise_columns(measurements.copy())

    required = {"session_id", "timestamp"}
    missing = required - set(frame.columns)

    if missing:
        raise ValueError(
            f"Measurement data is missing required columns: {sorted(missing)}"
        )

    frame["timestamp"] = pd.to_datetime(
        frame["timestamp"],
        utc=True,
        errors="coerce",
    )

    start = pd.to_datetime(incident.start_time, utc=True)
    end = pd.to_datetime(incident.end_time, utc=True)

    frame = frame.loc[
        (frame["session_id"].astype(str) == str(incident.session_id))
        & frame["timestamp"].between(start, end)
    ].copy()

    if incident.cell_id:
        cell_columns = [
            column
            for column in ("lte_cell_id", "nr_cell_id")
            if column in frame.columns
        ]

        if cell_columns:
            cell_mask = pd.Series(False, index=frame.index)
            for column in cell_columns:
                cell_mask |= (
                    frame[column].astype(str) == str(incident.cell_id)
                )
            frame = frame.loc[cell_mask].copy()

    if frame.empty:
        raise ValueError(
            "No measurements match the incident session, time window "
            "and available cell identifiers."
        )

    return frame


def _numeric_metrics(frame: pd.DataFrame) -> list[str]:
    """Return supported numeric KPI columns only."""
    return [
        column
        for column in SUPPORTED_KPIS
        if column in frame.columns
        and pd.api.types.is_numeric_dtype(frame[column])
    ]


def create_investigation_toolbox(
    measurements: pd.DataFrame,
    rag_handler: Callable[[IncidentRequest], Any] | None = None,
    include_simulation: bool = True,
) -> InvestigationToolbox:
    """Build a toolbox using the project's existing analytical modules."""

    def get_incident_data(incident: IncidentRequest) -> pd.DataFrame:
        return filter_incident_measurements(measurements, incident)

    def kpi_handler(incident: IncidentRequest) -> dict[str, Any]:
        frame = get_incident_data(incident)

        summary = compute_kpi_summary(
            frame,
            group_by=("session_id",),
        )

        return {
            "measurement_count": len(frame),
            "session_id": incident.session_id,
            "cell_id": incident.cell_id,
            "kpi_summary": summary,
        }

    def anomaly_handler(incident: IncidentRequest) -> dict[str, Any]:
        frame = get_incident_data(incident)
        available_metrics = _numeric_metrics(frame)
        metrics = [
            metric
            for metric in incident.suspected_kpis
            if metric in available_metrics
        ]

        if not metrics:
            metrics = available_metrics

        if not metrics:
            raise ValueError("No supported numeric KPI columns are available.")

        # The anomaly detector requires a measurement identifier.
        # Generate an internal row identifier when the source lacks one.
        if "measurement_id" not in frame.columns:
            frame = frame.copy()
            frame["measurement_id"] = range(len(frame))

        anomalies = detect_kpi_anomalies(
            frame,
            metrics=metrics,
            group_by=("session_id",),
        )

        flagged = anomalies.loc[
            anomalies["is_anomaly"].fillna(False).astype(bool)
        ].copy()

        if not flagged.empty:
            flagged["absolute_robust_z_score"] = (
                flagged["robust_z_score"].abs()
            )
            flagged = flagged.sort_values(
                "absolute_robust_z_score",
                ascending=False,
            )

        return {
            "measurement_count": len(frame),
            "metrics": metrics,
            "evaluated_observation_count": len(anomalies),
            "anomaly_count": len(flagged),
            "anomaly_samples": flagged.head(10).drop(
                columns=["absolute_robust_z_score"],
                errors="ignore",
            ),
        }

    def forecast_handler(incident: IncidentRequest) -> dict[str, Any]:
        frame = get_incident_data(incident)

        candidates = [
            metric
            for metric in incident.suspected_kpis
            if metric in _numeric_metrics(frame)
        ]

        if not candidates:
            candidates = _numeric_metrics(frame)

        if not candidates:
            raise ValueError("No supported numeric KPI is available.")

        metric = candidates[0]

        series = prepare_forecasting_series(
            frame,
            session_id=incident.session_id,
            metric=metric,
        )

        dataset = build_gap_aware_dataset(series)

        if len(dataset) < 30:
            raise ValueError(
                f"Insufficient forecasting examples for {metric}: "
                f"{len(dataset)} available; at least 30 required."
            )

        train, test = chronological_split(dataset)

        if train.empty or test.empty:
            raise ValueError("Chronological forecasting split is empty.")

        forecast_results, predictions = evaluate_forecasters(train, test)

        return {
            "metric": metric,
            "forecast_example_count": len(dataset),
            "train_count": len(train),
            "test_count": len(test),
            "model_evaluation": forecast_results,
            "prediction_samples": predictions.head(10),
            "interpretation": (
                "Historical model evaluation, not a confirmed prediction "
                "of the incident's root cause."
            ),
        }

    handlers: dict[str, Callable[[IncidentRequest], Any]] = {
        "kpi": kpi_handler,
        "anomaly": anomaly_handler,
        "forecast": forecast_handler,
    }

    if rag_handler is not None:
        handlers["rag"] = rag_handler

    if include_simulation:
        handlers["simulation"] = lambda incident: {
            "scope": (
                "Reference what-if scenarios; not calibrated to the "
                "incident's exact cell or measurements."
            ),
            "scenario_suite": run_scenario_suite(),
        }

    return InvestigationToolbox(handlers=handlers)
