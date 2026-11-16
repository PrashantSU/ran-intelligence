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

Anomaly severity should not be confused with
