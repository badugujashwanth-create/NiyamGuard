# API Guide

OpenAPI is available at `/docs` when the backend is running.

## Public

- `GET /api/health`
- `GET /api/ready`
- `GET /api/integration/health`
- `GET /api/public/rules/latest?service_id=income_certificate&rule_key=validity`
- `POST /api/chat`
- Citizen form, service catalog, session, STT, TTS, validation, summary, and location helper endpoints.

## Auth

- `POST /api/auth/login`
- `POST /api/auth/logout`
- `POST /api/auth/refresh`
- `GET /api/auth/me`
- `POST /api/auth/users` admin only
- `GET /api/auth/users` admin only
- `PATCH /api/auth/users/{user_id}` admin only

## Government Core

- Knowledge: `/api/knowledge/*`
- Connected systems: `/api/connected-systems*`
- Compliance: `/api/compliance/*`
- Cascade: `/api/cascade/*`
- Priority: `/api/dashboard/*`
- Conflicts: `/api/conflicts/*`
- Reports: `/api/reports/*`
- Audit: `/api/audit/*`

Legacy `/api/...` routes remain available. `/api/v1/...` aliases are provided for versioned clients.
