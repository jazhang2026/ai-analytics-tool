"""Tests for entity creation, relationships, and unique constraints."""

import pytest
from sqlalchemy.exc import IntegrityError

from app.auth import hash_password
from app.models import (
    AnalyticsRequest,
    BackupRecord,
    DataSource,
    Operator,
    Tenant,
    TenantMembership,
    User,
)


class TestTenant:
    def test_create_tenant(self, db_session):
        t = Tenant(name="Test Corp")
        db_session.add(t)
        db_session.commit()
        assert t.id is not None
        assert t.status == "active"

    def test_tenant_name_unique(self, db_session):
        db_session.add(Tenant(name="UniqueCorp"))
        db_session.commit()
        db_session.add(Tenant(name="UniqueCorp"))
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestUser:
    def test_create_user(self, db_session):
        t = Tenant(name="Acme")
        db_session.add(t)
        db_session.flush()
        u = User(tenant_id=t.id, email="user@acme.com", password_hash=hash_password("Test1234"))
        db_session.add(u)
        db_session.commit()
        assert u.tenant_id == t.id
        assert u.is_active

    def test_user_email_unique_within_tenant(self, db_session):
        t = Tenant(name="Acme")
        db_session.add(t)
        db_session.flush()
        db_session.add(User(tenant_id=t.id, email="dup@acme.com", password_hash="x"))
        db_session.commit()
        db_session.add(User(tenant_id=t.id, email="dup@acme.com", password_hash="x"))
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestOperator:
    def test_create_operator(self, db_session):
        op = Operator(email="op@test.com", password_hash=hash_password("Op12345"))
        db_session.add(op)
        db_session.commit()
        assert op.is_active

    def test_operator_email_unique(self, db_session):
        db_session.add(Operator(email="op@test.com", password_hash="x"))
        db_session.commit()
        db_session.add(Operator(email="op@test.com", password_hash="x"))
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestTenantMembership:
    def test_membership_unique(self, db_session):
        t = Tenant(name="Acme")
        db_session.add(t)
        db_session.flush()
        u = User(tenant_id=t.id, email="u@acme.com", password_hash="x")
        db_session.add(u)
        db_session.flush()
        db_session.add(TenantMembership(tenant_id=t.id, user_id=u.id, role="admin"))
        db_session.commit()
        db_session.add(TenantMembership(tenant_id=t.id, user_id=u.id, role="user"))
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestDataSource:
    def test_create_source(self, db_session):
        t = Tenant(name="Acme")
        db_session.add(t)
        db_session.flush()
        ds = DataSource(tenant_id=t.id, source_type="xlsx", name="sales.xlsx", status="active")
        db_session.add(ds)
        db_session.commit()
        assert ds.source_type == "xlsx"


class TestAnalyticsRequest:
    def test_create_request(self, db_session):
        t = Tenant(name="Acme")
        db_session.add(t)
        db_session.flush()
        u = User(tenant_id=t.id, email="u@acme.com", password_hash="x")
        db_session.add(u)
        db_session.flush()
        ar = AnalyticsRequest(
            tenant_id=t.id, user_id=u.id, title="Test", objective="Analyze",
            status="draft", selected_method="tabular",
        )
        db_session.add(ar)
        db_session.commit()
        assert ar.status == "draft"


class TestBackupRecord:
    def test_create_backup(self, db_session):
        op = Operator(email="op@test.com", password_hash="x")
        db_session.add(op)
        db_session.flush()
        br = BackupRecord(operator_id=op.id, file_path="/tmp/b.db", file_size=100)
        db_session.add(br)
        db_session.commit()
        assert br.file_size == 100
