# API and Application Design

## 1. Purpose

The RAN Intelligence Platform will provide a web interface where engineers can explore network measurements, monitor KPIs, investigate incidents and run simulation experiments.

The application will use two main parts:

- **FastAPI:** Handles backend requests and connects the platform's processing modules.
- **Streamlit:** Provides the user interface.

The separation allows the analytical modules to be used independently of the interface. It also makes it easier to test the backend and potentially introduce another interface in the future.

## 2. Application Architecture

The initial application architecture will look like this:

```text
                 Engineer
                    |
                    v
              Streamlit App
                    |
                    v
               FastAPI
                    |
       +------------+-------------+
       |            |             |
       v            v             v
  Data Services  Analytics     RAG Services
       |            |             |
       v            v             v
  Data Storage   ML Models    Document Index
       |            |             |
       +------------+-------------+
                    |
                    v
             Investigation Agent
                    |
                    v
              Report Service
```

The Streamlit application will communicate with FastAPI through HTTP requests.

FastAPI will validate incoming requests, invoke the appropriate services and return structured responses.

The backend should not contain business logic directly inside API route functions. Routes should call the relevant service modules.

## 3. Technology Choices

| Component | Technology | Purpose |
|---|---|---|
| Frontend | Streamlit | Web interface |
| Backend | FastAPI | API and service coordination |
| API validation | Pydantic | Request and response schemas |
| Data processing | Pandas, NumPy | Data handling |
| Database | SQLite initially | Structured metadata and results |
| Analytics | Scikit-learn, XGBoost, PyTorch | ML and statistical analysis |
| RAG | Sentence Transformers, FAISS, BM25 | Document retrieval |
| Agent workflow | LangGraph | Incident investigation |
| Visualisation | Plotly | Interactive charts |
| Testing | Pytest | Automated testing |

We will begin with a small and manageable setup. Additional infrastructure should only be introduced when there is a clear reason.

## 4. Main Application Pages

The Streamlit application should be organised around the tasks an engineer wants to perform.

### 4.1 Overview Dashboard

The landing page should provide a summary of the available network data.

It may display:

- Number of available cells.
- Number of available measurements.
- Latest measurement timestamp.
- Average throughput.
- Average SINR.
- Current anomaly count.
- Recent investigation reports.

The displayed values should come from the selected dataset, not static example numbers.

### 4.2 Network Data Explorer

This page will allow users to inspect available network measurements.

Features:

- Select a dataset.
- Select one or more cells.
- Choose a time range.
- Select KPIs.
- View measurement tables.
- Inspect missing values and data quality.
- Download filtered results where appropriate.

This page will also help users understand the data before running more advanced analysis.

### 4.3 KPI Monitoring

This page will focus on network performance.

Users should be able to:

- Select a cell.
- Select a KPI.
- Choose an aggregation interval.
- View KPI trends.
- Compare cells.
- Compare selected periods.
- Inspect KPI distributions.

Plotly will be used for interactive charts.

### 4.4 Anomaly Detection

This page will allow users to run and inspect anomaly detection.

Possible controls:

- Select a dataset.
- Select a cell or group of cells.
- Choose the KPI or feature set.
- Select an anomaly detection method.
- Configure relevant parameters.

The output should show detected anomalies, timestamps, affected KPIs and anomaly scores where available.

### 4.5 KPI Forecasting

This page will allow users to generate forecasts for selected network KPIs.

Users should be able to:

- Select a cell.
- Select a KPI.
- Choose a forecasting method.
- Specify the forecast horizon.
- View historical measurements and predicted values.
- Inspect model evaluation results.

Forecasts should be visually distinguishable from observed measurements.

### 4.6 Telecom Knowledge Assistant

This page will provide a question-and-answer interface for technical telecom documentation.

Users should be able to ask questions about 3GPP, O-RAN, radio performance and other indexed material.

Answers should include:

- A concise explanation.
- Supporting document passages.
- Source titles and metadata.
- Links to original documents where available.

The interface should clearly indicate when the knowledge base does not contain enough information to answer a question.

### 4.7 Incident Investigation

This will be one of the main application pages.

An engineer should be able to describe an incident and submit it for investigation.

The page should display:

- Original incident request.
- Parsed incident details.
- Selected cell and time window.
- Investigation progress and status.
- KPI findings.
- Anomaly results.
- Historical and neighbouring-cell comparisons.
- Retrieved technical references.
- Candidate explanations.
- Final investigation report.

The engineer should be able to inspect the evidence behind each finding.

### 4.8 Network Simulation Lab

This page will provide access to the simulation environment.

Users should be able to configure selected parameters, execute scenarios and compare results.

Initial controls may include:

- Number of base stations.
- Number of users.
- Traffic profile.
- Interference level.
- Scheduling strategy.
- Simulation duration.

Later versions can include more advanced beamforming and backhaul delay experiments.

### 4.9 5G NR Research Lab

This page will provide a dedicated interface for advanced wireless experiments.

Possible experiments:

- Beamforming comparison.
- Coordinated versus uncoordinated transmission.
- Scheduling policy comparison.
- Backhaul delay experiments.
- Prediction-assisted coordination.

Results should include relevant metrics such as sum rate, user throughput and 5th-percentile throughput.

The research lab should remain clearly separated from the general KPI monitoring workflow.

## 5. API Design

The FastAPI backend will expose endpoints grouped by function.

The initial API design is described below. Endpoint names may change during implementation as the request and response schemas become clearer.

### 5.1 Health and System Information

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Check whether the API is running |
| GET | `/api/v1/system/info` | Return available platform information |

### 5.2 Data Management

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/datasets` | List available datasets |
| POST | `/api/v1/datasets/upload` | Upload a dataset |
| GET | `/api/v1/datasets/{dataset_id}` | Retrieve dataset metadata |
| GET | `/api/v1/datasets/{dataset_id}/quality` | Retrieve data quality results |
| GET | `/api/v1/datasets/{dataset_id}/measurements` | Query network measurements |

### 5.3 KPI Analytics

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/kpis/summary` | Retrieve KPI summary |
| GET | `/api/v1/kpis/trends` | Retrieve KPI time series |
| GET | `/api/v1/kpis/compare` | Compare cells or time periods |

### 5.4 Anomaly Detection

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/v1/anomalies/run` | Run anomaly detection |
| GET | `/api/v1/anomalies/results/{run_id}` | Retrieve detection results |

### 5.5 Forecasting

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/v1/forecast/run` | Generate a KPI forecast |
| GET | `/api/v1/forecast/results/{run_id}` | Retrieve forecast results |

### 5.6 Telecom RAG

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/v1/rag/query` | Ask a telecom question |
| GET | `/api/v1/rag/documents` | List indexed documents |

### 5.7 Incident Investigation

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/v1/incidents` | Submit a new investigation |
| GET | `/api/v1/incidents` | List investigations |
| GET | `/api/v1/incidents/{incident_id}` | Retrieve investigation details |
| GET | `/api/v1/incidents/{incident_id}/report` | Retrieve the final report |

### 5.8 Simulation

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/v1/simulation/run` | Execute a simulation |
| GET | `/api/v1/simulation/results/{run_id}` | Retrieve simulation results |
| GET | `/api/v1/simulation/scenarios` | List available scenarios |

These endpoints describe the intended interface. We do not need to implement all of them at once.

## 6. Request and Response Structure

API requests and responses should use consistent JSON structures.

For example, an anomaly detection request could look like this:

```json
{
  "dataset_id": "aerpaw_sample",
  "cell_id": "CELL_001",
  "kpi": "sinr_db",
  "method": "isolation_forest",
  "parameters": {
    "contamination": 0.03
  }
}
```

A simplified response could look like this:

```json
{
  "run_id": "anomaly_001",
  "status": "completed",
  "cell_id": "CELL_001",
  "method": "isolation_forest",
  "anomaly_count": 12,
  "results_available": true
}
```

These are illustrative examples. Actual fields will be defined using Pydantic models during implementation.

Responses should also handle errors consistently.

For example:

```json
{
  "error": {
    "code": "DATASET_NOT_FOUND",
    "message": "The requested dataset was not found."
  }
}
```

## 7. Backend Service Structure

API routes should remain separate from the underlying processing logic.

A possible structure is:

```text
src/
└── ran_intelligence/
    ├── ingestion/
    ├── data_quality/
    ├── kpi_analytics/
    ├── anomaly_detection/
    ├── forecasting/
    ├── retrieval/
    ├── agents/
    ├── diagnosis/
    ├── simulation/
    └── reporting/

app/
├── api/
│   ├── main.py
│   ├── dependencies.py
│   ├── routes/
│   │   ├── health.py
│   │   ├── datasets.py
│   │   ├── kpis.py
│   │   ├── anomalies.py
│   │   ├── forecasting.py
│   │   ├── rag.py
│   │   ├── incidents.py
│   │   └── simulation.py
│   └── schemas/
│       ├── common.py
│       ├── datasets.py
│       ├── analytics.py
│       ├── incidents.py
│       └── simulation.py
│
└── streamlit_app/
    ├── main.py
    ├── pages/
    ├── components/
    └── services/
```

The `src/ran_intelligence/` modules should contain reusable platform logic.

The API layer should validate requests and call these modules.

The Streamlit service layer should handle communication with the backend rather than embedding HTTP requests throughout every page.

## 8. Data Storage

The initial application will use SQLite for structured metadata and results.

Possible entities include:

- Datasets.
- Dataset metadata.
- Ingestion runs.
- Analysis runs.
- Forecast runs.
- Anomaly detection results.
- Incident investigations.
- Simulation runs.
- Experiment configurations.

Large measurement files, document collections and model artifacts do not need to be stored directly inside SQLite.

They can remain in organised local directories, with metadata and file references stored in the database.

If the application later requires multiple concurrent users or more complex database operations, we can consider PostgreSQL.

## 9. Application Configuration

Configuration should be kept separate from application code.

Examples include:

- Database location.
- Dataset directory.
- Model directory.
- Document index location.
- API host and port.
- Logging level.
- Local model configuration.

Sensitive values should be stored in environment variables rather than committed to GitHub.

A `.env.example` file should document the required configuration without containing real secrets.

The application should have sensible defaults for local development.

## 10. Error Handling and Logging

The backend should return useful error messages when a request fails.

Examples:

- Dataset not found.
- Invalid cell identifier.
- Unsupported file format.
- Missing required KPI.
- Model unavailable.
- Document index not found.
- Simulation configuration invalid.

Logs should capture important events such as:

- API requests.
- Data ingestion.
- Model execution.
- Agent tool calls.
- Failed operations.
- Execution duration.

Logs should avoid unnecessary sensitive information and should not expose credentials or private data.

## 11. Security Considerations

Even though the initial application is intended for local and portfolio use, basic security practices should be followed.

These include:

- Validate uploaded files and input parameters.
- Restrict accepted file types and file sizes.
- Avoid executing uploaded code.
- Use parameterised database queries.
- Keep secrets outside the repository.
- Restrict file access to approved application directories.
- Avoid exposing unrestricted internal tool access to the agent.
- Apply appropriate request limits.

The initial public demo should use non-sensitive public or synthetic data.

It should not connect to a live operator network.

## 12. Local Development and Deployment

The first version should run locally.

A typical development setup will involve:

- Starting the FastAPI backend.
- Starting the Streamlit application.
- Loading a sample dataset.
- Running tests.

Docker can later be used to package the backend, interface and supporting services.

The public demo, if deployed, should use free hosting where practical and should not depend on a paid model API.

If local model inference is too resource-intensive for the free hosting environment, the demo can use precomputed results or a limited set of available features.

We should not promise that every advanced feature will run continuously on free hosting.

## 13. Implementation Order

The application will be developed incrementally.

**Stage 1 — FastAPI foundation**

Create the application, health endpoint and basic configuration.

**Stage 2 — Streamlit foundation**

Create the landing page and navigation.

**Stage 3 — Data endpoints**

Connect dataset listing, upload, inspection and quality reports.

**Stage 4 — KPI endpoints**

Connect KPI summaries, trends and comparisons.

**Stage 5 — ML endpoints**

Connect anomaly detection and forecasting.

**Stage 6 — RAG interface**

Connect document search and question answering.

**Stage 7 — Incident investigation**

Connect the LangGraph workflow and report generation.

**Stage 8 — Simulation interface**

Connect simulation configuration, execution and result visualisation.

**Stage 9 — Integration and testing**

Test the complete application and handle failures across components.

**Stage 10 — Deployment**

Prepare local Docker execution and evaluate free public demo options.

## 14. Expected Outcome

The application should provide a single interface for exploring network data, analysing performance, retrieving telecom knowledge, investigating incidents and running simulation experiments.

FastAPI will keep the backend modular, while Streamlit will provide a straightforward interface without requiring a separate frontend development stack.

The result should be easy to run locally, test and demonstrate to potential employers.
