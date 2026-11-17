import pandas as pd
import pytest

from ran_intelligence.ml.forecasting import (
    prepare_forecasting_series,
)


def make_measurements():
    return pd.DataFrame(
        {
            "session_id": ["s1", "s1", "s1", "s2"],
            "timestamp": pd.to_datetime(
                [
                    "2025-01-01 00:00:00.100",
                    "2025-01-01 00:00:00.400",
                    "2025-01-01 00:00:02.200",
                    "2025-01-01 00:00:00.200",
                ]
            ),
            "nr_sinr_db": [20.0, 22.0, 30.0, 99.0],
        }
    )


def test_series_resamples_using_median_and_forward_fill():
    result = prepare_forecasting_series(make_measurements(), "s1", "nr_sinr_db")

    assert len(result) == 3
    assert result["value"].tolist() == [21.0, 21.0, 30.0]
    assert result["timestamp"].is_monotonic_increasing


def test_series_keeps_sessions_separate():
    result = prepare_forecasting_series(make_measurements(), "s2", "nr_sinr_db")

    assert result["value"].tolist() == [99.0]


def test_series_rejects_unknown_metric():
    with pytest.raises(ValueError, match="Missing required columns"):
        prepare_forecasting_series(make_measurements(), "s1", "unknown_metric")


def test_series_rejects_negative_forward_fill():
    with pytest.raises(ValueError, match="non-negative integer"):
        prepare_forecasting_series(
            make_measurements(),
            "s1",
            "nr_sinr_db",
            max_forward_fill=-1,
        )


def test_series_does_not_fill_long_gaps():
    measurements = make_measurements()
    measurements.loc[2, "timestamp"] = pd.Timestamp("2025-01-01 00:00:03.200")

    result = prepare_forecasting_series(
        measurements,
        "s1",
        "nr_sinr_db",
        max_forward_fill=1,
    )

    assert result["value"].tolist() == [21.0, 21.0, 30.0]
    assert result["timestamp"].dt.second.tolist() == [0, 1, 3]


def make_regular_series(size=40):
    return pd.DataFrame(
        {
            "timestamp": pd.date_range("2025-01-01", periods=size, freq="1s"),
            "value": [float(value) for value in range(size)],
        }
    )


def test_supervised_dataset_uses_correct_forecast_horizon():
    from ran_intelligence.ml.forecasting import build_supervised_dataset

    result = build_supervised_dataset(make_regular_series())

    first = result.iloc[0]
    assert first["origin_timestamp"] == pd.Timestamp("2025-01-01 00:00:10")
    assert first["target_timestamp"] == pd.Timestamp("2025-01-01 00:00:15")
    assert first["target_value"] == 15.0


def test_supervised_features_use_only_current_and_past_values():
    from ran_intelligence.ml.forecasting import build_supervised_dataset

    result = build_supervised_dataset(make_regular_series())
    first = result.iloc[0]

    assert first["lag_0"] == 10.0
    assert first["lag_1"] == 9.0
    assert first["lag_5"] == 5.0
    assert first["rolling_mean_3"] == 9.0


def test_supervised_dataset_rejects_irregular_timestamps():
    from ran_intelligence.ml.forecasting import build_supervised_dataset

    series = make_regular_series()
    series.loc[20, "timestamp"] += pd.Timedelta(milliseconds=500)

    with pytest.raises(ValueError, match="regularly spaced"):
        build_supervised_dataset(series)


def test_chronological_split_purges_forecast_horizon():
    from ran_intelligence.ml.forecasting import (
        build_supervised_dataset,
        chronological_split,
    )

    dataset = build_supervised_dataset(make_regular_series())
    train, test = chronological_split(dataset, gap_steps=5)

    assert train["origin_timestamp"].max() < test["origin_timestamp"].min()
    assert train["target_timestamp"].max() < test["origin_timestamp"].min()


def test_chronological_split_rejects_insufficient_data():
    from ran_intelligence.ml.forecasting import chronological_split

    dataset = pd.DataFrame(
        {
            "origin_timestamp": pd.date_range("2025-01-01", periods=5, freq="1s"),
            "target_timestamp": pd.date_range("2025-01-01 00:00:05", periods=5, freq="1s"),
            "target_value": range(5),
        }
    )

    with pytest.raises(ValueError, match="Not enough rows"):
        chronological_split(dataset, gap_steps=5)


def test_forecasters_return_predictions_and_metrics():
    from ran_intelligence.ml.forecasting import (
        build_supervised_dataset,
        chronological_split,
        evaluate_forecasters,
    )

    dataset = build_supervised_dataset(make_regular_series(100))
    train, test = chronological_split(dataset, gap_steps=5)

    predictions, metrics = evaluate_forecasters(train, test, n_estimators=30)

    assert len(predictions) == len(test)
    assert set(metrics["model"]) == {"persistence", "random_forest"}
    assert predictions[["persistence_prediction", "random_forest_prediction"]].notna().all().all()
    assert (metrics["mae"] >= 0).all()
    assert (metrics["rmse"] >= 0).all()


def test_forecasters_reject_missing_features():
    from ran_intelligence.ml.forecasting import (
        build_supervised_dataset,
        chronological_split,
        evaluate_forecasters,
    )

    dataset = build_supervised_dataset(make_regular_series(100))
    train, test = chronological_split(dataset, gap_steps=5)
    test = test.copy()
    test.loc[test.index[0], "lag_1"] = float("nan")

    with pytest.raises(ValueError, match="missing values"):
        evaluate_forecasters(train, test, n_estimators=10)


def test_forecasters_reject_invalid_estimator_count():
    from ran_intelligence.ml.forecasting import (
        build_supervised_dataset,
        chronological_split,
        evaluate_forecasters,
    )

    dataset = build_supervised_dataset(make_regular_series(100))
    train, test = chronological_split(dataset, gap_steps=5)

    with pytest.raises(ValueError, match="n_estimators"):
        evaluate_forecasters(train, test, n_estimators=0)


def test_gap_aware_dataset_does_not_cross_missing_intervals():
    from ran_intelligence.ml.forecasting import build_gap_aware_dataset

    series = make_regular_series(50)
    series = series.drop(index=20).reset_index(drop=True)

    result = build_gap_aware_dataset(series)

    assert not result.empty
    assert (
        (result["target_timestamp"] - result["origin_timestamp"]).eq(pd.Timedelta(seconds=5)).all()
    )

    # Every feature row must remain within one continuous segment.
    for row in result.itertuples():
        assert row.target_timestamp - row.origin_timestamp == pd.Timedelta(seconds=5)


def test_gap_aware_dataset_rejects_series_with_only_short_segments():
    from ran_intelligence.ml.forecasting import build_gap_aware_dataset

    series = make_regular_series(20)
    series.loc[10:, "timestamp"] += pd.Timedelta(seconds=100)

    with pytest.raises(ValueError, match="No continuous segment"):
        build_gap_aware_dataset(series)
