# Final Project Checklist

## 1. Purpose

This document provides an overview of what needs to be completed to deliver the RAN Intelligence Platform.

It will serve as a reference throughout development and help track progress across the different components.

The project is considered complete when its major components work together, their results can be evaluated, and the platform can be demonstrated with reproducible examples.

Not every feature needs to be implemented at the same time.

## 2. Project foundation

- [ ] Repository structure established.
- [ ] Python project configured.
- [ ] Dependencies managed through `pyproject.toml`.
- [ ] Git ignore rules configured.
- [ ] Environment configuration added.
- [ ] Logging and exception handling implemented.
- [ ] Basic automated testing configured.
- [ ] GitHub Actions workflow established.

## 3. Data engineering

- [ ] Public dataset sources reviewed.
- [ ] AERPAW dataset downloaded and inspected.
- [ ] Dataset metadata recorded.
- [ ] Data ingestion pipeline implemented.
- [ ] Schema validation implemented.
- [ ] Missing and invalid values handled.
- [ ] Processed datasets stored in an appropriate format.
- [ ] Data quality reports generated.
- [ ] Additional datasets integrated where useful.

## 4. KPI analytics

- [ ] Core RAN KPIs implemented.
- [ ] KPI units and definitions documented.
- [ ] Time-based aggregation implemented.
- [ ] Cell-level comparisons supported.
- [ ] Historical KPI analysis implemented.
- [ ] KPI relationships explored.
- [ ] Dashboard visualisations created.

## 5. Anomaly detection

- [ ] Statistical baseline implemented.
- [ ] Isolation Forest implemented.
- [ ] Additional methods evaluated where appropriate.
- [ ] Synthetic anomaly scenarios generated.
- [ ] Evaluation metrics implemented.
- [ ] Anomaly explanations provided.
- [ ] Results integrated into the dashboard.

## 6. KPI forecasting

- [ ] Baseline forecasting methods implemented.
- [ ] ML forecasting model implemented.
- [ ] Chronological evaluation established.
- [ ] Forecasting metrics implemented.
- [ ] Prediction intervals considered where appropriate.
- [ ] Forecast visualisations created.
- [ ] Results integrated into the platform.

## 7. Telecom RAG

- [ ] Public technical document sources selected.
- [ ] Document extraction implemented.
- [ ] Chunking strategy implemented.
- [ ] Embeddings generated.
- [ ] FAISS index created.
- [ ] BM25 retrieval implemented.
- [ ] Hybrid retrieval implemented.
- [ ] Reranking evaluated.
- [ ] Grounded answer generation implemented.
- [ ] Source citations displayed.
- [ ] Retrieval evaluation completed.

## 8. Incident investigation agent

- [ ] Incident input schema defined.
- [ ] Investigation state implemented.
- [ ] KPI analysis tools connected.
- [ ] Anomaly detection tools connected.
- [ ] Document retrieval tools connected.
- [ ] Forecasting tools connected where useful.
- [ ] Hypothesis generation implemented.
- [ ] Evidence collection implemented.
- [ ] Hypothesis ranking implemented.
- [ ] Uncertainty and limitations reported.
- [ ] Investigation reports generated.
- [ ] Human review supported.
- [ ] Agent execution evaluated.

## 9. Network simulation

- [ ] Network topology model implemented.
- [ ] Base stations and UEs represented.
- [ ] Traffic generation implemented.
- [ ] Channel assumptions documented.
- [ ] Scheduling algorithms implemented.
- [ ] Interference scenarios supported.
- [ ] Network performance metrics calculated.
- [ ] What-if experiments supported.
- [ ] Simulation results visualised.

## 10. Advanced 5G NR Intelligence Lab

- [ ] NR experiment configuration defined.
- [ ] Channel modelling assumptions documented.
- [ ] Resource scheduling experiments implemented.
- [ ] Beamforming experiments implemented.
- [ ] Coordinated beamforming scenarios implemented.
- [ ] Backhaul delay scenarios implemented.
- [ ] Prediction-assisted scheduling investigated.
- [ ] Baseline comparisons performed.
- [ ] Results and limitations documented.

All experiments must use independently generated or appropriately licensed public data and code. Huawei proprietary material must not be included.

## 11. Backend and application

- [ ] FastAPI application implemented.
- [ ] API request and response schemas defined.
- [ ] Data ingestion endpoints implemented.
- [ ] Analytics endpoints implemented.
- [ ] ML endpoints implemented.
- [ ] RAG endpoints implemented.
- [ ] Incident investigation endpoint implemented.
- [ ] Simulation endpoints implemented.
- [ ] Streamlit dashboard implemented.
- [ ] Application pages connected to backend services.
- [ ] Errors and loading states handled.

## 12. Evaluation and benchmarking

- [ ] Data quality benchmarks recorded.
- [ ] KPI calculation tests completed.
- [ ] Anomaly detection models compared.
- [ ] Forecasting models compared.
- [ ] RAG retrieval benchmarks completed.
- [ ] Generated answers evaluated.
- [ ] Incident investigation evaluated.
- [ ] Simulation results validated against expected behaviour.
- [ ] Execution time and memory usage measured.
- [ ] Experiment configurations and results recorded.

## 13. Security and reliability

- [ ] Secrets excluded from Git.
- [ ] File uploads validated.
- [ ] API inputs validated.
- [ ] Agent tools restricted.
- [ ] Prompt injection scenarios tested.
- [ ] Sensitive information excluded from logs.
- [ ] Error handling tested.
- [ ] Resource limits configured.
- [ ] Public deployment settings reviewed.

## 14. Documentation and reproducibility

- [ ] README explains the project.
- [ ] Architecture documented.
- [ ] Data sources documented.
- [ ] Data dictionary completed.
- [ ] Installation instructions tested.
- [ ] Environment setup documented.
- [ ] Experiment procedures documented.
- [ ] Evaluation results published.
- [ ] Known limitations explained.
- [ ] Demonstration workflow documented.

## 15. Deployment

- [ ] Local application runs successfully.
- [ ] Backend starts successfully.
- [ ] Streamlit application starts successfully.
- [ ] Docker configuration tested.
- [ ] Reproducible environment established.
- [ ] Public demonstration approach selected.
- [ ] Resource limitations documented.
- [ ] Deployment instructions tested.

A public demonstration may use precomputed results and selected lightweight functionality if free hosting cannot support the full application.

## 16. Portfolio presentation

- [ ] Repository description updated.
- [ ] README includes architecture overview.
- [ ] Screenshots added.
- [ ] Architecture diagram added.
- [ ] Important evaluation graphs included.
- [ ] Example incident investigation report included.
- [ ] Example simulation results included.
- [ ] Technical decisions explained.
- [ ] Limitations clearly stated.
- [ ] Demonstration instructions provided.

The project should demonstrate both the working software and the reasoning behind its design.

## 17. Final completion criteria

The project will be considered ready for portfolio presentation when:

1. The main application runs successfully.
2. Public or synthetic network data can be ingested and analysed.
3. KPI monitoring and predictive analytics work.
4. Telecom documents can be searched with grounded answers and citations.
5. The investigation agent can collect evidence and produce a useful report.
6. The simulation environment supports reproducible experiments.
7. The advanced NR lab demonstrates meaningful wireless experiments.
8. Evaluation results are available for the important components.
9. The application has automated tests and basic security protections.
10. Another developer can follow the documentation and reproduce the main demonstration.

## 18. Final note

This checklist describes the intended destination, not a requirement to complete every item before showing progress.

We will build the platform in stages, test each component and integrate them as they become stable.

The emphasis is on a working engineering project with credible results, not simply completing a long list of features.
