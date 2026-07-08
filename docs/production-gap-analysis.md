# Production Gap Analysis

| Area | Current status | Missing production feature | Priority | Risk | Implementation plan | Test needed |
|---|---|---|---|---|---|---|
| Database | JSON MVP store existed | SQLAlchemy primary store, SQLite/Postgres | High | Medium | Add DB record layer, keep JSON fallback, seed demo into DB | seed, public rule, compliance DB tests |
| Auth | Admin APIs public | Login, JWT, refresh, users | High | Medium | Add auth service, user table, seeded users | login/wrong login/me tests |
| RBAC | No role checks | admin/reviewer/viewer/citizen permissions | High | Medium | Add dependencies and protect government routes | RBAC tests |
| Admin Login | `/admin` public | `/login`, protected admin, logout, role badge | High | Medium | Add frontend auth context and API token injection | frontend login/admin tests |
| Audit | Simple JSON event list | DB audit events and hash chain | High | Medium | Add audit table, actions, `/api/audit/verify` | audit logging/verify tests |
| Security | Wildcard CORS and default errors | CORS env, request IDs, clean errors, headers, rate limit | High | Low | Middleware and error handlers | security error tests |
| Observability | Basic app health only | `/api/health`, `/api/ready`, structured logs | High | Low | Add health routes and logging middleware | health/ready tests |
| API Versioning | `/api/...` only | `/api/v1/...` aliases | Medium | Low | Alias middleware preserving old routes | versioned API tests |
| Reports | Basic export | Filters, metadata, auth, audit | High | Low | Upgrade report service/routes | report filter/export tests |
| Citizen Knowledge | Voice/form guidance plus verified rule | Scheme/document/eligibility Q&A | Medium | Medium | Add deterministic `/api/chat` and route voice questions | chat tests/frontend source test |
| Circular Upload | Not present | Upload/review/extraction workflow | Medium | Medium | Defer unless core production work remains stable | future tests |
| Docker/Postgres | Backend Dockerfile only | full compose with frontend/backend/postgres | High | Low | Add Dockerfile.backend, Dockerfile.frontend, compose | compose config check |
| CI | None | GitHub Actions tests/build | High | Low | Add workflow using SQLite | CI yaml present |
| Docs | Demo docs | architecture, API, security, deployment, testing | High | Low | Update README and docs folder | doc review |
