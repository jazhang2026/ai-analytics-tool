---
name: "speckit-test-plan"
description: "Generate a test plan with unit and integration test cases for the active feature, mapping to spec requirements and success criteria."
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

Create a `test-plan.md` for the active feature covering **unit tests** and **integration tests**, with concrete test cases mapped to functional requirements (FR-###) and success criteria (SC-###). This complements `/speckit-plan` (which covers implementation planning only).

## Pre-Execution Checks

**Check for extension hooks (before test planning)**:
- Check if `.specify/extensions.yml` exists in the project root.
- If it exists, read it and look for entries under the `hooks.before_test_plan` key
- If the YAML cannot be parsed or is invalid, skip hook checking silently and continue normally
- Filter out hooks where `enabled` is explicitly `false`. Treat hooks without an `enabled` field as enabled by default.
- If no hooks are registered or `.specify/extensions.yml` does not exist, skip silently

## Execution Steps

1. **Locate the active feature**:
   - Read `.specify/feature.json` for `feature_directory` (e.g., `specs/002-ui-auth-enhancements`)
   - Output path: `<feature_directory>/test-plan.md`
   - If `test-plan.md` already exists, update it in place (do not duplicate sections)

2. **Load context**:
   - Read `<feature_directory>/spec.md` for user stories, FR-###, SC-###, and edge cases
   - Read `<feature_directory>/plan.md` for tech stack, testing line, and file structure
   - Read `<feature_directory>/data-model.md` for entities and constraints (if present)
   - Read `.specify/memory/constitution.md` for testing principles

3. **Generate the test plan** with this structure:

   ```markdown
   # Test Plan: <Feature Name>

   **Input**: Design documents from `<feature_directory>/`
   **Created**: <date>
   **Framework**: pytest + FastAPI TestClient (backend)

   ## Test Scope

   - In scope: <areas covered>
   - Out of scope: <areas excluded>

   ## Test Environment

   - In-memory SQLite with StaticPool (see `backend/tests/conftest.py`)
   - Run: `cd backend && source .venv/bin/activate && python -m pytest tests/ -v`

   ## Unit Test Plan

   One subsection per backend module:

   ### <module>.py (e.g., auth, models, storage, tenants, analytics, operators, data_sources)

   | Test Case | Requirement | Input | Expected Result | File |
   |-----------|-------------|-------|-----------------|------|
   | <name> | FR-### | <input> | <expected> | `tests/test_<module>.py` |

   ## Integration Test Plan

   ### API Flows

   | Test Case | Requirement | Steps | Expected Result | File |
   |-----------|-------------|-------|-----------------|------|
   | <name> | FR-### | <API calls> | <expected> | `tests/test_api.py` |

   ### Database + API Interaction

   | Test Case | Requirement | Steps | Expected Result | File |
   |-----------|-------------|-------|-----------------|------|

   ## Coverage Matrix

   | Requirement | Unit Test | Integration Test | Status |
   |-------------|-----------|------------------|--------|
   | FR-001 | ✅/❌ | ✅/❌ | Planned |

   ## Priority

   - P1: requirements blocking baseline functionality
   - P2: secondary requirements
   ```

4. **Derive test cases** from the requirements inventory:
   - Every FR gets at least one unit or integration test case
   - SCs that require buildable verification (response times, gating behavior) get integration test cases
   - Edge cases from spec.md become negative test cases (invalid input, duplicates, forbidden access)

5. **Write the test plan** to `<feature_directory>/test-plan.md`. Do not write test code — this is the planning artifact. `/speckit-test` consumes it to write the actual tests.

## Rules

- The test plan is a planning document — no test code in this step.
- Map every FR/SC to at least one test case; flag any requirement with no coverage.
- Follow the project's existing test conventions (see `backend/tests/test_auth.py`, `test_models.py`, `test_api.py`).
- Unit tests target single modules in isolation; integration tests exercise the HTTP API and database together.

## Post-Execution Checks

**Check for extension hooks (after test planning)**:
Check if `.specify/extensions.yml` exists in the project root.
- If it does not exist, or no hooks are registered under `hooks.after_test_plan`, skip to the Completion Report.
- If it exists, read it and look for entries under the `hooks.after_test_plan` key.
- If the YAML cannot be parsed or is invalid, skip hook checking silently and continue to the Completion Report.

## Completion Report

Output:
- Path to `test-plan.md`
- Total unit test cases planned
- Total integration test cases planned
- Requirements coverage (FRs with ≥1 test case / total FRs)
- Next step: `/speckit-test` to implement and run the tests
