# NiyamGuard Production Readiness

## Current verified state

- Backend: FastAPI application with citizen assistant routes, form catalog, public verified-rule API, admin dashboard APIs, compliance drift detection, cascade tracing, priority scoring, conflict detection, and report export.
- Storage: SQLAlchemy is authoritative for the typed policy-review core and auth/audit records; the JSON mirror remains local/demo compatibility only and is disabled in hardened environments.
- Frontend: Vite/React app with public citizen portal, `/demo` presentation dashboard, and `/admin` government dashboard.
- Demo seed: GO-138 changes Income Certificate validity to 6 months while connected systems still show the earlier 12-month rule.
- Current clean local gate: 298 backend tests, 61 frontend tests, the deterministic 20-case extraction benchmark, the Vite production build, `npm audit --omit=dev`, `pip-audit`, compile checks, and the no-video core Playwright accessibility regression pass. Docker image execution and hosted PostgreSQL/Render execution remain unverified external gates.

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
- [x] Frontend auth/API refactor complete for the current synthetic scope.
- [x] Docker setup and migration entrypoints are defined.
- [x] CI workflow includes backend, fresh PostgreSQL migration, frontend, dependency, and secret checks.
- [x] Final local backend tests passing.
- [x] Final local frontend tests/build passing.
- [x] Conditional OCR, original/derivative provenance, object-storage abstraction, fail-closed ClamAV boundary, and dependency-aware readiness implemented.
- [ ] Final commit pushed.

## Known Production Limitations

- The app can auto-create tables for local/demo use. Hardened deployments disable that compatibility path and run Alembic explicitly before startup.
- Live MeeSeva integration, official government APIs, production secrets manager, cloud deployment, and a full independent security audit remain future production steps.

## Readiness boundary

**CODE READY:** OCR, original/derivative provenance, local/S3-compatible object storage, ClamAV fail-closed scanning, dependency-aware `/api/ready`, hardened PostgreSQL configuration, migrations, and the synthetic flagship lifecycle are implemented and locally testable.

**EXTERNALLY VERIFIED PRODUCTION READY:** not claimed. Hosted PostgreSQL, object-storage durability, ClamAV signatures/quarantine, OCR runtime operation, TLS/cookie playback, penetration testing, formal accessibility certification, legal approval, government UAT, and official integrations remain external gates.
