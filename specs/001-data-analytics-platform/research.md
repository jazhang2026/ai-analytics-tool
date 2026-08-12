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

## 4) File source support

**Decision**: Support file-based data sources only:
- File sources: text, PDF, Word, and Excel uploads.

**Rationale**:
- This matches the user story directly and simplifies the data pipeline.
- File-only sources reduce dependency on external database drivers and connection management.
- File ingestion can be handled through a common normalization layer before analytics run.

**Alternatives considered**:
- SQL/NoSQL database sources: adds external dependency and configuration complexity not needed for the MVP.
- Auto-discovery of files: too ambiguous for a first version.

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

**Decision**: Use tenant-scoped password-based authentication with hashed passwords, session or token-based login suitable for browser clients, and role-based access for tenant admins and tenant users. Add a separate operator authentication path for system-level cross-tenant access and backup/restore permissions.

**Rationale**:
- The project needs tenant registration, role assignment, login, and password changes for a browser UI.
- The operator role requires system-level authentication that is separate from tenant membership.
- The approach is familiar, testable, and compatible with Render/Railway-style hosting.
- Tenant-scoped authentication keeps users isolated to their own workspace and supports the admin/user model.
- The password policy is explicit and can be enforced consistently at the application layer for all account types.

**Alternatives considered**:
- OAuth/SSO: useful later, but not required for the first release.
- Magic-link auth: convenient, but adds email delivery dependency.
- Passwordless login only: simpler for users, but does not fit the requested admin-managed tenant workflow.
- Merging operator into tenant admin role: would break tenant isolation and backup/restore boundaries.

## 8) Storage approach

**Decision**: Use an embedded database (SQLite) for users, requests, metadata, and audit logs in both production and local development; store uploaded files and backup files in the filesystem.

**Rationale**:
- SQLite eliminates the need for an external database server and simplifies deployment.
- Using the same embedded engine locally and in production eliminates environment drift.
- Uploaded files and backup files are stored separately from the application database.
- This structure makes downloads, retries, backup, restore, and result traceability easier.
- Local development is simpler when backend state, file storage, and backups are self-contained.

**Alternatives considered**:
- PostgreSQL: powerful and mature, but requires an external server which contradicts the embedded-database requirement.
- Storing everything in files: simple, but difficult to query and audit.
- NoSQL-only persistence: possible, but less natural for auth and request lifecycle tracking.

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

## 10) Backup and restore strategy

**Decision**: Use file-based backup for the embedded database, triggered by the operator through API endpoints, with backup files stored on the filesystem.

**Rationale**:
- An embedded database like SQLite supports simple file-copy backup that is reliable and fast.
- File-based backup avoids external tool dependencies and keeps the deployment self-contained.
- Operator-triggered backup and restore via the UI gives system administrators control without direct filesystem access.
- Backup files stored in a dedicated directory make restore operations straightforward.

**Alternatives considered**:
- External backup tools or services: adds deployment complexity and contradicts the embedded-database goal.
- Automated scheduled backups: useful later, but not required for the MVP.
- Streaming replication: overkill for an embedded database and the expected scale.
