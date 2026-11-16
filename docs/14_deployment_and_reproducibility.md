# Deployment and Reproducibility

## 1. Purpose

The RAN Intelligence Platform should be straightforward to install and run on a local machine.

The project will initially be developed and tested locally, with Google Colab used for experiments that require additional GPU resources.

Docker will eventually provide a consistent way to run the application and its supporting services.

We will also explore a public demo using free hosting options. However, the main application should not depend on a paid cloud service or commercial model API.

This document describes the planned installation, configuration, execution and deployment process.

## 2. Development Environments

The project will support two main development environments.

### 2.1 Local Development

Local development will be used for:

- Python development.
- Data ingestion and processing.
- API development.
- Streamlit interface development.
- Unit and integration testing.
- Small and medium-sized experiments.
- Running local language models where hardware permits.

The local environment should be sufficient for developing most platform features.

### 2.2 Google Colab

Google Colab will be used for experiments that benefit from GPU acceleration.

Examples include:

- Training neural network models.
- Larger embedding experiments.
- Beamforming research experiments.
- Computationally intensive simulation runs.

Notebooks should be designed so that they can run independently and save their outputs in reproducible formats.

The project should not depend on a particular Colab runtime remaining available.

## 3. System Requirements

The initial application should have modest resource requirements.

Suggested development environment:

| Component | Recommendation |
|---|---|
| Operating system | Windows, Linux or macOS |
| Python | 3.11 or another explicitly supported version |
| RAM | 8 GB minimum; 16 GB or more recommended |
| Storage | Depends on datasets and local models |
| GPU | Optional |
| Internet | Required for initial dependency and dataset downloads |

Some advanced experiments and local language models may require more resources.

The project should provide lightweight alternatives wherever possible.

## 4. Python Environment Setup

Python dependencies should be managed through a project configuration file.

We will use a virtual environment to keep project dependencies separate from other Python installations.

Example setup on Windows:

```powershell
# Clone the repository
git clone https://github.com/PrashantSU/ran-intelligence.git

# Enter the project directory
cd ran-intelligence

# Create a virtual environment
py -3.11 -m venv .venv

# Activate the environment
.venv\Scripts\Activate.ps1

# Install the project
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

Example setup on Linux or macOS:

```bash
git clone https://github.com/PrashantSU/ran-intelligence.git
cd ran-intelligence

python3.11 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
pip install -e ".[dev]"
```

The exact installation command will be finalised when `pyproject.toml` is created.

## 5. Dependency Management

Dependencies should be documented and version-controlled.

The project should distinguish between:

- Core dependencies.
- Development dependencies.
- Optional ML dependencies.
- Optional local LLM dependencies.

This avoids forcing every user to install large machine learning libraries just to run basic functionality.

For example, a user interested only in KPI monitoring should not need to install every optional deep-learning dependency.

We should also avoid installing unnecessary packages simply because they are popular in the AI ecosystem.

## 6. Environment Configuration

The application should use environment variables for configurable paths and service settings.

An example configuration file will be provided:

```text
.env.example
```

Possible settings:

```dotenv
APP_ENV=development
API_HOST=127.0.0.1
API_PORT=8000

DATABASE_URL=sqlite:///./data/ran_intelligence.db

DATA_DIR=./datasets
MODEL_DIR=./models
DOCUMENT_DIR=./documents

LOG_LEVEL=INFO
```

These are example defaults. Actual settings may change during implementation.

The real `.env` file should be excluded from Git.

Credentials, access tokens and other secrets must never be committed to the public repository.

## 7. Running the Backend

FastAPI will provide the backend service.

During development, the API can be started using:

```bash
uvicorn app.api.main:app --reload --host 127.0.0.1 --port 8000
```

The API should be accessible locally.

FastAPI's interactive documentation will be available at:

```text
http://127.0.0.1:8000/docs
```

This will help developers inspect endpoints and test requests.

The health endpoint should also make it possible to check whether the backend is running.

## 8. Running the Streamlit Application

The Streamlit interface will run separately during development.

Example:

```bash
streamlit run app/streamlit_app/main.py
```

The application should connect to the configured FastAPI backend.

The default local development setup will use:

```text
http://127.0.0.1:8000
```

The backend URL should be configurable rather than hardcoded throughout the application.

## 9. Local Language Models

The project should support local language model inference where practical.

Ollama is one possible option for running models locally.

However, model selection should depend on:

- Available RAM and GPU memory.
- Model size.
- Quantisation.
- Response quality.
- Inference speed.
- Compatibility with the application.

The RAG and investigation workflows should be designed so that the language model provider can be changed without rewriting the entire platform.

Where a local model is unavailable, we should provide useful alternatives:

- Retrieval-only search.
- Precomputed demonstration answers.
- Mocked responses for automated tests.
- A clearly documented optional model integration.

The platform's core functionality should not require a paid API key.

## 10. Docker Deployment

Docker will be introduced after the basic local application works.

The initial container setup may contain:

- FastAPI backend.
- Streamlit frontend.
- Supporting storage directories.

A `docker-compose.yml` file should eventually make it possible to start the application with a single command.

Example intended usage:

```bash
docker compose up --build
```

The exact service definitions will depend on the final implementation.

Persistent volumes should be used for datasets, database files and other outputs that must survive container restarts.

Large language models should not automatically be downloaded during every container build.

They should be configured separately.

## 11. Data and Model Storage

The repository should not contain every raw dataset or model file.

Large files should be stored separately.

A possible local directory structure is:

```text
data/
├── raw/
├── processed/
├── external/
└── benchmark/

models/
├── anomaly_detection/
├── forecasting/
├── embeddings/
└── local_llm/

storage/
├── database/
├── vector_index/
└── reports/
```

These directories may be created at runtime and should be handled appropriately in `.gitignore`.

The repository should include small sample datasets and scripts for obtaining larger public datasets where permitted.

For each dataset, we should record:

- Original source.
- Download location.
- Licence or usage terms.
- Version or download date.
- Processing steps.
- Any known limitations.

We should not redistribute source documents or datasets without checking their terms.

## 12. Reproducible Experiments

Every important experiment should be reproducible as far as practical.

Each experiment should record:

- Dataset identifier and version.
- Code version or Git commit.
- Python version.
- Dependency versions.
- Model configuration.
- Random seed.
- Hardware information.
- Evaluation metrics.

Random seeds should be configured for Python, NumPy and relevant ML frameworks.

For GPU operations, exact reproducibility may not always be possible because of nondeterministic operations and hardware differences. This limitation should be documented.

Experiment scripts should be preferred over notebooks for repeatable execution.

Notebooks will remain useful for exploration and visualisation.

## 13. Public Demo

A public demonstration would make the project easier for recruiters and other developers to explore.

We will investigate free hosting options, including Streamlit Community Cloud, if the platform's resource requirements and current hosting terms allow it.

The public demo should prioritise features that can run within the available limits.

A practical demonstration could include:

- A small sample RAN dataset.
- KPI visualisation.
- Precomputed anomaly detection results.
- A limited forecasting example.
- Telecom document retrieval.
- A small number of precomputed incident investigations.
- Lightweight simulation scenarios.

The public demo does not need to run every advanced model continuously.

For example, GPU-heavy beamforming experiments can be demonstrated through saved experiment results and reproducible notebooks.

We should not expose a public application to unrestricted file uploads or unrestricted model execution.

## 14. Deployment Security

Before making the application publicly accessible, we should review:

- File upload restrictions.
- Request size limits.
- API input validation.
- Allowed file paths.
- Secret management.
- Database access.
- Error messages.
- Logging.
- Resource limits.

The public version should use only public or synthetic datasets.

It should not expose private research data, personal files or internal network information.

## 15. Installation and Usage Documentation

The repository README should eventually provide a clear quick-start guide.

It should explain:

1. What the project does.
2. What technologies it uses.
3. System requirements.
4. How to install dependencies.
5. How to configure the environment.
6. How to start the backend.
7. How to start the frontend.
8. How to load sample data.
9. How to run tests.
10. Where to find technical documentation.

Advanced development and experiment instructions can remain in separate documentation files.

## 16. Implementation Order

Deployment work will be introduced gradually.

**Stage 1 — Local Python setup**

Create the virtual environment and project dependency configuration.

**Stage 2 — Application configuration**

Add environment variable handling and `.env.example`.

**Stage 3 — Local execution**

Verify that FastAPI and Streamlit can run independently and communicate.

**Stage 4 — Storage setup**

Configure local database and data directories.

**Stage 5 — Optional local model support**

Add local inference without making it a mandatory dependency.

**Stage 6 — Docker**

Create container definitions and test persistent storage.

**Stage 7 — Reproducible experiments**

Record configurations, random seeds and experiment outputs.

**Stage 8 — Public demo preparation**

Select lightweight features and prepare sample data.

**Stage 9 — Deployment and security review**

Test the public configuration and remove unnecessary exposure.

## 17. Expected Outcome

A developer should be able to clone the repository, install its dependencies, load sample data and run the main application locally.

The project should also provide reproducible experiment instructions and a deployment option that does not require paid infrastructure.

The public demo will showcase the most useful features within realistic free hosting limits, while the complete research and experimentation environment remains available through the repository.
