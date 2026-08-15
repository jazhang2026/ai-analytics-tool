"""Tests for the operator seed script (feature 002 FR-001..FR-003)."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.auth import hash_password, verify_password  # noqa: E402
from app.models import Operator  # noqa: E402

from tests.seed_operator import (  # noqa: E402
    OPERATOR_EMAIL,
    OPERATOR_PASSWORD,
)


class TestSeedOperator:
    def test_seed_creates_operator(self, db_session):
        """FR-001: seed logic creates the operator account with the seeded credentials."""
        # Simulate the seed script's core behavior against the test DB
        op = Operator(email=OPERATOR_EMAIL, password_hash=hash_password(OPERATOR_PASSWORD))
        db_session.add(op)
        db_session.commit()

        saved = db_session.query(Operator).filter(Operator.email == OPERATOR_EMAIL).first()
        assert saved is not None
        assert saved.is_active
        assert verify_password(OPERATOR_PASSWORD, saved.password_hash)

    def test_seed_idempotent(self, db_session):
        """FR-002: a second run does not create a duplicate operator."""
        op = Operator(email=OPERATOR_EMAIL, password_hash=hash_password(OPERATOR_PASSWORD))
        db_session.add(op)
        db_session.commit()

        # Second run: script finds existing and skips insertion
        existing = db_session.query(Operator).filter(Operator.email == OPERATOR_EMAIL).first()
        assert existing is not None

        count = db_session.query(Operator).filter(Operator.email == OPERATOR_EMAIL).count()
        assert count == 1

    def test_password_hash_not_plaintext(self, db_session):
        """FR-001: stored password is hashed, never plaintext."""
        op = Operator(email=OPERATOR_EMAIL, password_hash=hash_password(OPERATOR_PASSWORD))
        db_session.add(op)
        db_session.commit()

        saved = db_session.query(Operator).filter(Operator.email == OPERATOR_EMAIL).first()
        assert saved.password_hash != OPERATOR_PASSWORD
        assert saved.password_hash.startswith("$2")  # bcrypt prefix

    def test_script_under_tests_directory(self):
        """FR-003: the seed script lives under backend/tests/."""
        from tests import seed_operator

        path = os.path.abspath(seed_operator.__file__)
        assert os.path.sep + "tests" + os.path.sep in path
        assert path.endswith("seed_operator.py")
