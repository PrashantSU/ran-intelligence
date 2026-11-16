# Internal Data Model

## 1. Purpose

The platform will use data from several public telecom datasets, synthetic scenarios and simulation experiments.

These sources will not have identical column names, formats, units or levels of detail. One dataset might identify a measurement by sector, another by cell, and another by base station and user.

Rather than building separate analytics code for every dataset, we will convert incoming data into a common internal representation.

This document defines the main entities and relationships used across the platform.

The model is an initial design. We will refine it after inspecting the actual datasets.

## 2. Design principles

The data model should follow a few basic principles:

- Preserve the original source information.
- Use consistent names and units for common measurements.
- Keep cell, user, measurement and event information separate.
- Support time-series analysis.
- Allow measurements from different datasets to coexist.
- Distinguish real measurements from synthetic and simulated data.
- Do not assume every dataset contains every field.

Missing information should remain missing. We should not invent cell configurations, locations or radio measurements just to fill the schema.

## 3. Main entities

The initial model contains six main entities:

| Entity | Purpose |
|---|---|
| Dataset | Describes the original data source |
| Base station | Represents a network site or transmission point |
| Cell | Represents a logical radio cell or sector |
| User equipment | Represents a connected or observed UE |
| Measurement | Stores time-dependent network measurements |
| Network event | Records an incident or event associated with the network |

We will also maintain experiment and document metadata for the simulation and RAG components.

## 4. Dataset entity

Every imported dataset will have a dataset record.

| Field | Type | Description |
|---|---|---|
| dataset_id | String | Unique internal identifier |
| name | String | Dataset name |
| source | String | Original publisher |
| source_url | String | Original source link |
| version | String | Dataset release or version |
| licence | String | Licence or usage terms |
| acquired_at | Timestamp | Date downloaded |
| data_type | String | Public, synthetic or simulated |
| description | String | Short description |

Example:

```json
{
  "dataset_id": "aerpaw_5g_v1",
  "name": "AERPAW Ericsson 5G Measurements",
  "source": "AERPAW / Dryad",
  "source_url": "https://doi.org/10.5061/dryad.wh70rxx06",
  "version": "v1",
  "licence": "To be verified",
  "acquired_at": "2026-11-16T12:00:00Z",
  "data_type": "public",
  "description": "Public 5G RF and throughput measurements"
}
```

The licence field must be updated after checking the actual dataset terms. The example is not a claim about its licence.

## 5. Base station entity

A base station represents a physical or simulated transmission point.

| Field | Type | Description |
|---|---|---|
| base_station_id | String | Internal identifier |
| dataset_id | String | Source dataset |
| external_id | String | Original identifier, if available |
| technology | String | LTE, NR or unknown |
| latitude | Float | Latitude, if available |
| longitude | Float | Longitude, if available |
| description | String | Optional information |

Not every dataset will contain base station coordinates. These fields will be nullable.

## 6. Cell entity

A cell represents a logical radio cell or sector associated with a base station.

| Field | Type | Description |
|---|---|---|
| cell_id | String | Internal identifier |
| base_station_id | String | Associated base station |
| dataset_id | String | Source dataset |
| external_id | String | Original cell or sector identifier |
| technology | String | LTE, NR or unknown |
| band | String | Frequency band, if available |
| frequency_mhz | Float | Carrier frequency |
| bandwidth_mhz | Float | Channel bandwidth |
| pci | Integer | Physical Cell ID, if available |
| description | String | Optional information |

A dataset may identify sectors rather than cells. The ingestion layer will map them only when the meaning is clear.

## 7. User equipment entity

A UE represents a device or user identifier observed in a dataset or simulation.

| Field | Type | Description |
|---|---|---|
| ue_id | String | Internal identifier |
| dataset_id | String | Source dataset |
| external_id | String | Original UE identifier |
| serving_cell_id | String | Serving cell, if known |
| description | String | Optional information |

We will not attempt to identify real people or devices. External identifiers will be treated as dataset-specific identifiers.

If a dataset does not provide stable UE identifiers, the UE entity may not be created for that dataset.

## 8. Measurement entity

This is the central entity for KPI analytics, anomaly detection and forecasting.

Each row represents a measurement at a particular time and, where available, for a particular cell and UE.

| Field | Type | Description |
|---|---|---|
| measurement_id | String | Unique measurement identifier |
| dataset_id | String | Source dataset |
| timestamp | Timestamp | Measurement time |
| base_station_id | String | Associated base station, if known |
| cell_id | String | Associated cell, if known |
| ue_id | String | Associated UE, if known |
| rsrp_dbm | Float | Reference Signal Received Power |
| rsrq_db | Float | Reference Signal Received Quality |
| sinr_db | Float | Signal-to-Interference-plus-Noise Ratio |
| cqi | Float | Channel Quality Indicator |
| mcs | Integer | Modulation and Coding Scheme index |
| throughput_dl_mbps | Float | Downlink throughput |
| throughput_ul_mbps | Float | Uplink throughput |
| bler | Float | Block Error Rate |
| harq_retx_count | Integer | HARQ retransmission count |
| prb_utilization_pct | Float | Physical Resource Block utilisation |
| source_row_id | String | Original row identifier, if available |

These fields are optional because different datasets contain different measurements.

### 8.1 Measurement units

We will use consistent units internally.

| Metric | Internal unit |
|---|---|
| RSRP | dBm |
| RSRQ | dB |
| SINR | dB |
| Throughput | Mbps |
| PRB utilisation | Percentage |
| BLER | Fraction between 0 and 1 |
| Frequency | MHz |
| Bandwidth | MHz |
| Timestamp | UTC |

If a source provides throughput in Kbps, it will be converted to Mbps during preprocessing.

If BLER is expressed as a percentage, it will be converted to a fraction.

We will preserve the original values and units in source data or ingestion metadata so that conversions can be audited.

### 8.2 Measurement granularity

Measurements may exist at different levels:

- UE-level: a measurement associated with an individual UE.
- Cell-level: an aggregate measurement for a cell.
- Base-station-level: a measurement associated with a transmission point.
- Network-level: an aggregate across several cells.

We must retain the measurement level. A cell-level average should not be treated as an individual UE measurement.

The internal schema may later include a `measurement_level` field to make this distinction explicit.

## 9. Network event entity

Network events provide context for incident investigation.

| Field | Type | Description |
|---|---|---|
| event_id | String | Unique event identifier |
| dataset_id | String | Source dataset |
| timestamp | Timestamp | Event start time |
| end_timestamp | Timestamp | Event end time, if known |
| base_station_id | String | Associated base station |
| cell_id | String | Associated cell |
| event_type | String | Event category |
| severity | String | Event severity, if available |
| description | String | Event description |
| source | String | Original event source |
| is_synthetic | Boolean | Whether the event was generated |

Possible event types include:

- Cell outage.
- Handover failure.
- Congestion.
- Interference.
- Radio degradation.
- Backhaul degradation.
- Configuration change.

Some events will be generated for controlled experiments. These will be clearly marked as synthetic.

An event label does not automatically establish its cause. The investigation component must distinguish recorded events from its own hypotheses.

## 10. Experiment entity

The simulation and research components need to record how an experiment was configured.

| Field | Type | Description |
|---|---|---|
| experiment_id | String | Unique experiment identifier |
| name | String | Experiment name |
| created_at | Timestamp | Creation time |
| scenario_type | String | Experiment category |
| configuration | JSON | Parameters used |
| software_version | String | Relevant code version |
| dataset_id | String | Input dataset, if applicable |
| description | String | Experiment description |

Examples include:

- Scheduling policy comparison.
- Interference sensitivity experiment.
- Backhaul delay experiment.
- Beamforming comparison.
- KPI forecasting benchmark.

Results should reference the experiment that produced them.

## 11. Document metadata entity

The RAG system will maintain metadata for each document and its extracted sections.

| Field | Type | Description |
|---|---|---|
| document_id | String | Unique document identifier |
| title | String | Document title |
| publisher | String | 3GPP, ETSI, O-RAN or other publisher |
| version | String | Document version |
| publication_date | Date | Publication date, if available |
| source_url | String | Original document link |
| document_type | String | Specification, paper, manual, etc. |
| licence | String | Usage or redistribution terms |
| indexed_at | Timestamp | Date added to the knowledge base |

Individual chunks will have their own identifiers and reference their parent document.

Chunk metadata will include section information, page numbers where available, and the text location needed to produce citations.

## 12. Entity relationships

The main relationships are:

```text
Dataset
  |
  +---- Base Station
  |        |
  |        +---- Cell
  |                |
  |                +---- Measurement
  |                |
  |                +---- Network Event
  |
  +---- User Equipment
  |
  +---- Measurement
  |
  +---- Network Event

Experiment
  |
  +---- Configuration
  |
  +---- Results

Document
  |
  +---- Document Chunks
```

These relationships are logical. A dataset may not provide enough information to establish every relationship.

For example, a measurement may have a cell identifier but no known base station identifier. We should retain that measurement rather than discard it.

## 13. Storage approach

The initial storage design will use a combination of files and a relational database.

**Parquet files**

Used for:

- Imported measurements.
- Cleaned and transformed measurements.
- Large time-series tables.
- Synthetic measurement datasets.

**SQLite**

Used for:

- Dataset metadata.
- Cell and base station metadata.
- Network events.
- Experiment records.
- Investigation results.
- Application metadata.

**FAISS index and document metadata**

Used for:

- Vector embeddings.
- Retrieved document chunks.
- Document references and citation metadata.

We will avoid duplicating large measurement tables in SQLite unless a specific query or application requirement justifies it.

## 14. Data validation rules

The ingestion layer will check:

- Required identifiers are present where the source provides them.
- Timestamps can be parsed.
- Measurement values have valid numeric types.
- Units are known before conversion.
- Duplicate records are identified.
- Unexpected values are flagged.
- Relationships reference valid entities where those entities are available.

We should not apply overly broad physical limits without considering the measurement type and dataset context. An unusual value may be a genuine observation rather than a data error.

Validation results will be recorded so that downstream components can decide whether to use, exclude or flag questionable records.

## 15. Dataset-specific mapping

Each source dataset will have its own mapping into the internal model.

For example:

```text
AERPAW source columns
        |
        v
AERPAW schema mapping
        |
        v
Internal measurement schema
        |
        +---- KPI analytics
        +---- Anomaly detection
        +---- Forecasting
        +---- Incident investigation
```

The mapping layer will handle:

- Column renaming.
- Unit conversion.
- Timestamp parsing.
- Identifier mapping.
- Missing optional fields.
- Source-specific transformations.

We will not force all datasets into an identical raw format. Only the normalised output needs to follow the common internal model.

## 16. Implementation order

We will implement the model gradually.

**First:** Define the measurement schema and dataset metadata using the AERPAW dataset.

**Second:** Add the ingestion mapping and unit conversion logic.

**Third:** Add cell, base station and UE metadata where the source provides enough information.

**Fourth:** Add network events and synthetic incident scenarios.

**Fifth:** Add experiment records for simulation and benchmarking.

**Finally:** Add document and chunk metadata for the RAG system.

## 17. Important limitations

The internal model is a common representation, not a complete 3GPP or O-RAN information model.

It is designed for this project's analytics and investigation workflows.

Different datasets may use different definitions, sampling intervals, measurement procedures and aggregation levels. Normalising column names does not make those measurements directly comparable.

Any cross-dataset comparison must account for those differences.

The model will be updated as we inspect real data and discover fields or relationships that need to be represented more accurately.
