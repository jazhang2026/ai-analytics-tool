# ai-analytics-tool
 A data analytic project design and developed using spec-driven development

## /speckit.specify 
Build a multi-tenant application that can run data analytic tasks. 
1. Register tenant with tenant admin.
2. Tenant admin create tenant user and assign user role: admin, user.
3. Admin and user login, change password. Minimum password request: 8-12 chars include upcase, lowercase, number, 
4. User send request from a browser UI
5. Application run data analytic. Data sources: text file, pdf, word, excel, any other file type that can be processed.
6. Find good data analytic method.
7. Show result on UI and also can be downloaded.
8. Not using external database for application data storage. instead use embedded database or file system.
9. Add operator role to manage tenant and data backup and restore.
10. Operator can view all tenant data and manage them.
11. Operator backup and restore data application database.
12. On the data model, define the needed index and unique index to help the performance.

## /speckit.plan 
The application uses Vite with minimal number of libraries. Use vanilla HTML, CSS, and JavaScript as much as possible for UI. Backend is python. The selectedUI and backend libraries should be suppored with popular WEB hosting plan (support js and python).

## /speckit.tasks 

## /speckit.implement


# To Run Locally

## Backend
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

## Frontend (separate terminal)
cd frontend
npm install

npm run dev


# More feature changes

## /speckit.specify 
Feature changes and bug fixes for `001-data-analytics-platform`:
1. Seeddata for operator account: username = operator@aiatool.com, password = Operator123.
2. UI changes: the header show "AI Analytics Tool" on the left side. Login or logged in user email on the right side. Click on the email will show a dropdown menu with "Change Password" and "Logout" options.
3. UI changes: when not logged in, show login page with email and password fields. After login, show the navigation bar. Change "Don't have an account? Register" to "Register a new tenant account."
4. UI changes: After login, under the header, show a navigation bar with "Dashboard", "Data Sources", "Data Analytics", "Users".
5. UI changes: Add "New Request" button on Data Analytics page. On top of the data analytics list. Add "New Request" button on Dashboard page. On top right of the Recent Requests list.

## /speckit.plan 
The application uses Vite with minimal number of libraries. Use vanilla HTML, CSS, and JavaScript as much as possible for UI. Backend is python. The selectedUI and backend libraries should be suppored with popular WEB hosting plan (support js and python).

## /speckit.tasks 

## /speckit.implement

Seed operator account:
cd backend && python tests/seed_operator.py