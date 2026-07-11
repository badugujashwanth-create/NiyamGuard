# Final One-by-One Test Report

Date: 2026-07-11  
Backend tested at: `http://127.0.0.1:8010`  
Frontend tested at: `http://127.0.0.1:5180`

## 1. Login tests

All seeded accounts authenticated against the live backend with the expected role:

| Account | HTTP | Role | Intended frontend landing |
|---|---:|---|---|
| `citizen@niyamguard.local` | 200 | citizen | `/citizen` |
| `officer@niyamguard.local` | 200 | officer | `/government` |
| `admin@niyamguard.local` | 200 | admin | `/government` |
| `reviewer@niyamguard.local` | 200 | reviewer | `/government` |
| `sandbox@niyamguard.local` | 200 | sandbox_admin | `/sandbox` |

Wrong email and wrong password returned 401 with the shared friendly API error handling. Empty email and empty password returned structured 422 validation responses. Frontend role routing is covered for all five roles. Headed browser verification covered citizen, officer, admin, reviewer, and sandbox-admin landing pages.

## 2. Citizen portal tests

Pass. The citizen landing, service catalog, applications, tracking, verification, chatbot, notifications, and scheme finder routes render without a government action being exposed to a citizen. The service API returned the seeded Income, Caste/Community, Residence, EWS, Birth, Death, and Family Member services. Public and citizen routes did not produce an unexpected 403.

## 3. Apply form tests

Pass. The Income Certificate form renders dynamic fields including identity, address, district, mandal, occupation, monthly/annual income, purpose, and documents. Valid values create a draft and the complete API flow submits an application. Aadhaar/mobile/income validation, missing required items, file type validation, and required-document validation are covered by backend and frontend tests. The assistant corrects a personal name entered as occupation and gives the supported occupation examples.

## 4. Voice assistant multiple-input tests

The exact transcript is logged at `niyamguard.assistant` and sent in the `message` field. Browser voice tests confirm the final STT transcript is forwarded unchanged. Known inputs no longer receive the first-turn generic field question.

| Input | Expected Intent | Actual Answer Summary | Result |
|---|---|---|---|
| `mandalam` | mandal | Defines the administrative area and says to use address proof | Pass |
| `mandal lo emi rayali` | mandal | Defines mandal/address-proof value and offers location help | Pass |
| `occupation lag raha hai Imran Ali` | occupation | Says occupation is work, not a name; lists valid examples | Pass |
| `ऑक्यूपेशन` | occupation | Direct occupation guidance | Pass |
| `monthly income` | monthly_income | Explains one-month income and the 15000 example | Pass |
| `मैन्युअल इनकम` | monthly_income | Hindi monthly-income explanation | Pass |
| `annual income` | annual_income | Explains monthly × 12 and 180000 example | Pass |
| `income certificate validity entha` | validity | Says 6 months and cites GO-138/Revenue | Pass |
| `documents enti` | documents | Schema-backed required document list | Pass |
| `aadhaar` | aadhaar | 12 digits, spacing guidance, privacy warning | Pass |
| `mobile number` | mobile | Active 10-digit number and OTP/update guidance | Pass |
| `random text` | unknown | Friendly field-help fallback | Pass |

Additional English, Telugu, Hindi, mixed-language, typed-input, browser-speech, TTS, and unknown-input cases pass in the automated suites.

## 5. Chatbot tests

Pass. Citizen validity, documents, application process, tracking, and certificate verification now return deterministic or verified source-backed responses with method/source metadata. Government GO-138, affected-system registry, compliance drift, pending officer review, and old-to-new rule questions route to exact-rule or live operational handlers. The LLM remains explanatory; safe fallback is used only when verified data is unavailable.

## 6. Government portal tests

Pass. Overview, circular upload/intake, policy review, compliance, priority, cascade, audit, application review, reports/admin workspaces, readiness, hybrid answer UI, and chatbot-backed APIs load for their allowed roles. The Overview circular upload uses the existing ingestion/extraction pipeline. The async form-reset browser error found during testing was fixed.

## 7. Application review tests

Pass. A citizen application was created, required PDFs uploaded, submitted, paid, and observed in the pending queue. Officer approval generated a certificate. A separate complete application was rejected by admin. Existing tests cover duplicate terminal-state handling, access denial for disallowed roles, status history, notifications, public verification, certificate download, and audit events.

The required aliases return 200 for officer/admin and call the same service layer as `/api/officer/...`:

- `GET /api/government/applications`
- `GET /api/government/applications/pending`
- `POST /api/government/applications/{id}/approve`
- `POST /api/government/applications/{id}/reject`

## 8. Sandbox circular tests

Pass. Revenue/Income, Social Welfare/Caste, Social Welfare/Pension, Residence processing-time, and EWS-style field/value payloads were exercised through tests or live UI/API flows. Required UI values are HTML-required; backend rejects empty core values and unchanged old/new values with 422. Omitted API effective dates retain the intentional server default to the current date.

## 9. PDF generation tests

Pass. POST generation and authenticated GET return a non-empty `application/pdf` beginning with `%PDF`. Text extraction tests verify actual per-circular department, number, title, affected service, rule key, old value, new value, effective date, body, and demo disclaimer. Two different department/service PDFs were checked for cross-contamination and contained only their own values.

## 10. Publish-to-government tests

Pass. `Publish to NiyamGuard` is enabled after PDF generation. Publish creates/reuses a circular-ingestion document, records `government_document_id`, sets delivery to `Received by NiyamGuard`, creates audit events, and places the same PDF in the Government Circular Inbox. Officer PDF access uses the government-scoped PDF endpoint; the sandbox endpoint remains sandbox-admin/admin only.

## 11. Compliance tests

Pass. Circular approval triggers publication/compliance behavior. Direct `POST /api/compliance/run` returned 200. The headed flow verified non-zero seeded Circulars, Rule Candidates, Open Mismatches, and Critical Priority values, approved an uploaded rule candidate, and received the “compliance checks completed” result. The full demo patched connected systems and reran compliance successfully.

## 12. Certificate verification tests

Pass. Public verification remains unauthenticated. Valid certificate/hash verification is covered by full service flow and browser tests; invalid lookup returned HTTP 200 with `valid: false`; empty UI input is prevented by form validation. The public result does not expose hidden application evidence.

## 13. API endpoint tests

The following live checks returned the expected successful status and no 500:

- `GET /api/integration/health` — 200
- `GET /api/ai/status` — 200
- `GET /api/portal/services` — 200
- `POST /api/chatbot/ask` — 200 for allowed logged-in roles
- `GET /api/government/applications/pending` — 200 for officer
- sandbox create/generate/get/publish — 200
- government inbox and government PDF — 200
- government parse and policy approval — 200
- `POST /api/compliance/run` — 200
- `POST /api/demo/run-full-end-to-end` — 200

Disallowed role checks return 403, missing authentication returns 401, and public certificate verification remains public.

## 14. Browser console/network checks

Pass. The final headed Playwright run explicitly collected console errors, uncaught page errors, and responses with status >= 400. All three collections were empty. No CORS error, missing import, missing route, failed PDF request, or allowed-role 403 remained.

## 15. Full end-to-end demo result

Pass. `POST /api/demo/run-full-end-to-end` returned `success: true`, 18/18 successful steps, application `NGSP-2026-INC-000001`, certificate `NGCERT-2026-INC-000001`, verified rule `6 months` from GO-138, and 30 audit events. The chain includes reset, circular publication/ingestion, extraction, verified-rule update, citizen application, OTP/payment, officer approval, certificate generation/signing/verification, connected-system patch, compliance rerun, audit, hybrid answer, and optional Ollama/fallback explanation.

## 16. Bugs found

1. Field aliases/intents were incomplete; broad `income` matching stole validity questions.
2. Known first-turn answers were prefixed with the generic “which field” intro.
3. Citizen verification/tracking and government operational chatbot questions were preempted by safe fallback.
4. Assistant frontend calls explicitly disabled auth headers.
5. Frontend role rules excluded admin from citizen/government routes and had no real `/sandbox` landing.
6. Government application aliases were absent, returning 404.
7. Sandbox publish was a disabled compatibility stub that performed manual export.
8. Government users had no role-correct route for the published sandbox PDF.
9. Circular upload accessed `event.currentTarget` after an await, causing a browser page error.
10. Sandbox core fields and unchanged old/new values lacked API validation.

## 17. Bugs fixed

All ten findings above were fixed without moving modules or introducing competing portal/publish flows. The existing officer review, circular ingestion, extraction, publication, compliance, audit, and PDF generation services are reused.

## 18. Bugs still pending

No known blocker remains within the requested voice, chatbot, RBAC, application review, circular overview, sandbox PDF, publish, compliance, or verification scope. Ollama may report deterministic fallback when no local Ollama server/model is available; this is expected and visibly labeled, not treated as an official decision.

## 19. Evidence and artifact paths

- Pre-fix audit: `BUGFIX_VOICE_REVIEW_SANDBOX_AUDIT.md`
- Backend regression tests: `backend/app/tests/test_bugfix_voice_review_sandbox.py`
- Two-PDF data test: `backend/app/tests/test_sandbox_pdf_data.py`
- Playwright HTML report: `frontend/playwright-report/index.html`
- Successful headed-run video: `frontend/test-results/full-demo-flow-unified-Niy-d9e5c-ent-admin-and-sandbox-flows/video.webm`
- Runtime logs: `backend-8010.err.log`, `frontend-5180.log`

## 20. Final verdict

Pass. The requested flows work end to end with role-correct access, real request routing, real circular data in PDFs, publish-to-inbox delivery, approval/compliance/audit integration, and source-backed assistant/chatbot answers.

### Final command results

- Backend: `python -m pytest app/tests -q` — **260 passed**
- Frontend: `npm test -- --run` — **69 passed**
- Build: `npm run build` — **passed**, 72 modules transformed
- E2E: `npx playwright test --headed` — **1 passed**

### Files changed for this bug-fix pass

- `BUGFIX_VOICE_REVIEW_SANDBOX_AUDIT.md`
- `FINAL_ONE_BY_ONE_TEST_REPORT.md`
- `backend/app/api/assistant_routes.py`
- `backend/app/api/chatbot_routes.py`
- `backend/app/api/government_routes.py`
- `backend/app/api/sandbox_routes.py`
- `backend/app/api/service_portal_routes.py`
- `backend/app/citizen_assistant/assistant_service.py`
- `backend/app/citizen_assistant/field_detector.py`
- `backend/app/citizen_assistant/guidance_engine.py`
- `backend/app/citizen_assistant/knowledge_chat_service.py`
- `backend/app/citizen_assistant/location_helper.py`
- `backend/app/demo/government_inbox_service.py`
- `backend/app/extraction/sandbox_circular_service.py`
- `backend/app/forms/service_portal_service.py`
- `backend/app/models/sandbox_models.py`
- `backend/app/tests/test_bugfix_voice_review_sandbox.py`
- `frontend/src/api/sandboxApi.js`
- `frontend/src/api/voiceApi.js`
- `frontend/src/app/App.jsx`
- `frontend/src/government-portal/components/GovernmentPortal.jsx`
- `frontend/src/government-portal/components/VirtualGovernmentSandbox.jsx`
- `frontend/src/test/App.test.jsx`
- `frontend/src/test/authUtils.test.js`
- `frontend/src/test/fixtures.js`
- `frontend/src/utils/authUtils.js`
- `frontend/tests/e2e/full-demo-flow.spec.ts`

The repository already contained unrelated dirty changes before this pass; they were preserved and are not attributed to this fix list.
