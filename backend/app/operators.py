"""Operator authentication, cross-tenant access, backup and restore."""

import os
import shutil
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from .auth import (
    create_token, current_operator, hash_password, validate_password_policy,
    verify_password,
)
from .models import (
    AnalyticsRequest, AuditLog, BackupRecord, DataSource, Operator, Tenant,
    TenantMembership, User,
)
from .storage import BACKUP_DIR, DB_PATH, get_db

router = APIRouter(tags=["operators"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class OperatorLoginRequest(BaseModel):
    email: EmailStr
    password: str


class TenantDetailRequest(BaseModel):
    tenant_id: str


class TenantUsersRequest(BaseModel):
    tenant_id: str


class RestoreRequest(BaseModel):
    backup_id: str


# ---------------------------------------------------------------------------
# POST /api/operator/login
# ---------------------------------------------------------------------------

@router.post("/operator/login")
def operator_login(body: OperatorLoginRequest, db: Session = Depends(get_db)):
    op = db.query(Operator).filter(Operator.email == body.email).first()
    if not op or not verify_password(body.password, op.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not op.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is inactive")
    token = create_token(op.id, {"type": "operator"})
    return {
        "operator": {"id": op.id, "email": op.email},
        "token": token,
        "message": "logged_in",
    }


# ---------------------------------------------------------------------------
# POST /api/operator/logout
# ---------------------------------------------------------------------------

@router.post("/operator/logout")
def operator_logout():
    return {"message": "logged_out"}


# ---------------------------------------------------------------------------
# GET /api/operator/tenants
# ---------------------------------------------------------------------------

@router.get("/operator/tenants")
def list_tenants(op: Operator = Depends(current_operator), db: Session = Depends(get_db)):
    tenants = db.query(Tenant).order_by(Tenant.created_at.desc()).all()
    return [{"id": t.id, "name": t.name, "status": t.status, "created_at": t.created_at.isoformat() if t.created_at else None} for t in tenants]


# ---------------------------------------------------------------------------
# POST /api/operator/tenants/detail
# ---------------------------------------------------------------------------

@router.post("/operator/tenants/detail")
def tenant_detail(body: TenantDetailRequest, op: Operator = Depends(current_operator), db: Session = Depends(get_db)):
    tenant = db.query(Tenant).filter(Tenant.id == body.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tenant not found")

    users = (
        db.query(User, TenantMembership)
        .join(TenantMembership, TenantMembership.user_id == User.id)
        .filter(TenantMembership.tenant_id == tenant.id)
        .all()
    )
    sources = db.query(DataSource).filter(DataSource.tenant_id == tenant.id).all()
    requests = db.query(AnalyticsRequest).filter(AnalyticsRequest.tenant_id == tenant.id).order_by(AnalyticsRequest.requested_at.desc()).limit(20).all()

    return {
        "tenant": {"id": tenant.id, "name": tenant.name, "status": tenant.status},
        "users": [{"id": u.id, "email": u.email, "role": m.role} for u, m in users],
        "data_sources": [{"id": s.id, "name": s.name, "source_type": s.source_type, "status": s.status} for s in sources],
        "recent_requests": [{"id": r.id, "title": r.title, "status": r.status} for r in requests],
    }


# ---------------------------------------------------------------------------
# POST /api/operator/tenants/users
# ---------------------------------------------------------------------------

@router.post("/operator/tenants/users")
def tenant_users(body: TenantUsersRequest, op: Operator = Depends(current_operator), db: Session = Depends(get_db)):
    users = (
        db.query(User, TenantMembership)
        .join(TenantMembership, TenantMembership.user_id == User.id)
        .filter(TenantMembership.tenant_id == body.tenant_id)
        .all()
    )
    return [{"id": u.id, "email": u.email, "role": m.role} for u, m in users]


# ---------------------------------------------------------------------------
# POST /api/operator/backup
# ---------------------------------------------------------------------------

@router.post("/operator/backup")
def create_backup(op: Operator = Depends(current_operator), db: Session = Depends(get_db)):
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    backup_name = f"backup_{timestamp}.db"
    backup_path = os.path.join(BACKUP_DIR, backup_name)

    shutil.copy2(DB_PATH, backup_path)
    file_size = os.path.getsize(backup_path)

    record = BackupRecord(
        operator_id=op.id,
        file_path=backup_path,
        file_size=file_size,
    )
    db.add(record)
    db.add(AuditLog(
        operator_id=op.id,
        event_type="backup_created",
        entity_type="BackupRecord",
        entity_id=record.id,
    ))
    db.commit()

    return {
        "backup_id": record.id,
        "file_size": file_size,
        "created_at": record.created_at.isoformat(),
        "message": "backup_created",
    }


# ---------------------------------------------------------------------------
# GET /api/operator/backups  — list backup history
# ---------------------------------------------------------------------------

@router.get("/operator/backups")
def list_backups(op: Operator = Depends(current_operator), db: Session = Depends(get_db)):
    records = db.query(BackupRecord).order_by(BackupRecord.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "file_size": r.file_size,
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "notes": r.notes,
        }
        for r in records
    ]


# ---------------------------------------------------------------------------
# POST /api/operator/restore
# ---------------------------------------------------------------------------

@router.post("/operator/restore")
def restore_backup(body: RestoreRequest, op: Operator = Depends(current_operator), db: Session = Depends(get_db)):
    record = db.query(BackupRecord).filter(BackupRecord.id == body.backup_id).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Backup not found")
    if not os.path.exists(record.file_path):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Backup file missing")

    shutil.copy2(record.file_path, DB_PATH)

    db.add(AuditLog(
        operator_id=op.id,
        event_type="restore_completed",
        entity_type="BackupRecord",
        entity_id=record.id,
    ))
    db.commit()

    return {"message": "restore_completed"}