# Security and Privacy

## 1. Purpose

The RAN Intelligence Platform will process network measurements, configuration information, technical documents and incident reports. Some of this information may be sensitive, even when it does not contain personal data.

Security needs to be considered throughout the platform, including data ingestion, APIs, document retrieval, LLM interactions and experiment storage.

The platform is designed for analysis and investigation. It will not connect to or make changes to a live mobile network.

## 2. Security principles

The following principles will guide implementation:

- Use public or independently generated data for the portfolio project.
- Do not include confidential company information, credentials or proprietary datasets.
- Validate data before processing it.
- Restrict access to application resources.
- Keep secrets outside source code.
- Treat documents and retrieved text as untrusted input.
- Require human review before accepting important diagnostic conclusions.
- Keep the incident investigation agent restricted to approved tools.

Security should be part of the implementation rather than something added at the end.

## 3. Data protection

### 3.1 Data sources

The initial project will use public datasets, public technical documentation and synthetic network measurements.

We will not use:

- Confidential Huawei or other operator datasets.
- Internal company source code or configuration files.
- Private customer or subscriber information.
- Credentials or access tokens from external systems.

Public datasets must still be checked for licensing and redistribution restrictions.

### 3.2 Data validation

Files uploaded by users should be validated before processing.

Validation should include:

- Allowed file formats.
- File size limits.
- Required columns.
- Expected data types.
- Valid timestamp formats.
- Numeric ranges and missing values.
- Unexpected or malformed content.

Files should not be trusted simply because they have a CSV, JSON or PDF extension.

### 3.3 Sensitive information

The application should avoid collecting personally identifiable information.

If a dataset contains subscriber identifiers, phone numbers, IP addresses or other potentially sensitive fields, those fields should be excluded or anonymised where possible.

The platform should not claim that anonymisation guarantees complete privacy.

## 4. API security

The FastAPI backend will expose endpoints for data ingestion, analytics, retrieval, incident investigation and reporting.

The following protections should be considered:

- Validate request bodies using defined schemas.
- Restrict accepted file types and upload sizes.
- Handle invalid requests safely.
- Avoid exposing internal file paths.
- Avoid returning stack traces to users.
- Apply rate limits if the application becomes publicly accessible.
- Restrict administrative operations.
- Use HTTPS for deployed environments.

During local development, the API may run without user authentication. A publicly deployed application should not expose sensitive operations without appropriate access controls.

## 5. Secrets and configuration

API keys, passwords and tokens must never be committed to GitHub.

Configuration should be separated from source code.

Example:

```text
.env
.env.example
```

The `.env` file contains local secrets and must be excluded from Git.

The `.env.example` file contains only placeholder values showing which configuration variables are required.

Example:

```env
APP_ENV=development
DATABASE_URL=sqlite:///./data/ran_intelligence.db
MODEL_PROVIDER=local
MODEL_NAME=
API_KEY=
```

The application should fail safely when a required secret is missing rather than silently using an insecure default.

## 6. Document ingestion security

The RAG system will process technical documents from sources such as 3GPP, ETSI, O-RAN and research publications.

Retrieved documents must be treated as reference material, not as instructions for the application or its agent.

Document ingestion should include:

- File type validation.
- File size limits.
- Safe text extraction.
- Protection against malformed files.
- Source and version metadata.
- Duplicate detection where practical.
- Clear separation between document content and system instructions.

Only approved document sources should be included in the initial knowledge base.

## 7. Prompt injection and LLM security

A major risk in LLM applications is prompt injection.

A document or user-provided input may contain text designed to manipulate the model into ignoring its instructions, revealing information or performing an unintended action.

The RAG and agent components must therefore follow these rules:

1. Retrieved documents are untrusted information.
2. User input cannot override system-level instructions.
3. The model must not treat retrieved text as executable instructions.
4. Tool access must be restricted to explicitly defined operations.
5. Tool arguments must be validated before execution.
6. Sensitive configuration and secrets must never be included in model context.
7. The model must not be allowed to execute arbitrary shell commands or unrestricted Python code.

Prompt instructions alone are not a sufficient security boundary. Restrictions must also be enforced in the application code.

## 8. Incident investigation agent restrictions

The incident investigation agent will collect evidence and generate diagnostic reports.

Its tools should be limited to operations such as:

- Querying approved network measurements.
- Retrieving technical documentation.
- Running predefined KPI calculations.
- Executing approved anomaly detection models.
- Running controlled simulation experiments.
- Generating incident reports.

The agent must not:

- Connect to live network management interfaces.
- Change network configurations.
- Restart network services.
- Execute arbitrary system commands.
- Access unrestricted filesystem locations.
- Send data to external services without explicit configuration and approval.

The agent provides recommendations, not automatic network control.

## 9. Local models and external services

The initial implementation should prefer local inference through supported local model runtimes.

This helps avoid sending project data to external model providers by default.

If an external model API is introduced later, we must document:

- What information is sent.
- Which provider receives it.
- Whether the information is stored.
- Whether the provider may use it for model improvement.
- Any applicable data retention settings.
- The cost and usage implications.

No paid API should be required for the core project.

## 10. Logging and monitoring

Logs are important for debugging and investigating application failures.

However, they should not contain secrets or unnecessary sensitive information.

We should avoid logging:

- API keys and access tokens.
- Passwords.
- Full environment configuration.
- Unnecessary subscriber identifiers.
- Sensitive uploaded document contents.

Useful events to record include:

- Data ingestion success or failure.
- API request errors.
- Model execution failures.
- Retrieval failures.
- Agent tool execution.
- Experiment execution.
- Report generation.

Logs should contain enough context to diagnose problems without exposing confidential information.

## 11. Dependency and code security

The project will use Python packages for data processing, machine learning, retrieval and application development.

Security practices should include:

- Prefer maintained packages.
- Pin important dependency versions.
- Review new dependencies before adding them.
- Avoid installing packages from untrusted sources.
- Run automated dependency checks where practical.
- Keep secrets and generated artefacts out of Git.
- Review GitHub Actions permissions and workflow changes.

A `.gitignore` file should exclude local environments, secret files, temporary data, model checkpoints and generated files that do not belong in the repository.

## 12. Deployment security

The local development environment may use relaxed settings for convenience.

A public deployment should apply additional protections:

- HTTPS.
- Appropriate authentication where needed.
- Restricted file uploads.
- Resource and request limits.
- Safe error messages.
- Secret management through deployment configuration.
- Restricted API permissions.
- No exposed development or administrative endpoints.

Public demo access should not provide unrestricted access to expensive or resource-intensive operations.

## 13. Security testing

Security-related tests should cover:

| Area | Test |
|---|---|
| File uploads | Reject unsupported formats and oversized files |
| API validation | Reject malformed requests |
| Secrets | Ensure secret values are not exposed in responses or logs |
| Document ingestion | Handle malformed and suspicious files safely |
| Prompt injection | Test documents containing malicious instructions |
| Agent tools | Reject unapproved tool calls and invalid arguments |
| Filesystem | Prevent access outside approved directories |
| Deployment | Check that development settings are not exposed |

These tests should be added to the existing Pytest test suite.

## 14. Known limitations

This project is an engineering portfolio platform, not a certified telecom security product.

Its security measures will be developed and tested within the scope of the project.

We will not claim that the platform is suitable for deployment in a production operator network without a separate security assessment, threat modelling exercise and operational review.

## 15. Implementation order

Security controls will be introduced alongside the relevant components.

**During project setup:** Configure `.gitignore`, environment variables and dependency management.

**During data ingestion:** Implement file validation, size limits and safe parsing.

**During API development:** Add request validation and safe error handling.

**During RAG development:** Treat retrieved documents as untrusted input and test prompt injection scenarios.

**During agent development:** Restrict tools and validate every tool call.

**Before deployment:** Review authentication, HTTPS, resource limits, logging and configuration.

The goal is to build a platform whose behaviour is controlled and understandable, especially when an LLM or agent is involved.
