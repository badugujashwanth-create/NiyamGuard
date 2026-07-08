# Final Gap Analysis

| Feature | Exists in Jashwanth? | Exists in ybaddam? | Exists in chatbot repo? | Should add to Jashwanth? | Priority | Risk | Implementation plan | Tests needed |
|---|---|---|---|---|---|---|---|---|
| SQLite/Postgres persistence | Demo JSON only | Yes | Basic DB | Yes | P1 | Medium | SQLAlchemy primary store with JSON fallback | DB seed, compliance, public rule |
| Alembic migrations | No | Yes | No | Yes | P1 | Low | Add initial migration scaffold | migration files present |
| Auth/RBAC | No | Yes | No | Yes | P1 | Medium | Seed users, JWT access, refresh tokens, role deps | auth/RBAC tests |
| Audit hash chain | No | Yes | No | Yes | P1 | Medium | Add hash fields and verify endpoint | audit verify |
| Request IDs/security headers | Partial | Yes | No | Yes | P1 | Low | Middleware and error handlers | security tests |
| Reports metadata/filters | Basic | Partial | No | Yes | P1 | Low | Upgrade report service | reports tests |
| `/api/chat` | No | No | Yes | Yes | P2 | Medium | Deterministic local knowledge service | chat tests |
| Scheme documents/eligibility/process | Limited catalog | No | Yes | Yes | P2 | Medium | Seeded knowledge with source metadata | chat tests |
| Admin login UI | No | API only | No | Yes | P3 | Medium | Login page, auth context, protected admin shell | frontend tests |
| Admin audit/users pages | No | Audit/user APIs | No | Yes | P3 | Medium | Add pages backed by protected APIs | frontend tests |
| Docker compose | No full stack | Yes | No | Yes | P4 | Low | backend/frontend/postgres compose | config validation |
| CI workflow | No | No | No | Yes | P4 | Low | GitHub Actions backend/frontend | workflow present |
| Circular upload/review | No | Yes | Circular search | Defer if risky | P3 | Medium | Future admin workflow after core stable | future tests |

Priority legend: P1 production backend/security, P2 citizen knowledge, P3 frontend/admin polish, P4 DevOps/docs.
