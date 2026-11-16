# Anomaly Detection

## 1. Purpose

Anomaly detection is one of the main analytical capabilities of the RAN Intelligence Platform.

Network performance can change for many reasons. A sudden drop in throughput, an increase in BLER or an unexpected change in SINR may indicate a problem that deserves investigation.

The purpose of this component is to identify unusual measurements and periods of network degradation.

It will analyse historical and incoming measurements, identify deviations from expected behaviour and provide enough information for an engineer to investigate them.

An anomaly does not automatically mean that a network failure has occurred. The system should identify unusual behaviour, not claim a root cause without supporting evidence.

## 2. Types of Anomalies

The platform will initially focus on four types of anomalies.

### 2.1 Point Anomalies

A single measurement differs significantly from the expected range.

Examples:

- An unusually low SINR measurement.
- A sudden throughput drop.
- An unusually high BLER value.

These anomalies may indicate a short-lived network problem or a measurement issue.

### 2.2 Contextual Anomalies

A measurement may be unusual under a particular operating condition, even if the value itself is not extreme.

For example, a throughput value that is normal during low traffic may be unexpectedly low during a period when radio conditions and available resources are good.

Contextual anomalies require additional information such as time, cell, traffic conditions or neighbouring measurements.

### 2.3 Collective Anomalies

A sequence of measurements may indicate unusual behaviour even when individual values appear reasonable.

Examples:

- Gradual throughput degradation.
- Repeated fluctuations in SINR.
- Increasing BLER over several measurement intervals.
- Persistent poor radio quality for a particular cell.

These anomalies are important because network degradation does not always happen suddenly.

### 2.4 Multivariate Anomalies

Several KPIs may become unusual when considered together.

For example:

- Throughput decreases.
- BLER increases.
- SINR decreases.

Looking at each KPI independently may miss the combined pattern.

The platform should eventually support multivariate anomaly detection using several measurements together.

## 3. Input Data

The anomaly detection component will use measurements produced by the ingestion and KPI analytics pipelines.

Potential input features include:

- RSRP.
- RSRQ.
- SINR.
- CQI.
- MCS.
- Throughput.
- BLER.
- PRB utilisation.
- HARQ retransmissions.
- Time-based features.
- Cell-level aggregated statistics.

The exact feature set will depend on the dataset.

Missing measurements should be handled explicitly. A model should not silently treat missing values as zero.

## 4. Detection Methods

We will begin with simple statistical methods and gradually introduce machine learning models.

This gives us a baseline for comparison and makes the results easier to interpret.

### 4.1 Statistical Thresholds

The simplest approach is to define thresholds for selected KPIs.

Examples:

- SINR below a configured threshold.
- BLER above a configured threshold.
- Throughput below a configured threshold.

Thresholds should be configurable and documented. They may differ depending on the dataset and operating conditions.

This method is easy to understand and useful for identifying obvious problems, but it cannot capture every type of unusual behaviour.

### 4.2 Z-Score

The Z-score measures how far a value is from the mean in terms of standard deviations.

\[
z = \frac{x-\mu}{\sigma}
\]

Where:

- \(x\) is the observed value.
- \(\mu\) is the mean.
- \(\sigma\) is the standard deviation.

A large absolute Z-score indicates that the measurement is far from the historical average.

For example, we could flag observations where:

\[
|z| > 3
\]

This is a starting point, not a universal rule. It works best when the reference distribution is reasonably stable and is sensitive to outliers and changing operating conditions.

### 4.3 Interquartile Range

The Interquartile Range method identifies values outside a range based on the first and third quartiles.

\[
IQR = Q_3-Q_1
\]

The commonly used lower and upper bounds are:

\[
L = Q_1-1.5(IQR)
\]

\[
U = Q_3+1.5(IQR)
\]

Measurements outside these bounds can be flagged for inspection.

This method is less dependent on the mean and standard deviation and can be useful when KPI distributions are skewed.

### 4.4 Isolation Forest

Isolation Forest is an unsupervised machine learning algorithm for anomaly detection.

It works by randomly selecting features and split values to isolate observations. Unusual observations are generally isolated in fewer splits.

We will use it as one of the first machine learning approaches.

Potential applications include:

- Detecting unusual combinations of radio measurements.
- Identifying abnormal cell-level KPI patterns.
- Finding unusual throughput and BLER combinations.
- Comparing normal and degraded operating periods.

The model will be trained on a suitable dataset, with preprocessing and feature selection documented.

Its output is an anomaly score or prediction, not a confirmed diagnosis.

### 4.5 Local Outlier Factor

Local Outlier Factor compares the local density of a sample with the density around its neighbours.

A measurement can be considered unusual if it lies in a region with substantially lower density than nearby observations.

This may help identify unusual operating conditions that a global method such as Isolation Forest misses.

It will be considered after the initial baseline and Isolation Forest experiments.

### 4.6 Time-Series Anomaly Detection

Some network problems develop gradually rather than appearing as isolated measurements.

The platform should therefore support time-aware detection.

Initial approaches may include:

- Rolling mean and standard deviation.
- Rolling median and IQR.
- Changes in KPI trends.
- Residuals from forecasting models.

More advanced sequence-based methods can be considered if simpler approaches are insufficient.

## 5. Feature Engineering

Anomaly detection may require features beyond the raw KPI values.

Potential derived features include:

| Feature | Description |
|---|---|
| throughput_change | Change in throughput from the previous interval |
| sinr_change | Change in SINR |
| rolling_sinr_mean | Rolling average of SINR |
| rolling_bler_mean | Rolling average of BLER |
| throughput_deviation | Difference from a historical baseline |
| cell_load_change | Change in cell load |
| measurement_hour | Hour of the measurement |
| measurement_day | Day of the week |

Time-based features can help distinguish normal daily variations from unusual network behaviour.

Feature calculations should avoid using future information when evaluating historical detection performance.

## 6. Anomaly Output

Each detected anomaly should produce a structured result.

The result should contain:

| Field | Description |
|---|---|
| anomaly_id | Unique anomaly identifier |
| timestamp | Time of the observation |
| cell_id | Related cell, if available |
| ue_id | Related UE, if available |
| affected_kpis | KPIs associated with the anomaly |
| detection_method | Method that identified it |
| anomaly_score | Model score, where available |
| severity | Configured severity level |
| description | Short explanation |
| source_type | Real or synthetic |
| investigation_status | Pending, investigated or dismissed |

The system should retain enough information to reproduce the detection result.

Anomaly severity should not be confused with model confidence. These are separate concepts and may need separate fields in later versions.

## 7. Evaluation

Anomaly detection is difficult to evaluate when the dataset does not contain ground-truth incident labels.

We will use different evaluation approaches depending on the available data.

### 7.1 Labelled Synthetic Data

Synthetic scenarios will provide known normal and anomalous periods.

This allows us to calculate:

- Precision.
- Recall.
- F1-score.
- False positive rate.
- Detection delay.

We can also evaluate whether the detector identifies the correct time window and affected cell.

### 7.2 Public Measurements

For public datasets without reliable incident labels, evaluation will focus on:

- Whether detected anomalies correspond to unusual measurement patterns.
- Whether results are consistent across repeated runs.
- Whether the detector produces excessive false alarms.
- Whether detected periods can be explained using other available KPIs.

These results should not be presented as supervised classification accuracy.

### 7.3 Model Comparison

We will compare methods using the same evaluation data and preprocessing.

Initial comparison:

| Method | Main advantage | Limitation |
|---|---|---|
| Fixed thresholds | Simple and interpretable | Requires suitable thresholds |
| Z-score | Easy statistical baseline | Sensitive to distribution changes |
| IQR | More robust to some outliers | Does not capture complex patterns |
| Isolation Forest | Handles multivariate features | Scores may be difficult to interpret |
| Local Outlier Factor | Detects local density deviations | Sensitive to neighbourhood settings |
| Rolling statistics | Useful for time-dependent behaviour | May struggle with complex patterns |

The best method will depend on the type of anomaly and the available measurements.

## 8. Integration with Incident Investigation

Anomaly detection will provide evidence to the incident investigation component.

For example, if the system detects a period of reduced throughput, the investigation workflow may:

1. Retrieve the affected cell and time window.
2. Examine SINR, RSRP and BLER trends.
3. Compare the cell with neighbouring cells, if available.
4. Check resource utilisation.
5. Retrieve relevant technical documentation.
6. Rank possible explanations based on the available evidence.

The anomaly detector should not decide the root cause by itself.

Its responsibility is to identify unusual behaviour and provide evidence for further analysis.

## 9. Proposed Python Module Structure

```text
src/
└── ran_intelligence/
    └── anomaly_detection/
        ├── __init__.py
        ├── preprocessing.py
        ├── statistical.py
        ├── isolation_forest.py
        ├── local_outlier_factor.py
        ├── time_series.py
        ├── scoring.py
        └── evaluation.py
```

Responsibilities:

- `preprocessing.py`: Prepare features for detection.
- `statistical.py`: Implement threshold, Z-score and IQR methods.
- `isolation_forest.py`: Train and apply Isolation Forest.
- `local_outlier_factor.py`: Implement LOF experiments.
- `time_series.py`: Apply time-dependent detection methods.
- `scoring.py`: Convert model outputs into structured anomaly results.
- `evaluation.py`: Evaluate and compare detection methods.

## 10. Implementation Order

The implementation will proceed in the following order:

**Stage 1 — Statistical baselines**

Implement threshold-based detection, Z-score and IQR.

**Stage 2 — Feature engineering**

Create rolling statistics, KPI changes and cell-level features.

**Stage 3 — Isolation Forest**

Train an unsupervised model and inspect its anomaly scores.

**Stage 4 — Time-series detection**

Add methods for identifying persistent and gradual KPI degradation.

**Stage 5 — Evaluation**

Compare methods using synthetic scenarios with known labels.

**Stage 6 — Integration**

Expose anomaly results to the Streamlit dashboard and incident investigation workflow.

## 11. Expected Outcome

The anomaly detection component should identify unusual network measurements and periods of potential performance degradation.

Engineers should be able to see what was detected, when it occurred, which KPIs were affected and which method identified it.

The component should provide useful evidence for further investigation without presenting an anomaly as a confirmed network fault.
