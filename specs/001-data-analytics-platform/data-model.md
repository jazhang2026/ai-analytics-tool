# Data Model: Data Analytics Platform

## Overview

The platform is multi-tenant. Every user belongs to exactly one tenant, and every analytics request is tenant-scoped. Tenant admins can create and manage tenant users, assign roles, and enforce the password policy. Analytics requests must only use file sources approved for the same tenant. An operator role exists at the system level for cross-tenant administration and database backup/restore. Application data is stored in an embedded database.

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

**Indexes**
- **Unique index** on `name` — enforces tenant name uniqueness across the system
- **Index** on `status` — speeds up filtering active/suspended/disabled tenants

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

**Indexes**
- **Unique index** on `(tenant_id, email)` — enforces email uniqueness within a tenant
- **Index** on `tenant_id` — speeds up tenant-scoped user queries
- **Index** on `is_active` — speeds up filtering active/inactive users

---

### Operator

Represents a system-level operator account with cross-tenant access and backup/restore permissions.

**Fields**
- `id`: Unique identifier
- `email`: Login identifier
- `password_hash`: Hashed password only; never store raw passwords
- `is_active`: Whether the account can sign in
- `created_at`: Account creation timestamp
- `last_login_at`: Most recent successful login

**Validation Rules**
- Operator accounts are system-level and not associated with any tenant.
- Operator MUST follow the same password policy as tenant users.

**Relationships**
- One Operator can appear in many AuditLogs.

**Indexes**
- **Unique index** on `email` — enforces operator email uniqueness across the system
- **Index** on `is_active` — speeds up filtering active/inactive operators

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

**Indexes**
- **Unique index** on `(tenant_id, user_id)` — enforces one membership per user per tenant
- **Index** on `tenant_id` — speeds up listing members of a tenant
- **Index** on `role` — speeds up role-based filtering

---

### DataSource

Represents a tenant-uploaded file source for analytics input.

**Fields**
- `id`: Unique identifier
- `tenant_id`: Owning tenant
- `created_by_user_id`: User who uploaded the source
- `source_type`: `text`, `pdf`, `docx`, or `xlsx`
- `name`: User-visible label
- `status`: `pending`, `validating`, `active`, `invalid`, `disabled`
- `file_path`: Storage location of the uploaded file
- `file_size`: Size in bytes
- `created_at`: Creation timestamp
- `last_validated_at`: Last successful validation timestamp

**Validation Rules**
- Each source MUST belong to exactly one tenant.
- Sources MUST reference supported file types only.
- Files MUST be validated before use in analytics.

**Relationships**
- One DataSource belongs to one Tenant.
- One DataSource may be created by one User.
- One DataSource can be linked to many AnalyticsRequests through a join table.

**Indexes**
- **Index** on `tenant_id` — speeds up tenant-scoped source listing
- **Index** on `status` — speeds up filtering sources by connection status
- **Index** on `source_type` — speeds up filtering by file type

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

**Indexes**
- **Index** on `tenant_id` — speeds up tenant-scoped request listing
- **Index** on `user_id` — speeds up per-user request lookups
- **Index** on `status` — speeds up filtering by request lifecycle state
- **Index** on `requested_at` — speeds up time-ordered request listing

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

**Indexes**
- **Unique index** on `request_id` — enforces one result per request
- **Index** on `tenant_id` — speeds up tenant-scoped result queries

---

### BackupRecord

Represents a database backup file created by an operator.

**Fields**
- `id`: Unique identifier
- `operator_id`: Operator who created the backup
- `file_path`: Storage location of the backup file
- `file_size`: Size in bytes
- `created_at`: Backup creation timestamp
- `notes`: Optional operator notes about the backup

**Validation Rules**
- Backup files MUST be stored in a designated backup directory.
- Only operators can create or restore backups.

**Relationships**
- One BackupRecord belongs to one Operator.

**Indexes**
- **Index** on `operator_id` — speeds up operator-scoped backup listing
- **Index** on `created_at` — speeds up time-ordered backup history

---

### AuditLog

Represents immutable activity tracking for debugging and accountability.

**Fields**
- `id`: Unique identifier
- `tenant_id`: Tenant identifier (null for operator actions)
- `user_id`: Actor if available
- `operator_id`: Operator actor if available
- `event_type`: e.g. `tenant_registered`, `user_created`, `login`, `password_changed`, `file_uploaded`, `request_submitted`, `result_downloaded`, `operator_login`, `backup_created`, `restore_completed`
- `entity_type`: Affected entity name
- `entity_id`: Affected entity identifier
- `payload`: Small JSON snapshot of relevant metadata
- `created_at`: Event timestamp

**Validation Rules**
- Audit entries SHOULD be append-only.
- Audit logs SHOULD avoid storing secrets or raw credentials.

**Relationships**
- Many AuditLogs belong to one Tenant (nullable for operator actions).
- Many AuditLogs may belong to one User or Operator.
- Many AuditLogs may reference one entity.

**Indexes**
- **Index** on `tenant_id` — speeds up tenant-scoped audit log queries
- **Index** on `user_id` — speeds up per-user audit lookups
- **Index** on `operator_id` — speeds up operator action log lookups
- **Index** on `event_type` — speeds up filtering by event category
- **Index** on `created_at` — speeds up time-ordered log retrieval
- **Composite index** on `(entity_type, entity_id)` — speeds up entity-specific audit lookups

---

## Cross-Entity Rules

- Authentication data MUST never be exposed in result payloads or logs.
- Downloadable results MUST be generated from stored request/result records.
- A request using multiple file sources MUST preserve source provenance in the result metadata.
- File sources and configurations MUST remain accessible only to the owning tenant unless explicitly viewed by an operator.
- Password changes MUST update `password_changed_at` and invalidate any trusted login state as needed.
- Backup files MUST be stored outside the application database to allow independent restore.
- Application data storage MUST use the embedded database without requiring external database servers.
