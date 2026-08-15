# Test Plan: UI and Auth Enhancements

**Input**: Design documents from `specs/002-ui-auth-enhancements/`
**Created**: 2026-08-14
**Framework**: pytest + FastAPI TestClient (backend); manual browser validation for UI (frontend)

## Test Scope

- **In scope**:
  - Operator seed script behavior (creation, idempotency, tests-directory location)
  - Operator session support via `/api/me` (role = operator)
  - Operator password change via `/api/me/password`
  - Tenant user password change regression (unchanged behavior)
  - Unauthenticated access control (401)
- **Out of scope**:
  - Frontend UI rendering (header, dropdown, nav bar, buttons) — verified manually per `quickstart.md`; automated browser tests deferred
  - Analytics, data sources, operator backup/restore endpoints (covered by feature 001 test plan)

## Test Environment

- In-memory SQLite with StaticPool (see `backend/tests/conftest.py`)
- Run: `cd backend && source .venv/bin/activate && python -m pytest tests/ -v`
- Existing fixtures: `client` (TestClient with dependency override), `db_session`, `engine`

## Test Execution Results

| Run Date | Command | Unit | Integration | Total | Result |
|----------|---------|------|-------------|-------|--------|
| 2026-08-14 | `python -m pytest tests/ -v` | 25 | 19 | 44 | ✅ 44 passed, 2 warnings |

- Unit: `test_auth.py` (11), `test_models.py` (10), `test_seed_operator.py` (4)
- Integration: `test_api.py` (19)
- Warnings: StarletteDeprecationWarning (httpx/httpx2), passlib crypt deprecation — non-blocking

## Unit Test Plan

### auth.py (password policy, hashing, tokens)

Existing coverage in `tests/test_auth.py` — extend only if gaps found.

| Test Case | Requirement | Input | Expected Result | File |
|-----------|-------------|-------|-----------------|------|
| password policy accepts 8-12 chars | FR-007 (001) | `Abc12345` | no exception | `tests/test_auth.py` |
| password policy rejects short/long | FR-007 (001) | `Ab1`, 13 chars | HTTPException 400 | `tests/test_auth.py` |
| hash then verify round-trip | — | `Test1234` | verify True | `tests/test_auth.py` |
| token create/decode | — | user id + type | payload round-trip | `tests/test_auth.py` |

### seed_operator.py (operator seed script)

| Test Case | Requirement | Input | Expected Result | File |
|-----------|-------------|-------|-----------------|------|
| create operator on empty DB | FR-001 | fresh DB | operator row exists, email operator@aiatool.com | `tests/test_seed_operator.py` |
| idempotent second run | FR-002 | DB with operator | no duplicate, reports already exists | `tests/test_seed_operator.py` |
| script located under tests/ | FR-003 | file path | `backend/tests/seed_operator.py` | `tests/test_seed_operator.py` |

## Integration Test Plan

### API Flows

| Test Case | Requirement | Steps | Expected Result | File |
|-----------|-------------|-------|-----------------|------|
| operator login returns token | FR-001 | POST `/api/operator/login` op@test.com | 200, token present | `tests/test_api.py` |
| operator `/api/me` returns operator role | FR-004/FR-005 | login → GET `/api/me` with token | 200, `role == "operator"` | `tests/test_api.py` |
| operator change password | FR-006/FR-007 | login → PATCH `/api/me/password` | 200; old password fails, new works | `tests/test_api.py` |
| unauthenticated `/api/me` rejected | FR-009 | GET `/api/me` no token | 401 | `tests/test_api.py` |
| tenant user `/api/me` regression | FR-005 | register tenant → login → GET `/api/me` | 200, role admin/user, tenant_id present | `tests/test_api.py` |
| tenant password change regression | FR-006 | tenant login → PATCH `/api/me/password` | 200; old password fails | `tests/test_api.py` |

### Database + API Interaction

| Test Case | Requirement | Steps | Expected Result | File |
|-----------|-------------|-------|-----------------|------|
| operator persisted after seed | FR-001 | seed script → query operators table | 1 row, correct email | `tests/test_seed_operator.py` |
| operator password hash stored, not plaintext | FR-001 | seed → inspect `password_hash` | value != plaintext | `tests/test_seed_operator.py` |
| tenant user vs operator login isolation | FR-002/FR-009 | tenant login + operator login with same email pattern | each succeeds only via its own path | `tests/test_api.py` |

## Coverage Matrix

| Requirement | Unit Test | Integration Test | Status |
|-------------|-----------|------------------|--------|
| FR-001 (seed creates operator) | ✅ | ✅ | ✅ Passed |
| FR-002 (idempotent seed) | ✅ | — | ✅ Passed |
| FR-003 (script in tests/) | ✅ | — | ✅ Passed |
| FR-004 (header brand) | — | ⚠️ manual UI | Manual |
| FR-005 (user email in header) | — | ✅ `/api/me` + manual UI | ✅ Passed (API) |
| FR-006 (dropdown opens) | — | ⚠️ manual UI | Manual |
| FR-007 (Change Password nav) | — | ✅ API + manual UI | ✅ Passed (API) |
| FR-008 (Logout) | — | ⚠️ manual UI | Manual |
| FR-009 (login page when unauthenticated) | — | ✅ 401 checks | ✅ Passed |
| FR-010 (registration link text) | — | ⚠️ manual UI | Manual |
| FR-011 (nav bar links) | — | ⚠️ manual UI | Manual |
| FR-012 (Users admin-only) | — | ⚠️ manual UI | Manual |
| FR-013 (Dashboard New Request) | — | ⚠️ manual UI | Manual |
| FR-014 (Analytics New Request) | — | ⚠️ manual UI | Manual |
| FR-015 (button navigation) | — | ⚠️ manual UI | Manual |
| SC-001 (operator login works) | ✅ | ✅ | ✅ Passed |
| SC-002 (header on all pages) | — | ⚠️ manual UI | Manual |
| SC-003 (dropdown <200ms) | — | ⚠️ manual UI | Manual |
| SC-004 (nav <1s) | — | ⚠️ manual UI | Manual |
| SC-005 (Users hidden non-admin) | — | ⚠️ manual UI | Manual |
| SC-006 (New Request visible) | — | ⚠️ manual UI | Manual |

## Negative Cases (from spec edge cases)

| Test Case | Edge Case | Input | Expected Result |
|-----------|-----------|-------|-----------------|
| seed script run twice | duplicate operator | run seed twice | second run reports exists, no error |
| operator login wrong password | invalid credentials | bad password | 401 |
| change password with wrong current | wrong current pw | PATCH with bad current | 400 |
| change password violating policy | weak new password | PATCH with `short` | 400 |

## Priority

- **P1**: seed script tests (FR-001–003), operator `/api/me` + password (FR-005–007), auth isolation (FR-009)
- **P2**: tenant regression tests (tenant `/api/me`, tenant password change)
- **P3 (manual)**: all UI rendering checks (FR-004, FR-006, FR-008, FR-010–015, SC-002–006) per `quickstart.md`
