# ybaddam Reference Analysis

Repository: `https://github.com/ybaddam8-png/Niyam-guard.git`

## Useful Backend Patterns

- PostgreSQL-backed FastAPI service with SQLAlchemy models and Alembic migrations.
- Fixed admin/reviewer/viewer role model.
- JWT auth and role dependencies.
- Restricted CORS through environment configuration.
- Request ID middleware and structured logging.
- Rate limiting with `slowapi`.
- Tamper-evident audit hash chain.
- Docker Compose with Postgres health checks.
- LLM extraction retry/backoff and circular extraction APIs.

## Useful Ideas Reimplemented Here

- SQLite/PostgreSQL config via `DATABASE_URL`.
- SQLAlchemy-backed primary persistence with Alembic scaffold.
- JWT-style access token auth with refresh tokens.
- Admin/reviewer/viewer/citizen RBAC.
- Request IDs, security headers, clean error response, structured request logging.
- Audit event table with `previous_hash` and `current_hash`.
- `/api/audit/verify`.
- Docker/Postgres structure to add in this repo.

## What Should Not Be Copied

- The older `/check` flow is less aligned with Jashwanth's richer compliance/cascade/priority modules.
- ybaddam's domain models do not map 1:1 to the existing verified-rule/connected-system MVP and should not replace them.
- Its frontend is not the Jashwanth product UI.
- Any route shape that would break `/demo`, `/admin`, `/api/public/*`, or existing citizen assistant behavior.
