
"""Visualisations for digital-twin scenario comparisons."""

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

REQUIRED_COLUMNS = {
    "scenario",
    "total_throughput_mbps",
    "demand_satisfaction",
    "mean_sinr_db",
}


def plot_scenario_comparison(comparison: pd.DataFrame) -> go.Figure:
    """Compare throughput, demand satisfaction and SINR across scenarios."""
    missing = REQUIRED_COLUMNS - set(comparison.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    if comparison.empty:
        raise ValueError("Scenario comparison cannot be empty.")

    data = comparison.copy()

    fig = make_subplots(
        rows=1,
        cols=3,
        subplot_titles=(
            "Total Throughput (Mbps)",
            "Demand Satisfaction",
            "Mean SINR (dB)",
        ),
    )

    metrics = [
        ("total_throughput_mbps", "Throughput", 1),
        ("demand_satisfaction", "Demand satisfaction", 2),
        ("mean_sinr_db", "Mean SINR", 3),
    ]

    for column, label, col in metrics:
        fig.add_trace(
            go.Bar(
                x=data["scenario"],
                y=data[column],
                name=label,
                showlegend=False,
                text=data[column].round(2),
                textposition="outside",
            ),
            row=1,
            col=col,
        )

    fig.update_layout(
        title="RAN Digital Twin — What-if Scenario Comparison",
        template="plotly_white",
        height=480,
        margin=dict(l=35, r=35, t=90, b=110),
    )

    fig.update_xaxes(tickangle=-25)
    fig.update_yaxes(title_text="Mbps", row=1, col=1)
    fig.update_yaxes(title_text="Ratio", row=1, col=2)
    fig.update_yaxes(title_text="dB", row=1, col=3)

    return fig


def save_scenario_visualization(
    comparison: pd.DataFrame,
    output_path: str | Path,
) -> str:
    """Save the interactive scenario comparison as HTML."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    figure = plot_scenario_comparison(comparison)
    figure.write_html(str(path), include_plotlyjs=True)

    return str(path)
