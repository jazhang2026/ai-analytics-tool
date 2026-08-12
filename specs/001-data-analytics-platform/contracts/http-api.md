# HTTP API Contract: Data Analytics Platform

## Overview

This contract defines the browser-facing HTTP interface used by the frontend and any future integrations. All endpoints require authenticated access unless otherwise noted. Every authenticated request is tenant-scoped.

## Common Conventions

- Base path: `/api`
- Content type for JSON requests and responses: `application/json`
- File uploads: `multipart/form-data`
- Timestamps: ISO 8601 UTC strings
- Resource identifiers MUST be supplied in request bodies rather than path parameters
- Authentication errors should return `401`
- Authorization failures should return `403`
- Validation errors should return `400`

## Tenant Registration and Auth

### `POST /api/tenants`
Creates a new tenant and its initial tenant admin account.

**Request**
```json
{
  "tenant_name": "Acme Analytics",
  "admin_email": "admin@example.com",
  "admin_password": "string"
}
```

**Response**
```json
{
  "tenant": {
    "id": "uuid",
    "name": "Acme Analytics"
  },
  "user": {
    "id": "uuid",
    "email": "admin@example.com",
    "role": "admin"
  },
  "message": "tenant_created"
}
```

### `POST /api/auth/login`
Authenticates a tenant user.

**Request**
```json
{
  "email": "user@example.com",
  "password": "string"
}
```

**Response**
```json
{
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "role": "user"
  },
  "tenant": {
    "id": "uuid",
    "name": "Acme Analytics"
  },
  "message": "logged_in"
}
```

### `POST /api/auth/logout`
Ends the current session.

**Response**
```json
{ "message": "logged_out" }
```

### `GET /api/me`
Returns the current authenticated tenant user.

**Response**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "role": "admin",
  "tenant_id": "uuid",
  "is_active": true
}
```

### `PATCH /api/me/password`
Changes the current user's password.

**Request**
```json
{
  "current_password": "string",
  "new_password": "string"
}
```

**Response**
```json
{ "message": "password_updated" }
```

## Tenant User Management

### `GET /api/tenant/users`
Lists users for the current tenant.

### `POST /api/tenant/users`
Creates a tenant user.

**Request**
```json
{
  "email": "user@example.com",
  "password": "string",
  "role": "user"
}
```

**Response**
```json
{
  "id": "uuid",
  "email": "user@example.com",
  "role": "user"
}
```

### `POST /api/tenant/users/role`
Updates a tenant user's role.

**Request**
```json
{
  "user_id": "uuid",
  "role": "admin"
}
```

**Response**
```json
{ "message": "role_updated" }
```

## Data Sources

### `GET /api/data-sources`
Lists the authenticated tenant's data sources.

### `POST /api/data-sources`
Creates a data source or file upload record.

**Request examples**
- SQL/NoSQL source: connection details and source metadata
- File source: upload file and label

### `POST /api/data-sources/validate`
Validates a database connection or uploaded file source.

**Request**
```json
{
  "data_source_id": "uuid"
}
```

**Response**
```json
{
  "id": "uuid",
  "status": "active",
  "last_validated_at": "2026-08-11T12:00:00Z"
}
```

### `POST /api/data-sources/delete`
Disables or removes a source owned by the authenticated tenant.

**Request**
```json
{
  "data_source_id": "uuid"
}
```

**Response**
```json
{ "message": "data_source_deleted" }
```

## Analytics Requests

### `POST /api/analytics-requests`
Creates a new analytics request.

**Request**
```json
{
  "title": "Monthly Sales Analysis",
  "objective": "Find trends and anomalies in last month's sales data",
  "data_source_ids": ["uuid-1", "uuid-2"]
}
```

**Response**
```json
{
  "id": "uuid",
  "status": "queued",
  "selected_method": "descriptive_and_outlier_analysis"
}
```

### `GET /api/analytics-requests`
Lists analytics requests for the current tenant user.

### `POST /api/analytics-requests/detail`
Returns request status, chosen method, and progress metadata.

**Request**
```json
{
  "request_id": "uuid"
}
```

### `POST /api/analytics-requests/result`
Returns the completed result payload when the request has finished successfully.

**Request**
```json
{
  "request_id": "uuid"
}
```

**Response**
```json
{
  "request_id": "uuid",
  "summary_text": "...",
  "metrics_payload": {},
  "visualization_payload": {}
}
```

### `POST /api/analytics-requests/download`
Downloads the result in the requested format.

**Request**
```json
{
  "request_id": "uuid",
  "format": "csv"
}
```

## Health

### `GET /api/health`
Returns a simple service health response for deployment checks.

**Response**
```json
{ "status": "ok" }
```

## Error Shape

Validation and processing errors should follow a consistent structure:

```json
{
  "error": {
    "code": "validation_error",
    "message": "Human-readable explanation",
    "details": []
  }
}
```