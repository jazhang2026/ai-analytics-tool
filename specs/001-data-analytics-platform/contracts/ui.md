# UI Contract: Data Analytics Platform

## Overview

The browser UI is a single-page experience built with Vite and vanilla HTML, CSS, and JavaScript. It should feel simple, fast, and consistent across tenant registration, tenant user management, authentication, data source management, request submission, and results review.

## Primary Routes

### `/register`
- Tenant registration form
- Fields: tenant name, admin email, admin password, confirm password
- Primary action: create tenant
- Secondary action: go to login

### `/login`
- Existing tenant user sign-in form
- Fields: email, password
- Primary action: sign in
- Secondary action: go to registration

### `/dashboard`
- Landing view after authentication
- Shows recent analytics requests, data source summary, and quick actions
- Includes navigation to data sources, tenant users, password change, and request creation

### `/tenant/users`
- Lists users in the current tenant
- Supports create user and role update actions for tenant admins
- Shows role badges for each user

### `/account/password`
- Password change form
- Fields: current password, new password, confirm new password
- Shows password policy guidance

### `/data-sources`
- Lists configured SQL/NoSQL sources and uploaded files
- Supports add, validate, disable, and delete actions
- Shows status badges for each source

### `/requests/new`
- Request submission form
- Fields: title, objective, source selection
- Submission triggers analytics processing
- Shows validation feedback before submission

### `/requests/{id}`
- Request detail view
- Shows current status, selected method, rationale, and progress timeline
- Includes links to result and download actions when ready

### `/results/{id}`
- Result review page
- Shows summary text, key metrics, tables, charts, and download buttons
- Allows export to CSV, PDF, or Excel

## UI States

### Loading States
- Show clear loading indicators during tenant creation, login, password changes, data source validation, request submission, and result retrieval.

### Empty States
- Explain what the user should do next when no tenant users, data sources, or requests exist.

### Error States
- Show actionable, human-readable messages.
- Preserve user input when possible after validation errors.

### Success States
- Confirm completed actions clearly and consistently.

## Interaction Rules

- Navigation MUST remain usable on mobile and desktop widths.
- Form validation MUST happen before API submission when possible.
- Result download buttons MUST be visible only when a result is available.
- Status badges SHOULD use consistent labels across the app: `pending`, `validating`, `queued`, `running`, `succeeded`, `failed`, `canceled`.
- Tenant management actions SHOULD only be visible to tenant admins.
- The UI SHOULD not require page reloads for normal status refreshes.

## Accessibility Requirements

- All interactive controls MUST have visible labels.
- Keyboard navigation MUST work for forms, dialogs, and result downloads.
- Color should not be the only indicator of state.
- Error text MUST be readable and associated with the affected form field.