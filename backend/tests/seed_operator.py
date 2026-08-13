#!/usr/bin/env python3
"""Standalone operator seed script.

Run separately from the application:  python tests/seed_operator.py

This script is intentionally located under tests/ so it is never deployed
with the application code and operator credentials are not exposed in
production artifacts.
"""

import os
import sys

# Allow importing the app package from the backend directory
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

try:
    from app.auth import hash_password  # noqa: E402
    from app.models import Operator  # noqa: E402
    from app.storage import SessionLocal, init_db  # noqa: E402
except ModuleNotFoundError as exc:
    print(
        "ERROR: Missing dependency: " + str(exc) + "\n"
        "Make sure you are running inside the project virtual environment:\n"
        "  cd backend\n"
        "  source .venv/bin/activate\n"
        "  python tests/seed_operator.py\n",
        file=sys.stderr,
    )
    sys.exit(1)

OPERATOR_EMAIL = "operator@aiatool.com"
OPERATOR_PASSWORD = "Operator123"


def seed_operator() -> None:
    """Create the default operator account if it does not already exist."""
    init_db()
    db = SessionLocal()
    try:
        existing = db.query(Operator).filter(Operator.email == OPERATOR_EMAIL).first()
        if existing:
            print(f"Operator already exists: {OPERATOR_EMAIL}")
            return

        op = Operator(
            email=OPERATOR_EMAIL,
            password_hash=hash_password(OPERATOR_PASSWORD),
        )
        db.add(op)
        db.commit()
        print(f"Operator created: {OPERATOR_EMAIL}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_operator()
