# Performance and Scalability

## 1. Purpose

The RAN Intelligence Platform combines data processing, machine learning, document retrieval, simulation and an LLM-based investigation workflow.

These components have different computational requirements. Some operations involve processing large measurement datasets, while others require model inference or repeated database queries.

This document describes how we will measure and improve performance as the platform develops.

The objective is to keep the application responsive and make efficient use of available computing resources, without introducing unnecessary infrastructure.

## 2. Performance goals

The platform should aim for:

- Efficient loading and processing of network measurements.
- Responsive KPI dashboards.
- Reasonable execution times for anomaly detection and forecasting.
- Fast document retrieval.
- Controlled LLM inference and agent execution.
- Efficient simulation experiments.
- Reproducible performance measurements.

We will establish actual performance targets after measuring the first working implementations.

We should not claim performance improvements without benchmark results.

## 3. Data processing performance

Network measurement datasets can contain large numbers of rows and columns.

The data engineering pipeline should avoid unnecessary processing.

Practices include:

- Read only the required columns.
- Use appropriate numeric data types.
- Prefer vectorised Pandas and NumPy operations.
- Use Parquet for suitable processed datasets.
- Avoid repeatedly loading the same data.
- Process large files in chunks when necessary.
- Avoid unnecessary copies of large DataFrames.

For particularly large workloads, we can consider tools such as Polars or DuckDB.

These should be introduced only when measurements show that the existing implementation needs improvement.

## 4. Database performance

SQLite will be used initially because it is lightweight and requires no separate database server.

We should consider:

- Indexing frequently queried columns.
- Using appropriate data types.
- Avoiding unnecessary database queries.
- Using transactions for related updates.
- Separating large measurement files from application metadata.

Useful index candidates may include:

- Dataset ID.
- Cell ID.
- Timestamp.
- Experiment ID.
- Incident ID.

If concurrent access or data volume becomes a limitation, PostgreSQL can be considered later.

## 5. Machine learning performance

Different models have different computational requirements.

We should compare models using both predictive performance and execution cost.

Measurements may include:

- Training time.
- Prediction time.
- Memory usage.
- Model size.
- CPU utilisation.
- GPU utilisation, where applicable.

Simple baseline models should be retained when they provide sufficiently good results at much lower cost.

For deep learning experiments, Google Colab can be used when GPU acceleration is useful.

The main application should not require a GPU for basic KPI analytics or ordinary data exploration.

## 6. RAG performance

RAG performance depends on several stages:

1. Document extraction.
2. Chunking.
3. Embedding generation.
4. Vector indexing.
5. Keyword retrieval.
6. Hybrid result fusion.
7. Reranking.
8. Answer generation.

We should measure these stages separately.

Useful measurements include:

- Document ingestion time.
- Embedding generation time.
- Retrieval latency.
- Reranking latency.
- Generation latency.
- Total response time.
- Memory usage.

Embeddings and vector indexes should be reused rather than regenerated for every query.

The number of retrieved passages should be configurable because retrieving more documents does not always improve answer quality.

## 7. LLM inference performance

Local LLM inference can be one of the most resource-intensive parts of the platform.

We will consider:

- Model size.
- Quantisation.
- Available RAM and GPU memory.
- Context length.
- Prompt size.
- Output token count.
- Inference latency.

The system should support a configuration where analytical functionality remains available even if the local LLM is unavailable.

For example, KPI analysis, anomaly detection and basic incident evidence collection should not depend entirely on successful LLM inference.

We will prefer smaller models that can run within available hardware limits rather than assuming access to expensive GPUs.

## 8. Agent execution performance

An investigation agent may execute several tools before producing a report.

Unnecessary tool calls can increase response time and computational cost.

The workflow should:

- Use a defined investigation process.
- Avoid repeating successful tool calls.
- Limit the number of investigation steps.
- Set reasonable execution timeouts.
- Handle unavailable services.
- Avoid retrieving excessive document context.
- Preserve useful intermediate results.

The agent should collect enough evidence to support its conclusions without executing every available tool for every incident.

## 9. Simulation performance

Simulation performance depends on the size and complexity of the network scenario.

Important parameters include:

- Number of base stations.
- Number of UEs.
- Number of antennas.
- Simulation duration.
- Channel model complexity.
- Number of scheduling iterations.
- Number of experiment repetitions.

The initial simulation framework should support configurable scenarios.

We can use vectorised numerical operations and NumPy where appropriate.

More computationally expensive experiments can run in Colab.

Simulation performance should be measured separately from the Streamlit interface.

## 10. Application responsiveness

The Streamlit interface should avoid unnecessary recomputation.

We can use Streamlit caching for suitable operations, such as:

- Loading processed datasets.
- Reading experiment results.
- Loading configuration files.
- Reusing prepared analytical outputs.

Cache invalidation must be considered when the underlying data or configuration changes.

Long-running tasks should provide progress information where possible rather than leaving users uncertain about whether an operation is still running.

## 11. Performance benchmarks

Each major component should have relevant benchmarks.

| Component | Measurements |
|---|---|
| Data ingestion | Processing time, rows per second, memory |
| KPI analytics | Calculation time |
| Anomaly detection | Prediction time, memory |
| Forecasting | Prediction time and model size |
| RAG retrieval | Retrieval latency and quality |
| Reranking | Additional latency and quality change |
| LLM generation | Response time and token throughput |
| Incident agent | Total execution time and tool calls |
| Simulation | Runtime per scenario |
| API | Response latency and throughput |

Benchmarks should record the machine, software versions, dataset and configuration used.

Results from different hardware environments should not be compared without acknowledging the differences.

## 12. Caching strategy

Caching can reduce repeated computation.

Potential caching targets include:

- Processed datasets.
- KPI aggregations.
- Embeddings.
- Vector indexes.
- Model loading.
- Repeated retrieval results.
- Simulation outputs.

Cached results should be associated with the relevant dataset and configuration versions.

A cache should never silently return stale results after important inputs have changed.

## 13. Resource limits

The application should avoid operations that consume unlimited resources.

Examples include:

- Very large file uploads.
- Excessive document ingestion.
- Unrestricted agent loops.
- Extremely long LLM prompts.
- Large simulation configurations.
- Too many concurrent model requests.

Reasonable limits should be configurable.

The application should return clear messages when a requested operation exceeds the supported limits.

## 14. Scaling strategy

The project will begin as a modular application running locally.

Scaling will be introduced only when there is a clear need.

Possible future improvements include:

- PostgreSQL for concurrent application access.
- Background workers for long-running tasks.
- Batch processing for large measurement datasets.
- Dedicated inference services.
- More efficient vector indexing.
- Separate deployment of computationally expensive components.

We will not introduce distributed infrastructure simply to make the architecture look more advanced.

## 15. Performance evaluation process

Performance improvements will follow a consistent process:

1. Identify a component that is slow or resource-intensive.
2. Establish a baseline measurement.
3. Identify the likely bottleneck.
4. Implement a targeted improvement.
5. Repeat the benchmark under the same conditions.
6. Compare performance and verify that functionality remains correct.
7. Record the result.

This prevents unnecessary optimisation and gives us evidence for technical decisions.

## 16. Implementation order

Performance measurement will be introduced progressively.

**First:** Record execution time and memory usage for major operations.

**Second:** Improve data loading, transformations and database queries.

**Third:** Measure ML model training and inference.

**Fourth:** Benchmark retrieval, reranking and generation separately.

**Fifth:** Measure agent execution and simulation runtime.

**Finally:** Apply optimisations based on observed bottlenecks.

The goal is to build a platform that performs reasonably well on accessible hardware and can be improved systematically as its workload grows.
