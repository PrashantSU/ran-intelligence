# Incident Investigation Agent

## 1. Purpose

The incident investigation agent will help engineers investigate potential problems in a 4G or 5G radio access network.

Instead of asking an engineer to manually inspect several dashboards and technical documents, the agent will coordinate different platform components and collect relevant evidence.

For example, an engineer might report:

"Cell C102 has experienced a significant throughput drop during the last 30 minutes. Investigate the possible reasons."

The agent should be able to:

1. Understand the incident description.
2. Identify the affected cell and time window.
3. Retrieve the relevant network measurements.
4. Examine KPI trends.
5. Check whether anomalies have been detected.
6. Compare performance with historical measurements or neighbouring cells.
7. Retrieve relevant telecom documentation.
8. Rank plausible explanations.
9. Generate an investigation report.

The agent will provide decision support. It will not make changes to a live network or automatically execute network configuration commands.

## 2. Design Principles

The investigation workflow should follow a few important principles.

**Evidence before conclusions**

The agent should collect measurements and supporting information before suggesting a cause.

**Use tools for calculations**

KPI statistics, anomaly scores and forecasting results should come from the platform's analytical modules rather than being calculated from memory by the language model.

**Keep uncertainty visible**

The system should distinguish between observed facts, possible explanations and confirmed causes.

**Controlled tool access**

The agent should only have access to explicitly defined tools. It should not execute arbitrary code or access unrestricted system resources.

**Human review**

An engineer should review the investigation results before taking any operational action.

## 3. Incident Input

The investigation can begin with a structured incident request or a natural-language description.

An initial incident request may contain:

| Field | Description |
|---|---|
| incident_id | Unique incident identifier |
| description | Engineer's description of the problem |
| cell_id | Affected cell, if known |
| start_time | Beginning of the investigation window |
| end_time | End of the investigation window |
| affected_kpi | KPI associated with the reported problem, if known |
| severity | Reported incident severity, if available |
| additional_context | Other information provided by the engineer |

The agent should identify missing information before starting the investigation.

For example, if the user does not specify a cell, the agent may ask for clarification or investigate a broader dataset if the request permits it.

It should not invent cell identifiers or timestamps.

## 4. Agent Architecture

LangGraph will be used to coordinate the investigation workflow.

The agent will operate as a stateful process. Each stage will update the investigation state and pass its results to the next stage.

The initial workflow will look like this:

```text
Incident Request
       |
       v
Input Understanding
       |
       v
Incident Validation
       |
       v
Data Retrieval
       |
       v
KPI Analysis
       |
       v
Anomaly Investigation
       |
       v
Historical / Neighbour Comparison
       |
       v
Technical Document Retrieval
       |
       v
Hypothesis Assessment
       |
       v
Report Generation
       |
       v
Engineer Review
```

Some stages may be conditional.

For example, neighbour comparison should only run when suitable cell relationship information is available.

Similarly, forecasting should be used only when there is enough historical data to support a meaningful prediction.

## 5. Investigation Tools

The language model should interact with the platform through controlled tools.

Each tool will have a defined input and output.

### 5.1 Network Data Retrieval

Retrieves measurements for a specified cell and time range.

Possible inputs:

- Cell identifier.
- Start time.
- End time.
- Requested KPIs.

Expected output:

- Matching measurements.
- Available KPI fields.
- Measurement count.
- Data availability information.

### 5.2 KPI Summary

Calculates descriptive statistics for selected measurements.

Possible outputs:

- Mean and median.
- Minimum and maximum.
- Percentiles.
- KPI changes over time.
- Missing measurement information.

### 5.3 Anomaly Detection

Runs or retrieves anomaly detection results for the selected measurements.

Expected output:

- Detected anomalies.
- Affected KPIs.
- Detection method.
- Anomaly score.
- Relevant timestamps.

### 5.4 Historical Comparison

Compares current measurements against a suitable historical reference period.

Examples:

- Current throughput against previous periods.
- Current SINR against historical behaviour.
- Current cell performance against its baseline.

The comparison should use comparable time periods when possible.

### 5.5 Neighbouring Cell Comparison

Compares the affected cell with neighbouring cells.

This can help determine whether a performance change appears isolated or affects multiple cells.

The tool should only be used when cell relationship information and sufficient measurements are available.

### 5.6 KPI Forecasting

Retrieves forecasts for selected KPIs.

This may help determine whether observed measurements differ from expected behaviour.

Forecasts should be treated as additional evidence, not proof of an incident cause.

### 5.7 Telecom Document Search

Searches the RAG knowledge base for technical information relevant to the incident.

For example, an investigation involving high BLER and reduced throughput may retrieve documentation related to radio link quality, retransmissions and transmission reliability.

The tool should return supporting passages and their source metadata.

### 5.8 Report Generation

Combines the investigation results into a structured report.

The language model can help explain the findings, but numerical results and source references must come from the underlying tools.

## 6. Investigation State

LangGraph will maintain a shared state throughout the investigation.

The initial state may contain:

| Field | Description |
|---|---|
| incident_request | Original engineer request |
| incident_details | Structured incident information |
| dataset_context | Selected dataset and available measurements |
| kpi_results | Results from KPI analytics |
| anomaly_results | Results from anomaly detection |
| historical_results | Historical comparison results |
| neighbour_results | Neighbouring-cell comparison results |
| forecast_results | Available forecasting results |
| retrieved_documents | Technical passages from RAG |
| hypotheses | Candidate explanations |
| investigation_status | Current workflow status |
| final_report | Generated investigation report |

Not every field will contain a result in every investigation.

Unavailable information should be recorded explicitly instead of being silently omitted.

## 7. Hypothesis Assessment

This is one of the most important parts of the investigation workflow.

The agent should produce possible explanations based on the collected evidence.

For example:

| Possible explanation | Evidence to examine |
|---|---|
| Radio interference | Reduced SINR, increased BLER, changes in neighbouring-cell conditions |
| Poor coverage | Low RSRP and persistent weak signal conditions |
| Resource congestion | High PRB utilisation and increased traffic demand |
| Backhaul-related issue | Evidence of transport degradation or delayed information exchange |
| Handover problems | Handover failures and mobility-related interruptions |

These are examples of investigation paths, not universal diagnostic rules.

The agent should not infer a cause from a single KPI.

For example, low SINR alone does not prove interference. Other measurements and network context are required.

### 7.1 Evidence Classification

Each finding should be classified as one of the following:

**Observed evidence**

A directly measured value or a result returned by an analytical tool.

Example: "Average SINR decreased from the historical baseline during the selected time window."

**Supported hypothesis**

A possible explanation supported by multiple observations.

Example: "Interference is a plausible explanation because SINR decreased while BLER increased."

**Confirmed cause**

A cause supported by sufficiently strong independent evidence or an authoritative incident record.

The agent should not label a hypothesis as confirmed simply because the language model considers it likely.

### 7.2 Hypothesis Ranking

The system should rank hypotheses based on the available evidence.

The initial version will use rule-based reasoning supported by analytical results.

Later versions may introduce a structured scoring approach.

Any numerical score should have a documented definition. It should not be presented as a statistically calibrated probability unless it has been validated as one.

## 8. Investigation Report

Each completed investigation should produce a structured report.

The report should contain:

1. Incident summary.
2. Affected cell and time window.
3. Data availability.
4. Observed KPI changes.
5. Detected anomalies.
6. Historical and neighbouring-cell comparisons.
7. Relevant forecasting results, if available.
8. Retrieved technical references.
9. Ranked hypotheses.
10. Supporting and contradicting evidence.
11. Missing information.
12. Recommended next checks.
13. Investigation limitations.

The report should clearly separate measurements from interpretations.

It should also retain the source of every important result so that an engineer can verify the findings.

## 9. Human Review

The platform will include a review stage.

An engineer should be able to:

- Inspect the collected evidence.
- Open supporting technical documents.
- Review the suggested explanations.
- Mark a hypothesis as useful or incorrect.
- Add investigation notes.
- Record the actual confirmed cause when it becomes available.

Feedback may later be used to improve the diagnostic workflow and build a labelled evaluation dataset.

The system will remain advisory. It will not automatically modify network parameters or issue live network control commands.

## 10. Error Handling and Safety

The investigation workflow should handle incomplete data and tool failures.

Examples:

| Situation | Expected behaviour |
|---|---|
| Unknown cell identifier | Request clarification or report the issue |
| Missing measurements | Explain which data is unavailable |
| Insufficient historical data | Skip historical comparison |
| RAG retrieval failure | Continue with available analytical evidence |
| Forecasting failure | Continue without forecast results |
| Conflicting evidence | Report the disagreement |
| Agent cannot identify a plausible explanation | State that the cause remains unknown |

The agent should not fabricate measurements, document references or tool results.

Tool calls should use validated arguments and have appropriate limits on the requested time range and amount of data.

## 11. Proposed Python Module Structure

```text
src/
└── ran_intelligence/
    └── agents/
        ├── __init__.py
        ├── state.py
        ├── tools.py
        ├── prompts.py
        ├── workflow.py
        ├── investigation.py
        ├── hypothesis.py
        └── report.py
```

Responsibilities:

- `state.py`: Define the shared investigation state.
- `tools.py`: Define controlled tools for analytics and retrieval.
- `prompts.py`: Store prompts used by the agent.
- `workflow.py`: Define the LangGraph workflow.
- `investigation.py`: Start and manage investigations.
- `hypothesis.py`: Assess and rank candidate explanations.
- `report.py`: Generate structured investigation reports.

The structure may change as the workflow becomes more detailed.

## 12. Evaluation

The agent will be evaluated using controlled incident scenarios.

Synthetic data will be particularly useful because we can generate incidents with known underlying causes.

The evaluation should examine:

- Whether the agent identifies the affected cell correctly.
- Whether it retrieves the correct time window.
- Whether it calls the appropriate analytical tools.
- Whether its findings match the tool outputs.
- Whether its hypotheses are supported by evidence.
- Whether it avoids claiming unsupported causes.
- Whether citations point to the correct documents.
- Whether the final report contains all important findings.
- Whether the workflow handles missing data and tool failures.

We should also measure execution time, number of tool calls and failure rate.

A successful tool execution does not necessarily mean the diagnosis is correct. These should be evaluated separately.

## 13. Implementation Order

The agent will be developed incrementally.

**Stage 1 — Define the investigation state**

Create the structured state and incident input format.

**Stage 2 — Implement analytical tools**

Connect KPI analytics, anomaly detection and historical comparison.

**Stage 3 — Connect RAG**

Allow the agent to retrieve technical documentation and supporting passages.

**Stage 4 — Build the LangGraph workflow**

Implement the investigation stages and conditional transitions.

**Stage 5 — Add hypothesis assessment**

Generate and rank candidate explanations using collected evidence.

**Stage 6 — Generate reports**

Produce structured reports with evidence, citations and uncertainty.

**Stage 7 — Add human review**

Allow engineers to inspect findings and record feedback.

**Stage 8 — Evaluate the workflow**

Test the agent against synthetic incidents with known causes and record its performance.

## 14. Expected Outcome

The incident investigation agent should provide a structured way to investigate network performance problems.

An engineer should be able to submit an incident request and receive an investigation report containing relevant measurements, anomaly results, technical references and plausible explanations.

The main objective is to reduce the amount of manual searching and analysis required while keeping the engineer in control of the final diagnosis and any operational decision.
