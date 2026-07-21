# NiyamGuard v1.1 repository audit

Audit baseline: v1.1.0, 2026-07-21.

## Product boundary

NiyamGuard is a synthetic government-policy and citizen-service pilot sandbox. It is not an official portal and does not connect to real government identity, Gazette, MeeSeva/UMANG, payment, messaging, document-vault, or certificate-signing infrastructure.

## Current architecture

- `backend/app/main.py`: FastAPI application bootstrap.
- `backend/app/routes/`: auth, circulars, review/publication, compliance, cascade, priority, policy lineage, relationships, citizen services, applications, officer review, certificates, audit, reports, readiness, demo, health, and integration boundaries.
- `backend/app/services/`: deterministic policy/workflow, knowledge, citizen guidance, compliance, audit, auth, platform, sandbox provider, and optional AI services.
- `backend/app/models/` and `backend/app/repositories/`: Pydantic/SQLAlchemy contracts and storage isolation.
- `backend/app/security/` and `backend/app/middleware/`: password hashing, JWT/refresh, RBAC, rate limits, trusted-host/security-header, request-ID, structured-log, and clean-error boundaries.
- `frontend/src/app/App.jsx`: React/Vite route shell for citizen, officer, government/admin, and synthetic service views.
- `frontend/src/services/`: centralized API access and sandbox integrations.

## Storage and deployment

SQLAlchemy is the primary application store with SQLite for the released local/single-container sandbox and PostgreSQL support through `DATABASE_URL`. JSON assets remain synthetic seed/fallback data, not a second production authority.

The repository includes backend, frontend, and full-stack Dockerfiles, Docker Compose, a same-origin full-stack container, a Render Blueprint, health/readiness endpoints, migrations, seed commands, and deployment documentation. Provider provisioning and live operational monitoring remain owner/external checkpoints.

## Verified workflows

- Circular ingestion, extraction, reviewer approval, publication, versioning, supersession, rollback, and policy lineage.
- Compliance drift across mock connected systems, cascade tracing, citizen-impact priority, propagation, patch state, and audit evidence.
- Evidence-derived compliance coverage and department readiness; no invented longitudinal/predictive claim.
- Source-aware citizen guidance, scheme/service finder, guided application drafts, officer review, synthetic payment/certificate generation, tracking, and public verification.
- Role-specific authentication and authorization for admin, reviewer, officer, viewer, and citizen fixtures.

## Verification baseline

| Gate | Result |
|---|---|
| Backend | 243 tests passed |
| Frontend | 60 tests passed |
| Frontend build | Passed |
| Browser walkthrough | Passed end to end |
| Full-stack container | Same-origin SPA/API and deep-route checks passed |
| Dependency audit | npm production and installed backend audits passed |
| Secret scan | Current tree and history passed |
| Demo | 337.408 seconds, 1280×720 VP9/Opus, narrated/captioned, 11 inspected frames |

## Genuine remaining gaps

- No authorized real-government or production provider integration.
- No production MFA/device trust, SIEM, managed secret rotation, certification, or completed disaster-recovery exercise.
- No hosted responsive/keyboard/screen-reader/low-bandwidth UAT matrix.
- No time-series production analytics, scale benchmark, or predictive compliance model.
- No real certificate legal validity, official application submission, identity verification, or money movement.

The canonical current gap source is [PILOT_READINESS_GAP_MATRIX.md](PILOT_READINESS_GAP_MATRIX.md).
