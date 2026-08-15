"""Integration tests for key API endpoints (feature 001 + 002 operator support)."""

import pytest


class TestHealth:
    def test_health(self, client):
        r = client.get("/api/health")
        assert r.status_code == 200
        assert r.json() == {"status": "ok"}


class TestTenantRegistration:
    def test_register_tenant(self, client):
        r = client.post("/api/tenants", json={
            "tenant_name": "TestCorp",
            "admin_email": "admin@testcorp.com",
            "admin_password": "Admin123",
        })
        assert r.status_code == 200
        data = r.json()
        assert data["tenant"]["name"] == "TestCorp"
        assert data["user"]["role"] == "admin"
        assert "token" in data

    def test_register_duplicate_tenant(self, client):
        client.post("/api/tenants", json={
            "tenant_name": "DupCorp",
            "admin_email": "a@dup.com",
            "admin_password": "Admin123",
        })
        r = client.post("/api/tenants", json={
            "tenant_name": "DupCorp",
            "admin_email": "b@dup.com",
            "admin_password": "Admin123",
        })
        assert r.status_code == 409

    def test_register_weak_password(self, client):
        r = client.post("/api/tenants", json={
            "tenant_name": "WeakCorp",
            "admin_email": "a@weak.com",
            "admin_password": "short",
        })
        assert r.status_code == 400


class TestAuth:
    @pytest.fixture(autouse=True)
    def setup_tenant(self, client):
        client.post("/api/tenants", json={
            "tenant_name": "AuthTest",
            "admin_email": "admin@authtest.com",
            "admin_password": "Admin123",
        })

    def test_login_success(self, client):
        r = client.post("/api/auth/login", json={
            "email": "admin@authtest.com",
            "password": "Admin123",
        })
        assert r.status_code == 200
        assert "token" in r.json()

    def test_login_bad_password(self, client):
        r = client.post("/api/auth/login", json={
            "email": "admin@authtest.com",
            "password": "WrongPass1",
        })
        assert r.status_code == 401

    def test_me_with_token(self, client):
        login = client.post("/api/auth/login", json={
            "email": "admin@authtest.com",
            "password": "Admin123",
        })
        token = login.json()["token"]
        r = client.get("/api/me", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        assert r.json()["email"] == "admin@authtest.com"
        assert r.json()["tenant_id"] is not None

    def test_me_without_token(self, client):
        r = client.get("/api/me")
        assert r.status_code == 401

    def test_change_password(self, client):
        login = client.post("/api/auth/login", json={
            "email": "admin@authtest.com",
            "password": "Admin123",
        })
        token = login.json()["token"]
        r = client.patch("/api/me/password", json={
            "current_password": "Admin123",
            "new_password": "NewPass456",
        }, headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200

        # Old password should no longer work
        r2 = client.post("/api/auth/login", json={
            "email": "admin@authtest.com",
            "password": "Admin123",
        })
        assert r2.status_code == 401

        # New password should work
        r3 = client.post("/api/auth/login", json={
            "email": "admin@authtest.com",
            "password": "NewPass456",
        })
        assert r3.status_code == 200

    def test_change_password_wrong_current(self, client):
        login = client.post("/api/auth/login", json={
            "email": "admin@authtest.com",
            "password": "Admin123",
        })
        token = login.json()["token"]
        r = client.patch("/api/me/password", json={
            "current_password": "Wrong123",
            "new_password": "NewPass456",
        }, headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 400

    def test_change_password_weak(self, client):
        login = client.post("/api/auth/login", json={
            "email": "admin@authtest.com",
            "password": "Admin123",
        })
        token = login.json()["token"]
        r = client.patch("/api/me/password", json={
            "current_password": "Admin123",
            "new_password": "short",
        }, headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 400


class TestOperator:
    @pytest.fixture(autouse=True)
    def setup_operator(self, db_session):
        from app.auth import hash_password
        from app.models import Operator
        op = Operator(email="op@test.com", password_hash=hash_password("Op12345"))
        db_session.add(op)
        db_session.commit()

    def test_operator_login(self, client):
        r = client.post("/api/operator/login", json={
            "email": "op@test.com",
            "password": "Op12345",
        })
        assert r.status_code == 200
        assert r.json()["operator"]["email"] == "op@test.com"

    def test_operator_bad_password(self, client):
        r = client.post("/api/operator/login", json={
            "email": "op@test.com",
            "password": "wrong",
        })
        assert r.status_code == 401

    def test_operator_me_returns_operator_role(self, client):
        """FR-004/FR-005: operator token returns role 'operator' from /api/me."""
        login = client.post("/api/operator/login", json={
            "email": "op@test.com",
            "password": "Op12345",
        })
        token = login.json()["token"]
        r = client.get("/api/me", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        assert r.json()["role"] == "operator"
        assert r.json()["tenant_id"] is None

    def test_operator_change_password(self, client):
        """FR-006/FR-007: operator can change password; old password invalidated."""
        login = client.post("/api/operator/login", json={
            "email": "op@test.com",
            "password": "Op12345",
        })
        token = login.json()["token"]
        r = client.patch("/api/me/password", json={
            "current_password": "Op12345",
            "new_password": "NewOp12345",
        }, headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200

        r2 = client.post("/api/operator/login", json={
            "email": "op@test.com",
            "password": "Op12345",
        })
        assert r2.status_code == 401

        r3 = client.post("/api/operator/login", json={
            "email": "op@test.com",
            "password": "NewOp12345",
        })
        assert r3.status_code == 200

    def test_operator_tenants_list(self, client):
        login = client.post("/api/operator/login", json={
            "email": "op@test.com",
            "password": "Op12345",
        })
        token = login.json()["token"]
        r = client.get("/api/operator/tenants", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_tenant_user_cannot_access_operator_endpoint(self, client):
        """FR-009: tenant token is rejected by operator-only endpoints."""
        client.post("/api/tenants", json={
            "tenant_name": "IsolationTest",
            "admin_email": "admin@iso.com",
            "admin_password": "Admin123",
        })
        login = client.post("/api/auth/login", json={
            "email": "admin@iso.com",
            "password": "Admin123",
        })
        token = login.json()["token"]
        r = client.get("/api/operator/tenants", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 403


class TestAnalytics:
    @pytest.fixture(autouse=True)
    def setup(self, client, db_session):
        from app.auth import hash_password
        from app.models import DataSource, Tenant, TenantMembership, User
        t = Tenant(name="AnalyticsCorp")
        db_session.add(t)
        db_session.flush()
        u = User(tenant_id=t.id, email="a@analytics.com", password_hash=hash_password("Admin123"))
        db_session.add(u)
        db_session.flush()
        db_session.add(TenantMembership(tenant_id=t.id, user_id=u.id, role="admin"))
        ds = DataSource(tenant_id=t.id, source_type="xlsx", name="data.xlsx", status="active")
        db_session.add(ds)
        db_session.commit()
        self.token = client.post("/api/auth/login", json={
            "email": "a@analytics.com", "password": "Admin123",
        }).json()["token"]
        self.source_id = ds.id

    def test_create_request(self, client):
        r = client.post("/api/analytics-requests", json={
            "title": "Monthly Sales",
            "objective": "Find trends",
            "data_source_ids": [self.source_id],
        }, headers={"Authorization": f"Bearer {self.token}"})
        assert r.status_code == 200
        assert r.json()["status"] == "queued"
        assert r.json()["selected_method"] == "tabular_descriptive_analysis"

    def test_list_requests(self, client):
        client.post("/api/analytics-requests", json={
            "title": "Test", "objective": "Test",
            "data_source_ids": [self.source_id],
        }, headers={"Authorization": f"Bearer {self.token}"})
        r = client.get("/api/analytics-requests", headers={"Authorization": f"Bearer {self.token}"})
        assert r.status_code == 200
        assert len(r.json()) == 1
