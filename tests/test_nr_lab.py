
import numpy as np
import pytest

from ran_intelligence.simulation.nr_lab import (
    compare_beamforming_methods,
    compute_precoder,
    evaluate_backhaul_delay,
    evaluate_beamforming,
    proportional_fair_schedule,
)


@pytest.fixture
def channel():
    return np.array([
        [1.0 + 0.2j, 0.3 + 0.1j, 0.1 + 0.2j, 0.4 + 0.1j],
        [0.2 + 0.1j, 1.0 + 0.3j, 0.4 + 0.2j, 0.1 + 0.1j],
    ])


def test_pf_scheduler_selects_highest_priority():
    result = proportional_fair_schedule(
        np.array([20, 10, 30]),
        np.array([10, 10, 30]),
        max_scheduled=2,
    )
    assert result["scheduled_users"] == [0, 1]


def test_pf_scheduler_returns_selected_rates():
    result = proportional_fair_schedule(
        np.array([20, 10, 30]),
        np.array([10, 10, 30]),
        max_scheduled=2,
    )
    assert result["total_scheduled_rate_mbps"] == 30


def test_pf_scheduler_rejects_invalid_limit():
    with pytest.raises(ValueError):
        proportional_fair_schedule(
            np.array([10, 20]),
            np.array([10, 20]),
            max_scheduled=3,
        )


@pytest.mark.parametrize("method", ["mrt", "zf", "rzf"])
def test_precoder_shape_and_power(channel, method):
    precoder = compute_precoder(channel, method=method)
    assert precoder.shape == (4, 2)
    assert np.linalg.norm(precoder, "fro") == pytest.approx(1.0)


def test_precoder_rejects_unknown_method(channel):
    with pytest.raises(ValueError, match="method"):
        compute_precoder(channel, method="unknown")


def test_beamforming_returns_user_metrics(channel):
    result = evaluate_beamforming(channel)
    assert len(result["user_metrics"]) == 2
    assert result["summary"]["total_transmit_power_w"] == pytest.approx(1.0)


def test_beamforming_respects_transmit_power(channel):
    result = evaluate_beamforming(channel, tx_power_w=2.0)
    assert result["summary"]["total_transmit_power_w"] == pytest.approx(2.0)


def test_beamforming_method_comparison(channel):
    result = compare_beamforming_methods(channel)
    assert set(result["method"]) == {"mrt", "zf", "rzf"}
    assert len(result) == 3


def test_backhaul_delay_returns_both_results(channel):
    delayed = channel * 0.85 + 0.1
    result = evaluate_backhaul_delay(channel, delayed)
    assert "perfect_csi" in result
    assert "delayed_csi" in result
    assert np.isfinite(result["comparison"]["relative_loss_percent"])


def test_matching_channel_shapes_required(channel):
    with pytest.raises(ValueError, match="matching shapes"):
        evaluate_beamforming(channel, np.ones((3, 4)))


def test_non_positive_noise_rejected(channel):
    with pytest.raises(ValueError, match="positive"):
        evaluate_beamforming(channel, noise_power_w=0)
