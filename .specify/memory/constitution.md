<!--
Sync Impact Report:
Version change: 1.0.0 → 1.1.0
Modified principles: II (TDD → Simplicity First), V (AI Reliability → Security & Data Integrity)
Added sections: None
Removed sections: Outdated technology stack entries (LangChain, ChromaDB, FAISS, NumPy, mypy)
Templates requiring updates: ✅ plan-template.md, ✅ spec-template.md, ✅ tasks-template.md (compatible)
Follow-up TODOs: None
-->

# AI Analytics Tool Constitution

## Core Principles

### I. Code Quality
All code MUST be clear, self-documenting, and consistent. Python code follows PEP 8. JavaScript code uses consistent ES module patterns. Functions and classes MUST have descriptive names. Duplication MUST be avoided — shared logic belongs in reusable modules. Complex logic MUST be simplified or documented.

### II. Simplicity First
Prefer the simplest solution that meets the requirement. Vanilla HTML, CSS, and JavaScript are preferred over frameworks for the frontend. New dependencies MUST be justified — each added library increases maintenance burden and attack surface. The embedded database (SQLite) eliminates external infrastructure dependencies. YAGNI: do not build features before they are needed.

### III. User Experience Consistency
All pages MUST share a consistent header, navigation, and visual style. Terminology MUST be uniform across the application. Error messages MUST be actionable and human-readable. Forms MUST provide clear validation feedback. Response times SHOULD be under 2 seconds for standard operations.

### IV. Performance
File uploads MUST be validated within 5 seconds for files up to 10MB. Database queries MUST use appropriate indexes for common access patterns. Page navigation MUST feel responsive — under 1 second for standard transitions. Analytics requests MUST be acknowledged within 2 seconds of submission.

### V. Security & Data Integrity
All credentials MUST be stored as hashed values — never in plaintext. API keys and secrets MUST be read from environment variables, never hardcoded. User data is tenant-scoped: one tenant MUST never access another tenant's data. Operator credentials and seed scripts MUST be excluded from deployment artifacts. Input validation is mandatory on all user-supplied data.

## Technology Stack

- **Backend**: Python 3.11+, FastAPI, Uvicorn, SQLAlchemy
- **Frontend**: Vite, vanilla HTML/CSS/JavaScript (ES modules)
- **Database**: SQLite (embedded, no external server required)
- **Data Processing**: Pandas, python-docx, pypdf, openpyxl
- **Auth**: passlib (bcrypt), python-jose (JWT)
- **Testing**: pytest (where applicable)
- **Code Quality**: pylint, black

## Development Standards

### File Organization
- `backend/app/` — FastAPI application modules
- `backend/tests/` — test scripts and seed data (excluded from deployment)
- `frontend/src/` — Vite source files
- `specs/` — Spec-Driven Development feature specifications

### Security
- All API keys and credentials MUST be stored in environment variables
- Passwords MUST be hashed with bcrypt before storage
- User data MUST be tenant-scoped at the application layer
- Input validation is mandatory for all user inputs
- No hardcoded secrets in code

### Documentation
- Backend functions SHOULD have docstrings
- Architecture decisions MUST be documented in the specs directory
- User-facing documentation MUST be kept in sync with features
- README.md MUST contain up-to-date setup and run instructions

## Governance

This constitution supersedes all other development practices. Amendments require:
- Documentation of the proposed change
- Version increment following semantic versioning (MAJOR for principle removals, MINOR for additions/refinements, PATCH for wording fixes)

When a principle cannot be satisfied, the exception MUST be documented with justification.

**Version**: 1.1.0 | **Ratified**: 2026-08-06 | **Last Amended**: 2026-08-14