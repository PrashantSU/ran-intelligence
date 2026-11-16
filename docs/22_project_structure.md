# Project Structure

## 1. Purpose

This document defines how the RAN Intelligence Platform repository will be organised.

The project contains several connected components, so a clear structure is important. Data processing, machine learning, telecom retrieval, incident investigation and simulation should remain separate modules while sharing common data models and services.

The structure should also make it possible to develop and test individual components without running the entire application.

We will use a Python-based modular architecture, with Streamlit for the user interface and FastAPI for the backend.

## 2. Repository layout

The planned repository structure is:

```text
ran-intelligence/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── pages/
│       ├── dashboard.py
│       ├── data_explorer.py
│       ├── anomaly_detection.py
│       ├── forecasting.py
│       ├── telecom_assistant.py
│       ├── incident_investigation.py
│       ├── simulation_lab.py
│       ├── nr_intelligence_lab.py
│       └── experiments.py
│
├── backend/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── routes/
│   │   ├── schemas/
│   │   └── dependencies.py
│   ├── core/
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── exceptions.py
│   └── services/
│
├── src/
│   └── ran_intelligence/
│       ├── __init__.py
│       │
│       ├── common/
│       │   ├── config.py
│       │   ├── constants.py
│       │   ├── exceptions.py
│       │   └── schemas/
│       │
│       ├── data_engineering/
│       │   ├── ingestion/
│       │   ├── validation/
│       │   ├── cleaning/
│       │   ├── transformation/
│       │   └── storage/
│       │
│       ├── analytics/
│       │   ├── kpis/
│       │   ├── aggregation/
│       │   └── comparison/
│       │
│       ├── ml/
│       │   ├── anomaly_detection/
│       │   ├── forecasting/
│       │   ├── features/
│       │   └── evaluation/
│       │
│       ├── rag/
│       │   ├── ingestion/
│       │   ├── extraction/
│       │   ├── chunking/
│       │   ├── embeddings/
│       │   ├── indexing/
│       │   ├── retrieval/
│       │   ├── reranking/
│       │   ├── generation/
│       │   └── evaluation/
│       │
│       ├── agents/
│       │   ├── state.py
│       │   ├── graph.py
│       │   ├── nodes/
│       │   ├── tools/
│       │   └── reporting/
│       │
│       ├── simulation/
│       │   ├── topology/
│       │   ├── channel/
│       │   ├── traffic/
│       │   ├── scheduling/
│       │   ├── beamforming/
│       │   ├── interference/
│       │   └── evaluation/
│       │
│       ├── nr_lab/
│       │   ├── scenarios/
│       │   ├── channel_prediction/
│       │   ├── coordinated_beamforming/
│       │   ├── resource_scheduling/
│       │   └── experiments/
│       │
│       ├── evaluation/
│       │   ├── benchmarks/
│       │   ├── metrics/
│       │   └── reports/
│       │
│       └── services/
│
├── data/
│   ├── raw/
│   ├── interim/
│   ├── processed/
│   ├── synthetic/
│   ├── external/
│   └── metadata/
│
├── notebooks/
│   ├── 01_data_exploration/
│   ├── 02_data_engineering/
│   ├── 03_kpi_analytics/
│   ├── 04_anomaly_detection/
│   ├── 05_forecasting/
│   ├── 06_rag/
│   ├── 07_incident_investigation/
│   ├── 08_simulation/
│   └── 09_nr_intelligence_lab/
│
├── experiments/
│   ├── anomaly_detection/
│   ├── forecasting/
│   ├── retrieval/
│   ├── diagnosis/
│   └── simulation/
│
├── configs/
│   ├── data/
│   ├── models/
│   ├── rag/
│   ├── simulation/
│   └── application/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── api/
│   ├── evaluation/
│   └── fixtures/
│
├── scripts/
│   ├── download_data.py
│   ├── prepare_data.py
│   ├── build_knowledge_base.py
│   └── run_experiment.py
│
├── docs/
│
├── reports/
│   ├── figures/
│   ├── tables/
│   └── experiment_reports/
│
├── .github/
│   └── workflows/
│
├── .env.example
├── .gitignore
├── pyproject.toml
├── README.md
├── Dockerfile
└── docker-compose.yml
```

This is the planned full structure. Directories and files will be created as their components are implemented rather than creating hundreds of empty files at the beginning.

## 3. Main application

The `app/` directory contains the Streamlit interface.

Each page has a specific purpose:

| Page | Responsibility |
|---|---|
| Dashboard | Overall network health and KPI overview |
| Data Explorer | Inspect datasets and measurements |
| Anomaly Detection | Explore detected anomalies |
| Forecasting | View future KPI estimates |
| Telecom Assistant | Ask questions about technical documentation |
| Incident Investigation | Run evidence-based investigations |
| Simulation Lab | Run network what-if experiments |
| NR Intelligence Lab | Explore advanced 5G NR experiments |
| Experiments | Compare recorded experiment results |

The pages should call backend services rather than implementing core ML or data-processing logic themselves.

## 4. Backend

The `backend/` directory contains the FastAPI application.

Its responsibilities include:

- Exposing API endpoints.
- Validating incoming requests.
- Returning structured responses.
- Connecting application pages to the underlying services.
- Handling errors and application configuration.

The API should not contain large amounts of business logic. That logic belongs in the corresponding modules under `src/ran_intelligence/`.

## 5. Core Python package

The `src/ran_intelligence/` directory contains the main application logic.

This is the central part of the project.

### Common

Contains shared schemas, configuration, constants and exceptions.

### Data engineering

Handles ingestion, validation, cleaning, transformation and storage.

### Analytics

Contains KPI calculations, aggregation and comparisons between cells or time periods.

### Machine learning

Contains anomaly detection, forecasting, feature engineering and model evaluation.

### RAG

Handles document extraction, chunking, embeddings, indexing, retrieval, reranking and answer generation.

### Agents

Contains the LangGraph investigation workflow, its state, nodes, approved tools and report generation.

### Simulation

Contains the general RAN simulation environment, including topology, traffic, channel, scheduling and interference.

### NR Lab

Contains more specialised 5G NR experiments, including coordinated beamforming, channel prediction and resource scheduling.

### Evaluation

Provides shared metrics, benchmarks and evaluation reports.

### Services

Provides reusable interfaces that connect application components where appropriate.

## 6. Data organisation

The `data/` directory separates datasets according to their processing stage.

| Directory | Contents |
|---|---|
| `raw/` | Original downloaded datasets |
| `interim/` | Data undergoing processing |
| `processed/` | Validated and transformed datasets |
| `synthetic/` | Independently generated network data |
| `external/` | Additional external datasets |
| `metadata/` | Dataset descriptions, versions and source information |

Large datasets should not be committed to GitHub.

The repository should contain download scripts, dataset descriptions and small examples where licensing permits.

## 7. Notebooks

The `notebooks/` directory is intended for exploration and experimentation.

Google Colab can be used for notebooks that require more computing resources.

Notebooks will help us:

- Inspect public datasets.
- Test preprocessing approaches.
- Explore KPI relationships.
- Compare ML models.
- Evaluate retrieval configurations.
- Experiment with network simulation.
- Investigate advanced NR scenarios.

Once an approach becomes stable, reusable logic should be moved into the Python package.

The application should not depend on executing research notebooks.

## 8. Experiments and configurations

The `experiments/` directory stores experiment configurations and result summaries.

The `configs/` directory stores reusable settings for:

- Data processing.
- Machine learning models.
- RAG retrieval and generation.
- Network simulation.
- Application behaviour.

Separating configuration from implementation makes it easier to compare experiments without repeatedly changing source code.

## 9. Tests

The `tests/` directory mirrors the main testing responsibilities.

- `unit/`: Individual functions and modules.
- `integration/`: Interactions between components.
- `api/`: FastAPI endpoint behaviour.
- `evaluation/`: Model, retrieval and diagnostic evaluation checks.
- `fixtures/`: Reusable test datasets and sample inputs.

Tests should be added as each component is implemented.

## 10. Scripts

The `scripts/` directory contains reusable command-line entry points.

Examples include:

- Downloading public datasets.
- Preparing and validating measurements.
- Building the telecom knowledge base.
- Running experiments.

Scripts should call functions from the main Python package rather than duplicating implementation logic.

## 11. Reports and documentation

The `reports/` directory contains generated figures, tables and experiment reports.

The `docs/` directory contains project requirements, architecture, data definitions, implementation plans, design decisions and technical documentation.

Generated reports should identify the dataset, experiment and code version used to produce them.

## 12. Dependency management

The project will use `pyproject.toml` to manage Python dependencies and development tools.

Dependencies should be grouped logically where practical:

- Core application dependencies.
- Machine learning dependencies.
- RAG and LLM dependencies.
- Development and testing dependencies.

We should avoid installing every possible library at the beginning. Dependencies will be added when their corresponding components are implemented.

## 13. Git and generated files

Git should track source code, documentation, configurations, tests and small reproducible examples.

It should generally exclude:

- Virtual environments.
- `.env` files.
- Large raw datasets.
- Model checkpoints.
- Temporary files.
- Python cache files.
- Generated vector indexes.
- Large experiment artefacts.

The `.gitignore` file will define these exclusions.

## 14. Architectural rules

The following rules will keep the repository maintainable:

1. Streamlit pages should not contain core model implementations.
2. API routes should delegate work to application services.
3. Shared data structures should be defined in common schemas.
4. Data processing should be reusable outside notebooks.
5. ML models should have separate training and inference logic.
6. RAG retrieval and generation should remain independently testable.
7. Agent tools should call approved application services.
8. Simulation assumptions should be configurable and documented.
9. Evaluation code should be reusable across experiments.
10. Components should have clear interfaces rather than depending on unrelated internal modules.

## 15. Implementation approach

We will build the repository progressively.

The first implementation stage will create the Python package, application entry points, configuration, tests and basic data directories.

As each major component is developed, its corresponding modules, notebooks, configurations and tests will be added.

The final repository should reflect a working platform, not simply a large collection of empty folders.

The structure may evolve during development, but significant architectural changes should be documented.
