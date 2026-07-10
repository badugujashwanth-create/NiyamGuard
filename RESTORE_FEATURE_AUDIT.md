# Restore Feature Audit

Generated: 2026-07-10

## 1. Features Currently Visible

- `/` shows a clean two-choice landing: `Citizen Portal` and `Government Portal`.
- `/citizen` shows the main `VoiceAssistantPanel` under `Apply for Certificates with Voice Assistant`.
- `/citizen` also shows text fallback, Browse Services, Apply Income Certificate, My Applications, Track Application, Verify Certificate, Scheme Finder, and source-backed citizen Q&A chips.
- `/government` shows Circulars & Policy Updates, Self-Updating Policy Engine, Compliance Drift, Connected Systems / Propagation, Virtual Government Sandbox, Officer Review, Certificates, Audit Trail, Reports, Hybrid Answer Engine / Ollama, Readiness & Ops, Legacy Demo Dashboard, and Run Full End-to-End Demo.
- Original detailed routes remain linked and working: `/demo`, `/admin/*`, `/virtual-gov/*`, `/officer`, `/services`, `/applications`, `/track`, `/verify-certificate`, `/mock/meeseva`, and `/mock/public-faq`.

## 2. Features Hidden From UI Before The Restore

- The main voice assistant was not obvious enough from `/citizen`.
- `/demo` had been displaced by the new portal flow and needed explicit route preservation.
- Government features existed but needed a complete organized entry point from `/government`.
- Mock connected systems and propagation routes existed but needed direct Government Portal links.

## 3. Features Accidentally Removed

- No source feature files were deleted.
- No backend route/service/model feature was removed.
- The correction was routing, visibility, and portal organization.

## 4. Routes Still Working

All requested frontend routes returned HTTP 200 on `http://127.0.0.1:5180`:

`/`, `/citizen`, `/government`, `/demo`, `/services`, `/apply/income_certificate`, `/applications`, `/track`, `/verify-certificate`, `/officer`, `/admin`, `/admin/compliance`, `/admin/policy-updates`, `/admin/propagation`, `/admin/audit`, `/admin/readiness`, `/virtual-gov`, `/virtual-gov/gazette`, `/virtual-gov/scenario-runner`, `/mock/meeseva`, `/mock/public-faq`.

## 5. Routes Broken

- None found in the requested route set.
- Admin pages still require login for protected data; this is expected.

## 6. Components Present And Linked

- `VoiceAssistantPanel.jsx`: visible in Citizen Portal and still used in guided form flow.
- `SchemeFinder.jsx`: linked from Citizen Portal.
- `ServiceCatalog.jsx`: used by `/citizen/assistant`.
- `ServicePortal.jsx`: used by services, applications, tracking, verification, payment, citizen, and officer routes.
- `AdminPortal.jsx`: used by `/admin/*`.
- `DemoDashboard.jsx`: restored at `/demo`.
- `VirtualGovernmentSandbox.jsx`: used by `/virtual-gov/*`.
- `MockConnectedSystems.jsx`: used by `/mock/meeseva` and `/mock/public-faq`.
- `UnifiedDemoPortal.jsx`: used by `/government`.

## 7. APIs Present But Still Sandbox-Scoped

- OTP, payment, certificate signing, virtual government, and connected-system patching are sandbox APIs.
- Ollama is real local AI when running, but it only explains verified context.
- Official policy answers and compliance decisions still come from deterministic verified rules.
- Real government source feeds, PKI, payment gateway, SMS/email, and identity provider are not connected.

## 8. Restored Immediately

- Main voice assistant is visible and usable on `/citizen`.
- Friendly fallback replaces the scary browser speech service message.
- `/government` exposes all major government/admin/officer/sandbox modules.
- `/demo` and old feature routes are preserved.
- Full end-to-end demo calls real backend endpoint `POST /api/demo/run-full-end-to-end`.
- Officer account now uses a separate `officer` role while retaining officer-review access.
