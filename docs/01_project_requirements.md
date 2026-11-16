# RAN Intelligence Platform — Project Requirements

## 1. Project Overview

**Project Name:** RAN Intelligence Platform

**Description:** AI-Powered 5G Network Intelligence and Incident Investigation Platform.

RAN Intelligence is an integrated software platform designed to analyse Radio Access Network (RAN) performance, identify abnormal network behaviour, predict potential performance degradation, retrieve relevant telecom knowledge and assist engineers in investigating network incidents.

The platform combines data engineering, machine learning, information retrieval, generative AI and wireless network analysis into a unified application.

## 2. Problem Statement

Modern mobile networks generate large volumes of performance measurements, configuration information, network events and technical documentation.

Engineers often need to examine multiple data sources and tools to understand network performance issues.

The platform aims to simplify this process by providing:

- Centralised network data ingestion and analysis.
- Automated detection of abnormal network behaviour.
- Predictive analysis of network performance.
- Intelligent retrieval of telecom technical knowledge.
- AI-assisted incident investigation.
- Evidence-supported diagnostic reports.

## 3. Project Objectives

1. Develop a reliable pipeline for ingesting and processing network measurements.
2. Build an interactive network KPI analytics system.
3. Implement machine learning models for anomaly detection and KPI forecasting.
4. Develop an advanced Retrieval-Augmented Generation (RAG) system for telecom documentation.
5. Build an AI agent capable of performing structured, multi-step incident investigations.
6. Develop simplified 5G NR experiments and network simulation capabilities.
7. Establish reproducible evaluation pipelines for all major components.
8. Deliver an integrated application with a user-friendly interface.

## 4. Target Users

- Radio Access Network (RAN) engineers.
- Telecom network optimisation engineers.
- Network performance analysts.
- Data scientists working with telecom data.
- Machine learning and AI engineers.
- Telecom research and development teams.

## 5. Functional Requirements

### FR-01: Network Data Ingestion

The platform shall support:

- Importing network measurements from CSV and other structured formats.
- Validating incoming records and identifying missing or invalid values.
- Cleaning and transforming network measurements.
- Storing processed measurements for subsequent analysis.
- Maintaining basic data provenance and ingestion information.

### FR-02: Network KPI Analytics

The platform shall support analysis of:

- RSRP and RSRQ.
- SINR.
- Throughput.
- CQI and MCS.
- BLER.
- PRB utilisation.
- Retransmission rates.
- Cell availability and load.

It shall provide KPI summaries, historical trends, cell comparisons and interactive visualisations.

### FR-03: Anomaly Detection

The platform shall:

- Identify unusual KPI patterns.
- Detect potential performance degradation.
- Support multiple anomaly detection approaches.
- Display anomaly scores and relevant measurements.
- Evaluate detection performance using labelled test data.

### FR-04: KPI Forecasting

The platform shall:

- Forecast selected network KPIs over configurable future intervals.
- Compare predicted and observed values.
- Evaluate forecasting performance.
- Visualise forecast uncertainty where supported.

### FR-05: Telecom Knowledge Retrieval

The platform shall:

- Ingest telecom technical documentation.
- Extract and process document content.
- Generate vector embeddings.
- Support semantic and keyword-based retrieval.
- Implement hybrid search and reranking.
- Generate answers grounded in retrieved documents.
- Provide citations and source references.

### FR-06: AI-Assisted Incident Investigation

The platform shall:

- Accept a network incident or performance alert.
- Retrieve relevant network measurements and historical information.
- Analyse KPI patterns and detected anomalies.
- Retrieve relevant technical documentation.
- Generate and rank possible root-cause hypotheses.
- Support controlled tool-based investigation using an AI agent.
- Produce an evidence-supported investigation report.
- Allow an engineer to review the findings.

The system must distinguish observed evidence, possible explanations and confirmed causes.

### FR-07: 5G NR Intelligence Lab

The platform shall provide experimental capabilities involving:

- Radio signal and interference analysis.
- Beamforming experiments.
- Radio resource scheduling.
- Cell association and load balancing.
- Coordinated beamforming.
- Prediction-assisted scheduling.
- Backhaul delay experiments.

### FR-08: Network Simulation

The platform shall support simplified what-if experiments to examine the potential impact of selected network parameters on network performance.

Simulation results must be clearly distinguished from measurements of real networks.

### FR-09: Evaluation and Reporting

The platform shall provide:

- Machine learning evaluation metrics.
- Retrieval quality metrics.
- Generation quality and citation evaluation.
- Incident investigation evaluation.
- Latency and reliability measurements.
- Exportable investigation reports.

## 6. Non-Functional Requirements

### NFR-01: Modularity

The application shall use a modular architecture with clearly separated responsibilities.

### NFR-02: Reproducibility

Experiments, model configurations and evaluation procedures should be reproducible.

### NFR-03: Maintainability

Code shall follow consistent naming conventions, documentation practices and testing standards.

### NFR-04: Performance

The application should support efficient processing of its selected datasets and provide reasonable response times on available hardware.

### NFR-05: Reliability

Important application components shall include error handling, input validation and automated tests.

### NFR-06: Security

Secrets shall not be committed to GitHub. Uploaded data and application inputs shall be validated.

### NFR-07: Cost

The project shall prioritise free and open-source technologies. No paid API or subscription shall be mandatory.

### NFR-08: Usability

The platform shall provide an accessible interface through Streamlit.

## 7. Technology Stack

| Area | Technology |
|---|---|
| Programming | Python |
| Data processing | Pandas, NumPy |
| Database | PostgreSQL / SQLite |
| Backend | FastAPI |
| Frontend | Streamlit |
| Visualisation | Plotly |
| Machine learning | Scikit-learn, XGBoost |
| Deep learning | PyTorch |
| Embeddings | Sentence Transformers |
| Vector search | FAISS |
| Keyword search | BM25 |
| RAG and agents | LangChain, LangGraph |
| Local LLM inference | Ollama |
| Testing | Pytest |
| Deployment | Docker |
| Version control | Git, GitHub |

Technology choices may be revised during implementation when justified by technical requirements.

## 8. Data Requirements

The platform shall use publicly available or synthetically generated datasets.

Potential data categories include:

- RAN performance measurements.
- Cell configuration information.
- Network event and incident records.
- Telecom technical documentation.
- Research publications and standards.

Each dataset must have documented provenance, licensing and limitations.

No confidential Huawei data, proprietary code or restricted network measurements shall be used.

## 9. Evaluation Criteria

Each major component shall have measurable evaluation criteria.

| Component | Evaluation |
|---|---|
| Data ingestion | Validation accuracy, processing time |
| Anomaly detection | Precision, recall, F1-score |
| Forecasting | MAE, RMSE |
| Document retrieval | Recall@K, MRR, nDCG |
| RAG | Faithfulness, answer relevance, citation correctness |
| Incident diagnosis | Top-1 and Top-3 accuracy, evidence coverage |
| Agent workflow | Task completion rate, tool failure rate |
| Application | Latency, reliability, test coverage |

All reported results must come from actual experiments.

## 10. Project Scope and Limitations

### Included

- Network data processing and analytics.
- Machine learning-based network analysis.
- Telecom RAG.
- AI-assisted incident investigation.
- Experimental 5G NR analysis.
- Simplified network simulation.
- Interactive application and evaluation framework.

### Excluded

- Direct control of commercial mobile networks.
- Live telecom network configuration changes.
- Access to confidential operator data.
- Full-scale commercial 5G network simulation.
- Paid LLM APIs as mandatory dependencies.

The platform is intended as an engineering and research prototype, not a replacement for commercial network management systems.

## 11. Expected Deliverables

1. Public GitHub repository with organised source code.
2. Documented and tested data engineering pipeline.
3. Network KPI analytics application.
4. Anomaly detection and forecasting models.
5. Telecom document retrieval and RAG system.
6. AI-assisted incident investigation workflow.
7. 5G NR experimental module.
8. Network simulation module.
9. Reproducible evaluation and benchmark reports.
10. Streamlit application and FastAPI backend.
11. Technical documentation and architecture diagrams.
12. Demonstration of the completed platform.

## 12. Definition of Success

The project will be considered successful when the major components work together in a unified application, the core functionality is covered by automated tests, the AI and ML components have reproducible evaluation results, and the complete system can be demonstrated using documented public or synthetic data.
