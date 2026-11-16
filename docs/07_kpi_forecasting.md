# KPI Forecasting

## 1. Purpose

The KPI forecasting component will estimate future network conditions using historical measurements.

While anomaly detection identifies unusual behaviour in existing measurements, forecasting looks ahead and estimates what may happen next.

For example, the platform could estimate future throughput, SINR or cell load based on recent measurements. This may help engineers identify possible performance degradation before it becomes severe.

The initial implementation will focus on a small number of KPIs with sufficient historical data. More advanced forecasting methods will be introduced only when they provide a meaningful improvement over simpler baselines.

Forecasts are estimates, not guarantees about future network behaviour.

## 2. Forecasting Targets

The platform may support forecasting for the following KPIs:

| KPI | Forecasting purpose |
|---|---|
| Throughput | Estimate future data transfer rates |
| SINR | Identify possible changes in radio conditions |
| RSRP | Estimate changes in received signal strength |
| BLER | Estimate future transmission error levels |
| PRB utilisation | Estimate future resource utilisation |
| Cell load | Predict changes in network demand |

The availability of each target will depend on the selected dataset.

The first experiments will prioritise throughput and other measurements with sufficient time-series observations.

## 3. Forecasting Granularity

Forecasting should support different levels of aggregation.

### 3.1 UE-Level Forecasting

Where UE identifiers and sufficient historical measurements exist, the platform can estimate future KPI values for individual users.

This may be useful for analysing user-level throughput and radio conditions.

### 3.2 Cell-Level Forecasting

Cell-level forecasting will estimate aggregated performance indicators for a particular cell.

Examples:

- Average throughput per cell.
- Average SINR per cell.
- Cell load.
- Resource utilisation.

This is likely to be the most practical initial use case.

### 3.3 Network-Level Forecasting

Network-level forecasting will combine measurements across multiple cells.

It may help identify broader traffic patterns and network-wide changes.

This will be considered after cell-level forecasting is implemented.

## 4. Forecasting Horizons

The platform should allow forecasts over different future intervals.

Possible horizons include:

- Short-term: next few measurement intervals.
- Medium-term: next several intervals or hours.
- Longer-term: daily or weekly patterns, when the dataset supports them.

The actual forecasting horizon must respect the sampling frequency of the dataset.

For example, a dataset sampled every five minutes can support forecasts at five-minute intervals. It should not be described as providing second-level predictions.

The initial experiments will use short forecasting horizons.

## 5. Forecasting Methods

We will begin with simple methods and use them as baselines before testing more advanced models.

### 5.1 Naive Forecast

The naive method predicts that the next value will be equal to the most recently observed value.

\[
\hat{y}_{t+1}=y_t
\]

It is simple but provides an important baseline.

A more complex model should demonstrate an improvement over this approach before being considered useful.

### 5.2 Moving Average

The moving average predicts future values using the average of recent observations.

\[
\hat{y}_{t+1}=\frac{1}{k}\sum_{i=0}^{k-1}y_{t-i}
\]

Where \(k\) is the number of historical observations used.

This can reduce the influence of short-term fluctuations.

### 5.3 Exponential Smoothing

Exponential smoothing gives more importance to recent observations.

\[
\hat{y}_{t+1}=\alpha y_t+(1-\alpha)\hat{y}_t
\]

Where:

- \(y_t\) is the current observation.
- \(\hat{y}_t\) is the previous forecast.
- \(\alpha\) controls the influence of the latest observation.

This method may work well when recent measurements are more informative than older ones.

### 5.4 ARIMA

ARIMA is a statistical time-series forecasting method.

It combines autoregressive terms, differencing and moving-average terms.

It may be useful for relatively stable time series where historical values contain meaningful temporal patterns.

We will evaluate it on suitable KPIs rather than applying it automatically to every measurement.

### 5.5 Machine Learning Models

We will also investigate machine learning approaches using historical KPI values and derived features.

Potential models include:

- Random Forest.
- XGBoost.
- Gradient Boosting.

Possible input features include:

- Previous KPI values.
- Rolling averages.
- Rolling standard deviations.
- Recent KPI changes.
- Time of day.
- Day of the week.
- Cell-level traffic indicators.

These models can capture relationships between multiple features, although they require careful time-based validation.

### 5.6 Deep Learning Models

Deep learning models may be considered for more complex time-series patterns.

Potential approaches include:

- LSTM.
- GRU.
- Temporal Convolutional Networks.

These methods will be introduced only if the available data and forecasting task justify them.

We should not assume that a deep learning model will outperform a simpler statistical or machine learning baseline.

## 6. Feature Engineering

The forecasting pipeline will prepare features from historical measurements.

Examples:

| Feature | Description |
|---|---|
| lag_1 | Previous measurement |
| lag_2 | Measurement from two intervals earlier |
| lag_3 | Measurement from three intervals earlier |
| rolling_mean | Average over a recent window |
| rolling_std | Standard deviation over a recent window |
| recent_change | Difference from a previous measurement |
| hour | Hour of the day |
| day_of_week | Day of the week |
| cell_id | Cell identifier, where applicable |

Lag and rolling features should be generated using past observations only.

Future information must never enter the training features.

## 7. Training and Validation

Time-series data must be split differently from ordinary randomly shuffled datasets.

Random splitting can allow future measurements to influence the training process and produce misleading evaluation results.

We will use chronological splits.

For example:

```text
Earlier observations       Later observations
|----------------------|------------------|
       Training              Testing
```

A validation period may also be included when selecting model parameters.

For more reliable evaluation, we can use rolling or expanding-window validation.

The exact split will depend on the length and sampling frequency of the selected dataset.

## 8. Evaluation Metrics

Forecasting performance will be evaluated using several metrics.

### 8.1 Mean Absolute Error

\[
MAE=\frac{1}{n}\sum_{i=1}^{n}|y_i-\hat{y}_i|
\]

MAE measures the average absolute difference between actual and predicted values.

It is relatively easy to interpret in the original KPI units.

### 8.2 Root Mean Squared Error

\[
RMSE=\sqrt{\frac{1}{n}\sum_{i=1}^{n}(y_i-\hat{y}_i)^2}
\]

RMSE gives greater weight to larger prediction errors.

It is useful when large forecasting mistakes are particularly undesirable.

### 8.3 Mean Absolute Percentage Error

\[
MAPE=\frac{100}{n}\sum_{i=1}^{n}\left|\frac{y_i-\hat{y}_i}{y_i}\right|
\]

MAPE expresses error as a percentage.

However, it can behave poorly when actual values are zero or close to zero. We will avoid using it blindly for KPIs where this situation occurs.

### 8.4 Model Comparison

All forecasting models should be evaluated on the same test period.

The comparison should include:

- Naive baseline.
- Moving average.
- Exponential smoothing.
- Suitable statistical models.
- Machine learning models.
- Deep learning models, if justified.

The best model should be selected based on forecasting performance, stability and computational cost.

## 9. Forecast Output

Each forecast result should contain:

| Field | Description |
|---|---|
| forecast_id | Unique forecast identifier |
| cell_id | Related cell, if available |
| kpi_name | KPI being predicted |
| forecast_timestamp | Time for which the prediction is made |
| predicted_value | Estimated KPI value |
| lower_bound | Lower prediction interval, if available |
| upper_bound | Upper prediction interval, if available |
| model_name | Model used |
| model_version | Model version |
| horizon | Forecasting horizon |
| generated_at | Time the forecast was generated |

Where possible, the platform should provide prediction intervals rather than displaying only a single predicted value.

These intervals help communicate uncertainty.

## 10. Visualisation

The Streamlit dashboard should provide interactive forecast visualisations.

The initial visualisations should include:

1. Historical KPI measurements.
2. Predicted KPI values.
3. Actual versus predicted measurements.
4. Forecast error over time.
5. Comparison between forecasting models.
6. Prediction intervals, where supported.

Historical observations and future predictions should be visually distinguishable.

Users should be able to select the KPI, cell and forecasting horizon.

## 11. Integration with Other Components

Forecasting will connect with several other platform components.

**KPI analytics**

Historical measurements and aggregated KPIs will provide the input data.

**Anomaly detection**

Forecasting residuals can help identify unusual deviations between expected and observed behaviour.

For example, a large difference between predicted and actual throughput may indicate a possible performance change.

**Incident investigation**

The investigation agent can use forecasts as additional evidence when examining a potential degradation event.

**Reporting**

Forecast results can be included in incident reports, with the model, horizon and uncertainty clearly stated.

**Network simulation**

Synthetic scenarios can be used to test forecasting performance under controlled traffic and radio conditions.

## 12. Proposed Python Module Structure

```text
src/
└── ran_intelligence/
    └── forecasting/
        ├── __init__.py
        ├── preprocessing.py
        ├── features.py
        ├── baselines.py
        ├── statistical_models.py
        ├── ml_models.py
        ├── deep_learning.py
        ├── evaluation.py
        └── prediction.py
```

Responsibilities:

- `preprocessing.py`: Prepare time-series data.
- `features.py`: Generate lag, rolling and time-based features.
- `baselines.py`: Implement naive and moving-average forecasts.
- `statistical_models.py`: Implement exponential smoothing and ARIMA.
- `ml_models.py`: Train machine learning forecasting models.
- `deep_learning.py`: Implement sequence-based models if required.
- `evaluation.py`: Compare models using chronological evaluation.
- `prediction.py`: Generate and format forecast results.

## 13. Implementation Order

The component will be developed incrementally.

**Stage 1 — Prepare time-series data**

- Select a KPI.
- Check timestamps and sampling intervals.
- Aggregate measurements if necessary.
- Handle missing observations.

**Stage 2 — Implement baselines**

- Naive forecasting.
- Moving average.
- Exponential smoothing.

**Stage 3 — Add statistical and ML models**

- Evaluate ARIMA where appropriate.
- Train Random Forest or XGBoost models.
- Compare results against the baselines.

**Stage 4 — Evaluate forecasting performance**

- Use chronological train, validation and test periods.
- Calculate MAE and RMSE.
- Inspect errors across different periods and conditions.

**Stage 5 — Add visualisation**

- Display historical and predicted values.
- Add model comparisons.
- Show prediction intervals where available.

**Stage 6 — Integrate with the platform**

- Expose forecasting functions to the API.
- Make forecasts available to incident investigation.
- Include forecast results in reports.

## 14. Expected Outcome

The forecasting component should estimate future network KPI values and make those estimates accessible through the platform.

An engineer should be able to inspect historical measurements, select a KPI and cell, generate a forecast and compare predicted values with actual measurements.

The first version will prioritise reliable baselines and correct evaluation. More advanced models will be added only when they provide measurable value.
