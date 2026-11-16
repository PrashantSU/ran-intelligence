# Data Acquisition Plan

## 1. Purpose

The RAN Intelligence Platform needs several types of data. No single public dataset is likely to contain everything we need, from radio measurements and network events to traffic patterns and beamforming experiments.

We will therefore combine public telecom datasets with independently generated synthetic data.

The first priority is to obtain a small, usable dataset and build the ingestion pipeline around it. We can add more complex datasets once the initial workflow is working.

## 2. Data categories

We will collect data for five main areas.

| Data category | Examples | Main use |
|---|---|---|
| Radio measurements | RSRP, RSRQ, SINR, CQI, MCS | KPI analytics and anomaly detection |
| Network performance | Throughput, BLER, retransmissions, PRB usage | Monitoring and forecasting |
| Network configuration | Cell IDs, sectors, neighbours, configuration | Cell-level analysis |
| Network events | Handover failures, outages, congestion | Incident investigation |
| Wireless simulation | Channel conditions, interference, scheduling | 5G NR research lab |

Telecom documentation will be collected separately for the RAG knowledge base.

## 3. Public datasets

### 3.1 AERPAW 5G measurement dataset

**Priority: First dataset**

Source: [AERPAW Ericsson 5G NSA RF and throughput measurements](https://doi.org/10.5061/dryad.wh70rxx06)

This dataset is a good starting point because it is relatively small and contains actual 5G-related measurements.

Relevant fields include:

- RSRP
- SINR
- CQI
- MCS
- Throughput
- LTE and NR measurement information
- Sector and measurement context

**Planned use:**

- Test CSV ingestion.
- Build the first measurement schema.
- Calculate and visualise KPIs.
- Study relationships between radio conditions and throughput.
- Test basic anomaly detection.
- Build the first working dashboard.

We will inspect the actual files and column names before defining the final mapping. We should not assume every field is available in every record.

### 3.2 FCCLab FccIQ dataset

**Priority: Second dataset**

Source: [FCCLab](https://fcclab.stanford.edu/)

This dataset provides measurements from a 5G NR testbed. Its reported measurements include radio and protocol-level indicators such as:

- SS-RSRP
- SS-RSRQ
- SS-SINR
- CQI
- BLER
- HARQ retransmissions
- MCS
- Throughput-related measurements

It also includes controlled interference scenarios.

**Planned use:**

- Investigate radio degradation.
- Compare normal and interference conditions.
- Test anomaly detection with labelled scenarios where available.
- Study relationships between interference, retransmissions and throughput.
- Create more realistic incident investigation examples.

This dataset may require more preprocessing than AERPAW, so we will inspect its format and documentation before integrating it.

### 3.3 Colosseum and OpenRAN Gym

**Priority: Third dataset**

Sources:

- [Colosseum](https://www.northeastern.edu/colosseum/)
- [OpenRAN Gym](https://openrangym.com/)

These resources are useful for experiments involving multiple base stations, users, traffic and scheduling policies.

Depending on the available dataset, relevant information may include:

- Base station and user identifiers.
- Scheduling decisions.
- Resource block allocation.
- Traffic and throughput.
- Network slice information.
- Cell load and performance measurements.

**Planned use:**

- Resource allocation analysis.
- Scheduling comparisons.
- Load-related experiments.
- Multi-cell network scenarios.
- Additional evaluation of the simulation and research components.

We will start with downloadable datasets rather than relying on access to a live testbed.

### 3.4 Telecom Italia traffic dataset

**Priority: Optional**

Source: [Telecom Italia Big Data Challenge](https://dandelion.eu/datamine/open-big-data/)

This dataset contains mobile activity information over geographical grid cells, including traffic patterns at regular time intervals.

It is not a radio-layer dataset. It does not replace measurements such as SINR or RSRP.

**Planned use:**

- Traffic forecasting.
- Temporal load analysis.
- Understanding geographical variation in network demand.
- Testing aggregation and time-series processing.

The original data can be large, so we will use a manageable subset if we decide to include it.

## 4. Synthetic data

Public datasets will not cover every scenario required by the platform. We will generate synthetic data for controlled experiments.

The synthetic generator will create records for:

- Multiple base stations.
- Multiple cells and users.
- Radio measurements.
- Throughput and traffic demand.
- Resource utilisation.
- Interference conditions.
- Network degradation events.

We can also generate specific scenarios such as:

| Scenario | Expected behaviour |
|---|---|
| Congestion | PRB utilisation increases and throughput may fall |
| Poor radio conditions | SINR and possibly RSRP decrease |
| Interference | SINR decreases and retransmissions may increase |
| Backhaul limitation | Throughput becomes constrained despite reasonable radio conditions |
| Sudden outage | Measurements or traffic drop sharply |
| Gradual degradation | KPIs deteriorate over a period of time |

These scenarios will have known labels, making them useful for testing anomaly detection and incident investigation.

Synthetic data must always be identified as synthetic. It will not be presented as real operator measurements.

For the advanced 5G NR lab, we can independently create a simulation configuration inspired by research-style setups, such as three base stations, multiple users and multi-antenna transmission. This is not a reproduction of Huawei's internal system or data.

## 5. Telecom documentation for RAG

The knowledge base will use publicly accessible technical documentation.

Potential sources include:

- [3GPP specifications](https://www.3gpp.org/specifications)
- [ETSI publications](https://www.etsi.org/standards)
- [O-RAN Alliance](https://www.o-ran.org/)
- Open-access research papers.
- Public technical documentation and manuals.

We will prioritise documents relevant to:

- 5G NR radio measurements.
- RAN architecture.
- Mobility and handover.
- Scheduling and resource allocation.
- Beamforming and MIMO.
- Interference management.
- Network performance and troubleshooting.

Each document will have metadata such as its title, publisher, version, publication date, source URL and relevant sections.

We will check the terms of use before redistributing documents. Where redistribution is not permitted, we will keep the source metadata and download instructions rather than committing the original PDF to GitHub.

## 6. Dataset selection by subsystem

The datasets will not all be used for every component.

| Subsystem | Initial data source |
|---|---|
| Data ingestion | AERPAW |
| KPI analytics | AERPAW |
| Anomaly detection | AERPAW and synthetic data |
| KPI forecasting | AERPAW and synthetic data |
| Interference analysis | FCCLab and synthetic data |
| Scheduling analysis | Colosseum / OpenRAN Gym |
| Traffic forecasting | Telecom Italia subset, if useful |
| Telecom RAG | 3GPP, ETSI, O-RAN and research papers |
| Incident investigation | Measurements, synthetic events and retrieved documents |
| 5G NR lab | Independently generated simulation data |

This lets us build the platform incrementally without waiting for every dataset.

## 7. Dataset acquisition procedure

Every dataset should follow the same acquisition process.

1. Find the original source and read its documentation.
2. Check its licence and conditions of use.
3. Record the download URL and dataset version.
4. Download the original files.
5. Inspect file formats, column names, units and missing values.
6. Create a dataset description and schema mapping.
7. Run the ingestion and validation pipeline.
8. Store the processed version separately from the original.
9. Record any preprocessing steps.

We should not modify the original files directly. Keeping raw and processed data separate makes it easier to reproduce experiments.

## 8. Repository organisation

The initial data directory will follow this structure:

```text
datasets/
├── README.md
├── metadata/
│   ├── aerpaw.json
│   ├── fcclab.json
│   └── colosseum.json
├── raw/
│   ├── aerpaw/
│   ├── fcclab/
│   └── colosseum/
├── processed/
│   ├── aerpaw/
│   ├── fcclab/
│   └── colosseum/
├── synthetic/
│   ├── measurements/
│   ├── events/
│   └── scenarios/
└── benchmark/
```

Large datasets will not be committed to GitHub.

The repository will contain:

- Dataset metadata.
- Download instructions or scripts where permitted.
- Schema definitions.
- Small samples when the licence allows.
- Processing scripts.
- Synthetic data generators.
- Evaluation datasets and benchmark definitions.

The raw and processed directories can be excluded from Git using `.gitignore`, with exceptions for any small, explicitly approved sample files.

## 9. Dataset metadata

For every external dataset, we will record:

| Field | Description |
|---|---|
| Dataset name | Official dataset name |
| Source | Original publisher or repository |
| Source URL | Original download or information page |
| Version | Dataset release or version |
| Download date | Date we obtained the data |
| Licence | Licence or terms of use |
| File format | CSV, Parquet, JSON, etc. |
| Size | Approximate download size |
| Description | What the dataset contains |
| Known limitations | Missing fields, sampling limitations or other issues |
| Intended use | Which platform components use it |

This information will make it clear where the data came from and how it can be reused.

## 10. Initial acquisition order

We will acquire the data in stages.

**Stage 1 — AERPAW**

Download and inspect the small AERPAW dataset. Use it to build the first ingestion and KPI analytics workflow.

**Stage 2 — Synthetic scenarios**

Create a synthetic measurement generator and labelled incident scenarios. Use these for repeatable anomaly detection and investigation tests.

**Stage 3 — FCCLab**

Inspect the FCCLab dataset and integrate its richer 5G NR measurements for interference-related analysis.

**Stage 4 — Colosseum / OpenRAN Gym**

Add data for multi-cell scheduling and resource allocation experiments.

**Stage 5 — Telecom documentation**

Build the RAG document collection from selected public specifications and research papers. This can proceed alongside the measurement-data work once the ingestion foundation is stable.

**Stage 6 — Additional traffic data**

Consider the Telecom Italia dataset only if it adds something useful to the forecasting and traffic-analysis components.

## 11. What counts as a usable dataset?

Before integrating a dataset into the platform, we should be able to answer:

- Where did the data come from?
- Are we allowed to use it?
- What does each row represent?
- What are the units of measurement?
- What time information is available?
- Which fields are missing?
- Are there known labels or experimental conditions?
- What can we reasonably conclude from it?

If these questions cannot be answered, the dataset should not be used to support technical conclusions.

## 12. First milestone

The first data milestone is deliberately small:

- Obtain the AERPAW dataset.
- Inspect its files and columns.
- Document its original schema.
- Map relevant fields to our internal measurement schema.
- Load the data into the ingestion pipeline.
- Generate a basic data-quality report.
- Save a processed Parquet version.
- Produce a small KPI analysis.

Once this works, we will have a real data pipeline to build on instead of starting with an artificial example.
