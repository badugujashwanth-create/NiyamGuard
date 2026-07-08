# Current Jashwanth Repo Audit

## Backend Folder Structure

- `backend/app/main.py`: FastAPI application bootstrap.
- `backend/app/routes/`: route modules for forms, sessions, assistant, TTS/STT, location, knowledge, connected systems, compliance, cascade, dashboard, conflicts, reports, public APIs, admin, auth, audit, health, demo, and chat.
- `backend/app/services/`: assistant, form, language, TTS/STT, knowledge, compliance, cascade, priority, conflict, reports, auth, audit, chat, and platform store services.
- `backend/app/models/`: Pydantic domain models plus production SQLAlchemy records for auth, audit, and DB-backed policy records.
- `backend/app/repositories/`: DB/storage isolation for auth, audit, policy store, knowledge, connected systems, compliance, cascade, priority, conflicts, reports.
- `backend/app/security/`: password hashing, JWT, RBAC, and rate limiting.
- `backend/app/middleware/`: request IDs, security headers, structured request logging, clean errors, and API v1 aliasing.
- `backend/alembic/`: initial migration scaffold.
- `backend/app/tests/`: backend regression and production-hardening tests.

## Frontend Folder Structure

- `frontend/src/App.jsx`: top-level path switch for citizen portal, demo, and admin.
- `frontend/src/components/`: citizen form components, voice assistant, admin portal, and demo dashboard.
- `frontend/src/hooks/`: speech recognition and synthesis hooks.
- `frontend/src/services/api.js`: existing API wrapper, to be replaced/bridged by the production API client layer.
- `frontend/src/test/`: frontend tests and API fixtures.

## Current Storage Method

- Baseline storage was JSON-backed under `backend/app/storage`.
- Production work adds SQLAlchemy as the primary store with SQLite local fallback and PostgreSQL support through `DATABASE_URL`.
- JSON demo data remains as a safe fallback and seed source.

## Current Routes

- Public/citizen: `/api/forms`, `/api/services`, `/api/sessions`, `/api/assistant/*`, `/api/tts/*`, `/api/stt/*`, `/api/location/*`, `/api/public/*`, `/api/chat`.
- Health/public demo: `/api/health`, `/api/ready`, `/api/integration/health`, `/api/demo/*`.
- Government/admin: `/api/admin/*`, `/api/connected-systems`, `/api/compliance/*`, `/api/cascade/*`, `/api/dashboard/*`, `/api/conflicts/*`, `/api/reports/*`, `/api/audit/*`, `/api/auth/*`.
- Version alias: `/api/v1/...` maps to existing `/api/...` routes.

## Current Services

- Citizen assistant and form guidance are preserved.
- Government core services cover verified rules, connected systems, compliance drift, cascade tracing, priority scoring, conflict detection, reports, audit, auth, and citizen knowledge chat.

## Current Tests

- Baseline: 140 backend tests, 34 frontend tests.
- Production backend after hardening: 169 backend tests passing.
- Frontend tests still need auth/login/API updates after frontend changes.

## `/demo` Behavior

- Public page for presentation flow.
- Uses public health/rule/dashboard data and demo-safe run/export endpoints.
- Must remain accessible without login.

## `/admin` Behavior

- Baseline admin was public.
- Production behavior requires login and role-based API access.
- Admin pages remain `/admin`, `/admin/compliance`, `/admin/conflicts`, `/admin/reports`; `/admin/audit` and `/admin/users` are being added.

## Voice Assistant Flow

- Citizen starts from the service catalog, selects a dynamic form, and receives form guidance.
- Rule/current circular questions use the verified public rule API.
- Scheme/document/eligibility questions are routed to `/api/chat`.
- Assistant does not auto-submit government applications.

## Public APIs

- `/api/public/rules/latest`
- `/api/public/services/{service_id}/documents`
- `/api/public/services/{service_id}/eligibility`
- `/api/public/search`
- `/api/integration/health`
- `/api/health`
- `/api/ready`
- `/api/chat`

## Current Limitations and Production Gaps

- Frontend still needs the central API client and login-protected admin shell.
- Docker/CI/deployment documentation must be completed.
- Circular upload/review workflow is not implemented yet; it is lower priority than auth, DB, audit, and citizen knowledge.
- Live government integrations remain future work.
