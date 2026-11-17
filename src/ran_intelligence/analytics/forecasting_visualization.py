
"""Reusable visualizations for KPI forecasting experiments."""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

PREDICTION_COLUMNS = {
    "persistence_prediction": "Persistence",
    "random_forest_prediction": "Random Forest",
    "xgboost_prediction": "XGBoost",
    "linear_trend_prediction": "Linear Trend",
    "gru_prediction": "GRU",
}


def _validate_predictions(predictions):
    if not isinstance(predictions, pd.DataFrame) or predictions.empty:
        raise ValueError("predictions must be a non-empty DataFrame")

    required = {"origin_timestamp", "target_timestamp", "actual"}
    missing = required - set(predictions.columns)

    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    available = [
        column for column in PREDICTION_COLUMNS
        if column in predictions.columns
    ]

    if not available:
        raise ValueError("No supported model prediction columns found")

    return available


def plot_forecast_comparison(
    predictions: pd.DataFrame,
    session_id: str,
    metric: str = "nr_sinr_db",
):
    """Compare actual values and all available model predictions."""
    available = _validate_predictions(predictions)

    if "session_id" in predictions.columns:
        data = predictions.loc[
            predictions["session_id"] == session_id
        ].copy()
    else:
        data = predictions.copy()

    if data.empty:
        raise ValueError(f"No predictions found for session: {session_id}")

    data = data.sort_values("target_timestamp")

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=data["target_timestamp"],
        y=data["actual"],
        mode="lines",
        name="Actual",
        line={"width": 2.8},
    ))

    for column in available:
        fig.add_trace(go.Scatter(
            x=data["target_timestamp"],
            y=data[column],
            mode="lines",
            name=PREDICTION_COLUMNS[column],
            line={"width": 1.8},
        ))

    fig.update_layout(
        title=f"{metric} Forecast Comparison — {session_id}",
        xaxis_title="Target timestamp",
        yaxis_title=metric,
        template="plotly_white",
        hovermode="x unified",
        legend_title="Series",
    )

    return fig


def plot_forecast_metric_comparison(
    metrics: pd.DataFrame,
    metric: str = "mae",
):
    """Compare a forecasting metric across models and sessions."""
    required = {"session_id", "model", metric}

    if not isinstance(metrics, pd.DataFrame) or metrics.empty:
        raise ValueError("metrics must be a non-empty DataFrame")

    missing = required - set(metrics.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    fig = go.Figure()

    for session_id in sorted(metrics["session_id"].unique()):
        subset = metrics.loc[metrics["session_id"] == session_id]

        fig.add_trace(go.Bar(
            x=subset["model"],
            y=subset[metric],
            name=session_id,
        ))

    fig.update_layout(
        title=f"Forecasting Model Comparison — {metric.upper()}",
        xaxis_title="Model",
        yaxis_title=metric.upper(),
        barmode="group",
        template="plotly_white",
    )

    return fig


def plot_forecast_residuals(
    predictions: pd.DataFrame,
    session_id: str,
):
    """Plot prediction residuals over time for available models."""
    available = _validate_predictions(predictions)

    if "session_id" in predictions.columns:
        data = predictions.loc[
            predictions["session_id"] == session_id
        ].copy()
    else:
        data = predictions.copy()

    if data.empty:
        raise ValueError(f"No predictions found for session: {session_id}")

    data = data.sort_values("target_timestamp")

    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=False,
        vertical_spacing=0.14,
        subplot_titles=("Residuals over time", "Residual distributions"),
    )

    for column in available:
        residual = data["actual"] - data[column]
        label = PREDICTION_COLUMNS[column]

        fig.add_trace(
            go.Scatter(
                x=data["target_timestamp"],
                y=residual,
                mode="lines",
                name=label,
            ),
            row=1,
            col=1,
        )

        fig.add_trace(
            go.Histogram(
                x=residual,
                name=label,
                opacity=0.55,
                nbinsx=25,
            ),
            row=2,
            col=1,
        )

    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="black",
        row=1,
        col=1,
    )

    fig.update_layout(
        title=f"Forecast Residual Analysis — {session_id}",
        template="plotly_white",
        barmode="overlay",
        height=700,
        xaxis_title="Target timestamp",
        yaxis_title="Actual − predicted",
        xaxis2_title="Residual",
        yaxis2_title="Frequency",
    )

    return fig


def plot_gru_seed_stability(
    seed_results: pd.DataFrame,
    metric: str = "mae",
):
    """Compare GRU metric distributions across random seeds."""
    required = {"session_id", "seed", metric}

    if not isinstance(seed_results, pd.DataFrame) or seed_results.empty:
        raise ValueError("seed_results must be a non-empty DataFrame")

    missing = required - set(seed_results.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    fig = go.Figure()

    for session_id in sorted(seed_results["session_id"].unique()):
        subset = seed_results.loc[
            seed_results["session_id"] == session_id
        ]

        fig.add_trace(go.Box(
            y=subset[metric],
            name=session_id,
            boxpoints="all",
            jitter=0.25,
            pointpos=0,
        ))

    fig.update_layout(
        title=f"GRU Training Stability Across Random Seeds — {metric.upper()}",
        xaxis_title="Session",
        yaxis_title=metric.upper(),
        template="plotly_white",
    )

    return fig
