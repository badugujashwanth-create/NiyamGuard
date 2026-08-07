# NiyamGuard productionization state

**State date:** 2026-08-08
**Canonical branch:** `main`
**Latest local change:** conditional OCR, durable object storage, fail-closed scanning, readiness, and core accessibility gates
**Public release:** `v1.1.0` (a new release is not claimed until the changes are committed and published)
**Classification:** synthetic policy-drift MVP; production-boundary work in progress

**Readiness boundary:** **CODE READY** for the local/document-processing path; **EXTERNALLY VERIFIED PRODUCTION READY** is not claimed until hosted dependencies, security, accessibility, legal, and ownership gates are verified.

## Implemented in this pass

- Corrected the service-portal missing-field path to return HTTP 422 and retained its regression test.
- Tightened deterministic extraction to require one explicit, evidence-backed old→new rule statement; ambiguous or unsupported circulars now return a reviewable HTTP 422.
- Added a frozen 20-case deterministic extraction benchmark covering valid, ambiguous, and unsupported wording (20/20 locally).
- Made `DEMO_MODE` and startup demo seeding opt-in; production validation still rejects demo mode, debug mode, and placeholder secrets.
- Hardened `APP_ENV=staging` to use the same fail-closed controls as production, and renamed the synthetic Render/local-container environment to `APP_ENV=demo`; hardened environments now reject SQLite `DATABASE_URL` values.
- Hardened database validation now rejects SQLite driver variants and every non-PostgreSQL scheme before startup.
- Protected operational status and dataset import/RAG-build mutations with JWT role checks.
- Gated deterministic OTP endpoints behind explicit demo mode and removed absolute filesystem paths from ops status.
- Added STT upload size/format/MIME bounds and guaranteed temporary-file cleanup.
- Added a ClamAV upload-scanning boundary: local synthetic mode is explicit, while production requires ClamAV and fails closed on scanner unavailability or indeterminate results.
- Added conditional native PDF extraction (PyMuPDF first, pypdf native fallback) and OCRmyPDF/Tesseract processing for low-text PDFs; immutable originals, separate OCR derivatives, extraction source, OCR usage, page provenance, and controlled OCR errors are persisted.
- Added a `StorageBackend` protocol with atomic local filesystem and S3-compatible implementations, generated safe object keys, metadata/health operations, and production validation that requires S3-compatible durable storage.
- Extended `/api/ready` with database, storage, scanner, OCR, AI-optional, and redacted configuration readiness; `/api/health` remains a liveness-only endpoint.
- Applied the same scan-before-persist boundary to citizen service-document uploads; accepted files are atomically written with restrictive `0600` permissions, SHA-256 and scanner status are retained as provenance metadata, and scanner failures return a controlled error without leaving a file behind.
- Added atomic SHA-256 keyed source-artifact storage with restrictive permissions; APIs expose only a relative artifact key and source provenance metadata. Hosted object-storage durability remains an operational gate.
- Added TTS text limits, rate limiting, and bounded cache eviction.
- Added JWT issuer/audience checks and atomic refresh-token rotation.
- Added opt-in same-origin HttpOnly access/refresh cookies; production validation requires cookie mode with secure cookies, while bearer/localStorage remains a local-demo fallback.
- Added database-backed session records, session-linked refresh tokens, JWT session IDs, logout revocation, and production enforcement of revocable sessions.
- Added a database-backed fixed-window rate limiter for cross-worker deployments; local/demo environments retain the in-memory path, while production validation requires `RATE_LIMIT_BACKEND=database`.
- Added a database-backed policy-store revision and optimistic write check; stale full-store replacements now fail with a retryable conflict instead of silently overwriting another reviewer.
- Stopped writing the compatibility JSON mirror when `LEGACY_FILE_STORE_ENABLED=false`; production writes now remain database-only while local/demo mode retains the mirror.
- Added typed relational tables and foreign keys for circular documents, rule candidates, rule deltas, approval workflows, verified rule versions, publication events, knowledge updates, compliance runs, propagation plans, propagation tasks, connected-system patches, rollback events, connected-system snapshots, and compliance findings. The serialized store remains a compatibility mirror, while these fourteen core policy-review collections are preferred on reads.
- Added deterministic evidence offsets to rule candidates so reviewers can locate the exact source-text span that produced a candidate; offsets remain nullable for legacy records and page coordinates are not claimed for OCR-free text.
- Serialized audit appends and made chain verification ordering deterministic; PostgreSQL workers also take a transaction-scoped advisory lock.
- Added Alembic execution to both container entrypoints and switched containers to a non-root runtime user.
- Made migration ownership explicit: deployed containers set `AUTO_CREATE_TABLES=false`, while local/test environments may opt into the compatibility fallback.
- Disabled legacy JSON-store fallback for non-demo deployments; production state now comes only from the configured database and returns an empty store when no authoritative records exist.
- Tightened `/api/ready` so a database is not considered ready until the migrated users, refresh-token, audit, and policy-record tables are present.
- Made containerized production frontends default to HttpOnly-cookie mode; local Docker Compose explicitly opts into bearer mode for the synthetic HTTP demo.
- Removed synthetic demo credential literals from the default production frontend bundle; only the explicit local Compose demo build receives those values.
- Updated every protected frontend route guard to recognize the non-sensitive stored user record when cookie mode is enabled; cookie-authenticated admin and citizen workflows no longer redirect to login because tokens are intentionally invisible to JavaScript.
- Added production fail-closed checks for credentialed wildcard CORS and wildcard/empty trusted-host settings.
- Refocused the landing screen on the GO-138 policy-drift incident, source evidence, impact chain, and reviewer/citizen workflow choices.
- Added visible focus treatment and reduced-motion handling; captured desktop/mobile Product Design evidence.
- Added core reviewer accessibility semantics: labelled main landmarks, active-page navigation state, keyboard-visible focus, status/live regions for loading and actions, and text-labelled lifecycle/module states.
- Added a production-shaped Compose harness with PostgreSQL, MinIO, ClamAV/OCR runtime dependencies, migrations, healthcheck, secure-cookie settings, and non-root containers.

## Verification

| Check | Result |
|---|---|
| Focused backend correctness/security suites | Pass (service portal, auth/RBAC, readiness, dataset, speech, audit, and runtime boundaries) |
| Full backend suite | Pass: 298 tests execute successfully with third-party pytest plugin autoload disabled |
| Deterministic extraction benchmark | Pass: 20/20 frozen synthetic cases |
| Frontend tests | Pass: 61 tests in default bearer-demo mode and 61 tests with `VITE_AUTH_COOKIE_MODE=true` |
| Frontend production build | Pass: Vite build |
| `npm audit --omit=dev` | Pass: 0 vulnerabilities |
| `pip-audit -r backend/requirements.txt` | Pass: no known vulnerabilities |
| `git diff --check` / Python compile | Pass |
| Product Design capture | Pass: landing and reviewer workflow captured at desktop and 390px mobile; no horizontal overflow |
| Docker image build | Not verified: Docker daemon unavailable in the current environment |
| Hosted Render deployment | Not verified: previous public hostname returned 404 |
| PostgreSQL migration CI gate | Configured: fresh PostgreSQL service runs Alembic, readiness, and production-style app import in GitHub Actions; not executed locally |
| Fresh SQLite Alembic migration and normalized seed/load round trip | Pass: migrations through `20260808_0011`, including OCR/page-provenance columns, readiness, review/publication/propagation row counts, and candidate evidence columns verified locally |
| Isolated policy-drift lifecycle | Pass: 11/11 steps, exact GO-138 evidence, four propagation tasks, one changed eligibility fixture, and typed publication/knowledge/compliance/propagation rows |
| Production frontend credential boundary | Pass: default Vite production bundle contains no synthetic demo credential literals |
| Hardened environment boundary | Pass: staging rejects demo mode and SQLite; synthetic deployment is explicitly labeled `APP_ENV=demo` |
| Database scheme boundary | Pass: hardened startup rejects SQLite driver variants and non-PostgreSQL URLs |
| Core Playwright/E2E accessibility regression | Pass: landing, reviewer lifecycle, admin login, labelled landmarks, live status, and active navigation verified locally with video disabled |
| Production-like Compose configuration | Pass: `docker compose -f docker-compose.production.yml config --quiet`; image build/runtime not verified because Docker daemon is unavailable |

## Remaining blockers

1. Execute the PostgreSQL CI/deployment gate against a fresh database and verify `alembic upgrade head`, health, readiness, and the full policy lifecycle.
2. Confirm the Render service owner, database, CORS/trusted-host values, and public synthetic-sandbox intent before publishing a new release.
3. Replace the remaining non-core generic JSON payload rows with normalized relational records and domain transaction boundaries for a true pilot; the fourteen flagship policy-review collections are now typed and foreign-key constrained, while the serialized store remains a compatibility mirror.
4. Provision and verify hosted object-storage durability, fresh ClamAV signatures/quarantine, and OCR runtime operation before accepting real government documents.
5. Complete formal keyboard/screen-reader/contrast testing with assistive technology; local semantic regression and reduced-motion rules pass, but screenshots and automated checks do not establish WCAG certification.
6. Review owner/legal approval for licensing and credential policy; no license is intentionally published.
7. Verify same-origin HTTPS cookie playback and session renewal in the hosted environment; container defaults now enable cookie mode, while local/demo overrides remain explicit.

## Honest public boundary

NiyamGuard is a synthetic sandbox. It does not verify government identity, Gazette, MeeSeva, DigiLocker, eSign, payment, messaging, or production model integrations. Demo users and synthetic mutation routes are available only when an operator explicitly enables demo mode. No pilot or government-production claim should be published from this state.

## Evidence

- Product Design audit: [`docs/design-audit/NIYAMGUARD_PRODUCT_DESIGN_AUDIT.md`](design-audit/NIYAMGUARD_PRODUCT_DESIGN_AUDIT.md)
- Ground-truth baseline and current deltas: [`docs/NIYAMGUARD_GROUND_TRUTH.md`](NIYAMGUARD_GROUND_TRUTH.md)
- Test report: [`docs/TEST_REPORT.md`](TEST_REPORT.md)
