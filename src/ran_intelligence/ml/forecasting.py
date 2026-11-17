"""Feature engineering and chronological splitting for KPI forecasting."""

import pandas as pd


def prepare_forecasting_series(
    df: pd.DataFrame,
    session_id: str,
    metric: str,
    frequency: str = "1s",
    max_forward_fill: int = 2,
) -> pd.DataFrame:
    """Create a regular, causally imputed KPI time series."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError("df must be a pandas DataFrame.")

    if df.empty:
        raise ValueError("Input DataFrame cannot be empty.")

    required = {"session_id", "timestamp", metric}
    missing = required - set(df.columns)

    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    if not isinstance(session_id, str) or not session_id.strip():
        raise ValueError("session_id must be a non-empty string.")

    if not isinstance(metric, str) or not metric.strip():
        raise ValueError("metric must be a non-empty string.")

    if (
        isinstance(max_forward_fill, bool)
        or not isinstance(max_forward_fill, int)
        or max_forward_fill < 0
    ):
        raise ValueError("max_forward_fill must be a non-negative integer.")

    try:
        interval = pd.Timedelta(frequency)
    except (TypeError, ValueError) as exc:
        raise ValueError("frequency must be a valid time interval.") from exc

    if interval <= pd.Timedelta(0):
        raise ValueError("frequency must be positive.")

    session_data = df.loc[
        df["session_id"] == session_id,
        ["timestamp", metric],
    ].copy()

    if session_data.empty:
        raise ValueError(f"No measurements found for session: {session_id}")

    session_data["timestamp"] = pd.to_datetime(session_data["timestamp"], errors="coerce")
    session_data[metric] = pd.to_numeric(session_data[metric], errors="coerce")
    session_data = session_data.dropna(subset=["timestamp", metric])

    if session_data.empty:
        raise ValueError("No valid timestamp and KPI observations found.")

    session_data = session_data.set_index("timestamp").sort_index()

    regular_series = session_data[metric].resample(frequency).median().ffill(limit=max_forward_fill)

    result = regular_series.dropna().rename("value").rename_axis("timestamp").reset_index()

    if result.empty:
        raise ValueError("No usable observations after resampling.")

    return result


def build_supervised_dataset(
    series: pd.DataFrame,
    horizon_steps: int = 5,
    lags: tuple[int, ...] = (0, 1, 2, 3, 5, 10),
    rolling_windows: tuple[int, ...] = (3, 5),
) -> pd.DataFrame:
    """Build lag-based features for direct, fixed-horizon forecasting.

    The input series must contain regularly spaced timestamp/value rows.
    Lag zero represents the latest available observation.
    """
    if not isinstance(series, pd.DataFrame):
        raise TypeError("series must be a pandas DataFrame.")

    required = {"timestamp", "value"}
    missing = required - set(series.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    if isinstance(horizon_steps, bool) or not isinstance(horizon_steps, int):
        raise ValueError("horizon_steps must be a positive integer.")
    if horizon_steps < 1:
        raise ValueError("horizon_steps must be a positive integer.")

    if not lags or any(
        isinstance(lag, bool) or not isinstance(lag, int) or lag < 0 for lag in lags
    ):
        raise ValueError("lags must contain non-negative integers.")
    if len(set(lags)) != len(lags):
        raise ValueError("lags must not contain duplicates.")

    if not rolling_windows or any(
        isinstance(window, bool) or not isinstance(window, int) or window < 1
        for window in rolling_windows
    ):
        raise ValueError("rolling_windows must contain positive integers.")

    data = series[["timestamp", "value"]].copy()
    data["timestamp"] = pd.to_datetime(data["timestamp"], errors="coerce")
    data["value"] = pd.to_numeric(data["value"], errors="coerce")
    data = data.dropna().sort_values("timestamp").reset_index(drop=True)

    if data.empty:
        raise ValueError("series contains no valid observations.")

    if data["timestamp"].duplicated().any():
        raise ValueError("timestamps must be unique.")

    differences = data["timestamp"].diff().dropna()
    if not differences.empty and not differences.eq(differences.iloc[0]).all():
        raise ValueError("series timestamps must be regularly spaced.")

    features = pd.DataFrame(index=data.index)

    for lag in lags:
        features[f"lag_{lag}"] = data["value"].shift(lag)

    for window in rolling_windows:
        features[f"rolling_mean_{window}"] = (
            data["value"].rolling(window=window, min_periods=window).mean()
        )

    result = pd.DataFrame(
        {
            "origin_timestamp": data["timestamp"],
            "target_timestamp": data["timestamp"].shift(-horizon_steps),
            "target_value": data["value"].shift(-horizon_steps),
        }
    )

    result = pd.concat([result, features], axis=1)
    result = result.dropna().reset_index(drop=True)

    if result.empty:
        raise ValueError("Not enough observations to build forecasting features.")

    return result


def chronological_split(
    dataset: pd.DataFrame,
    test_fraction: float = 0.2,
    gap_steps: int = 5,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split ordered forecasting examples and purge rows before the test set."""
    if not isinstance(dataset, pd.DataFrame) or dataset.empty:
        raise ValueError("dataset must be a non-empty DataFrame.")

    required = {"origin_timestamp", "target_timestamp", "target_value"}
    missing = required - set(dataset.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    if not 0 < test_fraction < 1:
        raise ValueError("test_fraction must be between 0 and 1.")

    if isinstance(gap_steps, bool) or not isinstance(gap_steps, int) or gap_steps < 0:
        raise ValueError("gap_steps must be a non-negative integer.")

    data = dataset.sort_values("origin_timestamp").reset_index(drop=True)
    split_index = int(len(data) * (1 - test_fraction))
    train_end = split_index - gap_steps

    if train_end < 1 or split_index >= len(data):
        raise ValueError("Not enough rows for the requested split and gap.")

    train = data.iloc[:train_end].copy()
    test = data.iloc[split_index:].copy()

    if train["target_timestamp"].max() >= test["origin_timestamp"].min():
        raise ValueError("Training targets overlap the test period; increase gap_steps.")

    return train, test


def evaluate_forecasters(
    train: pd.DataFrame,
    test: pd.DataFrame,
    n_estimators: int = 200,
    min_samples_leaf: int = 3,
    random_state: int = 42,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compare persistence and Random Forest forecasts on held-out data."""
    import numpy as np
    from sklearn.ensemble import RandomForestRegressor
    from sklearn.metrics import mean_absolute_error, mean_squared_error

    if not isinstance(train, pd.DataFrame) or not isinstance(test, pd.DataFrame):
        raise TypeError("train and test must be pandas DataFrames.")

    if train.empty or test.empty:
        raise ValueError("train and test cannot be empty.")

    required = {"origin_timestamp", "target_timestamp", "target_value", "lag_0"}
    for name, frame in (("train", train), ("test", test)):
        missing = required - set(frame.columns)
        if missing:
            raise ValueError(f"{name} is missing required columns: {sorted(missing)}")

    if isinstance(n_estimators, bool) or not isinstance(n_estimators, int) or n_estimators < 1:
        raise ValueError("n_estimators must be a positive integer.")

    if (
        isinstance(min_samples_leaf, bool)
        or not isinstance(min_samples_leaf, int)
        or min_samples_leaf < 1
    ):
        raise ValueError("min_samples_leaf must be a positive integer.")

    if isinstance(random_state, bool) or not isinstance(random_state, int) or random_state < 0:
        raise ValueError("random_state must be a non-negative integer.")

    feature_columns = [
        column
        for column in train.columns
        if column
        not in {
            "origin_timestamp",
            "target_timestamp",
            "target_value",
        }
    ]

    if not feature_columns or "lag_0" not in feature_columns:
        raise ValueError("Forecasting features must include lag_0.")

    if set(feature_columns) - set(test.columns):
        raise ValueError("Train and test feature columns do not match.")

    X_train = train[feature_columns].apply(pd.to_numeric, errors="coerce")
    X_test = test[feature_columns].apply(pd.to_numeric, errors="coerce")
    y_train = pd.to_numeric(train["target_value"], errors="coerce")
    y_test = pd.to_numeric(test["target_value"], errors="coerce")

    if (
        X_train.isna().any().any()
        or X_test.isna().any().any()
        or y_train.isna().any()
        or y_test.isna().any()
    ):
        raise ValueError("Training and test data must not contain missing values.")

    if not (
        np.isfinite(X_train.to_numpy()).all()
        and np.isfinite(X_test.to_numpy()).all()
        and np.isfinite(y_train.to_numpy()).all()
        and np.isfinite(y_test.to_numpy()).all()
    ):
        raise ValueError("Training and test data must contain finite values.")

    baseline_predictions = X_test["lag_0"].to_numpy()

    model = RandomForestRegressor(
        n_estimators=n_estimators,
        min_samples_leaf=min_samples_leaf,
        random_state=random_state,
        n_jobs=-1,
    )
    model.fit(X_train, y_train)
    model_predictions = model.predict(X_test)

    predictions = pd.DataFrame(
        {
            "origin_timestamp": test["origin_timestamp"].to_numpy(),
            "target_timestamp": test["target_timestamp"].to_numpy(),
            "actual": y_test.to_numpy(),
            "persistence_prediction": baseline_predictions,
            "random_forest_prediction": model_predictions,
        }
    )

    metrics = []
    for model_name, predicted in (
        ("persistence", baseline_predictions),
        ("random_forest", model_predictions),
    ):
        metrics.append(
            {
                "model": model_name,
                "mae": mean_absolute_error(y_test, predicted),
                "rmse": np.sqrt(mean_squared_error(y_test, predicted)),
                "test_observations": len(y_test),
            }
        )

    return predictions, pd.DataFrame(metrics)


def build_gap_aware_dataset(
    series: pd.DataFrame,
    frequency: str = "1s",
    horizon_steps: int = 5,
    lags: tuple[int, ...] = (0, 1, 2, 3, 5, 10),
    rolling_windows: tuple[int, ...] = (3, 5),
) -> pd.DataFrame:
    """Build forecasting examples without crossing gaps in the time series."""
    required = {"timestamp", "value"}
    if not isinstance(series, pd.DataFrame):
        raise TypeError("series must be a pandas DataFrame.")
    missing = required - set(series.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    interval = pd.Timedelta(frequency)
    if interval <= pd.Timedelta(0):
        raise ValueError("frequency must be positive.")

    data = series[["timestamp", "value"]].copy()
    data["timestamp"] = pd.to_datetime(data["timestamp"], errors="coerce")
    data["value"] = pd.to_numeric(data["value"], errors="coerce")
    data = data.dropna().sort_values("timestamp").reset_index(drop=True)

    if data.empty:
        raise ValueError("series contains no valid observations.")
    if data["timestamp"].duplicated().any():
        raise ValueError("timestamps must be unique.")

    segment_ids = data["timestamp"].diff().ne(interval).cumsum()
    segments = []

    for _, segment in data.groupby(segment_ids, sort=False):
        try:
            dataset = build_supervised_dataset(
                segment,
                horizon_steps=horizon_steps,
                lags=lags,
                rolling_windows=rolling_windows,
            )
        except ValueError as exc:
            if "Not enough observations" in str(exc):
                continue
            raise

        segments.append(dataset)

    if not segments:
        raise ValueError("No continuous segment is long enough for the requested features.")

    return (
        pd.concat(segments, ignore_index=True)
        .sort_values("origin_timestamp")
        .reset_index(drop=True)
    )


def evaluate_xgboost_forecaster(
    train: pd.DataFrame,
    test: pd.DataFrame,
    n_estimators: int = 300,
    max_depth: int = 3,
    learning_rate: float = 0.03,
    random_state: int = 42,
):
    """Train and evaluate an XGBoost time-series regressor."""
    import numpy as np
    import pandas as pd
    from xgboost import XGBRegressor

    required = {
        "target_value",
        "lag_0",
        "lag_1",
        "lag_2",
        "lag_3",
        "lag_5",
        "lag_10",
        "rolling_mean_3",
        "rolling_mean_5",
    }

    for name, frame in (("train", train), ("test", test)):
        if not isinstance(frame, pd.DataFrame) or frame.empty:
            raise ValueError(f"{name} must be a non-empty DataFrame.")

        missing = required - set(frame.columns)
        if missing:
            raise ValueError(f"{name} is missing required columns: {sorted(missing)}")

        values = frame[list(required)].to_numpy(dtype=float)
        if not np.isfinite(values).all():
            raise ValueError(f"{name} contains missing or non-finite values.")

    if n_estimators < 1:
        raise ValueError("n_estimators must be positive.")
    if max_depth < 1:
        raise ValueError("max_depth must be positive.")
    if not 0 < learning_rate <= 1:
        raise ValueError("learning_rate must be between 0 and 1.")

    feature_columns = [
        "lag_0",
        "lag_1",
        "lag_2",
        "lag_3",
        "lag_5",
        "lag_10",
        "rolling_mean_3",
        "rolling_mean_5",
    ]

    model = XGBRegressor(
        n_estimators=n_estimators,
        max_depth=max_depth,
        learning_rate=learning_rate,
        objective="reg:squarederror",
        subsample=0.8,
        colsample_bytree=0.8,
        reg_alpha=0.1,
        reg_lambda=2.0,
        random_state=random_state,
        n_jobs=2,
        verbosity=0,
    )

    model.fit(
        train[feature_columns],
        train["target_value"],
    )

    predictions = test[["origin_timestamp", "target_timestamp", "target_value"]].copy()

    predictions.rename(
        columns={"target_value": "actual"},
        inplace=True,
    )

    predictions["xgboost_prediction"] = model.predict(test[feature_columns])

    errors = predictions["actual"] - predictions["xgboost_prediction"]

    metrics = {
        "model": "xgboost",
        "mae": float(np.mean(np.abs(errors))),
        "rmse": float(np.sqrt(np.mean(errors**2))),
        "test_observations": len(predictions),
    }

    return predictions, metrics


def evaluate_gru_forecaster(
    train: pd.DataFrame,
    test: pd.DataFrame,
    sequence_length: int = 11,
    hidden_size: int = 16,
    epochs: int = 100,
    patience: int = 12,
    learning_rate: float = 1e-3,
    random_state: int = 42,
):
    """Train and evaluate a small GRU using chronological lag sequences."""
    import copy
    import random

    import numpy as np
    import pandas as pd
    import torch
    from sklearn.metrics import mean_absolute_error, mean_squared_error
    from sklearn.preprocessing import StandardScaler
    from torch import nn
    from torch.utils.data import DataLoader, TensorDataset

    if sequence_length < 2 or hidden_size < 1:
        raise ValueError("Invalid sequence_length or hidden_size")
    if epochs < 1 or patience < 1 or learning_rate <= 0:
        raise ValueError("epochs, patience and learning_rate must be positive")

    feature_columns = [f"lag_{i}" for i in range(sequence_length)]
    required = feature_columns + [
        "target_value", "origin_timestamp", "target_timestamp"
    ]

    for name, frame in (("train", train), ("test", test)):
        if not isinstance(frame, pd.DataFrame) or frame.empty:
            raise ValueError(f"{name} must be a non-empty DataFrame")
        missing = set(required) - set(frame.columns)
        if missing:
            raise ValueError(f"{name} is missing columns: {sorted(missing)}")
        values = frame[feature_columns + ["target_value"]].to_numpy(dtype=float)
        if not np.isfinite(values).all():
            raise ValueError(f"{name} contains non-finite values")

    if len(train) < 30:
        raise ValueError("At least 30 training rows are required")

    validation_size = max(5, int(len(train) * 0.15))
    if len(train) - validation_size < 20:
        raise ValueError("Not enough rows after validation split")

    fit_frame = train.iloc[:-validation_size]
    validation_frame = train.iloc[-validation_size:]

    # Oldest observation first, newest observation last.
    ordered_features = list(reversed(feature_columns))

    x_fit = fit_frame[ordered_features].to_numpy(dtype=np.float32)
    x_val = validation_frame[ordered_features].to_numpy(dtype=np.float32)
    x_test = test[ordered_features].to_numpy(dtype=np.float32)

    y_fit = fit_frame["target_value"].to_numpy(dtype=np.float32).reshape(-1, 1)
    y_val = validation_frame["target_value"].to_numpy(dtype=np.float32).reshape(-1, 1)

    # Fit scalers using only the model-fitting portion of training data.
    x_scaler = StandardScaler()
    x_scaler.fit(x_fit.reshape(-1, 1))

    def scale_sequences(values):
        scaled = x_scaler.transform(values.reshape(-1, 1))
        return scaled.reshape(values.shape).astype(np.float32)

    y_scaler = StandardScaler()
    y_scaler.fit(y_fit)

    x_fit_scaled = scale_sequences(x_fit)
    x_val_scaled = scale_sequences(x_val)
    x_test_scaled = scale_sequences(x_test)

    y_fit_scaled = y_scaler.transform(y_fit).astype(np.float32)
    y_val_scaled = y_scaler.transform(y_val).astype(np.float32)

    random.seed(random_state)
    np.random.seed(random_state)
    torch.manual_seed(random_state)

    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(random_state)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    class SmallGRU(nn.Module):
        def __init__(self):
            super().__init__()
            self.gru = nn.GRU(
                input_size=1,
                hidden_size=hidden_size,
                batch_first=True,
            )
            self.output = nn.Linear(hidden_size, 1)

        def forward(self, inputs):
            _, hidden = self.gru(inputs)
            return self.output(hidden[-1])

    model = SmallGRU().to(device)
    optimizer = torch.optim.Adam(
        model.parameters(),
        lr=learning_rate,
        weight_decay=1e-4,
    )
    loss_function = nn.MSELoss()

    fit_dataset = TensorDataset(
        torch.tensor(x_fit_scaled).unsqueeze(-1),
        torch.tensor(y_fit_scaled),
    )
    loader = DataLoader(
        fit_dataset,
        batch_size=min(32, len(fit_dataset)),
        shuffle=True,
        generator=torch.Generator().manual_seed(random_state),
    )

    x_val_tensor = torch.tensor(x_val_scaled).unsqueeze(-1).to(device)
    y_val_tensor = torch.tensor(y_val_scaled).to(device)

    best_loss = float("inf")
    best_state = None
    best_epoch = 0
    epochs_without_improvement = 0

    for epoch in range(epochs):
        model.train()

        for batch_x, batch_y in loader:
            batch_x = batch_x.to(device)
            batch_y = batch_y.to(device)

            optimizer.zero_grad()
            loss = loss_function(model(batch_x), batch_y)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

        model.eval()
        with torch.no_grad():
            validation_loss = loss_function(
                model(x_val_tensor),
                y_val_tensor,
            ).item()

        if validation_loss < best_loss:
            best_loss = validation_loss
            best_state = copy.deepcopy(model.state_dict())
            best_epoch = epoch + 1
            epochs_without_improvement = 0
        else:
            epochs_without_improvement += 1

        if epochs_without_improvement >= patience:
            break

    if best_state is None:
        raise RuntimeError("GRU training did not produce a valid model")

    model.load_state_dict(best_state)
    model.eval()

    with torch.no_grad():
        x_test_tensor = torch.tensor(x_test_scaled).unsqueeze(-1).to(device)
        scaled_predictions = model(x_test_tensor).cpu().numpy()

    predictions = y_scaler.inverse_transform(scaled_predictions).ravel()

    result = pd.DataFrame({
        "origin_timestamp": test["origin_timestamp"].to_numpy(),
        "target_timestamp": test["target_timestamp"].to_numpy(),
        "actual": test["target_value"].to_numpy(),
        "gru_prediction": predictions,
    })

    mae = mean_absolute_error(result["actual"], result["gru_prediction"])
    rmse = np.sqrt(mean_squared_error(result["actual"], result["gru_prediction"]))

    metrics = {
        "model": "gru",
        "mae": float(mae),
        "rmse": float(rmse),
        "test_observations": len(result),
        "best_epoch": best_epoch,
        "validation_loss_scaled": float(best_loss),
        "device": str(device),
    }

    return result, metrics
