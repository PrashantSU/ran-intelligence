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
