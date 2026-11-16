# Experiment Tracking

## 1. Purpose

The RAN Intelligence Platform will contain several machine learning, retrieval and simulation experiments.

As we develop these components, we will try different algorithms, configurations, datasets and parameters. We need a consistent way to record what was tested and what results were obtained.

Experiment tracking will help us:

- Reproduce previous results.
- Compare different approaches fairly.
- Understand why one configuration performs better than another.
- Identify regressions when code changes.
- Keep research results separate from assumptions.
- Present credible experimental evidence in the project documentation.

We will begin with lightweight experiment records rather than introducing a complex experiment-management platform.

## 2. What counts as an experiment?

An experiment is a recorded execution of a model, algorithm or simulation under a defined configuration.

Examples include:

| Area | Example experiment |
|---|---|
| Anomaly detection | Isolation Forest compared with an IQR baseline |
| Forecasting | Moving average compared with XGBoost |
| RAG | BM25 compared with vector retrieval and hybrid retrieval |
| Reranking | Retrieval results before and after reranking |
| Incident investigation | Different tool sequences and hypothesis-ranking methods |
| Simulation | Round-robin scheduling compared with proportional fair scheduling |
| Beamforming | Comparison of selected beamforming strategies |
| Backhaul delay | Performance with and without delayed information |

A change to an important parameter or dataset should generally produce a new experiment record.

## 3. Experiment metadata

Every experiment should record the following information.

| Field | Description |
|---|---|
| `experiment_id` | Unique experiment identifier |
| `experiment_name` | Short descriptive name |
| `component` | Component being evaluated |
| `created_at` | Experiment execution time |
| `dataset_id` | Dataset used |
| `dataset_version` | Dataset version |
| `model_name` | Algorithm or model |
| `parameters` | Model and experiment configuration |
| `random_seed` | Random seed, where applicable |
| `code_version` | Git commit or code version |
| `environment` | Python and relevant library versions |
| `metrics` | Evaluation results |
| `notes` | Observations and limitations |

Not every experiment requires every field. For example, a retrieval experiment may not have a random seed, while a machine learning experiment usually should record one.

## 4. Experiment record example

A record could look like this:

```json
{
  "experiment_id": "anom_001",
  "experiment_name": "Isolation Forest baseline",
  "component": "anomaly_detection",
  "created_at": "2026-11-16T14:00:00Z",
  "dataset_id": "aerpaw_5g_v1",
  "model_name": "IsolationForest",
  "parameters": {
    "n_estimators": 100,
    "contamination": 0.05,
    "random_state": 42
  },
  "random_seed": 42,
  "metrics": {
    "precision": null,
    "recall": null,
    "f1_score": null
  },
  "notes": "Initial baseline. Evaluation pending."
}
```

The null metric values are intentional. We should only populate them after running the experiment.

## 5. Tracking machine learning experiments

For anomaly detection and forecasting, we will record:

- Training and evaluation datasets.
- Feature selection.
- Preprocessing steps.
- Model type.
- Hyperparameters.
- Random seed.
- Train, validation and test periods.
- Evaluation metrics.
- Model execution time.

For time-series problems, the data split must preserve chronological order.

We should not compare models using different test periods without explaining the difference.

## 6. Tracking RAG experiments

RAG experiments require additional information.

We will record:

- Document collection and version.
- Chunk size and overlap.
- Embedding model.
- Vector index configuration.
- Keyword retrieval configuration.
- Number of retrieved passages.
- RRF parameters.
- Reranker model, if used.
- Generation model and prompt version.
- Evaluation dataset and results.

Retrieval quality and answer quality should be evaluated separately.

A better retrieval score does not automatically guarantee a better final answer.

## 7. Tracking simulation experiments

Simulation experiments must record the configuration that determines the simulated environment.

Examples include:

- Number of base stations.
- Number of UEs.
- Number of antennas.
- Channel assumptions.
- Traffic generation parameters.
- Scheduling policy.
- Beamforming configuration.
- Interference assumptions.
- Backhaul delay.
- Simulation duration.

The results should include relevant network metrics such as throughput, spectral efficiency, outage probability and edge-user performance, depending on the experiment.

Simulation assumptions must be recorded alongside the results.

## 8. Experiment comparison

Experiments should be compared using consistent evaluation conditions.

For example, an anomaly detection comparison might look like this:

| Method | Precision | Recall | F1 |
|---|---:|---:|---:|
| IQR baseline | Pending | Pending | Pending |
| Z-score | Pending | Pending | Pending |
| Isolation Forest | Pending | Pending | Pending |

These are placeholders, not measured results.

The comparison should use the same labelled evaluation data and consistent preprocessing.

For stochastic methods, we may repeat experiments with multiple seeds and report mean and standard deviation.

## 9. Storage structure

Experiment records will be stored separately from large model outputs and datasets.

The initial structure will be:

```text
experiments/
├── anomaly_detection/
│   ├── configs/
│   ├── results/
│   └── README.md
├── forecasting/
│   ├── configs/
│   ├── results/
│   └── README.md
├── retrieval/
│   ├── configs/
│   ├── results/
│   └── README.md
├── diagnosis/
│   ├── configs/
│   ├── results/
│   └── README.md
└── simulation/
    ├── configs/
    ├── results/
    └── README.md
```

Small configuration files and result summaries can be committed to GitHub.

Large model checkpoints, raw datasets and generated artefacts should remain outside Git unless there is a clear reason to include them.

## 10. Tools

We will start with:

- JSON or YAML for experiment configurations.
- CSV or JSON for result summaries.
- Git for tracking code changes.
- Python scripts and notebooks for execution.
- SQLite for application-level experiment metadata where needed.

MLflow is a possible later addition if experiment tracking becomes difficult to manage manually.

We will not introduce it before there is a practical need.

## 11. Reproducibility requirements

Before considering an experiment complete, we should be able to identify:

1. Which code version produced the result?
2. Which dataset and version were used?
3. Which preprocessing steps were applied?
4. Which parameters were selected?
5. Which evaluation procedure was followed?
6. What metrics were obtained?
7. What limitations affect the interpretation?

Where possible, another developer should be able to reproduce the experiment using the recorded configuration.

Exact reproducibility may not always be possible across different hardware, library versions or nondeterministic operations. Such limitations should be documented.

## 12. Reporting results

Each important experiment should have a short report containing:

- Objective.
- Dataset.
- Method.
- Configuration.
- Evaluation procedure.
- Results.
- Comparison with a baseline.
- Observations.
- Limitations.
- Next steps.

We should report negative results as well. An approach that performs poorly can still provide useful information about the problem.

## 13. Implementation order

We will introduce experiment tracking gradually.

**First:** Create a common experiment metadata format.

**Second:** Record anomaly detection experiments.

**Third:** Add forecasting and RAG experiment records.

**Fourth:** Add simulation experiment configurations and results.

**Finally:** Integrate experiment summaries into the platform dashboard.

The objective is to make every important result traceable without spending more time managing experiments than actually running them.
