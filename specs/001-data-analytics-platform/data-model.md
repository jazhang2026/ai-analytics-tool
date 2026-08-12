# Data Model: Data Analytics Platform

## Overview

The platform is multi-tenant. Every user belongs to exactly one tenant, and every analytics request is tenant-scoped. Tenant admins can create and manage tenant users, assign roles, and enforce the password policy. Analytics requests must only use data sources approved for the same tenant.

## Entities

### Tenant

Represents an isolated customer workspace.

**Fields**
- `id`: Unique identifier
- `name`: Tenant name, unique in the system
- `status`: `active`, `suspended`, `disabled`
- `created_at`: Tenant creation timestamp
- `created_by_user_id`: User who created the tenant

**Validation Rules**
- Tenant name MUST be unique.
- Only active tenants can authenticate users and run analytics.

**Relationships**
- One Tenant has many Users through TenantMembership.
- One Tenant has many DataSources.
- One Tenant has many AnalyticsRequests.
- One Tenant has many AuditLogs.

---

### User

Represents an account that can sign in to a tenant.

**Fields**
- `id`: Unique identifier
- `tenant_id`: Owning tenant
- `email`: Login identifier, unique within the tenant and normalized
- `password_hash`: Hashed password only; never store raw passwords
- `is_active`: Whether the account can sign in
- `created_at`: Account creation timestamp
- `last_login_at`: Most recent successful login
- `password_changed_at`: Most recent password change timestamp

**Validation Rules**
- Email MUST be unique within the tenant.
- Password MUST meet the policy defined by the application.
- Inactive users MUST not be allowed to authenticate.

**Relationships**
- One User belongs to one Tenant.
- One User may have many AnalyticsRequests.
- One User may appear in many AuditLogs.
- One User may own created DataSources.

---

### TenantMembership

Represents the role of a user within a tenant.

**Fields**
- `id`: Unique identifier
- `tenant_id`: Tenant identifier
- `user_id`: User identifier
- `role`: `admin` or `user`
- `created_at`: Membership creation timestamp

**Validation Rules**
- Each user MUST have exactly one membership record for their tenant.
- Only `admin` and `user` roles are allowed.
- The initial tenant creator MUST be assigned `admin`.

**Relationships**
- One TenantMembership belongs to one Tenant.
- One TenantMembership belongs to one User.

---

### DataSource

Represents a tenant-approved source of analytics input.

**Fields**
- `id`: Unique identifier
- `tenant_id`: Owning tenant
- `created_by_user_id`: User who created the source
- `source_type`: `sql`, `nosql`, `text`, `pdf`, `docx`, or `xlsx`
- `name`: User-visible label
- `connection_status`: `pending`, `validating`, `active`, `invalid`, `disabled`
- `connection_metadata`: Encrypted settings, connection info, or storage reference
- `created_at`: Creation timestamp
- `last_validated_at`: Last successful validation timestamp

**Validation Rules**
- Each source MUST belong to exactly one tenant.
- File-based sources MUST reference supported file types only.
- Database sources MUST be explicitly validated before use in analytics.
- Sensitive connection metadata MUST be protected at rest.

**Relationships**
- One DataSource belongs to one Tenant.
- One DataSource may be created by one User.
- One DataSource can be linked to many AnalyticsRequests through a join table.

---

### AnalyticsRequest

Represents a tenant-scoped analysis job.

**Fields**
- `id`: Unique identifier
- `tenant_id`: Owning tenant
- `user_id`: Request owner
- `title`: Short request label
- `objective`: User-provided analysis goal
- `status`: `draft`, `queued`, `running`, `succeeded`, `failed`, `canceled`
- `selected_method`: Chosen analytics method or recipe
- `method_rationale`: Human-readable explanation of why the method was selected
- `input_summary`: Normalized summary of source data and request scope
- `requested_at`: Submission timestamp
- `started_at`: Processing start timestamp
- `completed_at`: Completion timestamp
- `error_message`: Failure reason when applicable

**Validation Rules**
- A request MUST belong to exactly one tenant.
- A request MUST have at least one linked DataSource approved for the same tenant.
- A request MUST include a non-empty analysis objective.
- Requests SHOULD not move backward in the lifecycle.

**Relationships**
- One AnalyticsRequest belongs to one Tenant.
- One AnalyticsRequest belongs to one User.
- One AnalyticsRequest links to many DataSources.
- One AnalyticsRequest has zero or one AnalyticsResult.
- One AnalyticsRequest can have many AuditLogs.

**State Transitions**
- `draft` → `queued`
- `queued` → `running`
- `running` → `succeeded`
- `running` → `failed`
- `queued` or `running` → `canceled`

---

### AnalyticsResult

Represents the output of an analytics request.

**Fields**
- `id`: Unique identifier
- `tenant_id`: Owning tenant
- `request_id`: Owning analytics request
- `summary_text`: Plain-language summary of findings
- `metrics_payload`: Structured metrics and tables
- `visualization_payload`: Chart definitions or rendering instructions
- `download_manifest`: File export information for CSV, PDF, and Excel outputs
- `created_at`: Result creation timestamp

**Validation Rules**
- Each result MUST belong to exactly one AnalyticsRequest.
- Result content MUST correspond to the source request.
- Download artifacts MUST be reproducible from the stored result data.

**Relationships**
- One AnalyticsResult belongs to one Tenant.
- One AnalyticsResult belongs to one AnalyticsRequest.

---

### AuditLog

Represents immutable tenant-scoped activity tracking for debugging and accountability.

**Fields**
- `id`: Unique identifier
- `tenant_id`: Tenant identifier
- `user_id`: Actor if available
- `event_type`: e.g. `tenant_registered`, `user_created`, `login`, `password_changed`, `request_submitted`, `result_downloaded`
- `entity_type`: Affected entity name
- `entity_id`: Affected entity identifier
- `payload`: Small JSON snapshot of relevant metadata
- `created_at`: Event timestamp

**Validation Rules**
- Audit entries SHOULD be append-only.
- Audit logs SHOULD avoid storing secrets or raw credentials.

**Relationships**
- Many AuditLogs belong to one Tenant.
- Many AuditLogs may belong to one User.
- Many AuditLogs may reference one entity.

---

### RequestSourceLink

Join entity connecting analytics requests to approved data sources.

**Fields**
- `request_id`: AnalyticsRequest identifier
- `data_source_id`: DataSource identifier
- `role`: Optional role of the source in the request, such as `primary`, `reference`, or `supplemental`

**Validation Rules**
- Each link MUST reference an existing request and data source.
- A request MUST have at least one source link.
- The request and source MUST belong to the same tenant.

## Cross-Entity Rules

- Authentication data MUST never be exposed in result payloads or logs.
- Downloadable results MUST be generated from stored request/result records.
- A request using file sources and database sources together MUST preserve source provenance in the result metadata.
- Source configurations and uploaded files MUST remain accessible only to the owning tenant unless explicitly shared in a later version.
- Password changes MUST update `password_changed_at` and invalidate any trusted login state as needed.
