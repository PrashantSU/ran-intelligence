# Project Roadmap

## 1. Purpose

This roadmap describes how the RAN Intelligence Platform will be developed, from the initial Python project setup to a working application with network analytics, telecom RAG, incident investigation and simulation capabilities.

The project is large enough that trying to implement everything at once would make development unnecessarily difficult.

We will build it in stages. Each stage should leave us with something that works and can be tested before we move on.

The roadmap is organised around deliverables rather than fixed calendar dates. The time required for each stage will depend on implementation complexity and the results of testing.

## 2. Development Strategy

The development will follow this order:

1. Establish the Python project and development environment.
2. Obtain and inspect real public RAN data.
3. Build the data ingestion and quality pipeline.
4. Implement KPI analytics and visualisation.
5. Add anomaly detection and forecasting.
6. Build the telecom document retrieval system.
7. Develop the incident investigation agent.
8. Build the network simulation environment.
9. Add advanced 5G NR research experiments.
10. Integrate everything into the Streamlit application.
11. Evaluate, document and prepare the public demonstration.

Some work can happen in parallel, but the main dependencies should be respected.

For example, the incident investigation agent needs working analytics and retrieval tools before it can provide meaningful results.

## 3. Phase 1 — Project Foundation

**Objective:** Establish a clean and reproducible development environment.

Tasks:

- Finalise the initial repository structure.
- Create `pyproject.toml`.
- Configure Python and virtual environment.
- Add core dependencies.
- Set up Ruff and Pytest.
- Add `.gitignore`.
- Add `.env.example`.
- Create basic logging and configuration modules.
- Configure GitHub Actions for basic checks.

Deliverables:

- A working Python project.
- Reproducible dependency installation.
- Basic automated tests.
- A documented development setup.

Completion criteria:

Another developer should be able to clone the repository, install its dependencies and run the initial tests.

## 4. Phase 2 — Data Acquisition and Ingestion

**Objective:** Build the first working data pipeline using public RAN measurements.

The initial dataset should be small enough to inspect and process without requiring specialised infrastructure.

The AERPAW Ericsson 5G dataset is a good starting point because it contains real radio and throughput measurements.

Tasks:

- Download and inspect the dataset.
- Record its source and usage terms.
- Understand its original schema.
- Map the available fields to the platform schema.
- Implement CSV ingestion.
- Add timestamp and data type handling.
- Validate missing and invalid values.
- Generate data quality reports.
- Save processed measurements.

Deliverables:

- A reproducible data loading process.
- A documented dataset schema.
- A processed sample dataset.
- Automated ingestion tests.

Completion criteria:

The platform should be able to load the selected public dataset, validate it and produce a structured output that can be used by the analytics modules.

## 5. Phase 3 — KPI Analytics and Dashboard

**Objective:** Make the ingested network measurements useful.

Tasks:

- Implement KPI summary calculations.
- Add cell-level filtering.
- Add time-based aggregation.
- Implement KPI trend analysis.
- Add basic cell comparisons.
- Create interactive Plotly charts.
- Build the first Streamlit dashboard.

Initial KPIs will depend on the fields actually available in the selected dataset.

We should not manufacture measurements for KPIs that the source does not contain.

Deliverables:

- KPI analytics module.
- Interactive network data explorer.
- KPI monitoring page.
- Unit tests for calculations.

Completion criteria:

An engineer should be able to select a dataset, inspect its measurements and explore the available KPI trends through the application.

## 6. Phase 4 — Anomaly Detection and Forecasting

**Objective:** Add predictive network analytics.

### Anomaly detection

Tasks:

- Build statistical threshold baselines.
- Implement Z-score and IQR detection.
- Add Isolation Forest.
- Generate controlled abnormal scenarios.
- Evaluate precision, recall and F1-score.
- Display detected anomalies in Streamlit.

### KPI forecasting

Tasks:

- Implement last-value and moving-average baselines.
- Add an appropriate statistical or ML model.
- Create chronological training and testing splits.
- Evaluate MAE and RMSE.
- Compare models across forecast horizons.
- Visualise historical and predicted values.

Deliverables:

- Anomaly detection module.
- Forecasting module.
- Evaluation scripts.
- Anomaly and forecasting dashboard pages.

Completion criteria:

The platform should detect controlled abnormal conditions and produce forecasts that can be compared against simple baselines.

We should only retain more complex models when their results justify the added complexity.

## 7. Phase 5 — Telecom Document Knowledge Base

**Objective:** Build a document retrieval system for technical telecom questions.

Tasks:

- Identify suitable public technical documents.
- Record document versions and source metadata.
- Implement document extraction.
- Implement chunking and metadata preservation.
- Generate embeddings.
- Build FAISS vector search.
- Implement BM25 retrieval.
- Combine retrieval results using reciprocal rank fusion.
- Add reranking.
- Preserve document references and source links.
- Create a retrieval evaluation dataset.

Deliverables:

- Document ingestion pipeline.
- Searchable telecom knowledge base.
- Hybrid retrieval system.
- Retrieval benchmark results.

Completion criteria:

A technical question should retrieve relevant passages from the indexed documents, with source information preserved.

The first version can work as a retrieval-only system before adding answer generation.

## 8. Phase 6 — RAG Question Answering

**Objective:** Turn the retrieval system into a grounded telecom knowledge assistant.

Tasks:

- Select a suitable local language model.
- Connect retrieved passages to the generation process.
- Create prompts for technical questions.
- Require source-supported answers.
- Add citation handling.
- Handle questions outside the knowledge base.
- Evaluate answer quality and citation correctness.

Deliverables:

- Working telecom RAG assistant.
- Source-linked answers.
- Evaluation questions and reference answers.
- RAG benchmark results.

Completion criteria:

The assistant should answer questions using retrieved technical material and clearly communicate when sufficient supporting information is unavailable.

A local model should be used wherever practical so that the feature does not depend on paid API access.

## 9. Phase 7 — Incident Investigation Agent

**Objective:** Combine the platform's analytical and retrieval capabilities into one investigation workflow.

Tasks:

- Define the investigation state.
- Implement controlled analytical tools.
- Connect KPI analytics.
- Connect anomaly detection.
- Connect historical and neighbouring-cell comparisons.
- Connect forecasting where useful.
- Connect telecom document retrieval.
- Implement the LangGraph workflow.
- Add hypothesis assessment.
- Generate structured reports.
- Add human review and feedback.

Deliverables:

- Working investigation agent.
- Controlled tool interfaces.
- Structured incident reports.
- Synthetic incident evaluation dataset.
- Investigation benchmark results.

Completion criteria:

An engineer should be able to submit an incident and receive a report containing measurements, relevant technical references, plausible explanations and clearly stated limitations.

The system must distinguish observed evidence from hypotheses and confirmed causes.

## 10. Phase 8 — Network Digital Twin and Simulation

**Objective:** Create a controlled environment for RAN experiments.

Tasks:

- Implement base station and UE topology.
- Add simplified propagation and channel models.
- Generate traffic profiles.
- Implement resource allocation.
- Add scheduling baselines.
- Introduce interference scenarios.
- Generate simulated KPIs.
- Connect simulation results to platform analytics.
- Add scenario comparison.

Deliverables:

- Basic RAN simulation environment.
- Reproducible scenario configurations.
- Simulation result exports.
- What-if analysis functionality.

Completion criteria:

Users should be able to run controlled scenarios and compare their effects on selected network KPIs.

All simulation results must be identified as simulated rather than real operator measurements.

## 11. Phase 9 — Advanced 5G NR Research Lab

**Objective:** Add the research-oriented capabilities that distinguish the project from a conventional telecom analytics application.

This phase will build on the simulation foundation.

Tasks:

- Implement simplified channel matrix generation.
- Add beamforming baselines.
- Compare independent and coordinated beamforming.
- Add interference-aware precoding experiments.
- Implement scheduling comparisons.
- Introduce backhaul delay.
- Experiment with prediction-assisted coordination.
- Evaluate sum rate and edge-user performance.
- Document assumptions and experimental configurations.

Possible comparisons:

- No coordination.
- Independent beamforming.
- Coordinated beamforming.
- Coordination using delayed information.
- Prediction-assisted coordination.

Deliverables:

- Dedicated 5G NR research module.
- Reproducible experiment notebooks and scripts.
- Performance comparison plots.
- Technical experiment documentation.

Completion criteria:

The research lab should demonstrate measurable differences between selected strategies under controlled and documented conditions.

It should be clear which results come from simplified simulation and which come from actual public measurements.

## 12. Phase 10 — Complete Application Integration

**Objective:** Bring the individual modules together into one coherent application.

Tasks:

- Build the FastAPI backend.
- Define Pydantic request and response schemas.
- Connect backend services.
- Implement Streamlit navigation.
- Add the overview dashboard.
- Add data exploration and KPI monitoring.
- Add anomaly detection and forecasting pages.
- Add the telecom knowledge assistant.
- Add incident investigation.
- Add simulation and research lab pages.
- Implement consistent error handling.

Deliverables:

- Complete FastAPI application.
- Complete Streamlit interface.
- Integrated platform workflows.
- API and integration tests.

Completion criteria:

An engineer should be able to use the main platform features from a single application without manually running separate scripts for ordinary tasks.

## 13. Phase 11 — Testing and Benchmarking

**Objective:** Verify that the application is reliable and that its results are measurable.

Tasks:

- Expand unit tests.
- Complete integration tests.
- Test important end-to-end workflows.
- Evaluate anomaly detection.
- Evaluate forecasting.
- Benchmark retrieval approaches.
- Evaluate RAG answer grounding.
- Evaluate incident investigation.
- Test simulation reproducibility.
- Measure latency and resource usage.
- Record limitations.

Deliverables:

- Automated test suite.
- Benchmark reports.
- Evaluation plots.
- Reproducible experiment configurations.
- Documented limitations.

Completion criteria:

The repository should contain actual results from the implemented systems, with enough detail for another developer to understand how they were obtained.

## 14. Phase 12 — Deployment and Portfolio Preparation

**Objective:** Make the project easy to run, inspect and demonstrate.

Tasks:

- Finalise installation instructions.
- Add Docker support.
- Prepare sample datasets.
- Add demonstration scenarios.
- Create a public demo if free hosting limits allow.
- Improve the repository README.
- Add architecture and workflow diagrams.
- Add screenshots of the working application.
- Document benchmark results.
- Review licences and data attribution.
- Prepare a short project demonstration.

Deliverables:

- Documented repository.
- Local deployment instructions.
- Docker configuration.
- Public demonstration where feasible.
- Screenshots and benchmark results.
- Project walkthrough.

Completion criteria:

A recruiter or developer should be able to understand the project's purpose, inspect its implementation and run its main features without needing private credentials or paid services.

## 15. Priority Order

Not every feature has equal priority.

The following order will guide decisions when time or computing resources are limited.

| Priority | Component | Reason |
|---|---|---|
| 1 | Data ingestion and quality | Foundation for all analytics |
| 2 | KPI analytics and dashboard | First visible working application |
| 3 | Anomaly detection | Demonstrates practical ML |
| 4 | Telecom RAG | Demonstrates modern retrieval engineering |
| 5 | Incident investigation agent | Connects the major platform components |
| 6 | Forecasting | Adds predictive analytics |
| 7 | Network simulation | Provides controlled data and experiments |
| 8 | 5G NR research lab | Adds specialist wireless depth |
| 9 | Deployment and public demo | Makes the work accessible to others |

Testing, documentation and code quality are continuous activities, not final-stage tasks.

## 16. Definition of Done

A component should not be considered complete just because its code runs once.

For each major component, we should aim to have:

- Working implementation.
- Clear input and output definitions.
- Basic error handling.
- Automated tests.
- At least one reproducible example.
- Documented configuration.
- Evaluation results where applicable.
- Integration with the rest of the platform where required.

The documentation should describe what has actually been implemented, not what we hope to implement later.

## 17. Working Method

We will develop the project one manageable task at a time.

For each task, the process will be:

1. Understand the technical requirement.
2. Identify the files that need to be created or modified.
3. Implement the code.
4. Run it locally or in Colab, depending on the task.
5. Inspect the output.
6. Write or update tests.
7. Record important technical decisions.
8. Update the documentation.

We should avoid moving to the next major component while the current one has unresolved fundamental issues.

At the same time, we should not spend excessive time polishing small details before the main workflow works.

## 18. Expected Outcome

The final result should be a working RAN intelligence application with a real data pipeline, network analytics, ML models, telecom RAG, incident investigation and a research-oriented 5G simulation environment.

The project should demonstrate practical skills in Python engineering, data engineering, machine learning, LLM applications, API development, testing and wireless network analytics.

The priority is to build a coherent system that works and can be explained technically, rather than a large collection of disconnected demonstrations.
