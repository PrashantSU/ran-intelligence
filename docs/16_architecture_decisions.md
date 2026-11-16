# Architecture Decisions

This document records the main technical and architectural decisions behind the RAN Intelligence Platform.

The goal is not to choose the most complicated technology for every component. We want a system that is practical to build, easy to test, free to run, and technically strong enough to demonstrate real engineering skills.

These decisions describe the initial design. We can revise them as the project develops, provided we document why a change is needed.

## 1. Use Python as the primary language

**Decision:** Python will be used across the backend, data processing, machine learning, retrieval and simulation components.

**Why:**

- Strong ecosystem for data engineering and machine learning.
- Libraries such as Pandas, NumPy, PyTorch and scikit-learn cover most of our requirements.
- FastAPI and Streamlit allow us to build the API and application without introducing another language.
- The same language can be used in Google Colab and local development.

**Trade-off:** Python may not be the best choice for every performance-critical component. If simulation or data processing becomes too slow, we can consider optimising selected parts rather than rewriting the whole system.

## 2. Use Streamlit for the application

**Decision:** Streamlit will be used for the user interface.

**Why:**

- It works directly with Python.
- It supports interactive charts, tables, filters and file uploads.
- It is suitable for technical dashboards and internal engineering tools.
- It avoids the additional complexity of building a React frontend.

**Trade-off:** Streamlit provides less control over the user interface than a dedicated frontend framework. That is acceptable for this project's initial scope.

## 3. Use FastAPI for the backend

**Decision:** FastAPI will expose the platform's functionality through REST APIs.

**Why:**

- It provides request validation through Pydantic.
- It generates API documentation automatically.
- It supports asynchronous endpoints where useful.
- It allows the backend to remain separate from the Streamlit interface.

**Trade-off:** We will have two application layers to maintain. The separation is worthwhile because analytics, retrieval and investigation functions should not depend on the user interface.

## 4. Start with SQLite

**Decision:** SQLite will be the initial relational database.

**Why:**

- No database server needs to be installed or maintained.
- It is sufficient for a single-user development environment and small demonstrations.
- It is easy to use in local development and testing.

We may move to PostgreSQL if concurrent access, deployment requirements or data volume make SQLite unsuitable.

**Trade-off:** SQLite is not intended to support every production-scale multi-user workload. We will avoid designing the application around SQLite-specific behaviour where possible.

## 5. Use Parquet and CSV for measurement data

**Decision:** Measurement datasets will primarily be stored as Parquet files. CSV will be supported for importing external datasets.

**Why:**

- CSV is widely supported by public telecom datasets.
- Parquet is more efficient for analytical workloads and preserves column types.
- Pandas can work with both formats.
- Large measurement tables do not need to be stored as individual database records.

SQLite will hold application metadata, experiment records, investigation results and other structured information.

**Trade-off:** The application must keep track of dataset locations and versions. We will include dataset metadata and processing information to make this manageable.

## 6. Use hybrid retrieval for telecom RAG

**Decision:** The RAG system will combine BM25 keyword retrieval with vector retrieval using FAISS and Sentence Transformers.

**Why:**

Telecom documentation contains both natural-language explanations and precise technical terms.

For example, an engineer might search for a general explanation of handover failure, or use a specific term such as `SS-SINR`, `PDSCH` or `HARQ`.

- BM25 helps with exact terminology.
- Vector retrieval helps find semantically related passages.
- Reciprocal Rank Fusion (RRF) can combine the two result lists.
- A reranker can improve the ordering of retrieved passages.

**Trade-off:** Hybrid retrieval requires more components and evaluation than a simple vector database. We will measure whether each additional component improves retrieval quality rather than assuming it does.

## 7. Use LangGraph for incident investigation

**Decision:** LangGraph will manage the incident investigation workflow.

The agent will use a defined sequence of steps and a controlled set of tools. It will not be given unrestricted access to the system.

A typical investigation may involve:

1. Validating the incident details.
2. Retrieving relevant cell measurements.
3. Checking KPI trends and anomalies.
4. Searching telecom documentation.
5. Comparing possible explanations.
6. Producing a structured investigation report.

**Why:**

- The investigation has multiple steps and requires shared state.
- Different tools produce evidence that must be combined.
- The workflow needs predictable execution and error handling.
- Human review should remain part of the process.

**Trade-off:** A graph-based workflow requires more initial design than a simple chain. It is justified by the number of tools and the need to keep investigations traceable.

## 8. Avoid mandatory paid LLM APIs

**Decision:** The project should work without paid model APIs.

We will first investigate local models through Ollama and compatible open-source models. Google Colab can be used for experiments that require more compute.

The application should also support a limited mode in which retrieval and analytics work without an LLM. Where practical, precomputed outputs will be used for a public demonstration.

**Why:**

- There should be no recurring API cost to develop or run the project.
- Local inference makes experiments reproducible.
- It avoids depending on a provider's free-tier limits.

**Trade-off:** Local models may be slower or less capable than larger hosted models. Hardware and memory requirements will influence model selection.

We will measure response quality and resource usage before selecting a default model.

## 9. Use a modular monolith initially

**Decision:** The first version will be one Python application with clearly separated modules, rather than multiple independently deployed services.

**Why:**

- The project is being developed by one person.
- Separate services would introduce unnecessary deployment and networking work.
- Modules can still have clear interfaces and independent tests.
- The application can be split into services later if there is a real need.

**Trade-off:** A modular monolith has less independent scaling than a distributed architecture. That is not a concern for the initial development and demonstration workload.

## 10. Use Pytest and GitHub Actions

**Decision:** Pytest will be used for automated testing, with GitHub Actions running selected checks on repository changes.

Ruff will be used for linting and formatting.

**Why:**

- Automated tests help catch regressions as components are integrated.
- CI makes it easier to verify changes consistently.
- These tools are free and widely used in Python projects.

We will begin with unit tests and gradually add integration and end-to-end tests.

## 11. Introduce Docker after local development works

**Decision:** Docker will be added after the main application can run locally.

**Why:**

- Containerisation makes the environment easier to reproduce.
- It helps demonstrate practical deployment knowledge.
- It can simplify running the API and supporting services together.

We will not make Docker a prerequisite for the first data-processing experiments.

**Trade-off:** Containerising Python applications and local LLMs adds configuration and resource-management work. It should solve a real reproducibility or deployment problem, not become a project in itself.

## 12. Use public and independently generated data

**Decision:** The platform will use publicly available datasets and independently generated synthetic data.

Potential sources include:

- AERPAW 5G measurement datasets.
- FCCLab 5G NR datasets.
- Colosseum and OpenRAN Gym datasets.
- Other suitable public traffic and network datasets.

Synthetic data will be used for scenarios that are not covered by the available datasets, including controlled degradation, congestion, interference and backhaul-delay experiments.

**Why:**

- The project should be reproducible by other developers.
- Public data provides real measurements for selected analyses.
- Synthetic data allows us to create controlled test cases with known conditions.

No Huawei proprietary data, source code or confidential configuration will be included.

**Trade-off:** Public datasets may not contain every KPI or network condition needed. We will document missing fields and clearly distinguish synthetic measurements from real observations.

## 13. Build a lightweight RAN simulation

**Decision:** The simulation component will be implemented as a simplified research environment rather than a full commercial network simulator.

It will focus on selected experiments involving:

- Multiple base stations and users.
- Channel quality and interference.
- Resource scheduling.
- Beamforming-related comparisons.
- Backhaul delay.
- Network performance metrics.

**Why:**

A focused simulator is sufficient to investigate selected network behaviours and demonstrate how the platform connects simulation with analytics and incident investigation.

**Trade-off:** Its results will depend on modelling assumptions. We will document these assumptions and avoid presenting simulation results as measurements from a real operator network.

## 14. Evaluate components independently

**Decision:** Each major subsystem will have its own evaluation approach.

Examples include:

- Data ingestion: schema validation and data-quality checks.
- KPI analytics: correctness of calculations.
- Anomaly detection: precision, recall and F1-score on labelled test cases.
- Forecasting: MAE and RMSE on chronological test data.
- RAG: Precision@K, Recall@K, MRR and nDCG@K.
- Incident investigation: evidence quality, hypothesis ranking and report correctness.
- Simulation: consistency with expected behaviour under controlled conditions.

**Why:**

A working interface does not demonstrate that the underlying system is reliable. We need measurable results for the individual components.

**Trade-off:** Evaluation takes additional development time, but it is essential for making credible technical claims.

## 15. Revisit decisions when requirements change

These choices are not permanent restrictions.

We should reconsider them when there is a concrete reason, such as:

- SQLite becoming a bottleneck.
- Retrieval quality remaining poor after tuning.
- Local models failing to meet the required response quality.
- Simulation performance becoming inadequate.
- Deployment requirements exceeding what Streamlit can support.
- A need for multiple users or independent service scaling.

Any significant change should be recorded with its motivation and consequences.

## Summary

The initial architecture favours a Python-based modular application, free and open-source tools, public and synthetic data, and local model inference.

The intention is to spend time building and evaluating the actual telecom intelligence capabilities rather than maintaining unnecessary infrastructure.

As the platform develops, decisions will be updated based on test results, performance measurements and practical limitations.
