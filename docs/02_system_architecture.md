# RAN Intelligence Platform
## System Architecture

## 1. Overview

RAN Intelligence will use a modular architecture built primarily with Python. The application will combine network data processing, analytics, machine learning, document retrieval and AI-assisted incident investigation.

The aim is to keep the different parts independent enough to develop and test separately, while allowing them to work together through shared data and application services.

The user interface will be built with Streamlit. FastAPI will provide the backend API, while the main processing and AI functionality will live in separate Python modules.

During development, the system will run locally or through Google Colab for individual experiments. GitHub will be used to maintain the source code and documentation.

## 2. High-Level Architecture

The system is organised into six main layers:

1. **Data sources:** Network measurements, event records, technical documents and configuration data.
2. **Data processing:** Importing, validation, cleaning, transformation and storage.
3. **Analytics and machine learning:** KPI analysis, anomaly detection and forecasting.
4. **Knowledge retrieval:** Document processing, embeddings, hybrid search and reranking.
5. **Investigation and simulation:** AI-assisted incident analysis, evidence collection and network experiments.
6. **Application interface:** Dashboards, document search, incident investigation and reporting.

These layers are logical parts of the application. They do not necessarily need to run as separate services.

## 3. Architecture Components

### 3.1 User Interface — Streamlit

Streamlit will provide the main interface for users.

It will contain separate sections for:

- Network overview and KPI dashboards.
- Dataset upload and data quality results.
- Anomaly detection and forecasting.
- Telecom document search.
- AI-assisted incident investigation.
- 5G NR experiments and simulation.
- Evaluation results and reports.

The interface will focus on presenting results and collecting user inputs. The underlying data processing and model logic will remain outside the UI code.

### 3.2 Backend API — FastAPI

FastAPI will expose the main application functionality through API endpoints.

Its responsibilities will include:

- Receiving requests from the user interface.
- Handling dataset uploads and incident submissions.
- Calling the appropriate application services.
- Returning analysis results.
- Managing request validation and errors.

The API will also make it easier to test the application independently of Streamlit.

### 3.3 Data Ingestion and Storage

This component will handle the network data used throughout the application.

The initial pipeline will support structured files such as CSV.

The processing workflow will include:

1. Loading the source data.
2. Checking the expected columns and data types.
3. Identifying missing, duplicate and invalid records.
4. Cleaning and transforming the data.
5. Storing the processed measurements.
6. Recording basic information about the dataset and ingestion process.

SQLite will be used initially to keep development simple. PostgreSQL can be introduced when the application requires more advanced database functionality or concurrent access.

FAISS will be used separately for local vector search in the document retrieval module.

### 3.4 Analytics and Machine Learning

The analytics layer will operate on the processed network measurements.

It will contain separate modules for:

- KPI calculations and statistical summaries.
- Cell-level and time-based comparisons.
- Anomaly detection.
- KPI forecasting.
- Model evaluation.

Scikit-learn and XGBoost will be used for the initial machine learning experiments. PyTorch will be introduced where deep learning models are appropriate.

The models will be developed and evaluated independently before being connected to the main application.

### 3.5 Telecom Knowledge Retrieval

The retrieval component will manage telecom documents and provide relevant information to the application.

Its workflow will include:

1. Loading technical documents.
2. Extracting and cleaning their text.
3. Splitting documents into searchable passages.
4. Generating embeddings using Sentence Transformers.
5. Building a vector index using FAISS.
6. Implementing keyword retrieval using BM25.
7. Combining retrieval results.
8. Reranking the retrieved passages.
9. Passing selected context to a language model.

The generation component will use a configurable local language model where practical. Answers should include references to the documents and passages used.

### 3.6 Incident Investigation Agent

The investigation agent will coordinate the different components when an engineer submits an incident.

LangGraph will be considered for managing the workflow and its state.

The agent will have access to controlled application tools, such as:

- Retrieve network measurements.
- Calculate KPI summaries.
- Compare cell performance.
- Retrieve detected anomalies.
- Generate or retrieve forecasts.
- Search telecom documentation.
- Run selected simulation experiments.

The agent will use these tools to collect information before preparing its findings.

The output will contain the incident summary, observed evidence, possible explanations, supporting references and suggested next steps.

The agent will not directly modify network configurations or control live network equipment.

### 3.7 Simulation and 5G NR Experiments

This component will contain independent experiments for selected wireless network scenarios.

It will support work on beamforming, interference, scheduling, cell association and backhaul delay.

The simulation code will be separated from the general analytics and AI components. This will allow experiments to be run and evaluated without depending on the complete application.

Where relevant, experiment results can later be made available to the investigation workflow.

### 3.8 Evaluation and Monitoring

Evaluation will be implemented as a separate part of the project.

It will measure:

- Data processing quality.
- Anomaly detection performance.
- Forecasting errors.
- Retrieval quality.
- RAG answer quality and citation correctness.
- Incident investigation performance.
- Application latency and reliability.

Evaluation scripts should be runnable independently so that model improvements can be compared against earlier baselines.

## 4. Data Flow

The main data flow will follow this sequence:

1. Network measurements and technical documents are imported.
2. Measurements are validated, transformed and stored.
3. Processed network data becomes available to the analytics modules.
4. The analytics modules calculate KPIs, detect anomalies and generate forecasts.
5. Technical documents are processed and indexed for retrieval.
6. An engineer submits an incident through the application.
7. The investigation workflow retrieves relevant measurements, analytical results and technical information.
8. The agent collects evidence and prepares possible explanations.
9. The application displays the findings and allows the engineer to review them.
10. The investigation can be exported as a report.

Not every incident will require every component. The investigation workflow should select the tools relevant to the problem.

## 5. Main Incident Investigation Workflow

An example investigation could start with an alert about declining throughput in a particular cell.

The system would:

1. Identify the affected cell and time period.
2. Retrieve the corresponding measurements.
3. Check whether the available data is complete and valid.
4. Examine throughput, SINR, BLER, PRB utilisation and other relevant KPIs.
5. Compare the affected cell with its historical performance and neighbouring cells where data is available.
6. Check whether the anomaly detection module has identified unusual behaviour.
7. Search technical documentation for relevant explanations.
8. Collect additional evidence through available investigation tools.
9. Rank possible explanations according to the evidence.
10. Generate a report for engineering review.

The system should not claim that a particular issue is the confirmed root cause unless the available evidence supports that conclusion.

## 6. Proposed Backend Structure

The backend will be organised into separate Python packages.

| Module | Responsibility |
|---|---|
| ingestion | Importing network measurements and documents |
| data_quality | Data validation and cleaning |
| kpi_analytics | KPI calculations and analysis |
| anomaly_detection | Detecting unusual network behaviour |
| forecasting | Predicting selected network KPIs |
| retrieval | Document indexing and search |
| embeddings | Generating document embeddings |
| reranking | Ranking retrieved passages |
| generation | Language model interaction |
| agents | Investigation workflow |
| diagnosis | Incident analysis and reporting |
| simulation | Network experiments |
| evaluation | Model and system evaluation |
| reporting | Generating investigation reports |

The modules will be developed independently and connected through application services.

## 7. Database and Storage Design

The initial database will store the information needed for the core application.

The main entities are expected to include:

- **Dataset:** Information about imported datasets.
- **Cell:** Cell identifiers and available configuration information.
- **Measurement:** Time-based network KPI measurements.
- **Incident:** Submitted incident descriptions and affected cells.
- **Anomaly:** Detected abnormal observations.
- **Forecast:** Model predictions and their associated time periods.
- **Investigation:** Investigation status and summary.
- **Evidence:** Measurements, retrieved passages and other information used during an investigation.
- **Document:** Metadata about indexed telecom documents.

The exact database schema and relationships will be defined separately in the data design document.

Document files, model artefacts and vector indexes may be stored separately from the relational database.

## 8. API Design

FastAPI will expose endpoints for the main application operations.

The initial endpoint groups are:

| Endpoint | Purpose |
|---|---|
| `/health` | Check application status |
| `/datasets` | Upload and list datasets |
| `/measurements` | Retrieve network measurements |
| `/kpis` | Calculate and retrieve KPI summaries |
| `/anomalies` | Run or retrieve anomaly detection results |
| `/forecasts` | Generate KPI forecasts |
| `/documents` | Upload and manage documents |
| `/search` | Search telecom documentation |
| `/incidents` | Create and retrieve incidents |
| `/investigations` | Start and retrieve investigations |
| `/reports` | Generate investigation reports |

Request formats, response structures and error handling will be specified when these endpoints are implemented.

## 9. Development and Deployment Environment

The project will be developed using Python and Google Colab where appropriate.

GitHub will be the central repository for source code, notebooks, documentation, tests and experiment configurations.

The intended application environment will use:

- Streamlit for the interface.
- FastAPI for backend services.
- SQLite initially, with PostgreSQL as a possible later addition.
- Local model inference through Ollama where supported.
- Docker for packaging and reproducible execution.

The public demonstration will use free hosting where feasible. Since free hosting environments have resource limitations, some computationally expensive models may need to run locally, while the hosted application can demonstrate selected functionality using lightweight models or precomputed results.

## 10. Testing Strategy

Each module will have its own tests.

The testing process will include:

- Unit tests for individual functions.
- Data validation tests.
- Integration tests between application modules.
- API tests.
- Retrieval and generation evaluation.
- End-to-end tests for the incident investigation workflow.

Pytest will be used as the main testing framework.

The goal is to catch problems at the module level before integrating everything into the application.

## 11. Architecture Decisions

The architecture will be kept simple during the initial development stages.

A modular monolithic application will be used instead of starting with microservices. This avoids unnecessary deployment and maintenance complexity for a single-developer project.

Streamlit and FastAPI will have separate responsibilities, while the core business logic will remain in reusable Python modules.

SQLite will be preferred initially because it requires little setup. More advanced infrastructure will only be introduced when there is a clear need.

Local and open-source models will be preferred to avoid dependence on paid APIs.

These decisions can be revised as the project develops. Significant changes will be recorded with their reasons and trade-offs.

## 12. Known Limitations

The initial version will use public and synthetic datasets rather than live operator network data.

The quality of anomaly detection, forecasting and incident investigation will depend on the available data and evaluation scenarios.

The network simulation component will represent selected wireless behaviours rather than a complete commercial network.

Local language model performance will depend on available hardware and model size.

These limitations will be considered when evaluating and presenting the results.
