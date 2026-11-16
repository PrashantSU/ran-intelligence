# Data Sources and Schemas

## 1. Overview

The RAN Intelligence Platform will use a combination of publicly available telecom datasets and independently generated synthetic data.

Public datasets will provide real network measurements for analysis and model development. Synthetic data will help us test scenarios that are not sufficiently represented in public datasets, particularly network incidents with known causes.

The project will keep the origin of each dataset clear. Synthetic measurements will never be presented as real operator data.

The initial implementation will focus on a small number of datasets rather than downloading everything at once. We will inspect each source, understand its structure and licence, and then decide how it fits into the platform.

## 2. Selected Data Sources

### 2.1 AERPAW Ericsson 5G Measurements

**Source:** [AERPAW dataset on Dryad](https://doi.org/10.5061/dryad.wh70rxx06)

This will be our first real-world dataset.

The dataset contains measurements collected using an Ericsson 5G NSA network. It includes radio and throughput-related measurements collected under different measurement conditions.

Relevant fields include:

- RSRP
- SINR
- CQI
- MCS
- Throughput
- Cell and sector information
- Measurement conditions and location information, where available

**How we will use it:**

- Explore the relationship between radio conditions and throughput.
- Analyse how SINR and RSRP vary across measurements.
- Study the relationship between CQI, MCS and throughput.
- Build the initial data ingestion and validation pipeline.
- Create visualisations for network performance analysis.
- Establish a baseline for later predictive models.

We will first inspect the original files and document their actual column names, units and measurement intervals. The common schema will be created after this inspection rather than assuming that every dataset uses the same naming convention.

### 2.2 FCCLab 5G NR Dataset

**Source:** [FCCLab](https://fcclab.org/)

This dataset is a potential source for more detailed 5G NR measurements. It contains measurements from a 5G NR testbed and includes several radio, protocol and throughput-related indicators.

Relevant measurements include:

- SS-RSRP
- SS-RSRQ
- SS-SINR
- CQI
- BLER
- HARQ retransmissions
- MCS
- RLC and PDCP throughput
- Other protocol-level measurements

The dataset also includes controlled interference scenarios, making it useful for investigating the effect of interference on network performance.

**How we will use it:**

- Study interference-related performance degradation.
- Analyse BLER and retransmission behaviour.
- Investigate the relationship between radio quality and throughput.
- Develop and evaluate anomaly detection methods.
- Test whether models can distinguish normal operation from known experimental conditions.

This dataset will be considered after the initial AERPAW ingestion pipeline is working.

### 2.3 Colosseum / OpenRAN Gym Datasets

**Source:** [Colosseum](https://www.colosseum.net/)

Colosseum provides a 5G network emulation environment and associated research datasets. OpenRAN Gym datasets include measurements from multi-cell and multi-user experiments.

Depending on the selected dataset, available information can include:

- Base station and UE identifiers
- Traffic information
- Resource block allocation
- Scheduling decisions
- Cell and user performance
- Network configuration
- Experimental conditions

**How we will use it:**

- Study resource allocation and scheduling.
- Analyse cell load and user distribution.
- Investigate network performance under different traffic conditions.
- Build experiments around resource utilisation and scheduling policies.
- Support the 5G NR research lab.

We will select a specific dataset once we identify the files and fields that best fit these experiments.

### 2.4 Telecom Italia Traffic Dataset

**Source:** [Telecom Italia Big Data Challenge](https://www.telecomitalia.com/)

This dataset contains aggregated communication activity across geographical grid cells in Milan.

It is different from the radio measurement datasets. It focuses on traffic activity rather than radio-layer KPIs.

Depending on the selected release, it can include:

- Geographical grid identifiers
- Timestamp
- SMS activity
- Call activity
- Internet traffic

**How we will use it:**

- Explore traffic patterns over time.
- Study daily and weekly traffic variations.
- Build traffic forecasting experiments.
- Investigate how changes in traffic demand could affect network load.

The full dataset can be large, so we will use a manageable subset if this source is included.

## 3. Synthetic Data

Public datasets do not necessarily contain every network condition needed for testing the platform. They may also lack reliable labels describing the underlying cause of a performance problem.

To address this, we will generate synthetic network measurements.

Synthetic data will be used mainly for controlled experiments, testing and evaluation. It will be clearly labelled and stored separately from real measurements.

### 3.1 Initial Network Configuration

The synthetic network environment may include:

- 3 base stations
- 60 user equipment devices
- 64 antennas per base station
- Multiple cells and neighbouring-cell relationships
- Time-dependent traffic demand
- Different radio and network conditions

These parameters provide a starting point for the 5G NR experiments. They are inspired by the type of system studied in coordinated beamforming research, but the synthetic environment will be independently implemented.

### 3.2 Scenarios to Generate

We will initially consider the following scenarios:

| Scenario | Description | Possible indicators |
|---|---|---|
| Normal operation | Network operating within expected conditions | Stable KPIs |
| Congestion | High traffic demand and limited resources | High PRB utilisation, reduced throughput |
| Poor coverage | Weak radio signal | Low RSRP and potentially low SINR |
| Interference | Increased interference from other transmissions | Reduced SINR, increased BLER |
| Backhaul delay | Delayed information exchange between network elements | Delayed or outdated measurements |
| Traffic surge | Sudden increase in user demand | Increased cell load and resource utilisation |
| Handover problems | Users experience unsuccessful or unstable mobility events | Handover failures and interruptions |

The scenarios will have controlled parameters so that we can evaluate whether the analytics and diagnostic components respond as expected.

We will avoid treating a single KPI as definitive proof of an incident. For example, low SINR may be associated with interference, but it can also occur because of other radio conditions.

### 3.3 Synthetic Data Generation

The synthetic data generator will produce time-dependent measurements for cells and users.

It should support:

- Configurable network size.
- Configurable simulation duration.
- Different traffic patterns.
- Radio condition changes.
- Controlled incident injection.
- Known scenario labels.
- Reproducible random seeds.

The generator will be developed as a separate module so that synthetic data can be recreated whenever required.

## 4. Telecom Documentation for RAG

The retrieval system will use technical documents that help explain network behaviour and support incident investigation.

Potential sources include:

- [3GPP specifications](https://www.3gpp.org/)
- [ETSI publications](https://www.etsi.org/)
- [O-RAN Alliance specifications](https://www.o-ran.org/)
- Public research papers.
- Public technical reports and network documentation.

Documents may cover:

- 5G NR architecture.
- Radio resource management.
- Mobility and handover.
- Radio measurements.
- Scheduling and resource allocation.
- Beamforming and MIMO.
- Network performance indicators.
- Interference management.
- O-RAN architecture and interfaces.

The RAG system will retain document metadata so that generated answers can refer to the relevant source and section.

We will check the licence and redistribution conditions of each document before including its full contents in the GitHub repository. Where redistribution is not permitted, we will keep the source URL and metadata and download the document separately for local indexing.

## 5. Common Data Schema

The platform will eventually work with multiple datasets. Their original column names and formats may differ, so we need a common internal representation.

The initial schema will focus on measurements associated with a cell, UE and timestamp.

### 5.1 RAN Measurement Schema

| Field | Type | Description |
|---|---|---|
| timestamp | datetime | Measurement timestamp |
| dataset_id | string | Source dataset identifier |
| cell_id | string | Serving cell identifier |
| ue_id | string | UE identifier, if available |
| rsrp_dbm | float | Reference Signal Received Power |
| rsrq_db | float | Reference Signal Received Quality |
| sinr_db | float | Signal-to-Interference-plus-Noise Ratio |
| cqi | integer | Channel Quality Indicator |
| mcs | integer | Modulation and Coding Scheme |
| throughput_mbps | float | Measured throughput |
| bler | float | Block Error Rate, if available |
| prb_utilisation | float | Physical Resource Block utilisation, if available |
| latitude | float | Latitude, if available |
| longitude | float | Longitude, if available |
| source_type | string | Real or synthetic |
| scenario_label | string | Known scenario label, if available |

Not every dataset will contain every field. Missing values will remain missing rather than being filled with invented measurements.

The schema may be extended as we inspect the actual datasets.

### 5.2 Cell Information Schema

| Field | Type | Description |
|---|---|---|
| cell_id | string | Unique cell identifier |
| site_id | string | Physical site identifier, if available |
| technology | string | LTE, NR or other supported technology |
| band | string | Frequency band, if available |
| latitude | float | Cell latitude, if available |
| longitude | float | Cell longitude, if available |
| antenna_count | integer | Number of antennas, if known |
| neighbour_cells | list | Related neighbouring cell identifiers |

This information will help the platform compare neighbouring cells and analyse spatial relationships.

### 5.3 Network Event Schema

Network events will be used to represent incidents, alarms and controlled experimental conditions.

| Field | Type | Description |
|---|---|---|
| event_id | string | Unique event identifier |
| timestamp | datetime | Event timestamp |
| cell_id | string | Related cell |
| event_type | string | Event category |
| severity | string | Event severity, if known |
| description | string | Short event description |
| source_type | string | Real or synthetic |
| confirmed_cause | string | Confirmed cause, if available |

An important distinction will be maintained between an observed event and a confirmed root cause. The system should not automatically treat a suspected cause as a confirmed one.

### 5.4 Telecom Document Metadata Schema

| Field | Type | Description |
|---|---|---|
| document_id | string | Unique document identifier |
| title | string | Document title |
| source | string | Publisher or organisation |
| document_type | string | Specification, paper, report or manual |
| version | string | Document version, if available |
| publication_date | date | Publication date, if available |
| section | string | Section or chapter |
| page_number | integer | Page number, if available |
| source_url | string | Original document URL |
| licence | string | Licence or access information |

The document content will be processed separately into chunks for embedding and retrieval. Each chunk should retain its document identifier and source location so that citations can be generated.

## 6. Data Processing and Storage

The data ingestion pipeline will follow a consistent process:

1. Load the original dataset.
2. Record its source and metadata.
3. Inspect column names, types, units and missing values.
4. Convert fields into the common internal schema.
5. Validate timestamps and measurement ranges.
6. Identify duplicates and invalid records.
7. Store the processed measurements.
8. Record the transformation details.

The original data should remain unchanged. Processed data will be stored separately so that transformations can be reproduced.

For the initial implementation, we will use:

- CSV and Parquet for dataset files.
- Pandas for data inspection and transformation.
- SQLite for structured application data.
- FAISS for vector-based document retrieval.

We can introduce PostgreSQL or other storage systems later if the application requires them.

## 7. Dataset Organisation

The repository will keep data organised by source and processing stage.

```text
datasets/
├── raw/
│   ├── aerpaw/
│   ├── fcclab/
│   ├── colosseum/
│   └── telecom_italia/
├── processed/
│   ├── ran_measurements/
│   ├── cell_information/
│   └── traffic/
├── synthetic/
│   ├── network_measurements/
│   ├── incidents/
│   └── simulation/
└── benchmark/
    ├── anomaly_detection/
    ├── forecasting/
    └── diagnosis/
```

Large datasets will not be committed directly to GitHub. The repository will contain download instructions, metadata, processing scripts and, where appropriate, small samples that are permitted for redistribution.

The exact dataset structure may change as implementation progresses.

## 8. Data Quality and Validation

Before measurements are used for analytics or machine learning, the ingestion pipeline should check:

- Missing values.
- Duplicate records.
- Invalid timestamps.
- Unexpected data types.
- Impossible or suspicious measurement values.
- Inconsistent units.
- Unexpected changes in sampling intervals.
- Invalid cell or UE identifiers.
- Inconsistent source metadata.

Validation rules should account for differences between datasets. A missing CQI value, for example, should not cause an otherwise useful record to be discarded if the dataset does not provide CQI.

We will also distinguish between genuinely missing measurements and measurements that were not collected by the source.

## 9. Dataset Selection and Implementation Order

The planned order is:

| Priority | Dataset | Main purpose |
|---|---|---|
| 1 | AERPAW Ericsson 5G | Initial ingestion, EDA and KPI analytics |
| 2 | Synthetic RAN data | Controlled incidents and reproducible tests |
| 3 | FCCLab 5G NR | Interference and detailed radio analysis |
| 4 | Colosseum / OpenRAN Gym | Scheduling and resource allocation |
| 5 | Telecom Italia | Traffic analysis and forecasting |

Telecom documentation will be collected separately as the RAG subsystem is developed.

This order allows us to build a working pipeline early without spending time downloading and processing several large datasets at once.

## 10. Data Limitations

There are some limitations to keep in mind:

- Public datasets may not represent the full complexity of a commercial operator network.
- Different sources may use different measurement definitions, units and sampling intervals.
- Some datasets may not provide cell-level or UE-level identifiers.
- Public measurements may not contain confirmed incident labels.
- Synthetic data can help test known scenarios but cannot replace validation on real network measurements.
- Results from controlled experiments should not be presented as guaranteed performance in a live network.

The platform will make these limitations visible when presenting analytical results.

## 11. Initial Implementation Target

The first data milestone is deliberately small.

We will:

1. Download the AERPAW Ericsson dataset.
2. Inspect the available files and columns.
3. Identify measurement units and timestamps.
4. Create a data dictionary for the original dataset.
5. Map its fields to the common RAN measurement schema.
6. Implement basic validation and cleaning.
7. Save a processed version in CSV or Parquet format.
8. Create initial KPI visualisations.

Once this works, we can add synthetic incident data and gradually integrate the other sources.

The aim is to establish a reliable data foundation before building the more advanced analytics and AI components.
