# RAN Intelligence Platform
## Project Requirements

## 1. Introduction

RAN Intelligence is a project focused on analysing and understanding the performance of mobile radio access networks (RAN). The idea is to bring network data analysis, machine learning and generative AI together in one application that can help engineers investigate network performance issues.

Mobile networks produce large amounts of measurement data, configuration information and event logs. Understanding a performance issue often requires looking at several sources of information and comparing measurements over time.

This project aims to make that process easier. It will provide tools for exploring network performance, detecting unusual behaviour, forecasting selected KPIs and searching technical documentation. It will also include an AI-assisted investigation workflow that combines measurement data with information retrieved from telecom documentation.

The project will cover both general RAN analytics and selected 5G NR research topics, including coordinated beamforming and prediction-assisted scheduling.

## 2. Main Goals

The main goals of the project are:

- Build a data pipeline for importing, validating and processing network measurements.
- Analyse important radio and network performance indicators.
- Apply machine learning to anomaly detection and KPI forecasting.
- Develop a RAG system for searching telecom standards, technical documents and research papers.
- Build an AI-assisted workflow for investigating network incidents.
- Explore selected 5G NR problems through simulations and experiments.
- Evaluate the different components using reproducible experiments.
- Bring the functionality together in an interactive application.

The emphasis will be on building working components and evaluating their results, rather than simply demonstrating the use of different AI frameworks.

## 3. Intended Users

The application is primarily intended for:

- RAN and radio network engineers.
- Network performance and optimisation engineers.
- Telecom data scientists.
- Machine learning engineers working with network data.
- Researchers working on wireless communication systems.

The main use case is an engineer who wants to understand why a cell or group of cells is experiencing degraded performance.

## 4. Functional Requirements

### 4.1 Network Data Ingestion and Processing

The application should be able to import network measurements from structured files, initially using CSV.

The ingestion pipeline will handle:

- Reading and validating incoming data.
- Identifying missing, duplicate and invalid records.
- Converting measurements into consistent formats.
- Applying basic data quality checks.
- Storing processed data for further analysis.
- Keeping track of the source and processing history of datasets.

The initial implementation will use public and synthetic datasets.

### 4.2 Network KPI Analysis

The analytics module will focus on commonly used radio and network performance indicators, including:

- RSRP and RSRQ.
- SINR.
- Downlink and uplink throughput.
- CQI and MCS.
- BLER.
- PRB utilisation.
- Retransmission rates.
- Cell availability and load.

Users should be able to explore KPI distributions, compare cells, inspect historical trends and identify periods of poor performance.

The results will be presented through interactive charts and tables.

### 4.3 Anomaly Detection

This module will investigate how machine learning can identify unusual behaviour in network measurements.

The initial work will focus on detecting abnormal KPI values and changes in network performance over time.

Different approaches will be compared, starting with simple statistical baselines and progressing to machine learning methods where useful.

The module should display detected anomalies, their scores and the measurements that contributed to the detection.

Performance will be evaluated using labelled test data wherever possible.

### 4.4 KPI Forecasting

This module will explore whether historical network measurements can be used to predict future KPI values.

The initial focus will be on forecasting selected indicators, such as throughput, SINR and cell load.

The implementation will compare suitable forecasting methods against simple baseline approaches.

Forecasts will be compared with actual measurements using standard error metrics. Prediction uncertainty will also be included where the chosen method supports it.

### 4.5 Telecom Document Search and RAG

A separate module will handle telecom technical documentation.

The document collection may include publicly accessible 3GPP specifications, ETSI documents, technical manuals and research publications.

The system will support:

- Document loading and text extraction.
- Text cleaning and chunking.
- Embedding generation.
- Semantic search.
- Keyword-based search.
- Hybrid retrieval.
- Reranking of retrieved passages.
- Answer generation using a local language model.
- References to the documents and passages used to generate an answer.

The quality of retrieval and generated answers will be evaluated using a prepared set of questions and relevant source documents.

### 4.6 AI-Assisted Incident Investigation

This is one of the central features of the project.

An engineer should be able to submit an incident description, identify an affected cell and provide a relevant time period.

The system will then collect information from the available modules. Depending on the incident, this may include:

1. Retrieving the relevant network measurements.
2. Checking data quality and KPI trends.
3. Looking for detected anomalies.
4. Comparing the affected cell with historical or neighbouring cell measurements.
5. Retrieving relevant technical documentation.
6. Generating possible explanations for the observed behaviour.
7. Collecting additional evidence through controlled investigation tools.
8. Producing a structured investigation report.

LangGraph will be considered for managing the multi-step investigation workflow.

The system is intended to assist engineers, not replace their judgement. It must distinguish between directly observed measurements, possible explanations and confirmed causes. A low SINR value, for example, should not automatically be treated as proof of interference.

### 4.7 5G NR Research and Experiments

This module will focus on selected wireless communication problems that can be studied through data analysis and simulation.

Planned topics include:

- Radio signal and interference analysis.
- Beamforming and antenna configuration.
- Radio resource scheduling.
- Cell association and load balancing.
- Coordinated beamforming.
- Prediction-assisted scheduling.
- The effect of backhaul delay on network performance.

The implementation will use independently generated or publicly available data. Experiments will be documented with their assumptions, configurations and results.

### 4.8 Network Simulation

The project will include a simplified simulation environment for studying selected network scenarios.

Users should be able to change certain parameters and examine how those changes affect simulated network performance.

Possible experiments include changes in cell load, interference conditions, scheduling decisions and backhaul delay.

These simulations will be designed for experimentation and comparison. They will not be presented as complete or fully accurate models of commercial 5G networks.

### 4.9 Evaluation and Reporting

Each major component should have its own evaluation procedure.

The application should also be able to produce structured reports containing relevant measurements, model outputs, retrieved references and investigation findings.

Evaluation results should be reproducible, and the methods used to obtain them should be documented.

## 5. Non-Functional Requirements

### Code Organisation

The code should be organised into separate modules with clearly defined responsibilities. Data processing, model logic, retrieval and application interfaces should not be mixed together unnecessarily.

### Reproducibility

Experiments should use documented configurations and fixed random seeds where appropriate. Evaluation results should be reproducible.

### Performance

The system should run on commonly available hardware where practical. Models and datasets should be selected with local resource limitations in mind.

### Reliability

Input validation and error handling should be included in the main workflows. Important functions should have automated tests.

### Security

API keys, passwords and other credentials must not be committed to the public repository. Uploaded files and external inputs should be validated.

### Maintainability

Dependencies, setup instructions, code structure and important implementation decisions should be documented.

### Cost

The project should be built using free and open-source tools. Paid APIs and subscriptions must not be required for the core functionality.

## 6. Technology Choices

The initial technology choices are:

| Area | Technology |
|---|---|
| Programming language | Python |
| Data processing | Pandas, NumPy |
| Database | SQLite initially, PostgreSQL where needed |
| Backend | FastAPI |
| User interface | Streamlit |
| Visualisation | Plotly |
| Machine learning | Scikit-learn, XGBoost |
| Deep learning | PyTorch |
| Embeddings | Sentence Transformers |
| Vector search | FAISS |
| Keyword retrieval | BM25 |
| RAG and agent workflows | LangChain, LangGraph |
| Local language models | Ollama |
| Testing | Pytest |
| Containerisation | Docker |
| Version control | Git and GitHub |

These are initial choices rather than fixed requirements. If a simpler or more suitable alternative becomes apparent during development, the decision will be documented.

## 7. Data Sources

The project will use two types of data:

**Public data:** Publicly accessible wireless network measurements, technical specifications, research papers and other relevant telecom resources.

**Synthetic data:** Generated network measurements and incident scenarios for testing the application, training selected models and evaluating the investigation workflow.

The source, licence and limitations of each dataset will be recorded. Synthetic data will be clearly labelled and will not be presented as real operator measurements.

No confidential Huawei data, internal source code or restricted company material will be included.

## 8. Evaluation Plan

The system will be evaluated at the level of individual components.

| Component | Evaluation metrics |
|---|---|
| Data processing | Validation results, processing time, invalid record rate |
| Anomaly detection | Precision, recall, F1-score |
| KPI forecasting | MAE, RMSE |
| Document retrieval | Recall@K, MRR, nDCG |
| RAG | Faithfulness, answer relevance, citation correctness |
| Incident investigation | Top-1/Top-3 accuracy, evidence coverage |
| Agent workflow | Task completion rate, tool failure rate |
| Application | Response time, reliability, test results |

Where possible, improved methods will be compared against simpler baselines. Results will be reported only after experiments have actually been performed.

## 9. Scope and Limitations

The project will focus on analysis, experimentation and decision support.

It will not:

- Control or modify a live commercial mobile network.
- Make automatic changes to network configurations.
- Use confidential operator datasets.
- Attempt to reproduce a complete commercial 5G network simulator.
- Depend on paid LLM APIs for its main functionality.

The AI-generated investigation results will be treated as recommendations that require engineering review.

## 10. Expected Outcome

The final outcome will be a Python-based application that brings together network data processing, KPI analytics, machine learning, telecom document retrieval and AI-assisted incident investigation.

The project will be hosted on GitHub with source code, technical documentation, experiments and evaluation results. A Streamlit interface will provide a way to demonstrate the main functionality.

The focus throughout development will be on making the individual components work together, documenting the implementation and measuring how well the system performs.
