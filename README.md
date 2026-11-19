# RAN Intelligence Platform

**AI-Powered 5G Network Intelligence and Incident Investigation Platform**

An end-to-end research and engineering platform for analysing 4G/5G Radio Access Network (RAN) measurements, detecting KPI anomalies, forecasting network performance, retrieving telecom standards, and assisting engineers with evidence-based incident investigation.

Combines data engineering, machine learning, hybrid RAG, agentic AI, network simulation and application engineering in one integrated system.

**The platform is advisory. It does not connect to or make changes to live mobile networks.**

<p align="center">
  <a href="https://prashantsu-ran-intellige-srcran-intelligencedashboardapp-6ritgr.streamlit.app/"><strong>🚀 Live Dashboard</strong></a>
  &nbsp;·&nbsp;
  <a href="https://ran-intelligence-api.onrender.com/docs"><strong>API Documentation</strong></a>
  &nbsp;·&nbsp;
  <a href="https://github.com/PrashantSU/ran-intelligence"><strong>Source Code</strong></a>
</p>

## System Architecture

<p align="center">
  <img src="docs/images/RAN Intelligence Platform Architecture and Workflow.png" alt="RAN Intelligence Platform System Architecture" width="100%">
</p>

## What the Platform Includes

| Component | Implementation |
|---|---|
| Data Engineering | Measurement ingestion, validation, cleaning, transformation and Parquet storage |
| KPI Analytics | LTE/NR measurement summaries, session comparisons and time-series analysis |
| Anomaly Detection | Robust statistical detection and event grouping |
| KPI Forecasting | Persistence, Random Forest, XGBoost and GRU models |
| Telecom RAG | Hybrid FAISS/BM25 retrieval, Reciprocal Rank Fusion, reranking and grounded answers |
| Agentic Investigation | LangGraph workflow coordinating analytics, forecasting, RAG and simulation tools |
| Digital Twin | Simplified cell and user simulation with configurable network scenarios |
| 5G NR Lab | Educational beamforming and scheduling experiments |
| Evaluation & Observability | Retrieval metrics, report validation, tool latency and investigation traces |
| Human-in-the-Loop | Investigation reports pause for engineer approval or rejection |
| Backend & Application | FastAPI REST services and interactive Streamlit dashboard |

## Explore the Platform

The application is organised into seven interactive workspaces.

### 1. Network Overview
Explore the available RAN measurements and network-level analytical information.

### 2. KPI Explorer
Inspect radio and throughput measurements, compare measurement sessions and analyse KPI behaviour over time.

### 3. Anomaly Detection
Identify unusual KPI patterns using statistical detection methods and inspect grouped anomaly events.

### 4. Forecasting Lab
Compare four forecasting approaches:

- Persistence baseline
- Random Forest
- XGBoost
- GRU neural network

Evaluate prediction performance and inspect model behaviour on the available measurement sessions.

### 5. Telecom Knowledge — Hybrid RAG

A domain-specific retrieval-augmented generation pipeline over 3GPP/ETSI telecom documentation.

**Retrieval pipeline:**

1. Semantic retrieval using sentence embeddings and FAISS.
2. BM25 keyword retrieval for exact technical terminology.
3. Reciprocal Rank Fusion (RRF) to combine retrieval rankings.
4. Reranking to improve the ordering of candidate passages.
5. Grounded answer generation with supporting source references.

**Why hybrid retrieval?**

Telecom standards contain both conceptual explanations and precise technical identifiers. Semantic search captures conceptual similarity, while BM25 helps find exact specification references, protocol terms and parameter names. RRF combines their rankings, and reranking further refines the retrieved evidence before generation.

### 6. Incident Investigation — Agentic AI

A LangGraph-based investigation workflow that coordinates the platform's analytical tools.

An engineer provides an incident description, measurement session, time window and severity. The workflow can:

- Collect relevant KPI evidence.
- Examine anomaly detections.
- Retrieve forecasting results.
- Search relevant telecom standards and documentation.
- Use network simulation as additional evidence.
- Generate a structured investigation report.
- Pause for human review and feedback.

The workflow distinguishes observed evidence from hypotheses. An anomaly is not automatically a confirmed network fault, and an AI-generated explanation is not treated as an established diagnosis.

### 7. Architecture & Engineering

Inspect the system architecture and the components connecting data processing, analytics, machine learning, retrieval, agent workflows and application services.

---

## Data Engineering & Dataset

The platform uses the publicly available AERPAW Ericsson 5G NSA RF and throughput dataset.

**Source:** [AERPAW dataset — Dryad](https://doi.org/10.5061/dryad.wh70rxx06)

The pipeline processes two measurement sessions:

| Measurement | yaw315 | yaw45 |
|---|---:|---:|
| Radio observations | 2,898 | 2,949 |
| Throughput observations | 786 | 818 |
| Matched throughput | 769 | 797 |
| Unmatched throughput | 17 | 21 |

**Combined processing results:**

- 5,847 radio observations.
- 1,604 throughput observations.
- 1,566 matched radio-throughput observations.
- 38 unmatched throughput observations.

Radio and throughput observations are matched using timestamps with a 250 ms tolerance. Unmatched throughput observations are retained separately, and the pipeline generates data-quality reports.

The dataset contains only two short measurement sessions. Results are descriptive and experimental, not evidence of generalisation to operational mobile networks. Throughput units and measurement semantics should be verified before operational interpretation.

## Model Evaluation

### KPI Forecasting — yaw315

Models were evaluated using a time-ordered test split containing 151 observations.

| Model | MAE | RMSE |
|---|---:|---:|
| Persistence | 5.490 | 6.935 |
| Random Forest | 5.366 | 7.011 |
| XGBoost | 5.405 | 6.967 |
| **GRU** | **4.608** | **6.308** |

The GRU achieved the lowest MAE and RMSE among the evaluated models on this measurement session.

These results demonstrate model comparison on the available data. They do not establish generalisation to unseen sessions or networks.

### RAG and Agent Evaluation

The project includes evaluation components for:

- Retrieval Precision@K and Recall@K.
- Mean Reciprocal Rank (MRR).
- Normalised Discounted Cumulative Gain (NDCG).
- Investigation report validation.
- Tool execution status and evidence counts.
- Workflow latency and human-review state.

Retrieval evaluation uses manually judged queries. These are prototype evaluation capabilities, not comprehensive production benchmarks.

## Engineering Highlights

The project goes beyond standalone notebooks and models. It integrates the complete workflow into a modular application.

- **Data engineering:** Ingestion, schema validation, timestamp alignment, data-quality checks and Parquet-based processing.
- **Analytics:** KPI summaries, session comparisons and time-series exploration.
- **Machine learning:** Multiple forecasting models and statistical anomaly detection.
- **Retrieval engineering:** Semantic and lexical retrieval, ranking fusion, reranking and source-grounded generation.
- **Agent orchestration:** Multi-tool incident investigation using LangGraph.
- **Simulation:** Simplified digital twin and interactive 5G NR experiments.
- **Backend engineering:** Versioned REST APIs and structured request/response validation.
- **Frontend engineering:** Interactive Streamlit workspaces and Plotly visualisations.
- **Testing:** Automated tests covering core processing, analytics, ML,
