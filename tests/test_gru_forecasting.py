
import numpy as np
import pandas as pd
import pytest

pytest.importorskip("torch")

from ran_intelligence.ml.forecasting import evaluate_gru_forecaster


def make_forecasting_data(n, start):
    timestamps = pd.date_range(start=start, periods=n, freq="1s")
    values = 20 + 3 * np.sin(np.arange(n) / 5)

    data = {
        "origin_timestamp": timestamps,
        "target_timestamp": timestamps + pd.Timedelta(seconds=5),
        "target_value": values + 0.2,
    }

    for lag in range(11):
        data[f"lag_{lag}"] = values - lag * 0.1

    return pd.DataFrame(data)


def test_gru_returns_valid_predictions_and_metrics():
    train = make_forecasting_data(80, "2026-01-01")
    test = make_forecasting_data(20, "2026-01-02")

    predictions, metrics = evaluate_gru_forecaster(
        train,
        test,
        sequence_length=11,
        hidden_size=8,
        epochs=5,
        patience=2,
        random_state=42,
    )

    assert len(predictions) == len(test)
    assert predictions["gru_prediction"].notna().all()
    assert np.isfinite(metrics["mae"])
    assert np.isfinite(metrics["rmse"])
    assert metrics["model"] == "gru"
    assert metrics["best_epoch"] <= 5


def test_gru_rejects_missing_features():
    train = make_forecasting_data(80, "2026-01-01")
    test = make_forecasting_data(20, "2026-01-02")
    train = train.drop(columns=["lag_3"])

    with pytest.raises(ValueError, match="missing columns"):
        evaluate_gru_forecaster(
            train, test, sequence_length=11, epochs=5
        )


def test_gru_rejects_invalid_sequence_length():
    train = make_forecasting_data(80, "2026-01-01")
    test = make_forecasting_data(20, "2026-01-02")

    with pytest.raises(ValueError, match="sequence_length"):
        evaluate_gru_forecaster(
            train, test, sequence_length=1, epochs=5
        )
