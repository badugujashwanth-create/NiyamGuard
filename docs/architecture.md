# Architecture

NiyamGuard AI uses a layered FastAPI backend and a React/Vite frontend.

## Backend

- `routes`: HTTP API surface, auth dependencies, request/response wiring.
- `services`: policy, compliance, cascade, conflict, report, auth, audit, and chat behavior.
- `repositories`: database or storage access behind a stable interface.
- `models`: SQLAlchemy records and existing domain models.
- `schemas`: Pydantic validation models.
- `security`: password hashing, JWT, RBAC, and rate limiting.
- `middleware`: request ID, security headers, structured logging, version aliases, and error handling.

SQLite is the local default. PostgreSQL is supported with `DATABASE_URL=postgresql+psycopg://...`.

## Frontend

- `src/api`: central API client, auth token injection, public/admin/report/chat modules.
- `src/components`: citizen portal, demo dashboard, admin portal, dynamic forms, voice assistant.
- `/demo` remains public.
- `/login` handles admin authentication.
- `/admin/*` requires a stored access token.
- `/` remains the public citizen portal.

## Data Flow

Citizen questions use the form assistant for field help, the public verified-rule API for current circular rules, and `/api/chat` for scheme/document/process knowledge. Admin actions call protected APIs and produce audit events.
