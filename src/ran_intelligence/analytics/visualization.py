"""Interactive Plotly visualisations for RAN KPI monitoring."""

import pandas as pd
import plotly.graph_objects as go

from ran_intelligence.analytics.kpi import KPI_DEFINITIONS


def plot_kpi_timeseries(
    timeseries: pd.DataFrame,
    session_id: str,
    metric: str,
) -> go.Figure:
    """Plot an aggregated KPI time series for one session."""
    if metric not in KPI_DEFINITIONS:
        raise ValueError(f"Unsupported KPI: {metric}")

    required = {"session_id", "kpi", "timestamp", "value", "sample_count"}
    missing = required - set(timeseries.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    data = timeseries.loc[
        (timeseries["session_id"] == session_id) & (timeseries["kpi"] == metric)
    ].copy()

    if data.empty:
        raise ValueError(f"No time-series data for {session_id}, {metric}.")

    definition = KPI_DEFINITIONS[metric]
    data["timestamp"] = pd.to_datetime(data["timestamp"])

    figure = go.Figure()
    figure.add_trace(
        go.Scatter(
            x=data["timestamp"],
            y=data["value"],
            mode="lines+markers",
            name=definition["label"],
            customdata=data[["sample_count"]],
            hovertemplate=(
                "Time: %{x}<br>Value: %{y:.2f}<br>Observations: %{customdata[0]}<extra></extra>"
            ),
        )
    )

    figure.update_layout(
        title=f"{definition['label']} — {session_id}",
        xaxis_title="Time",
        yaxis_title=f"{definition['label']} ({definition['unit']})",
        template="plotly_white",
        hovermode="x unified",
    )
    return figure


def plot_session_kpi_comparison(
    summary: pd.DataFrame,
    metric: str,
) -> go.Figure:
    """Compare median KPI values across measurement sessions."""
    if metric not in KPI_DEFINITIONS:
        raise ValueError(f"Unsupported KPI: {metric}")

    required = {"session_id", "kpi", "median", "valid_observations"}
    missing = required - set(summary.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    data = summary.loc[summary["kpi"] == metric].copy()
    if data.empty:
        raise ValueError(f"No summary data available for {metric}.")

    definition = KPI_DEFINITIONS[metric]

    figure = go.Figure(
        go.Bar(
            x=data["session_id"],
            y=data["median"],
            text=data["median"].round(2),
            textposition="outside",
            customdata=data[["valid_observations"]],
            hovertemplate=(
                "Session: %{x}<br>"
                "Median: %{y:.2f}<br>"
                "Valid observations: %{customdata[0]}"
                "<extra></extra>"
            ),
        )
    )

    figure.update_layout(
        title=f"{definition['label']} — Session Comparison",
        xaxis_title="Session",
        yaxis_title=f"Median ({definition['unit']})",
        template="plotly_white",
    )
    return figure


def plot_kpi_missingness(summary: pd.DataFrame) -> go.Figure:
    """Compare missing KPI observations as percentages by session."""
    required = {"session_id", "kpi", "total_observations", "missing_observations"}
    missing = required - set(summary.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    data = summary.copy()
    data["missing_pct"] = 100 * data["missing_observations"] / data["total_observations"]

    figure = go.Figure()
    for session_id, group in data.groupby("session_id", sort=True):
        figure.add_trace(
            go.Bar(
                x=group["kpi"],
                y=group["missing_pct"],
                name=str(session_id),
                hovertemplate=("KPI: %{x}<br>Missing: %{y:.2f}%<extra></extra>"),
            )
        )

    figure.update_layout(
        title="KPI Missingness by Session",
        xaxis_title="KPI",
        yaxis_title="Missing observations (%)",
        barmode="group",
        template="plotly_white",
    )
    return figure


def plot_anomaly_detection(
    measurements: pd.DataFrame,
    anomalies: pd.DataFrame,
    session_id: str,
    metric: str,
):
    """Plot raw KPI measurements and detected anomaly observations."""
    import plotly.graph_objects as go

    required_measurement_columns = {"session_id", "timestamp", metric}
    required_anomaly_columns = {
        "session_id",
        "kpi",
        "timestamp",
        "value",
        "robust_z_score",
        "is_anomaly",
    }

    missing_measurements = required_measurement_columns - set(measurements.columns)
    missing_anomalies = required_anomaly_columns - set(anomalies.columns)

    if missing_measurements:
        raise ValueError(f"Measurements missing columns: {sorted(missing_measurements)}")
    if missing_anomalies:
        raise ValueError(f"Anomalies missing columns: {sorted(missing_anomalies)}")

    session_data = measurements[measurements["session_id"] == session_id].copy()

    if session_data.empty:
        raise ValueError(f"No measurements found for session: {session_id}")

    session_data["timestamp"] = pd.to_datetime(session_data["timestamp"], errors="coerce")
    session_data[metric] = pd.to_numeric(session_data[metric], errors="coerce")
    session_data = session_data.dropna(subset=["timestamp", metric]).sort_values("timestamp")

    if session_data.empty:
        raise ValueError(f"No valid observations found for {metric} in {session_id}")

    anomaly_data = anomalies[
        (anomalies["session_id"] == session_id)
        & (anomalies["kpi"] == metric)
        & anomalies["is_anomaly"].astype(bool)
    ].copy()

    anomaly_data["timestamp"] = pd.to_datetime(anomaly_data["timestamp"], errors="coerce")
    anomaly_data["value"] = pd.to_numeric(anomaly_data["value"], errors="coerce")
    anomaly_data["robust_z_score"] = pd.to_numeric(anomaly_data["robust_z_score"], errors="coerce")
    anomaly_data = anomaly_data.dropna(subset=["timestamp", "value", "robust_z_score"])

    fig = go.Figure()

    fig.add_trace(
        go.Scattergl(
            x=session_data["timestamp"],
            y=session_data[metric],
            mode="lines",
            name="KPI measurements",
            line={"width": 1.2},
        )
    )

    fig.add_trace(
        go.Scatter(
            x=anomaly_data["timestamp"],
            y=anomaly_data["value"],
            mode="markers",
            name="Detected anomalies",
            marker={
                "symbol": "x",
                "size": 10,
                "color": "red",
            },
            customdata=anomaly_data[["robust_z_score"]].to_numpy(),
            hovertemplate=(
                "Time: %{x}<br>"
                "Value: %{y}<br>"
                "Robust z-score: %{customdata[0]:.2f}"
                "<extra>Anomaly</extra>"
            ),
        )
    )

    fig.update_layout(
        title=f"{metric} — {session_id}",
        xaxis_title="Timestamp",
        yaxis_title=metric,
        hovermode="closest",
        template="plotly_white",
        legend_title="Observation type",
    )

    return fig


def plot_forecast_predictions(
    predictions: pd.DataFrame,
    session_id: str,
    metric: str,
):
    """Plot actual values against baseline and model forecasts."""
    import plotly.graph_objects as go

    required = {
        "origin_timestamp",
        "target_timestamp",
        "actual",
        "persistence_prediction",
        "random_forest_prediction",
    }

    missing = required - set(predictions.columns)
    if missing:
        raise ValueError(f"Missing prediction columns: {sorted(missing)}")

    if predictions.empty:
        raise ValueError("Predictions cannot be empty.")

    data = predictions.sort_values("target_timestamp").copy()

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=data["target_timestamp"],
            y=data["actual"],
            mode="lines",
            name="Actual",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=data["target_timestamp"],
            y=data["persistence_prediction"],
            mode="lines",
            name="Persistence baseline",
        )
    )

    fig.add_trace(
        go.Scatter(
            x=data["target_timestamp"],
            y=data["random_forest_prediction"],
            mode="lines",
            name="Random Forest",
        )
    )

    unit = KPI_DEFINITIONS.get(metric, {"unit": ""})["unit"]

    fig.update_layout(
        title=f"{metric} — 5-second forecast ({session_id})",
        xaxis_title="Target timestamp",
        yaxis_title=unit,
        hovermode="x unified",
        template="plotly_white",
        legend_title="Forecast",
    )

    return fig
