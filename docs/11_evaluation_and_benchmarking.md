# Evaluation and Benchmarking

## 1. Purpose

The RAN Intelligence Platform contains several components that need to be evaluated independently.

A working application does not automatically mean that its predictions are accurate, its retrieved documents are relevant or its incident investigations are reliable.

This document defines how we will test and measure the platform.

The evaluation will cover:

- Data ingestion and quality.
- KPI analytics.
- Anomaly detection.
- KPI forecasting.
- Telecom document retrieval and RAG.
- Incident investigation agent.
- Network simulation.
- API and application reliability.
- Execution time and resource usage.

The objective is to produce measurable results that can be reproduced and explained.

## 2. Evaluation Principles

A few principles will guide the evaluation.

**Use appropriate baselines**

A complex model should be compared against a simpler method. For example, an Isolation Forest model should not be presented as an improvement without comparison against a statistical threshold baseline.

**Keep training and test data separate**

For time-series problems, we should use chronological splits rather than randomly mixing future and past observations.

**Avoid data leakage**

Information from the test period must not influence model training, preprocessing or parameter selection.

**Evaluate components independently**

A good result from one component should not hide weaknesses in another.

**Record experiments**

Each experiment should include its configuration, dataset version, random seed, model settings and evaluation results.

**Report limitations**

Results from a small public dataset or synthetic simulation should not be presented as proof of performance on a commercial operator network.

## 3. Data Quality Evaluation

Before evaluating analytical models, we need to understand the quality of the input data.

The ingestion pipeline should produce a quality report for every dataset.

We should measure:

| Metric | Purpose |
|---|---|
| Row count | Number of records loaded |
| Missing value rate | Percentage of missing values |
| Duplicate rate | Percentage of duplicate records |
| Invalid value count | Values outside defined constraints |
| Timestamp validity | Invalid or inconsistent timestamps |
| Schema validation | Whether required columns are present |
| Processing failures | Number of records that could not be processed |

The pipeline should also report how many records were accepted, rejected or modified during cleaning.

A successful ingestion run should not be interpreted as evidence that every source measurement is correct.

## 4. KPI Analytics Evaluation

KPI analytics primarily involves calculations and transformations, so its evaluation should focus on correctness.

Tests should verify:

- Aggregated values against manually calculated examples.
- Correct handling of missing measurements.
- Correct grouping by cell and time window.
- Correct units and timestamp handling.
- Consistency between individual and aggregated measurements.

For example, the average throughput calculated by the platform should match the expected result for a small test dataset.

We should also verify that KPI calculations behave sensibly when there are no measurements or when the input contains invalid values.

## 5. Anomaly Detection Evaluation

Anomaly detection should be evaluated using labelled data where possible.

Synthetic scenarios will be useful because we can deliberately introduce known abnormalities.

Examples include:

- Sudden throughput degradation.
- Unusual SINR reduction.
- Increased BLER.
- Abnormally high PRB utilisation.
- Unusual combinations of KPI changes.
- Gradual performance degradation.

Public datasets can provide realistic measurements, but they may not contain reliable anomaly labels. We should not invent ground-truth labels for real observations.

### 5.1 Baselines and Models

The initial comparison should include:

1. Fixed threshold rules.
2. Z-score detection.
3. IQR-based detection.
4. Isolation Forest.
5. Local Outlier Factor, if suitable for the data.

More advanced time-series or deep-learning approaches can be considered later.

### 5.2 Evaluation Metrics

| Metric | What it measures |
|---|---|
| Precision | How many detected anomalies are actually labelled anomalies |
| Recall | How many labelled anomalies are detected |
| F1-score | Balance between precision and recall |
| False positive rate | How often normal observations are incorrectly flagged |
| Detection delay | How long the system takes to detect an introduced incident |

Precision and recall are especially important because excessive false alarms make a monitoring system less useful.

Results should be reported per anomaly type as well as overall.

We should also examine whether the detector identifies the correct affected KPI and time interval.

## 6. KPI Forecasting Evaluation

Forecasting models should be tested on future observations that were not used during training.

We will compare more complex approaches against simple forecasting baselines.

Initial baselines:

- Last observed value.
- Moving average.
- Exponential smoothing.

Potential additional models:

- ARIMA.
- Random Forest or XGBoost.
- Neural forecasting models, if the available data justifies them.

### 6.1 Evaluation Metrics

**Mean Absolute Error (MAE)**

\[
MAE = \frac{1}{n}\sum_{i=1}^{n}|y_i-\hat{y}_i|
\]

**Root Mean Squared Error (RMSE)**

\[
RMSE = \sqrt{\frac{1}{n}\sum_{i=1}^{n}(y_i-\hat{y}_i)^2}
\]

**Mean Absolute Percentage Error (MAPE)**

\[
MAPE = \frac{100}{n}\sum_{i=1}^{n}
\left|\frac{y_i-\hat{y}_i}{y_i}\right|
\]

MAPE can be misleading when actual values are zero or close to zero. In those cases, we should use MAE, RMSE or another suitable metric.

Evaluation should be performed at multiple forecast horizons where enough data is available.

We should also compare performance across different cells and traffic conditions rather than relying on one overall average.

## 7. RAG Evaluation

The telecom RAG system needs separate evaluation of retrieval and answer generation.

A technically convincing answer is not necessarily a correctly grounded answer.

We will create a small evaluation dataset containing questions, expected source documents and relevant passages.

Example question:

"What are the possible effects of high BLER on user throughput?"

The expected result should identify relevant technical documentation and retrieve passages that support the answer.

### 7.1 Retrieval Evaluation

The initial metrics will include:

**Precision@K**

Measures how many of the top K retrieved passages are relevant.

**Recall@K**

Measures how many of the known relevant passages appear in the top K results.

**Mean Reciprocal Rank (MRR)**

Measures how highly the first relevant result appears.

**Normalized Discounted Cumulative Gain (nDCG@K)**

Measures ranking quality while accounting for the position and relevance of retrieved passages.

We should compare:

- BM25 retrieval.
- Dense vector retrieval.
- Hybrid retrieval.
- Hybrid retrieval with reranking.

This will help establish whether each additional retrieval component improves results.

### 7.2 Answer Evaluation

Generated answers should be assessed for:

- Correctness.
- Relevance.
- Grounding in retrieved passages.
- Citation correctness.
- Completeness.
- Unsupported claims.

We should include questions for which the knowledge base does not contain sufficient information.

In those cases, the system should say that it cannot find enough supporting information rather than inventing an answer.

Some answers can be evaluated using manually reviewed reference answers. Automated evaluation can supplement this process, but should not be treated as unquestionable ground truth.

## 8. Incident Investigation Agent Evaluation

The investigation agent combines several platform components, so it needs end-to-end evaluation.

We will create a collection of controlled incidents with known scenario conditions.

Examples:

- Sudden cell congestion.
- Increased interference.
- Degraded radio coverage.
- Abnormal BLER.
- Backhaul information delay.
- Multiple simultaneous performance problems.

For each scenario, we will record:

- Incident description.
- Affected cell.
- Time window.
- Underlying simulated condition.
- Expected analytical evidence.
- Plausible explanations.
- Relevant technical documents.

### 8.1 Evaluation Criteria

| Metric | Purpose |
|---|---|
| Cell identification accuracy | Whether the correct cell is investigated |
| Time-window accuracy | Whether the requested period is analysed correctly |
| Tool selection accuracy | Whether appropriate tools are called |
| Evidence accuracy | Whether reported findings match tool outputs |
| Hypothesis relevance | Whether suggested explanations fit the evidence |
| Citation accuracy | Whether references support the associated claims |
| Unsupported conclusion rate | How often the agent claims something not supported by evidence |
| Workflow completion rate | How often investigations complete successfully |

We should also measure how often the agent correctly reports that the available evidence is insufficient.

This is important because a system that always produces a confident diagnosis is not necessarily a reliable system.

### 8.2 Human Review

A sample of investigation reports should be reviewed manually.

The reviewer should assess whether:

- The measurements are represented correctly.
- The suggested explanations are reasonable.
- Important contradictory evidence is included.
- The report distinguishes observations from hypotheses.
- The recommended next checks are relevant.

The evaluation dataset should be kept separate from any examples used to tune prompts or diagnostic rules.

## 9. Network Simulation Evaluation

The simulation environment should be evaluated for reproducibility and internal consistency.

Tests should cover:

- Repeatability with fixed random seeds.
- Correct parameter handling.
- Expected behaviour when traffic demand changes.
- Expected behaviour when interference is introduced.
- Resource allocation constraints.
- KPI calculation correctness.
- Consistency of results across repeated runs.

We should also compare simplified models against analytical expectations or published reference results where a suitable comparison exists.

Simulation outputs should always include the configuration and assumptions used to generate them.

## 10. API and Application Evaluation

The backend and user interface should also be tested.

### API tests

- Valid requests return expected responses.
- Invalid inputs produce useful errors.
- Missing parameters are handled correctly.
- Large or unreasonable requests are limited.
- API responses follow the documented schema.

### Integration tests

- Data ingestion connects to KPI analytics.
- KPI analytics connects to anomaly detection.
- RAG returns source references.
- The agent can call the required tools.
- Reports contain the expected information.

### User interface tests

- Users can select a dataset.
- KPI charts display the selected data.
- Anomaly results are visible.
- Forecasts are displayed with appropriate context.
- Investigation reports can be inspected.
- Errors are communicated clearly.

## 11. Performance and Resource Evaluation

The project should remain practical to run without paid infrastructure.

We should record:

| Measurement | Purpose |
|---|---|
| Data ingestion time | Time needed to load and process a dataset |
| Query latency | Time required to retrieve analytical results |
| Retrieval latency | Time required for document retrieval |
| Generation latency | Time required to generate an answer |
| Investigation duration | Time required for a complete investigation |
| Memory usage | RAM required during execution |
| Model size | Storage required by local models |
| Tool call count | Number of operations used in an investigation |

Where applicable, we should compare local inference options and report the hardware used.

Performance results should distinguish between CPU and GPU execution.

We should not claim that a system is suitable for real-time network operations based only on tests performed on a laptop.

## 12. Experiment Tracking

Every important experiment should be recorded.

An experiment record should contain:

- Experiment ID.
- Date.
- Component.
- Dataset and version.
- Model or method.
- Configuration.
- Random seed.
- Evaluation metrics.
- Execution time.
- Hardware.
- Notes and observations.

A simple CSV or JSON record will be sufficient initially.

We can introduce MLflow later if experiment tracking becomes difficult to manage manually.

The important part is reproducibility, not the choice of tracking software.

## 13. Benchmark Results

The project should maintain a central benchmark summary.

For example:

| Component | Baseline | Candidate | Main metric |
|---|---|---|---|
| Anomaly detection | Z-score | Isolation Forest | F1-score |
| Forecasting | Last-value forecast | XGBoost | MAE |
| Retrieval | BM25 | Hybrid + reranking | nDCG@K |
| Incident diagnosis | Rule-based baseline | LangGraph agent | Evidence accuracy |
| Simulation | Baseline scenario | Modified scenario | KPI differences |

Actual results will be added after experiments are completed.

We should never fill this table with expected or invented performance improvements.

Where results are close, we should report that rather than presenting a small difference as a major achievement.

## 14. Implementation Order

Evaluation will be developed alongside the individual components.

The implementation order will be:

**Stage 1 — Unit tests**

Test data processing, KPI calculations and other core functions.

**Stage 2 — Data quality reports**

Record dataset validation results.

**Stage 3 — ML evaluation**

Build repeatable anomaly detection and forecasting benchmarks.

**Stage 4 — RAG evaluation**

Create a question-and-reference dataset and compare retrieval approaches.

**Stage 5 — Agent evaluation**

Create controlled incident scenarios and evaluate the investigation workflow.

**Stage 6 — Simulation evaluation**

Test reproducibility and expected scenario behaviour.

**Stage 7 — Integration tests**

Test communication between platform components.

**Stage 8 — Performance benchmarks**

Record latency, memory usage and execution time.

**Stage 9 — Publish results**

Add benchmark tables, plots and experiment descriptions to the repository.

## 15. Expected Outcome

The evaluation framework should make it possible to understand how well each part of the platform performs.

It should also make weaknesses visible.

The final repository should contain reproducible experiments, documented evaluation methods and actual benchmark results.

The goal is not to make every metric look impressive. It is to demonstrate that the platform has been tested carefully and that its results can be independently understood and reproduced.
