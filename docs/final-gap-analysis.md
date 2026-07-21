# NiyamGuard v1.1 final gap analysis

This replaces the pre-implementation comparison table. Features are counted only when they are on the live FastAPI/React path and covered by repository evidence.

## Closed gaps

| Area | Verified v1.1 state |
|---|---|
| Persistence | SQLAlchemy with SQLite sandbox and PostgreSQL configuration path; migrations and seeds versioned |
| Auth/RBAC | Password hashing, JWT/refresh, role dependencies, seeded role fixtures, protected admin/officer APIs |
| Audit | Append-only event model with hash-chain verification and policy/citizen/certificate evidence |
| Policy lifecycle | Circular ingestion, extraction, approval, publication, versions, supersession, rollback, lineage |
| Compliance | Drift findings, conflicts, cascade, priority, coverage, readiness, propagation, patch state |
| Citizen workflow | Verified-rule guidance, service finder, application drafts, officer review, synthetic certificate/tracking/verification |
| Admin UX | Login-protected policy, compliance, propagation, audit, reports, readiness, and relationship views |
| Deployment | CI, Docker Compose, same-origin full-stack container, Render Blueprint, health/readiness documentation |
| Demonstration | Real synthetic browser simulation, 5:37 narrated/captioned media, eleven inspected milestone frames |

## Release-blocking external gaps

| Gate | Why it remains open | Required evidence |
|---|---|---|
| Hosting provision | Blueprint is verified but no owner-authenticated production service is claimed | Provider URL, health/deep-route/API checks, logs, rollback owner |
| Government integrations | No authorization, credentials, contracts, or official test environment | Written approval, data contract, sandbox credentials, threat-model update, contract tests |
| Identity/payment/messaging | Current adapters are synthetic | Approved providers, privacy/legal review, secrets, failure/recovery/UAT evidence |
| Security operations | Sandbox controls are not certification | Production MFA/device trust, key rotation, SIEM/alerts, incident and DR exercises |
| Accessibility/responsiveness | Documentation exists but hosted device/assistive-tech matrix is incomplete | Keyboard, screen-reader, zoom, mobile, low-bandwidth evidence |
| Performance/analytics | Current scores describe one synthetic snapshot | Time-stamped datasets, load profiles, retention, observability, honest budgets |

## Product decision

Do not add more named AI agents or predictive dashboards before the external pilot gates are owned. The next highest-value work is hosted UAT, adapter contracts, recovery evidence, and authorized integration discovery.

NiyamGuard remains an MVP/pilot sandbox and must not be described as an official government system, legal authority, real identity/payment service, or production deployment.
