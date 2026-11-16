# Data Ingestion and Quality

## 1. Purpose

The data ingestion pipeline is the entry point for network measurements in the RAN Intelligence Platform.

Its job is to take data from different sources, inspect and validate it, convert it into a consistent internal format, and make it available to the analytics and machine learning components.

The pipeline should be reusable. Adding a new dataset should not require rewriting the KPI analytics or incident investigation components.

The first implementation will use the AERPAW Ericsson 5G dataset. Other public datasets and synthetic measurements will be added later.

## 2. Ingestion Workflow

The ingestion process will follow these stages:

```text
Data Source
    |
    v
File Loading
    |
    v
Source Inspection
    |
    v
Schema Mapping
    |
    v
Data Validation
    |
    v
Data Cleaning
    |
    v
Processed Dataset
    |
    v
Storage and Analytics
```

Each stage should have a clear responsibility. This will make it easier to identify problems when a dataset contains unexpected columns, missing values or inconsistent measurements.

## 3. Supported Input Formats

The initial pipeline should support common formats used in public research datasets.

| Format | Purpose | Library |
|---|---|---|
| CSV | Tabular measurements | Pandas |
| JSON | Structured records and metadata | Python JSON |
| Parquet | Efficient columnar storage | Pandas / PyArrow |
| TXT | Logs and simple measurement files | Python |

We will add other formats only when a selected dataset requires them.

The first version will prioritise CSV because it is sufficient for the initial AERPAW dataset.

## 4. Pipeline Components

### 4.1 File Loading

The loader reads the source files and returns a structured representation for inspection.

Responsibilities:

- Identify supported file formats.
- Load files without modifying the original data.
- Report file loading errors.
- Record the source filename.
- Preserve the original column names.
- Avoid silently skipping unreadable files.

The loader should not make assumptions about the meaning of columns. That belongs to the schema mapping stage.

### 4.2 Source Inspection

Different datasets may represent the same measurement in different ways.

For example, one dataset may use `RSRP`, while another uses `ss_rsrp_dbm`.

The inspection stage should report:

- Available columns.
- Data types.
- Number of records.
- Missing values.
- Duplicate records.
- Minimum and maximum values for numeric columns.
- Timestamp format and sampling intervals.
- Possible measurement units.

The output should help us understand the dataset before applying transformations.

### 4.3 Schema Mapping

The schema mapping stage converts source-specific column names into the platform's common schema.

For example:

| Original column | Internal field |
|---|---|
| RSRP | rsrp_dbm |
| SINR | sinr_db |
| CQI | cqi |
| MCS | mcs |
| Throughput | throughput_mbps |

These are illustrative mappings. The actual mapping will be confirmed after inspecting the source files.

The mapping configuration should be kept separate from the transformation code. This will make it easier to support additional datasets.

### 4.4 Data Validation

Validation checks whether the measurements are structurally and logically usable.

The initial checks should include:

- Required columns are present.
- Numeric fields contain valid numeric values.
- Timestamps can be parsed.
- Identifiers are not unexpectedly empty.
- Measurement values are within plausible ranges.
- Duplicate records are identified.
- Missing values are reported.
- Units are consistent with the expected schema.

Validation should produce a report rather than simply returning a pass or fail result.

A dataset may be partially usable even when some fields are missing.

### 4.5 Data Cleaning

Cleaning should be conservative. We should avoid removing measurements simply because they look unusual.

Initial cleaning operations may include:

- Converting timestamps into a consistent datetime representation.
- Converting numeric columns to appropriate types.
- Normalising column names.
- Removing exact duplicate records when appropriate.
- Handling invalid values.
- Standardising units where conversion is well defined.
- Recording missing-value counts.

We should preserve the original measurements and document any transformation.

Outliers should generally be flagged for investigation rather than automatically deleted. An unusually low SINR or high BLER could represent a genuine network condition.

### 4.6 Processed Data Storage

After validation and cleaning, the pipeline should save the processed dataset separately from the original files.

The initial storage formats will be:

- CSV for easy inspection and sharing.
- Parquet for efficient analytical workloads.

SQLite will be introduced for application-level structured data, such as incident records, dataset metadata and analysis results.

The first implementation does not need a complex distributed storage system.

## 5. Data Quality Report

Each ingestion run should produce a basic data quality report.

The report should include:

| Metric | Description |
|---|---|
| Total records | Number of rows loaded |
| Valid records | Records passing the required checks |
| Invalid records | Records failing validation |
| Duplicate records | Number of duplicate rows |
| Missing values | Missing count per field |
| Timestamp range | Earliest and latest measurement |
| Data types | Detected types for each column |
| Validation warnings | Unusual or suspicious values |
| Processing status | Success, partial success or failure |

The report should also identify which source file was processed and which transformations were applied.

This information will be useful when debugging model results or comparing datasets.

## 6. Error Handling

The pipeline should handle common failures without silently producing misleading output.

Examples:

| Problem | Expected behaviour |
|---|---|
| Missing input file | Report the missing file |
| Unsupported format | Stop processing and explain the issue |
| Missing required columns | Report the missing columns |
| Invalid timestamps | Report affected records |
| Invalid numeric values | Flag or handle according to the field |
| Empty dataset | Stop processing |
| Partial data quality failure | Save a report and indicate partial success |

Errors should be logged with enough context to identify the source and processing stage.

## 7. Reproducibility and Data Lineage

Every processed dataset should be traceable to its original source.

We should record:

- Dataset identifier.
- Original filename.
- Source URL.
- Download date.
- Processing date.
- Schema version.
- Processing configuration.
- Number of input and output records.
- Validation results.

For synthetic datasets, we should additionally record the generation parameters and random seed.

This will help reproduce experiments and understand how a particular dataset was created.

## 8. Proposed Python Module Structure

The ingestion functionality will live inside the main Python package.

```text
src/
└── ran_intelligence/
    └── ingestion/
        ├── __init__.py
        ├── loaders.py
        ├── inspection.py
        ├── schema_mapping.py
        ├── validation.py
        ├── cleaning.py
        └── pipeline.py
```

Responsibilities:

- `loaders.py`: Read supported file formats.
- `inspection.py`: Inspect columns, types and basic statistics.
- `schema_mapping.py`: Map source columns to internal fields.
- `validation.py`: Check structural and logical data quality.
- `cleaning.py`: Apply documented transformations.
- `pipeline.py`: Coordinate the complete ingestion workflow.

The structure may be adjusted as implementation progresses.

## 9. Testing Strategy

The ingestion pipeline should be tested with small datasets before processing larger files.

Initial tests should cover:

1. Loading a valid CSV file.
2. Handling a missing file.
3. Detecting missing columns.
4. Converting valid timestamps.
5. Identifying duplicate records.
6. Detecting invalid numeric values.
7. Reporting missing values.
8. Applying schema mappings correctly.
9. Saving processed data.
10. Reproducing the same output from the same input and configuration.

We will use Pytest for automated testing.

Small synthetic test files will be created so that the tests do not depend on downloading public datasets every time.

## 10. Implementation Plan

The implementation will be incremental.

**Stage 1 — Inspect the first dataset**

- Download the AERPAW Ericsson dataset.
- Identify its files and formats.
- Inspect the original columns.
- Check measurement units and timestamps.
- Create a source-specific data dictionary.

**Stage 2 — Build the basic loader**

- Implement CSV loading.
- Add basic file and format validation.
- Generate an inspection report.

**Stage 3 — Add schema mapping**

- Define the AERPAW column mappings.
- Convert the measurements into the common schema.
- Handle unavailable fields appropriately.

**Stage 4 — Add validation and cleaning**

- Implement data quality checks.
- Report missing and invalid values.
- Apply documented cleaning operations.

**Stage 5 — Save processed data**

- Export the processed dataset.
- Save the data quality report.
- Record dataset metadata.

**Stage 6 — Test the pipeline**

- Add unit tests.
- Test error handling.
- Verify that the same input produces reproducible output.

## 11. Expected Outcome

At the end of this stage, the platform should have a working and reusable ingestion pipeline.

We should be able to load the AERPAW dataset, inspect its structure, map its measurements into the internal schema, validate the data and save a processed version.

The same pipeline design should then make it easier to introduce FCCLab measurements, Colosseum datasets and synthetic network data.

The priority is correctness and traceability, not building a complicated data engineering system before we need one.
