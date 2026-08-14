---
name: "speckit-test-run"
description: "Write and run unit tests and integration tests for the current feature, executing all planned test cases from test-plan.md and mapping coverage back to spec requirements."
compatibility: "Requires spec-kit project structure with .specify/ directory and a feature directory under specs/"
metadata:
  author: "ai-analytics-tool"
  source: "spec-kit workflow extension"
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Goal

Implement and execute the **unit test cases** and **integration test cases** planned in the active feature's `test-plan.md`. Write test code under `backend/tests/`, run the full suite, and report coverage against functional requirements (FR-###).

## Pre-Execution Checks

**Check for extension hooks (before test generation)**:
- Check if `.specify/extensions.yml` exists in the project root.
- If it exists, read it and look for entries under the `hooks.before_test` key
- If the YAML cannot be parsed or is invalid, skip hook checking silently and continue normally
- Filter out hooks where `enabled` is explicitly `false`. Treat hooks without an `enabled` field as enabled by default.
- If no hooks are registered or `.specify/extensions.yml` does not exist, skip silently

## Execution Steps

1. **Locate the active feature**:
   - Read `.specify/feature.json` for `feature_directory` (e.g., `specs/002-ui-auth-enhancements`)
   - Derive absolute paths: SPEC = `<feature_directory>/spec.md`, PLAN = `<feature_directory>/plan.md`, TEST_PLAN = `<feature_directory>/test-plan.md`, TASKS = `<feature_directory>/tasks.md`

2. **Load context**:
   - Read SPEC for functional requirements (FR-###), user stories, and edge cases
   - Read TEST_PLAN for the planned unit and integration test cases (if missing, report "run /speckit-test-plan first" and stop)
   - Read PLAN for tech stack and file structure
   - Read `.specify/memory/constitution.md` for testing principles

3. **Build the test inventory from test-plan.md**:
   - **Unit test cases** → module-level tests (auth, models, storage, routers)
   - **Integration test cases** → API flow tests and database+API interaction tests
   - Produce a coverage table mapping each test case → FR → test file → test function

4. **Write test code** under `backend/tests/`:
   - Unit tests: `test_auth.py`, `test_models.py`, `test_storage.py`, `test_<router>.py` (one per module)
   - Integration tests: `test_api.py` — HTTP endpoints (tenant registration, login, operator, analytics, data sources), including negative cases (invalid input, duplicates, cross-tenant access)
   - Use `conftest.py` fixtures (in-memory SQLite with StaticPool, TestClient)
   - Implement **all planned test cases**; mark any case that cannot be implemented with a reason

5. **Run the full suite** (unit + integration together):
   ```bash
   cd backend && source .venv/bin/activate && python -m pytest tests/ -v
   ```

6. **Report**:
   - Test inventory table: test case → FR → file → status (PASS/FAIL)
   - Unit test pass/fail totals
   - Integration test pass/fail totals
   - Any failing tests with the failing assertion context
   - Suggested next step (`/speckit-converge` if tests reveal unimplemented requirements)

## Rules

- Tests are READ-ONLY toward application code: never modify `backend/app/` to make a test pass.
- A failing test reveals either a bug (fix the app) or an incorrect test (fix the test) — report which before changing anything.
- Follow the existing test style in `backend/tests/` (see `test_auth.py`, `test_models.py`, `test_api.py`).
- If the user requests a subset (e.g., `speckit-test-run operators`), limit scope to that area's unit and integration cases.
- Do not skip planned integration test cases; if one is not feasible, document why.

## Post-Execution Checks

**Check for extension hooks (after test generation)**:
Check if `.specify/extensions.yml` exists in the project root.
- If it does not exist, or no hooks are registered under `hooks.after_test`, skip to the Completion Report.
- If it exists, read it and look for entries under the `hooks.after_test` key.
- If the YAML cannot be parsed or is invalid, skip hook checking silently and continue to the Completion Report.

## Completion Report

Output:
- Path to test files created/verified
- Unit test cases executed (count + pass rate)
- Integration test cases executed (count + pass rate)
- Total test count and pass rate
- Requirements coverage percentage (FRs with tests / total FRs)
