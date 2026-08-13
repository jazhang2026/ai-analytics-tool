# Quickstart: UI and Auth Enhancements

## Purpose

Validate the operator seed script, branded header, user dropdown, navigation bar, and quick-action buttons.

## Prerequisites

- Existing 001-data-analytics-platform implementation running locally
- Backend venv activated
- Frontend dev server running

## Validation Scenarios

### Scenario 1: Seed operator account

1. Ensure the database has no operator accounts.
2. Run: `cd backend && python tests/seed_operator.py`
3. Open the browser and navigate to `/operator/login`.
4. Log in with operator@aiatool.com / Operator123.

**Expected outcome**: Operator login succeeds.

### Scenario 2: Run seed script again (idempotent)

1. Run `python tests/seed_operator.py` a second time.

**Expected outcome**: Script reports "Operator already exists" and exits without error.

### Scenario 3: Verify seed script not in deployment

1. Check that `seed_operator.py` is excluded from deployment artifacts (e.g., in `.gitignore` or deployment config).

**Expected outcome**: The seed script is not bundled with the deployed application.

### Scenario 4: Header with brand and user dropdown

1. Log in as a tenant user.
2. Verify "AI Analytics Tool" appears on the left of the header.
3. Verify the user's email appears on the right.
4. Click the email.
5. Verify dropdown shows "Change Password" and "Logout".
6. Click "Change Password" — verify navigation to password page.
7. Click "Logout" — verify logout and return to login.

**Expected outcome**: Header and dropdown work on every authenticated page.

### Scenario 5: Login page text

1. Log out.
2. Verify the login page shows email and password fields.
3. Verify the registration link reads "Register a new tenant account."

**Expected outcome**: Login page has updated text.

### Scenario 6: Navigation bar

1. Log in as tenant admin.
2. Verify nav shows: Dashboard, Data Sources, Data Analytics, Users.
3. Click each link and verify navigation.
4. Log in as a non-admin tenant user.
5. Verify nav shows: Dashboard, Data Sources, Data Analytics (no Users).

**Expected outcome**: Navigation is role-aware and functional.

### Scenario 7: Quick-action "New Request" buttons

1. Navigate to Dashboard.
2. Verify "New Request" button at top right of Recent Requests.
3. Click it — verify navigation to new request form.
4. Navigate to Data Analytics page.
5. Verify "New Request" button at top of the list.
6. Click it — verify navigation to new request form.

**Expected outcome**: Quick-action buttons are present and functional on both pages.

## Completion Criteria

- Operator seed script runs idempotently and is excluded from deployment
- Header shows brand + email dropdown on all authenticated pages
- Login page shows updated registration link text
- Navigation bar is role-aware
- "New Request" buttons work on Dashboard and Data Analytics pages