# KPI Analytics and Network Performance Monitoring

## 1. Purpose

KPI analytics is one of the core components of the RAN Intelligence Platform.

It will turn raw network measurements into information that engineers can use to understand network performance, identify degradation and investigate unusual behaviour.

The initial implementation will focus on radio measurements and throughput from the AERPAW Ericsson dataset. As additional datasets become available, we will extend the analytics to include resource utilisation, mobility, retransmissions and other network indicators.

The goal is not simply to display KPI values. The platform should help explain how different measurements relate to each other and how network conditions change over time.

## 2. KPIs to Support

The platform will support the following indicators where the selected dataset provides the necessary measurements.

| KPI | Meaning | Why it matters |
|---|---|---|
| RSRP | Reference Signal Received Power | Indicates received signal strength |
| RSRQ | Reference Signal Received Quality | Provides information about signal quality |
| SINR | Signal-to-Interference-plus-Noise Ratio | Indicates radio link quality relative to interference and noise |
| CQI | Channel Quality Indicator | Represents reported channel quality |
| MCS | Modulation and Coding Scheme | Indicates the modulation and coding configuration |
| Throughput | Data transfer rate | Measures achieved user or network data rate |
| BLER | Block Error Rate | Indicates transmission block errors |
| PRB utilisation | Physical Resource Block utilisation | Indicates radio resource usage |
| HARQ retransmissions | Hybrid ARQ retransmissions | Helps analyse transmission reliability |
| Cell load | Demand or resource usage associated with a cell | Helps identify possible congestion |

Not every dataset will contain every KPI. The application should show which indicators are available instead of assuming that all measurements exist.

## 3. Main Analytics Capabilities

### 3.1 KPI Overview

The dashboard should provide a summary of the available network measurements.

Depending on the dataset, it may display:

- Average throughput.
- Average SINR.
- Average RSRP.
- Average RSRQ.
- Average BLER.
- Average PRB utilisation.
- Number of measurements.
- Number of cells and UEs.
- Selected time range.

Summary statistics should be calculated from the selected data and time window.

### 3.2 Time-Series Analysis

Network measurements change over time. A single average value may hide short periods of poor performance.

The platform should support time-series plots for available KPIs.

Examples:

- SINR over time.
- RSRP over time.
- Throughput over time.
- BLER over time.
- PRB utilisation over time.

Users should be able to select a KPI and inspect its behaviour over a chosen period.

Where useful, the application can show rolling averages to make longer-term trends easier to identify.

The original measurements should remain available so that smoothing does not hide short-lived changes.

### 3.3 Cell-Level Comparison

When cell identifiers are available, engineers should be able to compare performance across cells.

Possible comparisons include:

- Average throughput per cell.
- Average SINR per cell.
- RSRP distribution per cell.
- Cell load.
- Performance variation over time.

This can help identify whether a performance problem affects one cell or several cells.

Neighbouring-cell comparisons will be added when the dataset provides enough information about cell relationships.

### 3.4 UE-Level Analysis

If UE identifiers are available, the platform should support analysis at the individual user level.

Examples include:

- Throughput distribution across UEs.
- Radio quality variation between users.
- Number of users experiencing poor radio conditions.
- Comparison of UE performance within the same cell.

UE-level analysis should respect the available identifiers and measurement granularity. We should not assume that different datasets track the same UE across different sessions.

### 3.5 KPI Relationships

Some KPIs are useful when analysed together.

The platform should support comparisons such as:

- SINR against throughput.
- RSRP against throughput.
- CQI against MCS.
- BLER against throughput.
- PRB utilisation against throughput.
- SINR against BLER.

Scatter plots, correlation matrices and grouped summaries can help reveal relationships.

Correlation should not be interpreted as proof of causation. For example, a reduction in throughput may occur alongside lower SINR, but additional evidence is needed to establish the cause.

## 4. Network Performance Indicators

The platform should support simple rules for identifying potentially poor network conditions.

These rules will initially be configurable and used as indicators for further investigation.

Examples:

| Condition | Possible interpretation |
|---|---|
| Low SINR | Poor radio quality, interference or other radio conditions |
| Low RSRP | Weak received signal strength |
| High BLER | Increased transmission errors |
| High PRB utilisation | Possible resource congestion |
| Low throughput | Reduced achieved data rate |
| Sudden KPI variation | Possible change in network conditions |

The thresholds should not be hard-coded as universal values.

They may depend on the technology, configuration, measurement conditions and dataset. Thresholds used in experiments should be documented with their assumptions.

## 5. Aggregation and Statistical Analysis

The platform should provide configurable aggregation over different time intervals.

Examples include:

- Per measurement.
- Per minute.
- Per five minutes.
- Per hour.
- Per cell.
- Per UE.

Supported statistics may include:

- Mean.
- Median.
- Minimum and maximum.
- Standard deviation.
- Percentiles.
- Count of valid measurements.

Percentiles are particularly useful when average performance hides poor experiences for a subset of users.

For example, the fifth percentile of throughput can help examine the lower end of user performance.

Aggregation should account for missing measurements and irregular sampling intervals.

## 6. Visualisation

Plotly will be used for interactive visualisations in the Streamlit application.

The initial visualisations should include:

1. KPI summary metrics.
2. Time-series plots.
3. Cell-level comparison charts.
4. KPI distribution histograms.
5. Scatter plots between related KPIs.
6. Correlation heatmaps.
7. Throughput and radio quality comparisons.

The visualisations should allow users to select available KPIs, cells and time ranges.

We should prioritise useful plots over adding many charts that do not help answer a network performance question.

## 7. Relationship with Other Components

KPI analytics will provide structured information to other parts of the platform.

**Anomaly detection**

The anomaly detection component will use KPI measurements and derived features to identify unusual network behaviour.

**Forecasting**

The forecasting component will use historical KPI values to estimate future network conditions.

**Incident investigation**

The investigation agent will call analytics tools to retrieve KPI summaries, trends and cell comparisons.

**Network simulation**

Simulation results can be passed through the same analytics functions to compare different scenarios.

**Reporting**

The reporting component will use analytical results to create summaries and supporting evidence for incident investigations.

## 8. Proposed Python Module Structure

```text
src/
└── ran_intelligence/
    └── kpi_analytics/
        ├── __init__.py
        ├── metrics.py
        ├── aggregation.py
        ├── time_series.py
        ├── cell_analysis.py
        ├── ue_analysis.py
        ├── correlations.py
        └── thresholds.py
```

Responsibilities:

- `metrics.py`: Calculate basic KPI statistics.
- `aggregation.py`: Aggregate measurements across time and network entities.
- `time_series.py`: Prepare time-series data and rolling statistics.
- `cell_analysis.py`: Compare performance across cells.
- `ue_analysis.py`: Analyse UE-level measurements.
- `correlations.py`: Examine relationships between KPIs.
- `thresholds.py`: Apply configurable performance indicators.

The Streamlit application will use these functions rather than implementing analytical calculations directly inside the interface.

## 9. Testing and Evaluation

The analytics component should be tested using small datasets with known values.

Initial tests should verify:

- Correct calculation of averages and percentiles.
- Correct aggregation by cell and time.
- Handling of missing measurements.
- Handling of duplicate timestamps.
- Correct filtering by cell and time range.
- Correct KPI correlation calculations.
- Behaviour when a KPI is unavailable.
- Behaviour when the selected dataset is empty.

Results should also be checked against manually calculated values for small test cases.

## 10. Implementation Order

The component will be developed in stages.

**Stage 1 — Basic KPI calculations**

Implement mean, median, percentiles, minimum, maximum and standard deviation.

**Stage 2 — Time-series analytics**

Add timestamp handling, filtering, aggregation and rolling statistics.

**Stage 3 — Cell and UE analysis**

Add comparisons between cells and users where identifiers are available.

**Stage 4 — KPI relationships**

Implement correlation analysis and selected KPI comparisons.

**Stage 5 — Visualisation**

Connect the analytical functions to Streamlit and build the initial KPI dashboard.

**Stage 6 — Integration**

Expose the analytics functions so that anomaly detection, forecasting and incident investigation can reuse them.

## 11. Expected Outcome

The KPI analytics component should provide a reliable way to explore network measurements and understand performance changes.

An engineer should be able to select a dataset, inspect available KPIs, compare measurements over time and identify areas that may need further investigation.

The component will also provide the analytical foundation for anomaly detection, forecasting and automated incident investigation.

The first version will focus on correctness, clear visualisations and reusable Python functions. More advanced network diagnostics will be introduced as the other components are developed.
