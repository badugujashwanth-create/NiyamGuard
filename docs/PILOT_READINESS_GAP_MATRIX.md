# NiyamGuard pilot-readiness gap matrix

This matrix reconciles the July 2026 product-maturity review with the tested repository. A module name is not counted as a finished feature unless it is on the live FastAPI/React path or explicitly labelled as a sandbox boundary.

| Review area | Verified or integrated now | Genuine remaining gap | Current decision |
|---|---|---|---|
| Government integrations | Adapter-shaped boundaries plus synthetic Gazette, identity, OTP, payment, certificate, document-vault, MeeSeva, FAQ, and integration-health simulations | Authorized DigiLocker, eSign, government identity, official Gazette, MeeSeva/UMANG, and department APIs | Deferred until legal approval, credentials, data contracts, and security review exist |
| Circular intelligence | Circular ingestion, deduplication, extraction, officer approval, immutable rule versions, effective dates, rollback, supersession links, propagation, audit, and policy-lineage evidence | Cross-state comparison, explicit expiry detection, legal-citation graph, and multi-rule dependency visualization | Lineage integrated; cross-jurisdiction work remains P1 research |
| Knowledge relationships | Verified rule store, RAG index, source cards, cascade node/edge traces, and a searchable rule-to-system relationship explorer | Cross-domain graph spanning schemes, forms, legal citations, circular lineage, and multi-hop dependencies | Core explorer integrated; broader legal graph remains P1 |
| Compliance intelligence | Deterministic findings, conflict detection, impact/priority scores, evidence-derived compliance score, coverage score, and department readiness | Longitudinal trends, forecast models, policy simulation, heatmaps across real districts, and scheduled executive reports | Current scores are descriptive, not predictive |
| Citizen experience | Service catalog, scheme finder, guided forms, document validation, application drafts, status history, notifications, officer review, certificate generation, tracking, and public verification | Personal saved-service dashboard, certificate wallet, offline/PWA support, push notifications, and native mobile apps | Web pilot flow is integrated; mobile/offline remains deferred |
| AI trust | Deterministic rule engine, hybrid retrieval, source cards, confidence, answer validation, provider fallback, multilingual responses, and human approval before publication | Formal hallucination benchmark, cross-document evaluation set, explanation-calibration study, and safe feedback-learning loop | Evaluation is higher priority than adding more providers |
| Government dashboards | Admin dashboard, compliance, cascade, conflicts, department scale, citizen impact, policy updates, propagation, scheduler, readiness, reports, and audit | Longitudinal KPI/SLA views, officer-productivity governance, and production telemetry | Evidence-derived readiness added; production analytics remain unclaimed |
| Workflow engine | Human approval, policy publication, propagation tasks, patch state, scheduled sync, compliance reruns, rollback, and scenario orchestration | BPMN import/export, visual authoring, arbitrary approval graphs, escalation rules, and versioned reusable templates | Existing policy workflow is product-specific, not a general BPM suite |
| Analytics | Current counts, priority/risk labels, department readiness, dataset explorer, reports, and audit verification | Time-series persistence, geographic drill-down on real data, demand forecasting, search analytics, and AI-quality trends | Do not invent trend charts from one synthetic snapshot |
| Security | Password hashing, JWT/refresh flow, RBAC, rate limiting, trusted hosts, security headers, audit hash chain, generated deployment secret, and sandbox OTP | Production MFA provider, hardware keys, device trust, SIEM, secret rotation automation, disaster-recovery exercises, and certification evidence | Sandbox OTP is not claimed as production MFA |
| Document understanding | Text/PDF circular ingestion, deterministic/optional-model rule extraction, source excerpts, and knowledge indexing | Handwriting OCR, table/stamp/signature detection, image reasoning, translation QA, and historical document comparison | Keep outside claims until measured datasets exist |
| Enterprise platform | Multi-role access and repository/service boundaries | Tenant isolation, organizations, SAML/OIDC SSO, API keys, webhooks, plugin lifecycle, and tenant analytics | Current product is one synthetic departmental sandbox |
| DevOps and operations | CI tests, dependency and secret scans, same-origin container, Render Blueprint, health/readiness APIs, and deployment documentation | Live provider provisioning, backups/restore, distributed tracing, metrics dashboards, autoscaling, canary/blue-green release, and cost monitoring | Provisioning is the only immediate external checkpoint |
| Product polish | Distinct citizen/officer/admin flows, product simulation, status badges, visible synthetic boundary, narrated walkthrough, captions, and accessibility documentation | Guided first-run onboarding, feature discovery, responsive/a11y device matrix, performance budgets, and a production installer/mobile shell | Complete evidence-led UX passes before expanding scope |

## Prioritized next gates

1. Provision the released Render Blueprint after the owner authenticates and confirms the intended free resources.
2. Persist time-stamped compliance snapshots before presenting trends or predictive analytics.
3. Extend the relationship explorer only after legal citations and multi-hop entity contracts are defined.
4. Run keyboard, screen-reader, responsive, and low-bandwidth UAT against the hosted build.
5. Start any real government integration only after written authorization, a data contract, test credentials, and a threat-model update.

## Product boundary

NiyamGuard remains a synthetic government-policy sandbox. It does not submit official applications, verify real identities, move money, send government notifications, issue legally valid certificates, or publish official circulars.
