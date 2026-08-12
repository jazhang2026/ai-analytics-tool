"""Core tenant-scoped data models for the multi-tenant analytics platform."""

import datetime
import uuid

from sqlalchemy import (
    Column, String, Boolean, DateTime, Integer, Text, JSON, ForeignKey, Index,
    UniqueConstraint, Enum as SAEnum,
)
from sqlalchemy.orm import DeclarativeBase, relationship


def _new_uuid() -> str:
    return str(uuid.uuid4())


def _utcnow() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# Tenant
# ---------------------------------------------------------------------------

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(String, primary_key=True, default=_new_uuid)
    name = Column(String, nullable=False)
    status = Column(String, nullable=False, default="active")  # active, suspended, disabled
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    created_by_user_id = Column(String, nullable=True)

    users = relationship("User", back_populates="tenant")
    data_sources = relationship("DataSource", back_populates="tenant")
    analytics_requests = relationship("AnalyticsRequest", back_populates="tenant")
    audit_logs = relationship("AuditLog", back_populates="tenant")

    __table_args__ = (
        Index("ix_tenants_name", "name", unique=True),
        Index("ix_tenants_status", "status"),
    )


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=_new_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    email = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    password_changed_at = Column(DateTime(timezone=True), nullable=True)

    tenant = relationship("Tenant", back_populates="users")
    membership = relationship("TenantMembership", uselist=False, back_populates="user")
    analytics_requests = relationship("AnalyticsRequest", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")

    __table_args__ = (
        UniqueConstraint("tenant_id", "email", name="uq_users_tenant_email"),
        Index("ix_users_tenant_id", "tenant_id"),
        Index("ix_users_is_active", "is_active"),
    )


# ---------------------------------------------------------------------------
# Operator
# ---------------------------------------------------------------------------

class Operator(Base):
    __tablename__ = "operators"

    id = Column(String, primary_key=True, default=_new_uuid)
    email = Column(String, nullable=False)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    last_login_at = Column(DateTime(timezone=True), nullable=True)

    audit_logs = relationship("AuditLog", back_populates="operator")
    backup_records = relationship("BackupRecord", back_populates="operator")

    __table_args__ = (
        Index("ix_operators_email", "email", unique=True),
        Index("ix_operators_is_active", "is_active"),
    )


# ---------------------------------------------------------------------------
# TenantMembership
# ---------------------------------------------------------------------------

class TenantMembership(Base):
    __tablename__ = "tenant_memberships"

    id = Column(String, primary_key=True, default=_new_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    role = Column(String, nullable=False)  # admin, user
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)

    tenant = relationship("Tenant")
    user = relationship("User", back_populates="membership")

    __table_args__ = (
        UniqueConstraint("tenant_id", "user_id", name="uq_membership_tenant_user"),
        Index("ix_membership_tenant_id", "tenant_id"),
        Index("ix_membership_role", "role"),
    )


# ---------------------------------------------------------------------------
# DataSource
# ---------------------------------------------------------------------------

class DataSource(Base):
    __tablename__ = "data_sources"

    id = Column(String, primary_key=True, default=_new_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    created_by_user_id = Column(String, nullable=True)
    source_type = Column(String, nullable=False)  # text, pdf, docx, xlsx
    name = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")  # pending, validating, active, invalid, disabled
    file_path = Column(String, nullable=True)
    file_size = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    last_validated_at = Column(DateTime(timezone=True), nullable=True)

    tenant = relationship("Tenant", back_populates="data_sources")

    __table_args__ = (
        Index("ix_ds_tenant_id", "tenant_id"),
        Index("ix_ds_status", "status"),
        Index("ix_ds_source_type", "source_type"),
    )


# ---------------------------------------------------------------------------
# AnalyticsRequest
# ---------------------------------------------------------------------------

class AnalyticsRequest(Base):
    __tablename__ = "analytics_requests"

    id = Column(String, primary_key=True, default=_new_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    objective = Column(Text, nullable=False)
    status = Column(String, nullable=False, default="draft")  # draft, queued, running, succeeded, failed, canceled
    selected_method = Column(String, nullable=True)
    method_rationale = Column(Text, nullable=True)
    input_summary = Column(Text, nullable=True)
    requested_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    error_message = Column(Text, nullable=True)

    tenant = relationship("Tenant", back_populates="analytics_requests")
    user = relationship("User", back_populates="analytics_requests")
    result = relationship("AnalyticsResult", uselist=False, back_populates="request")
    audit_logs = relationship("AuditLog", back_populates="request")

    __table_args__ = (
        Index("ix_ar_tenant_id", "tenant_id"),
        Index("ix_ar_user_id", "user_id"),
        Index("ix_ar_status", "status"),
        Index("ix_ar_requested_at", "requested_at"),
    )


# ---------------------------------------------------------------------------
# AnalyticsResult
# ---------------------------------------------------------------------------

class AnalyticsResult(Base):
    __tablename__ = "analytics_results"

    id = Column(String, primary_key=True, default=_new_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=False)
    request_id = Column(String, ForeignKey("analytics_requests.id"), nullable=False)
    summary_text = Column(Text, nullable=True)
    metrics_payload = Column(JSON, nullable=True)
    visualization_payload = Column(JSON, nullable=True)
    download_manifest = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)

    tenant = relationship("Tenant")
    request = relationship("AnalyticsRequest", back_populates="result")

    __table_args__ = (
        Index("ix_aresult_request_id", "request_id", unique=True),
        Index("ix_aresult_tenant_id", "tenant_id"),
    )


# ---------------------------------------------------------------------------
# BackupRecord
# ---------------------------------------------------------------------------

class BackupRecord(Base):
    __tablename__ = "backup_records"

    id = Column(String, primary_key=True, default=_new_uuid)
    operator_id = Column(String, ForeignKey("operators.id"), nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)
    notes = Column(Text, nullable=True)

    operator = relationship("Operator", back_populates="backup_records")

    __table_args__ = (
        Index("ix_br_operator_id", "operator_id"),
        Index("ix_br_created_at", "created_at"),
    )


# ---------------------------------------------------------------------------
# AuditLog
# ---------------------------------------------------------------------------

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=_new_uuid)
    tenant_id = Column(String, ForeignKey("tenants.id"), nullable=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    operator_id = Column(String, ForeignKey("operators.id"), nullable=True)
    request_id = Column(String, ForeignKey("analytics_requests.id"), nullable=True)
    event_type = Column(String, nullable=False)
    entity_type = Column(String, nullable=True)
    entity_id = Column(String, nullable=True)
    payload = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=_utcnow)

    tenant = relationship("Tenant", back_populates="audit_logs")
    user = relationship("User", back_populates="audit_logs")
    operator = relationship("Operator", back_populates="audit_logs")
    request = relationship("AnalyticsRequest", back_populates="audit_logs")

    __table_args__ = (
        Index("ix_al_tenant_id", "tenant_id"),
        Index("ix_al_user_id", "user_id"),
        Index("ix_al_operator_id", "operator_id"),
        Index("ix_al_event_type", "event_type"),
        Index("ix_al_created_at", "created_at"),
        Index("ix_al_entity_type_entity_id", "entity_type", "entity_id"),
    )