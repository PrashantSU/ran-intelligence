# Testing and Quality Assurance

## 1. Purpose

The RAN Intelligence Platform will contain several interconnected components, including data processing, machine learning, document retrieval, an investigation agent, simulation and a web application.

As the project grows, changes in one component may affect another. Testing will help us catch these problems early.

This document describes the testing approach, tools and quality checks that will be used throughout development.

The main objectives are to:

- Verify that individual modules behave correctly.
- Check that different components work together.
- Identify failures caused by invalid or incomplete data.
- Verify that API endpoints return expected responses.
- Test the investigation workflow using controlled scenarios.
- Make sure important functionality continues working after code changes.

## 2. Testing Tools

The initial testing setup will use the following tools:

| Tool | Purpose |
|---|---|
| Pytest | Main testing framework |
| Pytest-cov | Test coverage measurement |
| HTTPX | Testing FastAPI endpoints |
| Pydantic | Input and output validation |
| Ruff | Code formatting and linting |
| MyPy | Optional static type checking |
| GitHub Actions | Automated testing during development |

We will start with a small set of tools and add others only when they provide a clear benefit.

## 3. Test Organisation

Tests should be organised separately from the application code.

Proposed structure:

```text
tests/
├── conftest.py
├── fixtures/
│   ├── sample_measurements.csv
│   ├── sample_cells.csv
│   └── sample_incidents.json
│
├── unit/
│   ├── test_ingestion.py
│   ├── test_data_quality.py
│   ├── test_kpi_analytics.py
│   ├── test_anomaly_detection.py
│   ├── test_forecasting.py
│   ├── test_retrieval.py
│   ├── test_hypothesis.py
│   └── test_simulation.py
│
├── integration/
│   ├── test_data_pipeline.py
│   ├── test_analytics_pipeline.py
│   ├── test_rag_pipeline.py
│   ├── test_investigation.py
│   └── test_api_services.py
│
├── api/
│   ├── test_health.py
│   ├── test_datasets.py
│   ├── test_kpis.py
│   ├── test_anomalies.py
│   └── test_incidents.py
│
├── evaluation/
│   ├── test_anomaly_metrics.py
│   ├── test_forecast_metrics.py
│   ├── test_retrieval_metrics.py
│   └── test_diagnosis_metrics.py
│
└── security/
    ├── test_file_uploads.py
    ├── test_input_validation.py
    └── test_path_access.py
```

The structure can be adjusted as the implementation develops. We should avoid creating empty test files before the corresponding modules exist.

## 4. Unit Testing

Unit tests will verify individual functions and classes independently.

They should be fast and should not require external services or large datasets.

### 4.1 Data Ingestion

Tests should cover:

- Reading supported CSV files.
- Handling missing columns.
- Rejecting unsupported formats.
- Handling empty files.
- Correct timestamp parsing.
- Correct data type conversion.
- Handling duplicate records.

Example:

If a dataset contains an invalid timestamp, the ingestion module should report it rather than silently treating it as a valid measurement.

### 4.2 Data Quality

Tests should verify:

- Missing value calculations.
- Duplicate detection.
- Invalid KPI ranges.
- Schema validation.
- Quality report generation.

The expected output should be known for each small test dataset.

### 4.3 KPI Analytics

Tests should verify:

- Mean and median calculations.
- KPI aggregation.
- Time-based grouping.
- Cell-level filtering.
- Handling missing values.
- Correct unit conversions.

Small hand-calculated examples will be used to check the results.

### 4.4 Anomaly Detection

Tests should verify:

- Correct model input format.
- Valid anomaly score generation.
- Expected output structure.
- Behaviour on empty input.
- Handling of constant-valued features.
- Reproducibility where supported.

The tests should not assume that every unusual value must be detected. Model performance belongs in the separate evaluation process.

### 4.5 Forecasting

Tests should cover:

- Input time-series validation.
- Forecast horizon handling.
- Correct output length.
- Missing timestamps.
- Invalid model parameters.
- Metric calculations.

For example, a forecast request for ten future steps should return ten predictions if the selected model supports that request.

### 4.6 Retrieval

Tests should cover:

- Document loading.
- Chunk creation.
- Metadata preservation.
- Embedding generation.
- Vector search.
- BM25 retrieval.
- Hybrid ranking.
- Reranking.
- Source reference preservation.

A test should verify that retrieved passages retain their original document identifiers.

### 4.7 Simulation

Tests should cover:

- Configuration validation.
- Topology creation.
- Traffic generation.
- Channel calculations.
- Resource allocation.
- KPI generation.
- Random seed reproducibility.

Simulation tests should use small configurations to keep execution time low.

## 5. Integration Testing

Integration tests will verify that multiple components work together correctly.

These tests are important because a module may pass its individual tests but still fail when connected to another module.

### 5.1 Data Pipeline

Test the complete process:

```text
Input CSV
   |
   v
Ingestion
   |
   v
Validation
   |
   v
Cleaning
   |
   v
Processed Dataset
   |
   v
KPI Analytics
```

The test should confirm that a sample file can pass through the pipeline and produce the expected processed measurements and KPI summaries.

### 5.2 Analytics Pipeline

Test the connection between:

- KPI analytics.
- Anomaly detection.
- Forecasting.
- Result storage.

The output of each component should follow the expected schema.

### 5.3 RAG Pipeline

Test the complete document retrieval process:

```text
Documents
   |
   v
Extraction
   |
   v
Chunking
   |
   v
Embeddings and BM25
   |
   v
Retrieval
   |
   v
Reranking
   |
   v
Context and Citations
```

The test should confirm that a question can retrieve relevant passages and preserve their source metadata.

Generation tests may use a mocked language model so that the test suite does not depend on an external API or a running local model.

### 5.4 Incident Investigation

The investigation workflow should be tested using controlled incident scenarios.

For example, a synthetic dataset could contain a sudden throughput reduction and increased PRB utilisation.

The test should verify that:

- The correct cell is selected.
- The requested time range is used.
- Relevant KPI analysis is executed.
- The investigation agent receives the analytical results.
- The final report contains the available evidence.
- Unsupported conclusions are not presented as confirmed causes.

The workflow should also be tested when one or more tools fail.

## 6. API Testing

FastAPI endpoints will be tested using HTTPX and FastAPI's test client.

Tests should cover:

- Successful requests.
- Invalid request bodies.
- Missing required parameters.
- Unknown dataset identifiers.
- Unsupported file uploads.
- Correct response schemas.
- Appropriate HTTP status codes.
- Error response consistency.

For example, requesting a dataset that does not exist should return a suitable error response rather than causing an unhandled server exception.

API tests should use temporary test data and isolated database state.

## 7. End-to-End Testing

End-to-end tests will check whether an engineer can complete important tasks through the application.

The initial workflows should include:

### Workflow 1 — Explore a dataset

1. Open the application.
2. Select a dataset.
3. Inspect its measurements.
4. View data quality information.
5. Explore selected KPIs.

### Workflow 2 — Detect anomalies

1. Select a dataset.
2. Choose a cell and KPI.
3. Run an anomaly detection method.
4. View the results.
5. Inspect the affected timestamps.

### Workflow 3 — Ask a telecom question

1. Open the knowledge assistant.
2. Submit a technical question.
3. Retrieve supporting passages.
4. Review the generated answer.
5. Open the cited source.

### Workflow 4 — Investigate an incident

1. Submit an incident description.
2. Review the parsed incident details.
3. Run the investigation.
4. Inspect analytical evidence.
5. Review candidate explanations.
6. Read the final report.

### Workflow 5 — Run a simulation

1. Select a simulation scenario.
2. Configure the network.
3. Execute the simulation.
4. Inspect generated KPIs.
5. Compare the results with another scenario.

We will prioritise automated testing of the backend workflows. UI automation can be added later if it provides enough value.

## 8. Test Data and Fixtures

Tests should use small, controlled datasets.

We will maintain a set of reusable fixtures for common scenarios.

Examples:

- A valid RAN measurement dataset.
- A dataset with missing values.
- A dataset with duplicate records.
- A dataset containing invalid KPI values.
- A dataset with a known throughput degradation.
- A dataset with an introduced interference scenario.
- A small collection of telecom documents.
- A minimal network simulation configuration.

Synthetic fixtures should have known expected outcomes.

Public datasets may be used for integration and realistic data testing, but tests should not depend on downloading large files every time.

## 9. Mocking External Dependencies

The automated test suite should not require paid services or external API access.

Where appropriate, we will mock:

- Language model responses.
- Embedding services.
- External document downloads.
- Large model inference.
- Slow simulation operations.

This will make the test suite faster and more reliable.

Separate optional tests can run against a locally installed model or a larger dataset.

A failed external service should not prevent basic unit tests from running.

## 10. Security Testing

Basic security checks should be included from the beginning.

The initial tests should cover:

- Unsupported file extensions.
- Oversized uploads.
- Malformed CSV files.
- Invalid API inputs.
- Path traversal attempts.
- Unsafe file paths.
- Unexpected tool arguments.
- Missing or invalid configuration.

Uploaded files must not be executed.

The agent should only call approved tools with validated arguments.

The application should not expose unrestricted access to local files or system commands.

## 11. Code Quality

Code quality checks will run alongside tests.

The initial checks will include:

**Formatting**

Ruff will be used to maintain consistent Python formatting.

**Linting**

Ruff will identify common programming errors and style issues.

**Type checking**

MyPy can be introduced for important service interfaces and data structures.

**Test coverage**

Pytest-cov will help identify areas that lack automated tests.

We should focus on meaningful coverage of important logic rather than trying to achieve a particular percentage by writing trivial tests.

## 12. Continuous Integration

GitHub Actions will run automated checks when code is pushed or a pull request is opened.

The initial workflow should:

1. Set up the supported Python version.
2. Install project dependencies.
3. Run Ruff checks.
4. Run unit tests.
5. Run integration tests that do not require external services.
6. Generate a coverage report.

A simplified workflow will eventually be stored at:

```text
.github/
└── workflows/
    └── ci.yml
```

The CI workflow should use small test fixtures and avoid downloading large datasets or language models.

More expensive evaluation experiments can be run separately.

## 13. Test Execution

Developers should be able to run tests locally.

Examples:

```bash
# Run all tests
pytest

# Run only unit tests
pytest tests/unit

# Run integration tests
pytest tests/integration

# Run API tests
pytest tests/api

# Run security tests
pytest tests/security

# Generate coverage report
pytest --cov=ran_intelligence --cov-report=term-missing
```

Individual tests should also be runnable while developing a particular module.

## 14. Test Reporting

Important test runs should record:

- Date and commit.
- Python version.
- Test category.
- Number of passed tests.
- Number of failed tests.
- Skipped tests.
- Execution time.
- Relevant error details.

Evaluation experiments and ordinary software tests should remain distinguishable.

A model achieving a high F1-score is not the same thing as the software implementation passing its unit tests.

## 15. Implementation Order

Testing infrastructure will be introduced gradually.

**Stage 1 — Basic Pytest setup**

Configure Pytest and create reusable fixtures.

**Stage 2 — Unit tests for core modules**

Test ingestion, data quality and KPI analytics.

**Stage 3 — ML tests**

Add tests for anomaly detection and forecasting.

**Stage 4 — Retrieval tests**

Test document processing and retrieval.

**Stage 5 — Agent workflow tests**

Test investigation state, tool calls and report generation.

**Stage 6 — API tests**

Test FastAPI routes and request validation.

**Stage 7 — Integration tests**

Test the main data and investigation workflows.

**Stage 8 — Security checks**

Test uploads, paths and input validation.

**Stage 9 — CI setup**

Automate the essential checks through GitHub Actions.

**Stage 10 — End-to-end testing**

Test the main engineer workflows through the complete application.

## 16. Expected Outcome

The project should have a repeatable testing process that makes it easier to add features without breaking existing functionality.

Important analytical calculations, data transformations, API contracts and investigation workflows should all have appropriate tests.

The final repository should make it clear how the software was tested and which parts have been evaluated using controlled experiments.
