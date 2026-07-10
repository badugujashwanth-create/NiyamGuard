# Current Missing And Cleanup Audit

## Already Working

- Backend starts and responds on `http://127.0.0.1:8010`.
- Frontend starts and responds on `http://127.0.0.1:5180`.
- Landing page now has only two primary choices: `Citizen Portal` and `Government Portal`.
- Citizen Portal links to services, apply, applications, tracking, certificate verification, scheme finder, and the hybrid assistant.
- Government Portal runs `POST /api/demo/run-full-end-to-end` and shows generated application, certificate, verification hash, full step status, hybrid answer, and Ollama/fallback output.
- Full demo flow connects circular ingestion, verified rule publishing, service portal update, citizen identity, OTP, payment, officer approval, certificate signing, public verification, connected-system patching, compliance rerun, audit, hybrid answer, and local AI.
- Ollama is installed, `qwen2.5:7b-instruct` is present, and `/api/ai/status` reports `online`.
- Text assistant works even when browser speech is unavailable.

## Missing Or Not Production-Ready

- No official government approval, real department integration, official logo, or production certificate authority.
- OTP, payment, certificate signing, and connected systems are sandbox/demo implementations.
- Admin credentials are demo credentials and not a production identity provider.
- Local SQLite/demo store is fine for demo but not a production database.
- Browser voice input still depends on browser/device support; text fallback is the reliable path.
- Ollama is optional. If the local service is stopped, deterministic fallback must remain visible.

## Confusing Or Unwanted Before Fix

- `/` opened the old citizen assistant instead of a simple project entry point.
- `/portal`, `/demo`, `/virtual-gov`, `/admin/*`, `/services`, and mock pages were all visible as separate concepts.
- Citizen and government features were mixed in one demo surface.
- Old voice failure copy sounded like a system outage.
- Generated folders such as `frontend/dist`, Playwright reports, test results, caches, and ignored scratch app folders were present locally.

## Duplicated Or Secondary UI

- `/demo` is now secondary and opens the Government Portal experience.
- Mock connected systems remain reachable by URL, but they are no longer part of the first screen.
- Scheme finder is reachable from Citizen Portal instead of being a separate primary entry point.
- Admin technical pages are available from Government Portal and direct `/admin/*` routes, not the citizen side.

## Cleanup Status

- Removed regenerateable local folders: `frontend/dist`, `frontend/playwright-report`, `frontend/test-results`, `backend/.pytest_cache`, recursive `__pycache__`, and ignored `apps`.
- Kept source, tests, docs, final recording assets, and live ignored demo DB/store files required by the running local demo.
- `.gitignore` now excludes local env files, DBs, generated storage, frontend build/report folders, and final recording video/screenshots.

## Integrations Classification

- Real local: Ollama CLI/service and local model execution.
- Sandbox: virtual gazette, circular ingestion, service portal, citizen identity, OTP, payment, officer review, certificate signing, public verification, connected systems, compliance rerun, audit trail.
- Fallback: deterministic AI explanation when Ollama is offline, text assistant when speech input is unavailable.
- Missing for production: official government connectors, payment gateway, SMS/email provider, PKI/certificate authority, department approval.

## Must Be Fixed Before A Real Pilot

- Replace sandbox OTP/payment/signing with approved providers.
- Replace demo auth and seeded users with approved identity and audit policies.
- Move SQLite/demo JSON store to managed production database/storage.
- Add official source ingestion contracts and department approval workflow.
- Security review, accessibility review, privacy review, and legal review are still required.
