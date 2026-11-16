# Data Dictionary

## 1. Purpose

This document describes the main fields and KPIs used by the RAN Intelligence Platform.

Different datasets may use different names, units and measurement methods for the same metric. The ingestion layer will map them to consistent internal names while preserving the original source information.

Not every dataset will contain every field. Missing measurements should remain missing rather than being estimated without a clearly documented method.

## 2. Radio measurement KPIs

| Field | Description | Unit | General interpretation |
|---|---|---|---|
| `rsrp_dbm` | Reference Signal Received Power | dBm | Indicates received reference signal power |
| `rsrq_db` | Reference Signal Received Quality | dB | Indicates reference signal quality |
| `sinr_db` | Signal-to-Interference-plus-Noise Ratio | dB | Indicates signal quality relative to interference and noise |
| `cqi` | Channel Quality Indicator | Index | Indicates reported channel quality |
| `mcs` | Modulation and Coding Scheme | Index | Represents modulation and coding selection |

### RSRP

RSRP measures the power of received reference signals.

It is useful for studying signal coverage and received signal strength.

A low RSRP value can indicate weak coverage, but it does not by itself establish the cause of poor throughput.

### RSRQ

RSRQ measures reference signal quality relative to received power and resource usage.

It can help identify situations where signal quality is poor despite reasonable received power.

### SINR

SINR measures the strength of the desired signal relative to interference and noise.

A low SINR can affect achievable data rates and link reliability. However, it does not automatically prove that interference is the cause.

### CQI

CQI is a channel quality indicator reported by the UE.

It is used by the network to support link adaptation. The exact interpretation depends on the reporting configuration and technology.

### MCS

MCS represents the modulation and coding scheme used for transmission.

Higher-order modulation and coding can provide higher spectral efficiency under suitable radio conditions, but the selected MCS also depends on link adaptation and other system constraints.

## 3. Network performance KPIs

| Field | Description | Unit |
|---|---|---|
| `throughput_dl_mbps` | Downlink throughput | Mbps |
| `throughput_ul_mbps` | Uplink throughput | Mbps |
| `bler` | Block Error Rate | Fraction |
| `harq_retx_count` | HARQ retransmission count | Count |
| `prb_utilization_pct` | Physical Resource Block utilisation | Percentage |
| `latency_ms` | Measured network latency | Milliseconds |
| `packet_loss_pct` | Packet loss | Percentage |

### Throughput

Throughput represents the achieved data transfer rate.

We will distinguish between UE-level, cell-level and application-level throughput whenever the source provides enough information.

These measurements are not necessarily interchangeable.

### BLER

BLER represents the proportion of transmitted blocks received incorrectly under a specified measurement procedure.

The platform will store BLER as a fraction between 0 and 1. If a source reports percentages, ingestion will convert them.

### HARQ retransmissions

HARQ retransmission counts provide information about retransmission activity.

A high count can indicate link-quality problems or challenging transmission conditions, but interpretation requires knowledge of the measurement interval and traffic volume.

### PRB utilisation

PRB utilisation describes how much of the available physical resource is being used over a defined interval.

High utilisation may indicate congestion, but the definition and aggregation method must be checked for each dataset.

### Latency

Latency measures the time required for data to travel between specified measurement endpoints.

We must record the measurement context. Radio scheduling delay, transport delay and end-to-end application latency are different quantities.

### Packet loss

Packet loss represents the proportion of packets that fail to reach the intended destination.

It is useful for investigating service quality but depends on where and how it was measured.

## 4. Network and topology fields

| Field | Description |
|---|---|
| `base_station_id` | Internal base station identifier |
| `cell_id` | Internal cell identifier |
| `external_id` | Identifier used by the original dataset |
| `ue_id` | Internal UE identifier |
| `technology` | LTE, NR or another supported technology |
| `frequency_mhz` | Carrier frequency |
| `bandwidth_mhz` | Channel bandwidth |
| `pci` | Physical Cell ID |
| `latitude` | Latitude, if available |
| `longitude` | Longitude, if available |

Identifiers must remain unique within their relevant dataset context. Two datasets may use the same external cell identifier for completely different cells.

## 5. Time-related fields

| Field | Description |
|---|---|
| `timestamp` | Time at which the measurement was recorded |
| `end_timestamp` | End of an event or measurement interval, if available |
| `interval_seconds` | Duration represented by an aggregated measurement |
| `acquired_at` | Time the dataset was obtained |
| `processed_at` | Time the data-processing step completed |

Timestamps will be stored in UTC internally.

We will preserve the original timestamp and timezone information during ingestion where available.

Measurements must not be compared as if they were simultaneous when their sampling intervals differ significantly.

## 6. Derived KPIs

Some useful indicators can be calculated from existing measurements.

| Derived metric | Description |
|---|---|
| `throughput_change_pct` | Percentage change in throughput |
| `sinr_change_db` | Change in SINR relative to a reference period |
| `rsrp_change_db` | Change in RSRP relative to a reference period |
| `prb_load_category` | Categorisation of resource utilisation |
| `rolling_throughput_mean` | Rolling average throughput |
| `rolling_sinr_mean` | Rolling average SINR |
| `kpi_anomaly_score` | Score produced by an anomaly detection method |

Derived metrics must record their calculation method and relevant time window.

For percentage change, special care is needed when the reference value is zero or close to zero.

## 7. Anomaly-related fields

The anomaly detection component will produce additional fields.

| Field | Description |
|---|---|
| `anomaly_id` | Unique anomaly identifier |
| `timestamp` | Time of the detected anomaly |
| `cell_id` | Associated cell |
| `metric_name` | KPI being evaluated |
| `observed_value` | Observed measurement |
| `expected_value` | Baseline or expected measurement |
| `anomaly_score` | Model or method-specific score |
| `detection_method` | Statistical or machine-learning method |
| `severity` | Assigned severity category |
| `is_synthetic` | Whether the test case is synthetic |

An anomaly score is not automatically a probability. Its meaning depends on the method that generated it.

Severity thresholds will be documented and evaluated rather than selected arbitrarily.

## 8. Incident and investigation fields

| Field | Description |
|---|---|
| `incident_id` | Unique incident identifier |
| `description` | Original incident description |
| `start_time` | Incident start time |
| `end_time` | Incident end time, if known |
| `affected_cell_ids` | Cells involved |
| `event_type` | Incident category |
| `hypothesis` | Possible explanation |
| `evidence` | Supporting measurements or documents |
| `confidence` | Confidence assessment |
| `investigation_status` | Current investigation status |

The investigation system must distinguish between:

- **Observed evidence:** directly available measurements, events or documented facts.
- **Hypothesis:** a possible explanation supported by some evidence.
- **Confirmed cause:** a cause established through reliable external evidence or an appropriate verification process.

The system should not label a hypothesis as a confirmed cause simply because an LLM considers it plausible.

## 9. Data quality fields

The ingestion and validation pipeline will also maintain information about data quality.

| Field | Description |
|---|---|
| `source_row_id` | Original row reference |
| `validation_status` | Pass, warning or failure |
| `missing_fields` | Missing expected fields |
| `invalid_fields` | Fields that failed validation |
| `duplicate_flag` | Whether the record is a duplicate |
| `unit_conversion_applied` | Whether unit conversion occurred |
| `quality_notes` | Additional validation information |

These fields will help trace unexpected results back to their source records.

## 10. Important interpretation rules

The following rules will guide KPI analysis:

1. Low RSRP indicates weak received signal power, not necessarily interference.
2. Low SINR can result from interference, noise or weak desired signal power.
3. High PRB utilisation can indicate heavy resource demand, but does not alone establish poor user experience.
4. High BLER and retransmission activity may indicate radio-link problems, but measurement definitions and traffic conditions matter.
5. Throughput depends on radio conditions, bandwidth, scheduling, load, protocol overhead and transport constraints.
6. CQI and MCS are related to link adaptation, but they are not interchangeable.
7. Cell-level averages can hide individual UE problems.
8. Measurements from different datasets should not be directly compared without checking their definitions and collection conditions.

## 11. Implementation notes

The first implementation will use only fields actually available in the AERPAW dataset.

As additional datasets are integrated, we will extend the mapping and schema where necessary.

The data dictionary will be updated whenever:

- A new KPI is introduced.
- A source uses a different unit or definition.
- A derived metric is added.
- A validation rule changes.
- An important limitation is discovered.

This document should remain consistent with the actual implementation rather than becoming a list of metrics the platform never uses.
