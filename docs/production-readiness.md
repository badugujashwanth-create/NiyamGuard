# NiyamGuard Production Readiness

## Current MVP State

- Backend: FastAPI application with citizen assistant routes, form catalog, public verified-rule API, admin dashboard APIs, compliance drift detection, cascade tracing, priority scoring, conflict detection, and report export.
- Storage before hardening: JSON files under `backend/app/storage`, with `platform_demo.json` acting as the government-core demo store.
- Frontend: Vite/React app with public citizen portal, `/demo` presentation dashboard, and `/admin` government dashboard.
- Demo seed: GO-138 changes Income Certificate validity to 6 months while connected systems still show the earlier 12-month rule.
- Baseline on `codex/production-hardening`: backend `pytest` had 139 passed and 1 existing Windows session-storage failure; frontend `npm test` had 34 passed; frontend `npm run build` passed.

## Compatibility Rules

- Preserve public citizen routes and same-language assistant behavior.
- Preserve `/demo`, `/admin`, the citizen portal, source cards, seeded GO-138 flow, and existing public APIs.
- Keep public citizen APIs open, especially `/api/public/*`, `/api/forms`, `/api/services`, voice/form assistant routes, `/api/health`, `/api/ready`, and `/api/integration/health`.
- Protect government/admin mutations and admin data with auth/RBAC.
- Keep SQLite as the local default and support PostgreSQL through `DATABASE_URL`.
- Keep old `/api/...` routes working while supporting `/api/v1/...` aliases.
- Do not include unrelated untracked folders such as `apps/demo-dashboard`.

## Changes Being Made

- Add environment-based configuration and `.env.example` files.
- Add SQLAlchemy-backed persistence with SQLite dev fallback and PostgreSQL-compatible configuration.
- Add Alembic migration scaffolding while keeping automatic table creation for local demo startup.
- Add default demo users, password hashing, access tokens, refresh tokens, and RBAC.
- Protect government APIs and keep demo-safe public endpoints for `/demo`.
- Add request IDs, security headers, structured request logs, and clean error responses.
- Add audit logging and protected audit APIs.
- Add health/readiness endpoints.
- Upgrade reports with filters, metadata, CSV/JSON/HTML exports, and export auditing.
- Improve frontend API structure, login flow, admin protection, and UX states.
- Add Docker, CI, and production documentation.

## Production Hardening Checklist

- [x] Branch created from the requested MVP baseline.
- [x] Baseline tests/build recorded.
- [x] Configuration system added.
- [x] Database-backed primary store added.
- [x] Auth and RBAC added.
- [x] Security middleware and request IDs added.
- [x] Audit logging added.
- [x] Health/readiness endpoints added.
- [x] Report filters and metadata exports added.
- [ ] Frontend auth/API refactor complete.
- [ ] Docker setup complete.
- [ ] CI workflow complete.
- [ ] Final backend tests passing.
- [ ] Final frontend tests/build passing.
- [ ] Final commit pushed.

## Known Production Limitations

- The app can auto-create tables for local/demo use. Alembic migration files are included for production migration discipline, but deployment should run migrations explicitly.
- Live MeeSeva integration, official government APIs, production secrets manager, cloud deployment, and a full independent security audit remain future production steps.
