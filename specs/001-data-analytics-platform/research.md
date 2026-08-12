# Research: Data Analytics Platform

## 1) Frontend stack

**Decision**: Use Vite with vanilla HTML, CSS, and modern JavaScript modules.

**Rationale**:
- Keeps the UI dependency footprint small, which matches the project goal.
- Vite supports fast local development and produces static assets that are easy to deploy.
- Vanilla JS is sufficient for the required browser flows: register/login, request submission, status updates, results display, and downloads.
- This approach fits popular static-site hosting and avoids framework lock-in.

**Alternatives considered**:
- React/Vue/Svelte: richer component ecosystems, but unnecessary for the MVP and add complexity.
- Server-rendered templates only: simpler on the backend, but less flexible for interactive analytics status updates.

## 2) Backend framework

**Decision**: Use FastAPI with Uvicorn as the Python backend.

**Rationale**:
- FastAPI is lightweight, modern, and well suited to file uploads, JSON APIs, authentication, and background-friendly request handling.
- It works well with minimal dependencies and pairs cleanly with Vite-based frontends.
- FastAPI is widely supported by common Python hosting platforms and also works well on Render/Railway-style deployments.

**Alternatives considered**:
- Flask: simpler, but less structured for API-heavy apps.
- Django: mature and feature-rich, but heavier than needed for this MVP.

## 3) Data processing libraries

**Decision**: Use pandas as the core analytics engine, with focused parsers for PDF, Word, Excel, and text files.

**Rationale**:
- pandas handles tabular analysis, summarization, grouping, joins, and export well.
- Dedicated file readers keep imports narrow and predictable.
- The project needs a flexible analysis layer, not a distributed compute stack.
- A rule-based analytics router can select the right method based on source type, schema, and request intent.

**Alternatives considered**:
- Spark/Dask: powerful but too heavy for the expected MVP scale.
- A single LLM-driven analysis path: flexible, but harder to make reliable and expensive to run.

## 4) File and database source support

**Decision**: Support two source families:
- Structured sources: SQL and NoSQL databases that the user configures explicitly.
- File sources: text, PDF, Word, and Excel uploads.

**Rationale**:
- This matches the user story directly.
- Explicit configuration avoids accidental access to untrusted or unknown sources.
- File ingestion can be handled through a common normalization layer before analytics run.

**Alternatives considered**:
- Auto-discovery of files and databases: too ambiguous for a first version.
- Supporting every database connector immediately: broad, but not necessary for the MVP.

## 5) Hosting and deployment target

**Decision**: Design for Render-compatible deployment, with the frontend deployed as a static site and the backend as a Python web service.

**Rationale**:
- Render supports both static sites for HTML/CSS/JS frontends and web services for FastAPI backends.
- This maps cleanly to a Vite frontend plus Python API architecture.
- The platform is popular, easy to understand, and aligns with the requirement to support both JS and Python hosting needs.

**Alternatives considered**:
- Railway: also supports Node and Python well, and is a viable alternate host.
- Vercel alone: good for frontend, but not ideal as the sole host for the Python backend.
- Single-container Docker deployment: flexible, but less aligned with the minimal-library goal.

## 6) Analytics method selection

**Decision**: Use a deterministic analytics router by default, with an optional OpenAI-compatible LLM provider for natural-language explanations and method descriptions.

**Rationale**:
- This removes the dependency on one specific model vendor.
- The system still satisfies the requirement to choose a good analytics method by selecting from a known set of analysis recipes.
- Optional LLM support improves explainability without blocking the core product.
- This reduces hosting and cost risk while keeping the architecture flexible.

**Alternatives considered**:
- Hard-require OpenAI or Anthropic: too restrictive and expensive for an MVP.
- Purely rule-based forever: reliable, but weaker explanations and less conversational guidance.

## 7) Authentication strategy

**Decision**: Use tenant-scoped password-based authentication with hashed passwords, session or token-based login suitable for browser clients, and role-based access for tenant admins and tenant users.

**Rationale**:
- The project needs tenant registration, role assignment, login, and password changes for a browser UI.
- The approach is familiar, testable, and compatible with Render/Railway-style hosting.
- Tenant-scoped authentication keeps users isolated to their own workspace and supports the admin/user model.
- The password policy is explicit and can be enforced consistently at the application layer.

**Alternatives considered**:
- OAuth/SSO: useful later, but not required for the first release.
- Magic-link auth: convenient, but adds email delivery dependency.
- Passwordless login only: simpler for users, but does not fit the requested admin-managed tenant workflow.

## 8) Storage approach

**Decision**: Use PostgreSQL for users, requests, metadata, and audit logs in both production and local development; store uploaded files in a filesystem or object-storage layer.

**Rationale**:
- PostgreSQL is a good fit for authentication, request state, and auditability.
- Using the same database engine locally and in production reduces environment drift.
- Uploaded files are better stored separately from metadata.
- This structure makes downloads, retries, and result traceability easier.
- Local development is simpler when backend state, file storage, and secrets are explicit and reproducible in the IDE.

**Alternatives considered**:
- Storing everything in files: simple, but difficult to query and audit.
- NoSQL-only persistence: possible, but less natural for auth and request lifecycle tracking.
- SQLite for local development: lightweight, but diverges from production behavior.

## 9) Local development and shared model access

**Decision**: Use a single project-level environment configuration so Devin can point to the same backend URL, database, and optional LLM provider settings in both localhost and deployed environments.

**Rationale**:
- Localhost debugging is a core requirement and should mirror deployed behavior as closely as possible.
- A shared `.env`/environment-variable contract avoids tool-specific drift between IDEs and agents.
- Devin can run against the same localhost services when it reads the same configuration values.
- The LLM layer remains optional: if provider settings are absent, the analytics platform still runs deterministically.
- Optional LLM access remains provider-agnostic as long as the tool references the same endpoint and key naming.

**Alternatives considered**:
- Tool-specific configuration per IDE: increases drift and makes debugging harder.
- Hardcoding model/provider settings into code: brittle and unsafe for credentials.
- Requiring an LLM for all runs: makes local debugging and deployment unnecessarily fragile.
