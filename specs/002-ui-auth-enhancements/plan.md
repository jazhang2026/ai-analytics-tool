# Implementation Plan: UI and Auth Enhancements

**Branch**: `002-ui-auth-enhancements` | **Date**: 2026-08-12 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-ui-auth-enhancements/spec.md`

## Summary

Enhance the existing data analytics platform with: a standalone operator seed script (not deployed), a branded header with user email dropdown menu, updated login page text, a persistent navigation bar, and quick-action "New Request" buttons on Dashboard and Data Analytics pages. All UI changes use the existing Vite + vanilla JS/CSS/HTML frontend stack and the Python FastAPI backend.

## Technical Context

**Language/Version**: JavaScript (ES modules) with Vite; Python 3.11+

**Primary Dependencies**: Vite, vanilla HTML/CSS/JavaScript, FastAPI (existing stack — no new dependencies)

**Storage**: Existing embedded SQLite database (no schema changes)

**Testing**: Manual browser validation across all pages; operator seed script test via CLI

**Target Platform**: Same as 001 — localhost inside Devin IDE + Render-compatible hosting

**Project Type**: Enhancement to existing full-stack web application

**Performance Goals**: Dropdown menu opens within 200ms; navigation responds within 1 second

**Constraints**: No new libraries; minimal changes to existing backend; seed script is standalone and excluded from deployment

**Scale/Scope**: Small enhancement; affects frontend shell and adds one backend CLI script

## Constitution Check

*GATE: Must pass before implementation.*

- Code quality satisfied by minimal, focused changes to existing files
- Test-first development satisfied by manual validation scenarios in quickstart
- User experience consistency satisfied by uniform header/nav across all pages
- Performance satisfied by lightweight vanilla JS dropdown and navigation
- AI reliability N/A for this feature

**Gate status**: PASS

## Project Structure

### Files to modify

```text
frontend/src/main.js        # Header, nav bar, dropdown menu
frontend/src/routes.js      # Login text, nav, "New Request" buttons
frontend/src/styles.css     # Header, nav, dropdown styles
backend/tests/seed_operator.py    # NEW: standalone CLI seed script (in tests/ — excluded from production)
```

### Files changed (backend)

```text
backend/app/main.py         # /api/me and /api/me/password extended for operator support
```

### Files unchanged

```text
frontend/src/api.js         # No API client changes
frontend/src/ui.js          # No UI helper changes
```

## Implementation Approach

### US1: Operator Seed Script
- New file: `backend/tests/seed_operator.py`
- Standalone Python script that imports from `app.models` and `app.auth`
- Creates operator if not exists; idempotent
- Located in `tests/` directory — naturally excluded from production deployment
- Run via: `python tests/seed_operator.py`

### US2: Header with Brand and User Menu
- Modify `main.js` navBar() to output header with brand + email dropdown
- Pure CSS dropdown (no JS library)
- Click handler toggles dropdown; outside click closes it

### US3: Login Page Updates
- Modify text in `routes.js` login route
- Ensure login page shows when unauthenticated

### US4: Navigation Bar
- Modify `main.js` navBar() to include persistent nav links
- "Users" link gated by admin role check

### US5: Quick Action Buttons
- Add "New Request" button to Dashboard and Data Analytics routes in `routes.js`