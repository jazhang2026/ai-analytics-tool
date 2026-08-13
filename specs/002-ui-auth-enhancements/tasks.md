# Tasks: UI and Auth Enhancements

**Input**: Design documents from `/specs/002-ui-auth-enhancements/`

**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: Manual browser validation per quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation.

## Phase 1: User Story 1 - Operator Seed Data Script (Priority: P1)

**Goal**: Standalone CLI script that creates the operator account; excluded from deployment

**Independent Test**: Run `python seed_operator.py` against a fresh DB, verify login with operator@aiatool.com / Operator123

- [x] T001 [US1] Create standalone operator seed script in `backend/tests/seed_operator.py`
- [x] T002 [US1] Verify `backend/tests/` is excluded from production deployment artifacts

**Checkpoint**: Operator account can be created via CLI; script is not in deployment artifacts

---

## Phase 2: User Story 2 - Header with Brand and User Menu (Priority: P1)

**Goal**: Header shows "AI Analytics Tool" on left, user email dropdown on right with Change Password and Logout

**Independent Test**: Log in and verify header + dropdown on every authenticated page

- [x] T003 [US2] Add header styles (brand, email, dropdown) in `frontend/src/styles.css`
- [x] T004 [US2] Implement header with brand name and user email dropdown in `frontend/src/main.js`
- [x] T005 [US2] Add dropdown toggle and outside-click-to-close behavior in `frontend/src/main.js`

**Checkpoint**: Header with brand + dropdown visible and functional on all authenticated pages

---

## Phase 3: User Story 3 - Login Page Updates (Priority: P1)

**Goal**: Login page shown when unauthenticated; registration link reads "Register a new tenant account."

**Independent Test**: Visit app without login; verify login page and updated link text

- [x] T006 [US3] Update registration link text to "Register a new tenant account." in `frontend/src/routes.js`

**Checkpoint**: Login page shows correct text

---

## Phase 4: User Story 4 - Navigation Bar (Priority: P1)

**Goal**: Persistent nav bar under header with Dashboard, Data Sources, Data Analytics, Users (admin-only)

**Independent Test**: Log in as admin and non-admin; verify nav links and role gating

- [x] T007 [US4] Add navigation bar styles in `frontend/src/styles.css`
- [x] T008 [US4] Implement role-aware navigation bar in `frontend/src/main.js`

**Checkpoint**: Nav bar present on all authenticated pages; Users link gated by admin role

---

## Phase 5: User Story 5 - Quick Action Buttons (Priority: P2)

**Goal**: "New Request" button on Dashboard (top right of Recent Requests) and Data Analytics page (top of list)

**Independent Test**: Navigate to Dashboard and Data Analytics; verify buttons navigate to new request form

- [x] T009 [US5] Add "New Request" button to Dashboard route in `frontend/src/routes.js`
- [x] T010 [US5] Add "New Request" button to Data Analytics route in `frontend/src/routes.js`

**Checkpoint**: Quick-action buttons present and functional on both pages

---

## Dependencies & Execution Order

- **T001–T002 (US1)**: Independent — no dependencies on other stories
- **T003–T005 (US2)**: Independent — header is self-contained
- **T006 (US3)**: Independent — single text change
- **T007–T008 (US4)**: Depends on T003 (header styles) for visual consistency
- **T009–T010 (US5)**: Independent — route-level additions

All user stories can proceed in parallel after any shared CSS foundation.

## Implementation Strategy

1. T003 (header styles) first to establish visual foundation
2. T001–T002 (seed script) and T004–T010 (all UI) in parallel
3. Validate all scenarios from quickstart.md
