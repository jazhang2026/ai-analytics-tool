"""Tenant registration, user management, and role handling."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from .auth import (
    create_token, current_tenant_admin, current_user, hash_password,
    validate_password_policy,
)
from .models import Tenant, TenantMembership, User
from .storage import get_db

router = APIRouter(tags=["tenants"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class TenantRegisterRequest(BaseModel):
    tenant_name: str
    admin_email: EmailStr
    admin_password: str


class TenantUserCreateRequest(BaseModel):
    email: EmailStr
    password: str
    role: str  # admin or user


class RoleUpdateRequest(BaseModel):
    user_id: str
    role: str


class TenantResponse(BaseModel):
    id: str
    name: str

    model_config = {"from_attributes": True}


class UserResponse(BaseModel):
    id: str
    email: str
    role: str

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# POST /api/tenants  — register tenant + first admin
# ---------------------------------------------------------------------------

@router.post("/tenants")
def register_tenant(body: TenantRegisterRequest, db: Session = Depends(get_db)):
    validate_password_policy(body.admin_password)

    existing = db.query(Tenant).filter(Tenant.name == body.tenant_name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Tenant name already exists")

    tenant = Tenant(name=body.tenant_name)
    db.add(tenant)
    db.flush()

    user = User(
        tenant_id=tenant.id,
        email=body.admin_email,
        password_hash=hash_password(body.admin_password),
    )
    db.add(user)
    db.flush()

    membership = TenantMembership(tenant_id=tenant.id, user_id=user.id, role="admin")
    db.add(membership)
    db.commit()

    token = create_token(user.id, {"type": "tenant_user"})
    return {
        "tenant": {"id": tenant.id, "name": tenant.name},
        "user": {"id": user.id, "email": user.email, "role": "admin"},
        "token": token,
        "message": "tenant_created",
    }


# ---------------------------------------------------------------------------
# GET /api/tenant/users  — list users for current tenant
# ---------------------------------------------------------------------------

@router.get("/tenant/users")
def list_tenant_users(user: User = Depends(current_user), db: Session = Depends(get_db)):
    memberships = (
        db.query(TenantMembership, User)
        .join(User, TenantMembership.user_id == User.id)
        .filter(TenantMembership.tenant_id == user.tenant_id)
        .all()
    )
    return [
        {"id": u.id, "email": u.email, "role": m.role}
        for m, u in memberships
    ]


# ---------------------------------------------------------------------------
# POST /api/tenant/users  — create tenant user
# ---------------------------------------------------------------------------

@router.post("/tenant/users")
def create_tenant_user(
    body: TenantUserCreateRequest,
    admin: User = Depends(current_tenant_admin),
    db: Session = Depends(get_db),
):
    validate_password_policy(body.password)
    if body.role not in ("admin", "user"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role must be 'admin' or 'user'")

    existing = (
        db.query(User)
        .filter(User.tenant_id == admin.tenant_id, User.email == body.email)
        .first()
    )
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists in this tenant")

    user = User(
        tenant_id=admin.tenant_id,
        email=body.email,
        password_hash=hash_password(body.password),
    )
    db.add(user)
    db.flush()

    membership = TenantMembership(tenant_id=admin.tenant_id, user_id=user.id, role=body.role)
    db.add(membership)
    db.commit()

    return {"id": user.id, "email": user.email, "role": body.role}


# ---------------------------------------------------------------------------
# POST /api/tenant/users/role  — update user role
# ---------------------------------------------------------------------------

@router.post("/tenant/users/role")
def update_user_role(
    body: RoleUpdateRequest,
    admin: User = Depends(current_tenant_admin),
    db: Session = Depends(get_db),
):
    if body.role not in ("admin", "user"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role must be 'admin' or 'user'")

    membership = (
        db.query(TenantMembership)
        .filter(
            TenantMembership.tenant_id == admin.tenant_id,
            TenantMembership.user_id == body.user_id,
        )
        .first()
    )
    if not membership:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found in this tenant")

    membership.role = body.role
    db.commit()
    return {"message": "role_updated"}