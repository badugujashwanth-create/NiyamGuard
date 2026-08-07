# NiyamGuard ground truth

**Audit date:** 2026-07-31
**Repository:** `https://github.com/badugujashwanth-create/NiyamGuard`
**Audited branch:** `main`
**HEAD / origin/main:** `a40fffcb20035fc7caf7e4b473abc11ac5f79fe1`
**Public release:** `v1.1.0`
**Audit scope:** Baseline audit captured before the 2026-08-07 productionization pass. The delta below is the current implementation evidence; older findings remain useful historical context but are not current-state claims.

## Current implementation delta (2026-08-07)

- The policy-drift routers are mounted on the canonical `main` runtime and the GO-138 lifecycle is exercised end to end by the backend/frontend test suites.
- The confirmed service-portal 422 defect is fixed; the focused regression now passes.
- Deterministic extraction now rejects ambiguous or unsupported circular wording instead of inventing a fallback source excerpt.
- Demo mode defaults to false and demo users are seeded only when both `DEMO_MODE=true` and `SEED_DEMO_ON_STARTUP=true` are explicitly set.
- `/api/ops/status` and dataset mutation endpoints now require authenticated roles; OTP endpoints are demo-gated; ops output no longer exposes host paths.
- STT/TTS requests are bounded and rate-limited; STT temporary files are removed; TTS cache eviction is bounded.
- Refresh tokens rotate atomically, JWT issuer/audience claims are validated, and in-process audit appends are serialized.
- Container entrypoints run Alembic migrations and drop root privileges.
- Deployed containers disable the legacy `create_all()` compatibility path; schema changes are owned by Alembic migrations.
- Production startup rejects credentialed wildcard CORS and wildcard/empty trusted-host settings.
- The landing now presents the policy-drift incident and impact chain before portal selection; desktop/mobile captures are in `docs/design-audit/` (screenshots are ignored internal evidence).
- Current verification: 259 backend tests pass with third-party pytest plugin autoload disabled; 60 frontend tests pass; Vite build, npm audit, pip-audit, compile, and diff checks pass. Docker daemon and hosted Render deployment remain unverified.

## Executive result

NiyamGuard is a substantial FastAPI/React synthetic policy-intelligence sandbox. The seeded GO-138 scenario is connected through circular ingestion, deterministic extraction, version comparison, conflict detection, impact/cascade analysis, reviewer decisions, policy publication, propagation tasks, compliance reruns, citizen guidance, eligibility helpers, and an audit hash chain.

The repository is not yet authorized for an unrestricted public or government deployment. The former P0 validation defect and the previously identified demo-seeding, endpoint-boundary, token-rotation, and container-migration gaps were addressed in the 2026-08-07 pass. Docker daemon access and the hosted Render service remain unverified, and relational pilot-grade storage, malware scanning, and legal/operational gates remain open.

## Existing feature inventory

| Feature | Implementation evidence | API / UI evidence | Tests | Status |
|---|---|---|---|---|
| Circular ingestion | `backend/app/api/circular_routes.py`, `backend/app/knowledge_base/circular_ingestion_service.py` | `/api/circulars/upload`, `/api/circulars/upload-file`, circular library UI | `test_policy_lifecycle.py`, validator tests | **Complete for synthetic PDF/TXT only** |
| File validation | Extension/MIME checks, size limit, PDF signature check in `circular_routes.py` | Upload form | Upload-related tests | **Partial** — no quarantine/malware hook, no source-file persistence pipeline |
| Date extraction | `circular_ingestion_service.extract_temporal_metadata` | Circular metadata and evidence views | lifecycle/date tests | **Complete for ISO dates** |
| Rule extraction | `backend/app/extraction/rule_extraction_service.py` | `/api/circulars/{id}/extract-rules`, candidate review UI | extraction/lifecycle tests | **Partial** — deterministic patterns are narrow; generic structured extraction is not implemented |
| Source evidence | `source_excerpt`, circular hash, source metadata | Candidate/evidence cards | lifecycle tests | **Complete for seeded/synthetic path** |
| Version comparison | `rule_delta_service.py`, policy models | `/api/policy-updates/*`, version/lineage UI | policy lifecycle tests | **Complete for supported rule values** |
| Supersession/version lineage | `policy_publication_service.py`, `VerifiedPolicyRuleVersion` | lineage/history routes | self-update/policy tests | **Complete for demo path** |
| Conflict detection | `backend/app/compliance/conflict_detector.py` | `/api/conflicts/*`, conflict UI | conflict tests | **Partial** — active same-service/rule value conflicts; broader semantic/date/document conflict classes are not implemented |
| Impact/cascade analysis | `cascade_trace_service.py`, connected-system/compliance services | `/api/cascade/*`, impact views | cascade/connected-system tests | **Complete for deterministic templates**; not a graph-derived engine |
| Compliance findings | `compliance_service.py`, `compliance_orchestrator_service.py` | `/api/compliance/*`, readiness dashboards | compliance tests | **Complete for seeded mock systems** |
| Reviewer workflow | candidate approve/reject/revision routes and approval models | officer/admin review UI | policy/RBAC tests | **Complete for current roles and demo records** |
| Publication and rollback | `policy_publication_service.py` | `/api/policy-updates/{candidate_id}/publish`, rollback/lineage UI | self-update tests | **Complete for demo path**; writes are store-replacement operations, not normalized transactional domain writes |
| Propagation | `propagation_service.py`, `system_patch_service.py` | propagation task UI | lifecycle/connected-system tests | **Partial** — mutations are explicitly demo/mock patches |
| Citizen guidance | `public_routes.py`, hybrid answer engine, citizen portal components | `/api/public/*`, citizen portal | public/chat/frontend tests | **Partial** — source-grounded seeded guidance works; eligibility endpoint is hard-coded for `income_certificate` |
| Eligibility re-evaluation | compliance rerun and service-portal eligibility helpers | compliance rerun routes, citizen forms | focused lifecycle tests | **Partial** — no general versioned scenario result model with prior/new comparison for every rule |
| Audit history | `audit_repository.py`, hash-chain verification | `/api/audit/events`, `/api/audit/verify` | audit tests | **Complete** for recorded events |
| Authentication | password hashing, JWT access tokens, refresh-token records | `/api/auth/*`, login UI | auth tests | **Partial** — refresh tokens rotate on refresh; known demo users remain synthetic and require explicit demo seeding |
| Authorization | `security/rbac.py`, route dependencies | role-gated officer/admin routes | RBAC tests | **Partial** — route role boundaries exist; department/object-level isolation is not comprehensively demonstrated |
| AI/fallback | hybrid/exact/RAG services, optional Ollama and remote providers | `/api/ai/*`, `/api/hybrid/*`, assistant UI | AI/RAG/Ollama tests | **Complete for deterministic fallback**; external providers remain optional/unverified |
| Voice | `stt_service.py`, `tts_service.py`, voice routes | citizen voice UI | STT/TTS/frontend tests | **Partial** — bounded, rate-limited synthetic voice endpoints; production speech providers remain unverified |
| Multilingual path | language helpers, browser/backend voice support | citizen voice/form UI | language/speech tests | **Complete for verified supported paths** |
| Reports | `report_routes.py`, report services | `/api/reports/*`, admin reports UI | report tests | **Complete for synthetic records** |
| Health/readiness | `health_routes.py`, `readiness_service.py` | `/api/health`, `/api/ready`, `/api/integration/health` | health/readiness tests | **Complete internally**; readiness wording can be mistaken for pilot readiness |
| Database persistence | SQLAlchemy `PolicyRecord` JSON collections plus auth/audit tables | SQLite default, PostgreSQL URL support | database seed tests | **Partial** — domain data is serialized JSON records; containers now run Alembic, while `create_all` remains a local/test fallback |
| Deployment | Dockerfiles, Compose, Render Blueprint | Render hostname from `render.yaml` | local container evidence in docs | **Not verified** — configured hostname returned HTTP 404 during this audit |

## Architecture

### Frontend

Vite/React single-page application in `frontend/src`. The app uses path inspection and guarded portal components rather than a central route manifest. Main surfaces include unified landing, citizen portal, government/admin portal, demo dashboard, review/impact views, and voice controls.

### Backend

FastAPI application bootstrapped in `backend/app/main.py`. Routers cover auth, circulars, rule candidates, policy publication, conflicts, compliance, cascade/impact, connected systems, propagation, audit, public guidance, service portal, reports, AI, voice, datasets, and demo/sandbox flows. Middleware provides request IDs, security headers, logging, trusted hosts, CORS, version aliases, and normalized errors.

### Database and storage

SQLite is the local default; PostgreSQL is supported through `DATABASE_URL`. `PolicyStoreRepository` stores most domain collections as JSON payloads in a generic `policy_records` table. Users, refresh tokens, sessions, and audit events have separate SQLAlchemy tables. A legacy JSON mirror remains under `backend/app/storage`.

Alembic migrations exist in `backend/alembic/versions`; both container entrypoints now run `alembic upgrade head` before application startup. `Base.metadata.create_all()` remains a local/test compatibility fallback and hosted migration behavior still needs live verification.

### AI

The deterministic hybrid/exact/template/RAG path is the authoritative answer boundary. Ollama and remote providers are optional. Source requirements and fallback behavior are tested; external model quality is not treated as verified production behavior.

### Authentication and authorization

Bearer JWT access tokens and hashed refresh tokens are implemented in `backend/app/security`. Role dependencies protect many officer/admin routes. Default synthetic users are seeded only when explicit demo mode and startup-seeding flags are enabled.

### Audit

`backend/app/repositories/audit_repository.py` appends hash-linked SQL audit events and exposes chain verification through `/api/audit/verify`.

## Critical findings

### P0 — citizen application validation crash (resolved 2026-08-07)

`backend/app/forms/service_portal_service.py:522` references the nonexistent `status.HTTP_422_UNPROCESSABLE_CONTENT` constant. The missing-fields submit path raises `AttributeError` instead of returning HTTP 422. This breaks the application → payment/review/certificate journey at a core validation boundary.

Evidence: `test_application_upload_payment_review_certificate_flow` now passes after replacing the unsupported constant with `status.HTTP_422_UNPROCESSABLE_ENTITY`.

### P1 — known demo credentials require explicit demo mode

`auth_service.DEFAULT_USERS` still contains known passwords for the synthetic walkthrough, but `backend/app/main.py` now seeds them only when both `DEMO_MODE=true` and `SEED_DEMO_ON_STARTUP=true`. Render remains intentionally configured as a staging sandbox and must not be treated as a pilot or production deployment.

`demo_mode` now defaults to `false`; demo, virtual-government, mock-system, and sandbox routers require explicit opt-in. Their mutating behavior is synthetic and must remain isolated.

`app_env` defaults to `development` and `debug` defaults to `true`; fail-closed validation only runs for `APP_ENV=production`. A misconfigured hosted service using `staging` or no environment value can therefore retain development controls and verbose error behavior. This remains an operational deployment gate.

### P1 — unauthenticated expensive/mutating endpoints

`/api/stt/transcribe` and `/api/tts/speak` remain citizen-facing, but now have rate limits and bounded upload/text/cache behavior. `/api/dataset/import` and `/api/dataset/rag/build` now require admin/reviewer roles.

`/api/security/otp/request` and `/api/security/otp/verify` are demo-gated; the deterministic verifier is unreachable when `DEMO_MODE=false`.

STT temporary files are removed in a `finally` block and the TTS cache has configured file/byte eviction limits. A distributed rate-limit and external speech-provider policy remain pilot work.

### P1 — deployment does not execute migrations

Both container entrypoints now run `alembic upgrade head` before starting Uvicorn. Fresh-database, upgrade, rollback, and hosted behavior still require a live Docker/PostgreSQL verification.

### P1 — deployment currently unverified

`https://niyamguard-sandbox-jashwanth.onrender.com/`, `/api/health`, `/api/ready`, and `/api/integration/health` returned HTTP 404 during this audit. The Render Blueprint is configuration evidence, not proof of a live deployment.

### P1 — domain model is mostly serialized JSON

Most policy, rule, conflict, impact, review, and eligibility records are serialized into generic JSON payload rows. This preserves the demo but does not yet provide the relational foreign keys, constraints, indexes, optimistic locking, and transaction boundaries required for a production-grade multi-user policy system.

Audit appends now read and write in one session under a process lock; PostgreSQL workers also take a transaction-scoped advisory lock, and verification orders by timestamp plus event id. A durable external archival/retention policy remains a pilot gate.

### P2 — ingestion and extraction boundaries

Uploads validate extension, declared MIME, size, and a PDF signature, but there is no quarantine/malware hook, randomized stored source file, processing queue, timeout state, or robust PDF/OCR path. External source sync is implemented only for `local_demo`; non-local sources are not real integrations.

Dataset QA/top-k and collection/search limits now have explicit upper bounds. Other domain-specific query costs still need operational monitoring.

### P2 — auth/session hardening

Refresh tokens now rotate atomically and JWT issuer/audience claims are validated. Rate limiting remains in-memory/per-process, and session ownership/expiry requires a separate pilot hardening pass.

`/api/ops/status` now requires an authenticated viewer/reviewer/admin role and returns only a dataset pack name, not an absolute path. Health endpoints remain intentionally small and non-sensitive.

### P2 — claims and documentation drift

README and test-report claims now reflect 259 collected/passing backend tests (with third-party plugin autoload disabled for the clean local gate). `docs/current-jashwanth-repo-audit.md` still contains historical path references and should not be treated as current evidence. Readiness terminology remains explicitly synthetic/internal.

The changelog describes a 1.2.0 candidate, but the public default branch currently has release/tag `v1.1.0`; a v1.2.0 public release is not verified. `docs/access-control.md` also labels the seeded officer account as a reviewer, while the code assigns the `officer` role.

The current localization paths are covered by frontend/assistant tests; a separate copy-edit pass for every mixed-language phrase remains useful, but the productionization pass did not claim a full language-quality audit.

The README requires Python 3.12, but the requirements do not enforce an upper bound; the current Python 3.13 environment exposed the service-portal exception.

The frontend stores access and refresh tokens in `localStorage` (`frontend/src/api/client.js`), which is an accepted demo risk but not the preferred production session boundary. The integration-readiness checklist still marks production audit-chain review as pending even though the internal readiness service reports that control as ready.

No license file is present; redistribution and public reuse remain an owner/legal decision even though the repository is publicly visible.

## Existing claims versus evidence

| Claim surface | Evidence result |
|---|---|
| Synthetic/non-official GovTech sandbox | Supported by README, docs, UI disclaimers, tests, and mock-system boundaries |
| Connected GO-138 policy lifecycle | Supported for the seeded/demo path by backend and frontend tests |
| 259 backend tests | 259 tests pass in the clean-environment gate documented in `docs/TEST_REPORT.md` |
| 60 frontend tests | Current `npm test -- --run` passed 60 tests |
| Government/identity/payment/messaging integration | Explicitly not verified; docs correctly label these synthetic/mock/optional |
| Production deployment | Not verified; configured Render hostname returned 404 |
| Pilot readiness | Internal readiness controls exist, but external authorization, security, accessibility, privacy, operations, and deployment gates remain open |

## Phase 0 conclusion

The existing architecture and demo path are worth preserving. The 2026-08-07 pass completed the first correctness/security boundary slice and the evidence-led Product Design entry point. The next gate is operational: run the migrated container against a fresh PostgreSQL database, verify hosted ownership/deployment, and close pilot-grade relational, ingestion, accessibility, and legal controls before making a stronger public claim.

## Public evidence checked

- GitHub repository: public, default branch `main`, HEAD `a40fffcb`; latest public release `v1.1.0`.
- Portfolio case page: `https://jashwanth-portfolio-ten.vercel.app/work/niyamguard/` returned HTTP 200.
- Portfolio media: `/media/niyamguard/demo.mp4` (200, `video/mp4`), `/media/niyamguard/demo.webm` (200, `video/webm`), `/media/niyamguard/demo-captions.vtt` (200, `text/vtt`), and `/media/niyamguard/poster.png` (200, `image/png`).
- Render Blueprint hostname and health routes returned HTTP 404; no live NiyamGuard deployment was verified.
