
"""Simplified, deterministic radio network digital twin.

This is a portfolio-grade system-level approximation, not a full 3GPP
link-level or commercial network simulator.
"""

from dataclasses import dataclass
from math import log10
from typing import Any

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class Cell:
    cell_id: str
    x_m: float
    y_m: float
    tx_power_dbm: float = 46.0
    bandwidth_mhz: float = 20.0
    noise_figure_db: float = 7.0
    interference_scale: float = 1.0
    active: bool = True

    def __post_init__(self):
        if not self.cell_id:
            raise ValueError("cell_id must not be empty")
        if self.bandwidth_mhz <= 0:
            raise ValueError("bandwidth_mhz must be positive")
        if self.noise_figure_db < 0:
            raise ValueError("noise_figure_db must be non-negative")
        if self.interference_scale < 0:
            raise ValueError("interference_scale must be non-negative")


@dataclass(frozen=True)
class UserEquipment:
    ue_id: str
    x_m: float
    y_m: float
    demand_mbps: float = 10.0

    def __post_init__(self):
        if not self.ue_id:
            raise ValueError("ue_id must not be empty")
        if self.demand_mbps < 0:
            raise ValueError("demand_mbps must be non-negative")


@dataclass(frozen=True)
class NetworkScenario:
    cells: tuple[Cell, ...]
    users: tuple[UserEquipment, ...]
    scenario_name: str = "baseline"
    path_loss_exponent: float = 3.5
    reference_loss_db: float = 38.0
    min_distance_m: float = 10.0
    max_spectral_efficiency: float = 7.4
    capacity_factor: float = 0.75

    def __post_init__(self):
        if not self.cells:
            raise ValueError("At least one cell is required")
        if not self.users:
            raise ValueError("At least one UE is required")
        if len({c.cell_id for c in self.cells}) != len(self.cells):
            raise ValueError("Cell IDs must be unique")
        if len({u.ue_id for u in self.users}) != len(self.users):
            raise ValueError("UE IDs must be unique")
        if self.path_loss_exponent <= 0:
            raise ValueError("path_loss_exponent must be positive")
        if self.min_distance_m <= 0:
            raise ValueError("min_distance_m must be positive")
        if self.max_spectral_efficiency <= 0:
            raise ValueError("max_spectral_efficiency must be positive")
        if not 0 < self.capacity_factor <= 1:
            raise ValueError("capacity_factor must be in (0, 1]")


def path_loss_db(
    distance_m: float,
    reference_loss_db: float = 38.0,
    path_loss_exponent: float = 3.5,
    min_distance_m: float = 10.0,
) -> float:
    """Log-distance path-loss approximation."""
    if distance_m < 0:
        raise ValueError("distance_m must be non-negative")
    if path_loss_exponent <= 0 or min_distance_m <= 0:
        raise ValueError("Path-loss parameters must be positive")

    distance = max(distance_m, min_distance_m)
    return reference_loss_db + 10 * path_loss_exponent * log10(distance / 1.0)


def dbm_to_mw(power_dbm: float) -> float:
    """Convert power in dBm to milliwatts."""
    return 10 ** (power_dbm / 10)


def mw_to_dbm(power_mw: float) -> float:
    """Convert power in milliwatts to dBm."""
    if power_mw <= 0:
        return float("-inf")
    return 10 * log10(power_mw)


def shannon_spectral_efficiency(
    sinr_db: float,
    maximum: float = 7.4,
) -> float:
    """Calculate capped Shannon spectral efficiency in bits/s/Hz."""
    sinr_linear = 10 ** (sinr_db / 10)
    return min(log10(1 + sinr_linear) / log10(2), maximum)


def _received_power_dbm(
    cell: Cell,
    ue: UserEquipment,
    scenario: NetworkScenario,
) -> tuple[float, float]:
    distance = float(np.hypot(cell.x_m - ue.x_m, cell.y_m - ue.y_m))
    loss = path_loss_db(
        distance,
        reference_loss_db=scenario.reference_loss_db,
        path_loss_exponent=scenario.path_loss_exponent,
        min_distance_m=scenario.min_distance_m,
    )
    return cell.tx_power_dbm - loss, distance


def simulate_network(scenario: NetworkScenario) -> dict[str, Any]:
    """Simulate UE association, radio quality and approximate cell capacity."""
    active_cells = [cell for cell in scenario.cells if cell.active]
    if not active_cells:
        raise ValueError("At least one cell must be active")

    ue_records = []

    for ue in scenario.users:
        received = {}
        distances = {}

        for cell in active_cells:
            power, distance = _received_power_dbm(cell, ue, scenario)
            received[cell.cell_id] = power
            distances[cell.cell_id] = distance

        serving_id = max(received, key=received.get)
        serving_cell = next(c for c in active_cells if c.cell_id == serving_id)
        signal_mw = dbm_to_mw(received[serving_id])

        interference_mw = sum(
            dbm_to_mw(power) * cell.interference_scale
            for cell in active_cells
            if cell.cell_id != serving_id
            for power in [received[cell.cell_id]]
        )

        bandwidth_hz = serving_cell.bandwidth_mhz * 1e6
        noise_dbm = (
            -174
            + 10 * log10(bandwidth_hz)
            + serving_cell.noise_figure_db
        )
        noise_mw = dbm_to_mw(noise_dbm)

        sinr_linear = signal_mw / (interference_mw + noise_mw)
        sinr_db = 10 * log10(sinr_linear)
        efficiency = shannon_spectral_efficiency(
            sinr_db,
            scenario.max_spectral_efficiency,
        )

        ue_records.append({
            "ue_id": ue.ue_id,
            "x_m": ue.x_m,
            "y_m": ue.y_m,
            "demand_mbps": ue.demand_mbps,
            "serving_cell": serving_id,
            "distance_m": distances[serving_id],
            "rsrp_dbm": received[serving_id],
            "sinr_db": sinr_db,
            "spectral_efficiency_bps_hz": efficiency,
            "estimated_capacity_mbps": (
                serving_cell.bandwidth_mhz
                * efficiency
                * scenario.capacity_factor
            ),
        })

    ue_metrics = pd.DataFrame(ue_records)

    cell_records = []
    for cell in active_cells:
        assigned = ue_metrics[ue_metrics["serving_cell"] == cell.cell_id]
        total_demand = float(assigned["demand_mbps"].sum())

        if assigned.empty:
            mean_efficiency = 0.0
        else:
            mean_efficiency = float(
                assigned["spectral_efficiency_bps_hz"].mean()
            )

        capacity = (
            cell.bandwidth_mhz
            * mean_efficiency
            * scenario.capacity_factor
        )

        served = min(total_demand, capacity)
        utilisation = (
            min(total_demand / capacity, 1.0) if capacity > 0 else 0.0
        )

        for index in assigned.index:
            demand = float(ue_metrics.at[index, "demand_mbps"])
            share = demand / total_demand if total_demand > 0 else 0.0
            ue_metrics.at[index, "throughput_mbps"] = served * share

        cell_records.append({
            "cell_id": cell.cell_id,
            "active": cell.active,
            "ue_count": len(assigned),
            "total_demand_mbps": total_demand,
            "estimated_capacity_mbps": capacity,
            "served_throughput_mbps": served,
            "prb_utilisation": utilisation,
            "mean_sinr_db": (
                float(assigned["sinr_db"].mean())
                if not assigned.empty else np.nan
            ),
        })

    cell_metrics = pd.DataFrame(cell_records)

    if "throughput_mbps" not in ue_metrics:
        ue_metrics["throughput_mbps"] = 0.0
    ue_metrics["throughput_mbps"] = ue_metrics["throughput_mbps"].fillna(0.0)

    total_demand = float(ue_metrics["demand_mbps"].sum())
    total_throughput = float(ue_metrics["throughput_mbps"].sum())

    summary = {
        "scenario_name": scenario.scenario_name,
        "active_cells": len(active_cells),
        "ue_count": len(scenario.users),
        "total_demand_mbps": total_demand,
        "total_throughput_mbps": total_throughput,
        "demand_satisfaction": (
            total_throughput / total_demand if total_demand else 1.0
        ),
        "mean_sinr_db": float(ue_metrics["sinr_db"].mean()),
        "mean_rsrp_dbm": float(ue_metrics["rsrp_dbm"].mean()),
        "overloaded_cells": int(
            (cell_metrics["prb_utilisation"] >= 1.0).sum()
        ),
    }

    return {
        "summary": summary,
        "ue_metrics": ue_metrics,
        "cell_metrics": cell_metrics,
    }


def compare_scenarios(
    baseline: NetworkScenario,
    alternative: NetworkScenario,
) -> pd.DataFrame:
    """Compare aggregate KPIs between two network scenarios."""
    base = simulate_network(baseline)["summary"]
    alt = simulate_network(alternative)["summary"]

    metrics = [
        "total_throughput_mbps",
        "mean_sinr_db",
        "mean_rsrp_dbm",
        "demand_satisfaction",
        "overloaded_cells",
    ]

    return pd.DataFrame([
        {
            "metric": metric,
            "baseline": base[metric],
            "alternative": alt[metric],
            "change": alt[metric] - base[metric],
        }
        for metric in metrics
    ])
