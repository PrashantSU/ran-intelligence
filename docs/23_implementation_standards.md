# Implementation Standards

## 1. Purpose

This document defines the coding and development practices for the RAN Intelligence Platform.

The project will contain multiple Python modules, APIs, machine learning models, retrieval pipelines and simulation components. Without consistent implementation practices, the code can become difficult to maintain and test.

These standards are intended to keep the code understandable, reusable and reliable as the project grows.

## 2. Programming language and style

Python will be the primary programming language.

We will follow standard Python conventions, particularly PEP 8 for formatting and naming.

General guidelines:

- Use clear and descriptive names.
- Prefer simple implementations over unnecessary abstractions.
- Keep functions focused on one responsibility.
- Avoid repeated code where a shared function makes sense.
- Add comments when the reasoning behind an implementation is not obvious.
- Avoid comments that simply repeat what the code already says.

Code should be understandable to another developer without requiring them to read the entire project first.

## 3. Naming conventions

We will use consistent naming across the repository.

| Element | Convention | Example |
|---|---|---|
| Python files | snake_case | `kpi_calculator.py` |
| Functions | snake_case | `calculate_throughput()` |
| Variables | snake_case | `cell_id` |
| Classes | PascalCase | `AnomalyDetector` |
| Constants | UPPER_SNAKE_CASE | `DEFAULT_CHUNK_SIZE` |
| Packages | lowercase | `data_engineering` |
| Test files | test prefix | `test_kpi_calculator.py` |

Names should describe their purpose rather than their implementation details whenever practical.

## 4. Functions and classes

Functions should have a clear responsibility.

For example, a KPI calculation should not also load files, modify the database and generate a chart.

Those operations should be handled by separate components.

Classes should be introduced when they provide a useful abstraction, such as:

- A dataset loader.
- An anomaly detection model.
- A document retriever.
- A network simulator.
- An incident investigation workflow.

We should avoid creating classes simply to wrap a single function without a clear benefit.

## 5. Type hints

Type hints should be used for important functions, service interfaces and data structures.

Example:

```python
def calculate_average_sinr(
    measurements: list[float],
) -> float:
    if not measurements:
        raise ValueError("Measurements cannot be empty")

    return sum(measurements) / len(measurements)
```

For structured application data, we will use appropriate Python typing tools such as Pydantic models and dataclasses.

Type hints improve readability and help catch certain errors during development.

## 6. Documentation and docstrings

Public functions, classes and complex modules should have useful docstrings.

Example:

```python
def calculate_cell_throughput(
    total_bits: int,
    duration_seconds: float,
) -> float:
    """Calculate average cell throughput in Mbps."""
```

Documentation should explain:

- What the component does.
- What inputs it expects.
- What it returns.
- Important assumptions.
- Relevant limitations.

Complex algorithms should also explain the reasoning behind important design choices.

## 7. Error handling

Errors should be handled explicitly.

We should:

- Validate inputs before performing calculations.
- Raise meaningful exceptions.
- Avoid silently ignoring failed operations.
- Avoid broad exception handling unless there is a clear recovery strategy.
- Return useful error messages through the API.
- Record relevant failures in application logs.

For example, an invalid dataset should produce a clear validation error rather than failing much later during model execution.

## 8. Logging

Use Python's standard `logging` module rather than relying on print statements throughout application code.

Logs should help identify:

- Data ingestion failures.
- Validation problems.
- Model execution errors.
- Retrieval failures.
- Agent tool execution.
- API errors.
- Simulation failures.

Sensitive values and credentials must never appear in logs.

## 9. Configuration management

Important settings should not be scattered throughout source code.

Examples include:

- Dataset paths.
- Database connection settings.
- Model names.
- Embedding configuration.
- Chunk size.
- Retrieval parameters.
- Simulation settings.
- Application environment.

These values should be managed through configuration files or environment variables.

We should distinguish between experimental parameters and application configuration.

## 10. Data handling standards

Data processing should preserve the meaning of the original measurements.

Important practices include:

- Keep original datasets unchanged.
- Record transformations.
- Use consistent units.
- Handle timestamps and time zones explicitly.
- Validate measurement ranges.
- Preserve source information.
- Avoid data leakage between training and evaluation sets.

For network KPIs, units must be explicit.

For example, throughput should not be stored as a mixture of Mbps and Gbps without a documented conversion.

## 11. Machine learning standards

Machine learning implementations should separate:

- Data preparation.
- Feature engineering.
- Training.
- Prediction.
- Evaluation.
- Model persistence.

Every reported result should identify the dataset, model configuration and evaluation procedure.

Time-series tasks must use chronological splits where appropriate.

Baseline methods should be implemented before more complex models so that improvements can be measured.

## 12. RAG and agent standards

RAG components should be independently testable.

Document extraction, chunking, embedding, indexing, retrieval, reranking and generation should remain separate operations.

For agents:

- Define an explicit state.
- Keep tools narrowly scoped.
- Validate tool arguments.
- Record important execution steps.
- Handle failed tool calls.
- Distinguish evidence from model-generated hypotheses.
- Require human review of diagnostic conclusions.

The LLM should not be treated as the source of truth for network measurements.

## 13. Testing standards

New functionality should include appropriate tests.

Tests should cover:

- Normal inputs.
- Empty inputs.
- Invalid inputs.
- Boundary conditions.
- Expected failures.
- Important edge cases.

Tests should not depend unnecessarily on external APIs, internet access or large datasets.

Use fixtures and small synthetic datasets wherever practical.

## 14. Code quality tools

We will use:

| Tool | Purpose |
|---|---|
| Ruff | Linting and formatting |
| Pytest | Automated testing |
| MyPy | Optional static type checking |
| Git | Version control |
| GitHub Actions | Automated checks |

These tools will be introduced progressively.

## 15. Git practices

Changes should be committed in logical units.

Commit messages should briefly describe the change.

Examples:

```text
Add AERPAW dataset loader
Implement KPI validation
Add Isolation Forest baseline
Build hybrid document retrieval
Add incident investigation workflow
```

Avoid committing unrelated changes together.

Experimental work should be committed when it reaches a useful and reproducible state.

## 16. Performance considerations

We should consider performance when processing large datasets or running expensive models.

Examples include:

- Avoid loading unnecessary columns.
- Use efficient Pandas operations.
- Prefer Parquet for suitable analytical datasets.
- Avoid repeated embedding generation.
- Reuse vector indexes when possible.
- Cache expensive computations where appropriate.
- Measure execution time before attempting premature optimisation.

Performance improvements should be supported by measurements.

## 17. Code review checklist

Before considering an implementation complete, check:

- Is the code understandable?
- Does each function have a clear responsibility?
- Are inputs validated?
- Are errors handled?
- Are units and assumptions documented?
- Are type hints used where useful?
- Are tests included?
- Are configuration values separated from source code?
- Are secrets excluded?
- Can the component be reused independently?

## 18. General development principle

The goal is not to produce the largest possible codebase or follow every software engineering practice from the beginning.

The goal is to build a technically credible platform with understandable implementation, meaningful tests and reproducible results.

These standards should support development without making simple tasks unnecessarily complicated.
