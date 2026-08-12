"""Analytics requests, method selection, results, and exports."""

import csv
import io
import os
from datetime import datetime, timezone

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from .auth import current_user
from .models import AnalyticsRequest, AnalyticsResult, AuditLog, DataSource
from .storage import UPLOAD_DIR, get_db

router = APIRouter(tags=["analytics"])


# ---------------------------------------------------------------------------
# Schemas
# ---------------------------------------------------------------------------

class AnalyticsRequestCreate(BaseModel):
    title: str
    objective: str
    data_source_ids: list[str]


class AnalyticsRequestDetail(BaseModel):
    request_id: str


class DownloadRequest(BaseModel):
    request_id: str
    format: str  # csv, pdf, xlsx


# ---------------------------------------------------------------------------
# Method router
# ---------------------------------------------------------------------------

METHOD_ROUTING = {
    "xlsx": "tabular_descriptive_analysis",
    "csv": "tabular_descriptive_analysis",
    "text": "document_summarization",
    "pdf": "document_extraction_and_analysis",
    "docx": "document_extraction_and_analysis",
}


def _select_method(source_types: list[str]) -> tuple[str, str]:
    types = set(source_types)
    if types & {"xlsx"}:
        method = "tabular_descriptive_analysis"
        rationale = "Excel spreadsheet detected — running descriptive statistics and trend analysis."
    elif types & {"pdf", "docx"}:
        method = "document_extraction_and_analysis"
        rationale = "Document file detected — extracting text and performing content analysis."
    elif types & {"text"}:
        method = "document_summarization"
        rationale = "Text file detected — generating summary and key phrase extraction."
    else:
        method = "generic_exploration"
        rationale = "Mixed or unknown source types — running general data exploration."
    return method, rationale


# ---------------------------------------------------------------------------
# POST /api/analytics-requests
# ---------------------------------------------------------------------------

@router.post("/analytics-requests")
def create_analytics_request(
    body: AnalyticsRequestCreate,
    user=Depends(current_user),
    db: Session = Depends(get_db),
):
    sources = (
        db.query(DataSource)
        .filter(
            DataSource.id.in_(body.data_source_ids),
            DataSource.tenant_id == user.tenant_id,
            DataSource.status == "active",
        )
        .all()
    )
    if len(sources) != len(body.data_source_ids):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="One or more data sources not found or not active")

    method, rationale = _select_method([s.source_type for s in sources])

    req = AnalyticsRequest(
        tenant_id=user.tenant_id,
        user_id=user.id,
        title=body.title,
        objective=body.objective,
        status="queued",
        selected_method=method,
        method_rationale=rationale,
        input_summary=f"{len(sources)} source(s): {', '.join(s.name for s in sources)}",
    )
    db.add(req)
    db.flush()

    db.add(AuditLog(
        tenant_id=user.tenant_id,
        user_id=user.id,
        event_type="request_submitted",
        entity_type="AnalyticsRequest",
        entity_id=req.id,
    ))
    db.commit()

    return {"id": req.id, "status": req.status, "selected_method": method}


# ---------------------------------------------------------------------------
# GET /api/analytics-requests  — list for current tenant user
# ---------------------------------------------------------------------------

@router.get("/analytics-requests")
def list_analytics_requests(
    user=Depends(current_user),
    db: Session = Depends(get_db),
):
    reqs = (
        db.query(AnalyticsRequest)
        .filter(AnalyticsRequest.tenant_id == user.tenant_id)
        .order_by(AnalyticsRequest.requested_at.desc())
        .all()
    )
    return [
        {
            "id": r.id,
            "title": r.title,
            "status": r.status,
            "selected_method": r.selected_method,
            "requested_at": r.requested_at.isoformat() if r.requested_at else None,
        }
        for r in reqs
    ]


# ---------------------------------------------------------------------------
# POST /api/analytics-requests/detail
# ---------------------------------------------------------------------------

@router.post("/analytics-requests/detail")
def get_analytics_request_detail(
    body: AnalyticsRequestDetail,
    user=Depends(current_user),
    db: Session = Depends(get_db),
):
    req = (
        db.query(AnalyticsRequest)
        .filter(AnalyticsRequest.id == body.request_id, AnalyticsRequest.tenant_id == user.tenant_id)
        .first()
    )
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
    return {
        "id": req.id,
        "title": req.title,
        "objective": req.objective,
        "status": req.status,
        "selected_method": req.selected_method,
        "method_rationale": req.method_rationale,
        "requested_at": req.requested_at.isoformat() if req.requested_at else None,
        "started_at": req.started_at.isoformat() if req.started_at else None,
        "completed_at": req.completed_at.isoformat() if req.completed_at else None,
        "error_message": req.error_message,
    }


# ---------------------------------------------------------------------------
# POST /api/analytics-requests/result
# ---------------------------------------------------------------------------

@router.post("/analytics-requests/result")
def get_analytics_request_result(
    body: AnalyticsRequestDetail,
    user=Depends(current_user),
    db: Session = Depends(get_db),
):
    result = (
        db.query(AnalyticsResult)
        .join(AnalyticsRequest)
        .filter(
            AnalyticsResult.request_id == body.request_id,
            AnalyticsRequest.tenant_id == user.tenant_id,
        )
        .first()
    )
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Result not found")
    return {
        "request_id": result.request_id,
        "summary_text": result.summary_text,
        "metrics_payload": result.metrics_payload,
        "visualization_payload": result.visualization_payload,
    }


# ---------------------------------------------------------------------------
# POST /api/analytics-requests/download
# ---------------------------------------------------------------------------

@router.post("/analytics-requests/download")
def download_analytics_result(
    body: DownloadRequest,
    user=Depends(current_user),
    db: Session = Depends(get_db),
):
    result = (
        db.query(AnalyticsResult)
        .join(AnalyticsRequest)
        .filter(
            AnalyticsResult.request_id == body.request_id,
            AnalyticsRequest.tenant_id == user.tenant_id,
        )
        .first()
    )
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Result not found")

    metrics = result.metrics_payload or {}
    summary = result.summary_text or ""

    if body.format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["Metric", "Value"])
        for k, v in metrics.items():
            writer.writerow([k, v])
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=result_{body.request_id}.csv"},
        )

    elif body.format == "xlsx":
        output = io.BytesIO()
        df = pd.DataFrame(list(metrics.items()), columns=["Metric", "Value"])
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Results")
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename=result_{body.request_id}.xlsx"},
        )

    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported format")