# Quickstart: Data Analytics Platform

## Purpose

This guide validates the planned end-to-end flow for the multi-tenant data analytics platform: tenant registration, tenant user management, login/password changes, connect data sources, submit an analytics request, review results, and download outputs.

## Prerequisites

- Node.js 20+ for the Vite frontend
- Python 3.11+ for the backend
- Access to PostgreSQL for local development and testing
- Sample files for upload: `.txt`, `.pdf`, `.docx`, `.xlsx`
- Environment variables configured for local development, ideally shared via the same project `.env`/secrets convention

## Expected Project Layout

```text
ai-analytics-tool/
├── frontend/
└── backend/
```

## Local Setup

### 1) Install frontend dependencies

```bash
cd frontend
npm install
npm run dev
```

Vite should serve the UI on localhost, typically on port `5173`.

### 2) Install backend dependencies

```bash
cd ../backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The backend should be available on localhost at port `8000` and connect to PostgreSQL using the same schema and metadata model as production.

### 3) Debug inside the IDE

- Open the frontend and backend folders in Devin.
- Keep the frontend and backend running locally while editing code.
- Use browser devtools plus backend console logs to debug request flow, uploads, and analytics results.
- Share the same environment variables in the project root so Devin uses the same backend and optional LLM settings.

### 4) Configure environment variables

Set values for the backend before starting the app:

- PostgreSQL connection string
- auth secret or signing key
- storage location for uploaded files
- optional AI provider key or endpoint
- optional shared model endpoint so Devin can use the same LLM access path
- if no LLM settings are provided, the platform should continue running in deterministic analytics mode

## Validation Scenarios

### Scenario 1: Register tenant admin

1. Open the browser UI.
2. Create a new tenant from `/register` with the first tenant admin account.
3. Sign in as the tenant admin.

**Expected outcome**: The tenant is created and the first admin reaches the tenant dashboard.

### Scenario 2: Create tenant user

1. While signed in as tenant admin, open tenant administration.
2. Create a tenant user and assign either `admin` or `user` role.
3. Confirm the user appears in the tenant user list.

**Expected outcome**: The user is created under the correct tenant with the selected role.

### Scenario 3: Log in and change password

1. Sign in as a tenant admin or tenant user.
2. Change the password using one that meets the policy.
3. Sign out and sign in again with the new password.

**Expected outcome**: The password change succeeds and the new password works while the old password no longer does.

### Scenario 4: Add a data source

1. Go to `/data-sources`.
2. Add either a database connection or upload a supported file.
3. Validate the source.

**Expected outcome**: The source appears with an active or validated status.

### Scenario 5: Submit an analytics request

1. Open `/requests/new`.
2. Select one or more approved data sources.
3. Enter an analysis objective.
4. Submit the request.

**Expected outcome**: The request is queued and a status page is available.

### Scenario 6: Review the result

1. Wait for the request to complete.
2. Open `/requests/{id}` or `/results/{id}`.
3. Review the summary, metrics, and visualizations.

**Expected outcome**: The result is visible in the browser and matches the submitted request.

### Scenario 7: Download the result

1. From the result page, choose CSV, PDF, or Excel export.
2. Open the downloaded file.

**Expected outcome**: The exported file opens successfully and contains the same core findings shown on screen.

## Deployment Check

For Render-style deployment:

- Frontend deploys as a static site built from `frontend/`
- Backend deploys as a Python web service from `backend/`
- The API health check should respond successfully at `/api/health`
- Localhost and deployed environments should use the same configuration shape so debugging remains consistent
- LLM-related environment variables are optional and can be omitted without blocking the main analytics workflow

## Completion Criteria

The feature is ready when:

- Tenant registration, role assignment, login, and password changes work end to end
- At least one SQL/NoSQL source and one file upload flow work within a tenant-scoped workspace
- Analytics requests complete and show results in the UI
- Downloaded files are generated correctly
- The app runs locally in Devin on localhost and is deployable on a JS + Python hosting platform