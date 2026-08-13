"""File-based data source upload, listing, validation, and deletion."""

import os
import shutil
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .auth import current_user
from .models import AuditLog, DataSource, User
from .storage import UPLOAD_DIR, get_db

router = APIRouter(tags=["data-sources"])

ALLOWED_EXTENSIONS = {".txt", ".pdf", ".docx", ".xlsx"}
EXT_TO_TYPE = {".txt": "text", ".pdf": "pdf", ".docx": "docx", ".xlsx": "xlsx"}


class ValidateRequest(BaseModel):
    data_source_id: str


class DeleteRequest(BaseModel):
    data_source_id: str


@router.get("/data-sources")
def list_data_sources(user: User = Depends(current_user), db: Session = Depends(get_db)):
    sources = (
        db.query(DataSource)
        .filter(DataSource.tenant_id == user.tenant_id)
        .order_by(DataSource.created_at.desc())
        .all()
    )
    return [
        {
            "id": s.id,
            "name": s.name,
            "source_type": s.source_type,
            "status": s.status,
            "file_size": s.file_size,
            "created_at": s.created_at.isoformat() if s.created_at else None,
        }
        for s in sources
    ]


@router.post("/data-sources")
async def create_data_source(
    file: UploadFile = File(...),
    name: str = Form(""),
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Allowed: .txt, .pdf, .docx, .xlsx",
        )

    source_type = EXT_TO_TYPE[ext]
    label = name.strip() or (file.filename or f"upload{ext}")

    # Stream file to the tenant's upload directory
    tenant_dir = Path(UPLOAD_DIR) / user.tenant_id
    tenant_dir.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}{ext}"
    stored_path = tenant_dir / stored_name

    size = 0
    with open(stored_path, "wb") as out:
        while chunk := await file.read(1024 * 1024):
            out.write(chunk)
            size += len(chunk)

    source = DataSource(
        tenant_id=user.tenant_id,
        created_by_user_id=user.id,
        source_type=source_type,
        name=label,
        status="active",
        file_path=str(stored_path),
        file_size=size,
    )
    db.add(source)
    db.flush()
    db.add(AuditLog(
        tenant_id=user.tenant_id,
        user_id=user.id,
        event_type="file_uploaded",
        entity_type="DataSource",
        entity_id=source.id,
    ))
    db.commit()

    return {
        "id": source.id,
        "name": source.name,
        "source_type": source.source_type,
        "status": source.status,
        "file_size": size,
    }


@router.post("/data-sources/validate")
def validate_data_source(
    body: ValidateRequest,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    source = (
        db.query(DataSource)
        .filter(DataSource.id == body.data_source_id, DataSource.tenant_id == user.tenant_id)
        .first()
    )
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data source not found")

    if not source.file_path or not os.path.exists(source.file_path):
        source.status = "invalid"
        db.commit()
        return {"id": source.id, "status": "invalid", "last_validated_at": None}

    source.status = "active"
    from datetime import datetime, timezone
    source.last_validated_at = datetime.now(timezone.utc)
    db.commit()
    return {
        "id": source.id,
        "status": source.status,
        "last_validated_at": source.last_validated_at.isoformat() if source.last_validated_at else None,
    }


@router.post("/data-sources/delete")
def delete_data_source(
    body: DeleteRequest,
    user: User = Depends(current_user),
    db: Session = Depends(get_db),
):
    source = (
        db.query(DataSource)
        .filter(DataSource.id == body.data_source_id, DataSource.tenant_id == user.tenant_id)
        .first()
    )
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Data source not found")

    if source.file_path and os.path.exists(source.file_path):
        try:
            os.remove(source.file_path)
        except OSError:
            pass

    db.delete(source)
    db.add(AuditLog(
        tenant_id=user.tenant_id,
        user_id=user.id,
        event_type="data_source_deleted",
        entity_type="DataSource",
        entity_id=source.id,
    ))
    db.commit()
    return {"message": "data_source_deleted"}