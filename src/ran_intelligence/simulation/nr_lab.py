
"""Simplified 5G NR scheduling and coordinated beamforming laboratory.

System-level educational model. It does not implement a complete 3GPP
physical layer or commercial-grade multi-cell simulator.
"""

from typing import Any

import numpy as np
import pandas as pd


def proportional_fair_schedule(
    achievable_rates_mbps: np.ndarray,
    average_throughput_mbps: np.ndarray,
    max_scheduled: int,
    epsilon: float = 1e-9,
) -> dict[str, Any]:
    """Select users using the proportional-fair rate / average-rate metric."""
    rates = np.asarray(achievable_rates_mbps, dtype=float)
    averages = np.asarray(average_throughput_mbps, dtype=float)

    if rates.ndim != 1 or averages.ndim != 1:
        raise ValueError("Rate inputs must be one-dimensional")
    if len(rates) == 0 or len(rates) != len(averages):
        raise ValueError("Rate arrays must be non-empty and have equal length")
    if not np.isfinite(rates).all() or not np.isfinite(averages).all():
        raise ValueError("Rate inputs must contain finite values")
    if (rates < 0).any() or (averages < 0).any():
        raise ValueError("Rates must be non-negative")
    if not 1 <= max_scheduled <= len(rates):
        raise ValueError("max_scheduled must be between 1 and user count")
    if epsilon <= 0:
        raise ValueError("epsilon must be positive")

    priorities = rates / np.maximum(averages, epsilon)
    selected = np.argsort(-priorities, kind="stable")[:max_scheduled]

    return {
        "scheduled_users": selected.tolist(),
        "priorities": priorities,
        "scheduled_rates_mbps": rates[selected],
        "total_scheduled_rate_mbps": float(rates[selected].sum()),
    }


def compute_precoder(
    channel_matrix: np.ndarray,
    method: str = "rzf",
    regularization: float = 0.1,
) -> np.ndarray:
    """Compute a normalized multi-user linear precoder.

    channel_matrix has shape (users, transmit_antennas).
    Returned precoder has shape (transmit_antennas, users).
    """
    channel = np.asarray(channel_matrix, dtype=np.complex128)

    if channel.ndim != 2 or min(channel.shape) < 1:
        raise ValueError("channel_matrix must be a non-empty 2D matrix")
    if not np.isfinite(channel).all():
        raise ValueError("channel_matrix must contain finite values")
    if method not in {"mrt", "zf", "rzf"}:
        raise ValueError("method must be 'mrt', 'zf' or 'rzf'")
    if regularization < 0:
        raise ValueError("regularization must be non-negative")

    conjugate_transpose = channel.conj().T

    if method == "mrt":
        precoder = conjugate_transpose

    elif method == "zf":
        gram = channel @ conjugate_transpose
        precoder = conjugate_transpose @ np.linalg.pinv(gram)

    else:
        gram = channel @ conjugate_transpose
        regularized_gram = (
            gram + regularization * np.eye(gram.shape[0])
        )
        precoder = conjugate_transpose @ np.linalg.pinv(regularized_gram)

    norm = np.linalg.norm(precoder, ord="fro")
    if norm <= 0 or not np.isfinite(norm):
        raise ValueError("Unable to construct a valid precoder")

    return precoder / norm


def evaluate_beamforming(
    current_channel: np.ndarray,
    channel_for_precoding: np.ndarray | None = None,
    method: str = "rzf",
    tx_power_w: float = 1.0,
    noise_power_w: float = 1e-9,
    regularization: float = 0.1,
) -> dict[str, Any]:
    """Evaluate precoding performance against the current channel.

    A different channel_for_precoding represents delayed or predicted CSI.
    Total transmit power is normalized across all scheduled streams.
    """
    current = np.asarray(current_channel, dtype=np.complex128)
    design = (
        current
        if channel_for_precoding is None
        else np.asarray(channel_for_precoding, dtype=np.complex128)
    )

    if current.ndim != 2 or min(current.shape) < 1:
        raise ValueError("current_channel must be a non-empty 2D matrix")
    if design.shape != current.shape:
        raise ValueError("Channel matrices must have matching shapes")
    if not np.isfinite(current).all() or not np.isfinite(design).all():
        raise ValueError("Channel matrices must contain finite values")
    if tx_power_w <= 0 or noise_power_w <= 0:
        raise ValueError("Power and noise must be positive")

    precoder = compute_precoder(
        design,
        method=method,
        regularization=regularization,
    )

    precoder = precoder * np.sqrt(tx_power_w)
    effective_channel = current @ precoder

    received_power = np.abs(effective_channel) ** 2
    signal = np.diag(received_power)
    interference = received_power.sum(axis=1) - signal

    sinr = signal / (interference + noise_power_w)
    sinr_db = 10 * np.log10(np.maximum(sinr, 1e-15))
    spectral_efficiency = np.log2(1 + sinr)

    user_metrics = pd.DataFrame({
        "user_index": np.arange(current.shape[0]),
        "signal_power_w": signal,
        "interference_power_w": interference,
        "sinr_linear": sinr,
        "sinr_db": sinr_db,
        "spectral_efficiency_bps_hz": spectral_efficiency,
    })

    return {
        "method": method,
        "precoder": precoder,
        "user_metrics": user_metrics,
        "summary": {
            "mean_sinr_db": float(np.mean(sinr_db)),
            "mean_spectral_efficiency_bps_hz": float(
                np.mean(spectral_efficiency)
            ),
            "sum_spectral_efficiency_bps_hz": float(
                np.sum(spectral_efficiency)
            ),
            "total_transmit_power_w": float(
                np.linalg.norm(precoder, ord="fro") ** 2
            ),
        },
    }


def compare_beamforming_methods(
    channel_matrix: np.ndarray,
    tx_power_w: float = 1.0,
    noise_power_w: float = 1e-9,
    regularization: float = 0.1,
) -> pd.DataFrame:
    """Compare MRT, ZF and RZF under identical channel conditions."""
    records = []

    for method in ("mrt", "zf", "rzf"):
        result = evaluate_beamforming(
            current_channel=channel_matrix,
            method=method,
            tx_power_w=tx_power_w,
            noise_power_w=noise_power_w,
            regularization=regularization,
        )
        records.append({
            "method": method,
            **result["summary"],
        })

    return pd.DataFrame(records)


def evaluate_backhaul_delay(
    current_channel: np.ndarray,
    delayed_channel: np.ndarray,
    method: str = "rzf",
    tx_power_w: float = 1.0,
    noise_power_w: float = 1e-9,
    regularization: float = 0.1,
) -> dict[str, Any]:
    """Compare perfect-current CSI and delayed-CSI precoding."""
    current_result = evaluate_beamforming(
        current_channel=current_channel,
        channel_for_precoding=current_channel,
        method=method,
        tx_power_w=tx_power_w,
        noise_power_w=noise_power_w,
        regularization=regularization,
    )

    delayed_result = evaluate_beamforming(
        current_channel=current_channel,
        channel_for_precoding=delayed_channel,
        method=method,
        tx_power_w=tx_power_w,
        noise_power_w=noise_power_w,
        regularization=regularization,
    )

    perfect_rate = current_result["summary"]["sum_spectral_efficiency_bps_hz"]
    delayed_rate = delayed_result["summary"]["sum_spectral_efficiency_bps_hz"]

    return {
        "perfect_csi": current_result,
        "delayed_csi": delayed_result,
        "comparison": {
            "perfect_sum_spectral_efficiency": perfect_rate,
            "delayed_sum_spectral_efficiency": delayed_rate,
            "relative_loss_percent": (
                100 * (perfect_rate - delayed_rate) / perfect_rate
                if perfect_rate > 0 else 0.0
            ),
        },
    }
