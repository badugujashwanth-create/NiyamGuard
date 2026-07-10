# Harsh Project Gap Audit

Generated: 2026-07-10  
Branch: `codex/self-updating-policy-engine`  
Latest existing commit before this local work: `27d70c6 Update final report with PR link`

## 1. What The Audit Says Is Implemented

The complete audit says NiyamGuard has a virtual government sandbox, circular/policy update workflow, verified rule engine, citizen service portal, applications, payment sandbox, officer review, certificate generation, public verification, compliance drift checks, audit trail, hybrid answer engine, optional Ollama, readiness controls, tests, and recording assets.

That is broadly true, but the earlier state was still presentation-risky because the working pieces were spread across `/demo`, `/virtual-gov`, `/services`, `/officer`, `/admin/*`, and the root assistant. The platform had a story, but not one clean browser start point.

## 2. What Is Actually Implemented In Code

- Backend routes exist for auth, public rules, compliance, reports, audit, service portal, readiness, virtual government, AI status, hybrid answer/search, mock systems, self-update, circulars, rule candidates, policy publication, propagation, scheduler, datasets, STT, and TTS.
- Frontend routes exist for `/`, `/portal`, `/demo`, `/virtual-gov`, `/services`, `/apply/*`, `/applications`, `/track`, `/verify-certificate`, `/officer`, `/scheme-finder`, `/mock/meeseva`, `/mock/public-faq`, `/login`, and `/admin/*`.
- `/api/demo/run-full-end-to-end` now orchestrates one backend scenario that creates real demo records in the local store.
- `/api/ai/status` reports requested provider, active provider, enabled flag, model, fallback availability, and status.
- `/api/ai/verified-explanation` now provides a verified-context explanation using Ollama if online or deterministic fallback if not.
- The voice assistant now has a demo-safe speech layer and visible text fallback.

## 3. What Was Missing

- Missing before this pass: unified `/portal`.
- Missing before this pass: one backend endpoint for the full end-to-end story.
- Missing before this pass: browser-safe speech fallback that avoided the scary network speech-service error.
- Missing before this pass: Playwright E2E test dedicated to the final browser demo flow.
- Missing before this pass: integration readiness checklist, code organization audit, cleanup report, final runbook, and final readiness report.
- Still missing for production: official MeeSeva APIs, real identity/eKYC, real SMS, real payment gateway, official certificate authority, government UAT, production security audit, cloud deployment, secrets manager, and legal approval.

## 4. What Is Duplicated Or Confusing

- There are two demo entry points: `/demo` and `/portal`. `/portal` is now the recommended start point; `/demo` remains useful but should be secondary.
- Virtual government concepts are still represented mostly through one `/virtual-gov` page and backend APIs, not separate pages for each provider.
- AI appears in multiple places: `/api/ai/status`, `/admin/regulatory-ai`, hybrid answer APIs, chat APIs, and portal explanation. This is powerful but needs a clear demo explanation.
- Service portal and older voice/form assistant both support citizen workflows. They are related, not identical.
- Existing docs are numerous and partially overlapping; the final runbook should be used during presentation.

## 5. What Can Break The Demo

- Backend running on the old code will make `/api/demo/run-full-end-to-end` return 404. Restart backend after pulling local changes.
- Frontend must use `VITE_API_BASE_URL=http://127.0.0.1:8010` for the current demo ports.
- Admin/officer pages need a valid login token.
- Ollama may be unavailable even when `AI_ENABLED=true`; fallback works but the presenter must say it is fallback.
- Browser speech recognition can fail due to browser/provider/network/microphone limitations. Text fallback now remains visible and safe.
- Local DB state can be reset by demo flows. Do not use real data.

## 6. What Integrations Are Incomplete

- Virtual Gazette: mocked/local demo source, not an official gazette feed.
- Virtual Identity Provider: sandbox profile plus OTP only, no eKYC.
- OTP/SMS: deterministic demo code `123456`, no real SMS/email delivery.
- Payment Gateway: sandbox state machine only, no real money movement.
- Certificate Authority: demo hash/signature only, no official signing authority.
- Document Vault: synthetic attachment metadata and local files only.
- Integration Monitor: connected system snapshots and mock pages only.
- Ollama: works if installed and running; fallback is active otherwise.

## 7. What Pages/Routes Were Scattered

The scattered route set remains intentionally available:

- `/virtual-gov`
- `/demo`
- `/services`
- `/apply/income_certificate`
- `/officer`
- `/verify-certificate`
- `/admin/compliance`
- `/admin/audit`
- `/admin/readiness`
- `/admin/regulatory-ai`
- `/mock/meeseva`
- `/mock/public-faq`
- `/`

The new `/portal` page is the single recommended start point.

## 8. What Tests Were Missing

Before this pass:

- No backend test for a complete `/api/demo/run-full-end-to-end` scenario.
- No frontend test for `/portal`.
- No speech-service unit tests.
- No Playwright final browser E2E test.

Now added:

- `backend/app/tests/test_full_demo.py`
- `/portal` coverage in `frontend/src/test/App.test.jsx`
- `frontend/src/test/speechService.test.js`
- `frontend/tests/e2e/full-demo-flow.spec.ts`

## 9. What Files/Folders Look Unwanted

Unwanted or generated local artifacts found:

- `niyamguard.db`
- `backend/niyamguard.db`
- `backend/app/storage/documents/`
- `backend/app/storage/certificates/`
- `frontend/dist/`
- `frontend/test-results/`
- `frontend/playwright-report/`
- `backend/.pytest_cache/`
- `backend/app/**/__pycache__/`
- `frontend/node_modules/`
- `apps/demo-dashboard/node_modules/`

Cleanup done:

- Removed generated pytest cache, Python `__pycache__`, frontend `dist`, Playwright report, and Playwright test-results.
- Kept `node_modules` because tests/build/demo need installed dependencies.
- Kept local DB files because the running demo server depends on local state.
- Kept final E2E screenshots/video as local evidence, but `.gitignore` prevents committing the new generated E2E assets.

## 10. What Must Be Fixed Before Final Presentation

Fixed in this pass:

- Add `/portal`.
- Add backend full demo endpoint.
- Wire portal cards/status/run button to real APIs.
- Add verified-context Ollama/fallback explanation.
- Fix browser speech error with safe fallback.
- Add E2E screenshots/video.
- Add runbook and readiness reports.

Remaining presentation risks:

- Ollama was fallback during verification because local Ollama was unavailable to the backend at test time.
- Official production readiness must not be claimed.
- Generated local DB state changes during demo runs; reset with `python -m app.seed_demo` or the portal flow as needed.

