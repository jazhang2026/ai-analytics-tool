# Tasks: Multi-Tenant Data Analytics Platform

**Input**: Design documents from `/specs/001-data-analytics-platform/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are not explicitly requested, so this task list focuses on implementation and validation-ready delivery work.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for the Vite frontend and Python backend

- [ ] T001 Create repository structure for `frontend/`, `backend/`, `backend/app/`, `backend/data/`, `backend/backups/`, and `specs/001-data-analytics-platform/` support files
- [ ] T002 [P] Initialize the Vite frontend scaffold in `frontend/package.json`, `frontend/index.html`, and `frontend/vite.config.js`
- [ ] T003 [P] Initialize the Python backend scaffold in `backend/requirements.txt` and `backend/app/__init__.py`
- [ ] T004 [P] Add local environment templates and ignore rules for embedded DB, auth, file storage, and optional LLM config in `.env.example`, `frontend/.env.example`, `backend/.env.example`, and `.gitignore`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**Independent Test**: The app can start locally, initialize the embedded database, and load the base frontend/backend shells without tenant-specific features

- [ ] T005 Implement embedded database (SQLite) connection, settings loading, and shared persistence bootstrap in `backend/app/storage.py`
- [ ] T006 [P] Implement tenant-scoped authentication, session handling, role checks, and password policy helpers in `backend/app/auth.py`
- [ ] T007 [P] Define the core tenant-scoped data models for Tenant, User, Operator, TenantMembership, DataSource, AnalyticsRequest, AnalyticsResult, BackupRecord, and AuditLog in `backend/app/models.py`
- [ ] T008 Implement FastAPI app bootstrap, error handling, dependency wiring, and route registration in `backend/app/main.py`
- [ ] T009 [P] Build the frontend app shell, shared API client, navigation state, and common layout in `frontend/src/main.js`, `frontend/src/api.js`, `frontend/src/ui.js`, and `frontend/src/styles.css`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Tenant Registration with Tenant Admin (Priority: P1)

**Goal**: Register a new tenant and create the first tenant admin account

**Independent Test**: Create a tenant through the browser UI and verify the tenant exists with one active admin account

- [ ] T010 [US1] Implement tenant registration service and `POST /api/tenants` endpoint in `backend/app/tenants.py`
- [ ] T011 [P] [US1] Build the tenant registration form, validation, and submission flow in `frontend/src/ui.js`, `frontend/src/api.js`, and `frontend/src/styles.css`
- [ ] T012 [US1] Wire tenant registration to session handoff and dashboard redirect in `frontend/src/main.js`

**Checkpoint**: Tenant registration should be fully functional and tenant-scoped

---

## Phase 4: User Story 2 - Tenant Admin User Management (Priority: P1)

**Goal**: Let tenant admins create tenant users and assign `admin` or `user` roles

**Independent Test**: Create a tenant user from the admin UI and confirm the user is listed in the tenant with the selected role

- [ ] T013 [US2] Implement tenant user creation and tenant user listing endpoints in `backend/app/tenants.py`
- [ ] T014 [US2] Implement tenant role update handling using body-based `user_id` in `backend/app/tenants.py`
- [ ] T015 [P] [US2] Build the tenant admin user management screen in `frontend/src/ui.js` and `frontend/src/api.js`
- [ ] T016 [US2] Enforce tenant-admin authorization and tenant membership checks in `backend/app/auth.py` and `backend/app/main.py`

**Checkpoint**: Tenant admins should be able to manage tenant users without affecting other tenants

---

## Phase 5: User Story 3 - Login and Password Management (Priority: P1)

**Goal**: Support tenant admin/user login and password changes with the required password policy

**Independent Test**: Log in with valid credentials, change the password, and confirm the new password works while the old password no longer does

- [ ] T017 [US3] Implement tenant-scoped login, logout, and `PATCH /api/me/password` in `backend/app/auth.py`
- [ ] T018 [US3] Enforce the 8-12 character password policy with uppercase, lowercase, and numeric requirements in `backend/app/auth.py`
- [ ] T019 [P] [US3] Build login and password change screens with password-policy guidance in `frontend/src/ui.js`, `frontend/src/api.js`, and `frontend/src/styles.css`
- [ ] T020 [US3] Add authentication state persistence and route guarding in `frontend/src/main.js`

**Checkpoint**: Tenant members should be able to sign in and update passwords securely

---

## Phase 6: User Story 4 - Analytics Request Submission (Priority: P1)

**Goal**: Allow a tenant user to submit a data analytics request from the browser UI

**Independent Test**: Submit a request through the browser and verify the system accepts it and tracks it for the current tenant

- [ ] T021 [US4] Implement analytics request creation and tenant-scoped request listing in `backend/app/analytics.py`
- [ ] T022 [US4] Implement request detail lookup using body-based `request_id` in `backend/app/analytics.py`
- [ ] T023 [P] [US4] Build the analytics request submission form and request list/detail navigation in `frontend/src/ui.js` and `frontend/src/api.js`
- [ ] T024 [US4] Connect request submission flow to tenant-scoped dashboard actions in `frontend/src/main.js`

**Checkpoint**: Tenant users should be able to submit and track analytics requests

---

## Phase 7: User Story 5 - File-Based Data Source Processing (Priority: P1)

**Goal**: Support file uploads for text, PDF, Word, and Excel as the only analytics data sources

**Independent Test**: Upload supported file types and confirm they are accepted and available only within the tenant workspace

- [ ] T025 [US5] Implement file upload persistence, file format validation, and source registration in `backend/app/storage.py`
- [ ] T026 [US5] Add tenant-source checks so analytics can only use files from the same tenant in `backend/app/analytics.py`
- [ ] T027 [P] [US5] Build the file upload screen, supported-format feedback, and source management in `frontend/src/ui.js`, `frontend/src/api.js`, and `frontend/src/styles.css`
- [ ] T028 [US5] Add source status display and tenant-aware file navigation in `frontend/src/main.js`

**Checkpoint**: Tenant-uploaded files should be usable for analytics and isolated from other tenants

---

## Phase 8: User Story 6 - Analytics Method Selection (Priority: P1)

**Goal**: Automatically choose a good analytics method based on the request data and objective

**Independent Test**: Submit different file-based request types and verify the selected method and explanation match the request type

- [ ] T029 [US6] Implement the analytics method router, file-type detection, and fallback selection logic in `backend/app/analytics.py`
- [ ] T030 [US6] Implement method rationale and confidence/explanation payload generation in `backend/app/analytics.py`
- [ ] T031 [P] [US6] Add method summary and rationale sections to the request detail UI in `frontend/src/ui.js` and `frontend/src/api.js`
- [ ] T032 [US6] Surface the selected analytics method and explanation in dashboard and request views in `frontend/src/main.js`

**Checkpoint**: Analytics requests should have an explainable method choice

---

## Phase 9: User Story 7 - Result Viewing and Download (Priority: P2)

**Goal**: Show results in the UI and allow them to be downloaded

**Independent Test**: Complete a request, open the result view, and download the generated output file successfully

- [ ] T033 [US7] Implement result persistence, retrieval, and body-based `request_id` lookup in `backend/app/analytics.py`
- [ ] T034 [US7] Implement CSV, PDF, and Excel export generation in `backend/app/analytics.py`
- [ ] T035 [P] [US7] Build the result review page and download actions in `frontend/src/ui.js` and `frontend/src/api.js`
- [ ] T036 [US7] Add result rendering, file-download states, and status refresh behavior in `frontend/src/main.js` and `frontend/src/styles.css`

**Checkpoint**: Analytics results should be visible and downloadable from the UI

---

## Phase 10: User Story 8 - Operator Login and Cross-Tenant Access (Priority: P1)

**Goal**: Allow an operator to log in, view all tenants, and navigate any tenant's workspace

**Independent Test**: Log in as operator, view the tenant list, and access a specific tenant's users and requests

- [ ] T037 [US8] Implement operator authentication, session handling, and role enforcement in `backend/app/auth.py`
- [ ] T038 [US8] Implement cross-tenant data access endpoints for operator in `backend/app/operators.py`
- [ ] T039 [US8] Implement tenant listing, tenant detail, and tenant-scoped data browsing for operators in `backend/app/operators.py`
- [ ] T040 [P] [US8] Build the operator dashboard, tenant list view, and tenant navigation in `frontend/src/ui.js`, `frontend/src/api.js`, and `frontend/src/styles.css`
- [ ] T041 [US8] Add operator authentication state and role-based route guarding in `frontend/src/main.js`

**Checkpoint**: Operators should be able to log in and browse all tenant workspaces

---

## Phase 11: User Story 9 - Operator Backup and Restore (Priority: P2)

**Goal**: Allow the operator to back up the application database to a file and restore from a backup

**Independent Test**: Create a backup, make a change, restore from the backup, and verify the restored state matches

- [ ] T042 [US9] Implement database backup creation and file storage in `backend/app/storage.py`
- [ ] T043 [US9] Implement database restore from backup file in `backend/app/storage.py`
- [ ] T044 [US9] Add backup/restore API endpoints for operators in `backend/app/operators.py`
- [ ] T045 [P] [US9] Build the backup/restore UI with status feedback in `frontend/src/ui.js`, `frontend/src/api.js`, and `frontend/src/styles.css`
- [ ] T046 [US9] Add backup/restore actions to the operator dashboard in `frontend/src/main.js`

**Checkpoint**: Operators should be able to back up and restore the application database

---

## Phase 12: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and production readiness

- [ ] T047 [P] Update README and quickstart documentation for file-only data sources, embedded database, operator role, and backup/restore in `README.md` and `specs/001-data-analytics-platform/quickstart.md`
- [ ] T048 Harden tenant-scoping edge cases, operator access boundaries, validation, and logging across `backend/app/auth.py`, `backend/app/tenants.py`, `backend/app/operators.py`, `backend/app/analytics.py`, and `backend/app/storage.py`
- [ ] T049 Validate the full localhost workflow end to end in `specs/001-data-analytics-platform/quickstart.md`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - blocks all user stories
- **User Stories (Phase 3+)**: Depend on Foundational phase completion
  - User stories can then proceed in priority order or in parallel when staffed
- **Polish (Final Phase)**: Depends on the desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational phase completion - no dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational phase completion - depends on tenant/auth foundations only
- **User Story 3 (P1)**: Can start after Foundational phase completion - depends on tenant/auth foundations only
- **User Story 4 (P1)**: Can start after Foundational phase completion - depends on tenant/auth and base UI shell
- **User Story 5 (P1)**: Can start after Foundational phase completion - depends on storage and file models
- **User Story 6 (P1)**: Can start after Foundational phase completion - depends on analytics foundations and source models
- **User Story 7 (P2)**: Can start after User Story 4 and User Story 6 are in place - depends on analytics processing and result models
- **User Story 8 (P1)**: Can start after Foundational phase completion - depends on tenant/auth and operator model foundations
- **User Story 9 (P2)**: Can start after User Story 8 is in place - depends on operator authentication and storage infrastructure

### Within Each User Story

- Implementation tasks should follow models/services/endpoints/UI order where applicable
- Frontend tasks can proceed in parallel with backend tasks when they touch different files
- Story complete before moving to the next priority when doing sequential delivery

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel once the setup shell exists
- Within each user story, frontend tasks marked [P] can run in parallel with backend service work
- User Stories 1, 2, 3, 4, 5, 6, and 8 can begin in parallel after Foundational phase completion

---

## Parallel Example: User Story 8

```text
Task: T037 Implement operator authentication, session handling, and role enforcement in `backend/app/auth.py`
Task: T040 Build the operator dashboard, tenant list view, and tenant navigation in `frontend/src/ui.js`, `frontend/src/api.js`, and `frontend/src/styles.css`
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Validate tenant registration locally
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → platform shell ready
2. Add User Story 1 → tenant onboarding works
3. Add User Story 2 and User Story 3 → tenant administration and secure access work
4. Add User Story 4 and User Story 5 → request submission and file source ingestion work
5. Add User Story 6 and User Story 7 → method selection and reporting complete the workflow
6. Add User Story 8 and User Story 9 → operator management and backup/restore complete
7. Finish with polish and local validation
