# NiyamGuard productionization state

**State date:** 2026-08-07
**Canonical branch:** `main`
**Latest local change:** database-authority boundary hardening after cookie-session productionization
**Public release:** `v1.1.0` (a new release is not claimed until the changes are committed and published)
**Classification:** synthetic policy-drift MVP; production-boundary work in progress

## Implemented in this pass

- Corrected the service-portal missing-field path to return HTTP 422 and retained its regression test.
- Tightened deterministic extraction to require one explicit, evidence-backed old→new rule statement; ambiguous or unsupported circulars now return a reviewable HTTP 422.
- Added a frozen 20-case deterministic extraction benchmark covering valid, ambiguous, and unsupported wording (20/20 locally).
- Made `DEMO_MODE` and startup demo seeding opt-in; production validation still rejects demo mode, debug mode, and placeholder secrets.
- Protected operational status and dataset import/RAG-build mutations with JWT role checks.
- Gated deterministic OTP endpoints behind explicit demo mode and removed absolute filesystem paths from ops status.
- Added STT upload size/format/MIME bounds and guaranteed temporary-file cleanup.
- Added a ClamAV upload-scanning boundary: local synthetic mode is explicit, while production requires ClamAV and fails closed on scanner unavailability or indeterminate results.
- Added TTS text limits, rate limiting, and bounded cache eviction.
- Added JWT issuer/audience checks and atomic refresh-token rotation.
- Added opt-in same-origin HttpOnly access/refresh cookies; production validation requires cookie mode with secure cookies, while bearer/localStorage remains a local-demo fallback.
- Serialized audit appends and made chain verification ordering deterministic; PostgreSQL workers also take a transaction-scoped advisory lock.
- Added Alembic execution to both container entrypoints and switched containers to a non-root runtime user.
- Made migration ownership explicit: deployed containers set `AUTO_CREATE_TABLES=false`, while local/test environments may opt into the compatibility fallback.
- Disabled legacy JSON-store fallback for non-demo deployments; production state now comes only from the configured database and returns an empty store when no authoritative records exist.
- Tightened `/api/ready` so a database is not considered ready until the migrated users, refresh-token, audit, and policy-record tables are present.
- Made containerized production frontends default to HttpOnly-cookie mode; local Docker Compose explicitly opts into bearer mode for the synthetic HTTP demo.
- Updated every protected frontend route guard to recognize the non-sensitive stored user record when cookie mode is enabled; cookie-authenticated admin and citizen workflows no longer redirect to login because tokens are intentionally invisible to JavaScript.
- Added production fail-closed checks for credentialed wildcard CORS and wildcard/empty trusted-host settings.
- Refocused the landing screen on the GO-138 policy-drift incident, source evidence, impact chain, and reviewer/citizen workflow choices.
- Added visible focus treatment and reduced-motion handling; captured desktop/mobile Product Design evidence.

## Verification

| Check | Result |
|---|---|
| Focused backend correctness/security suites | Pass (service portal, auth/RBAC, readiness, dataset, speech, audit, and runtime boundaries) |
| Full backend suite | Pass: 268 tests execute successfully with third-party pytest plugin autoload disabled |
| Deterministic extraction benchmark | Pass: 20/20 frozen synthetic cases |
| Frontend tests | Pass: 60 tests |
| Frontend production build | Pass: Vite build |
| `npm audit --omit=dev` | Pass: 0 vulnerabilities |
| `pip-audit -r backend/requirements.txt` | Pass: no known vulnerabilities |
| `git diff --check` / Python compile | Pass |
| Product Design capture | Pass: landing and reviewer workflow captured at desktop and 390px mobile; no horizontal overflow |
| Docker image build | Not verified: Docker daemon unavailable in the current environment |
| Hosted Render deployment | Not verified: previous public hostname returned 404 |
| PostgreSQL migration CI gate | Configured: fresh PostgreSQL service runs Alembic, readiness, and production-style app import in GitHub Actions; not executed locally |

## Remaining blockers

1. Execute the PostgreSQL CI/deployment gate against a fresh database and verify `alembic upgrade head`, health, readiness, and the full policy lifecycle.
2. Confirm the Render service owner, database, CORS/trusted-host values, and public synthetic-sandbox intent before publishing a new release.
3. Replace the remaining generic JSON payload rows with normalized relational records and foreign-key/optimistic-lock constraints for a true pilot; the legacy file fallback is now disabled outside local/demo mode.
4. Provision and verify ClamAV signatures/quarantine plus robust PDF/OCR processing before accepting real government documents.
5. Complete keyboard/screen-reader/contrast/reduced-motion testing with assistive technology; screenshots alone do not establish WCAG conformance.
6. Review owner/legal approval for licensing and credential policy; no license is intentionally published.
7. Verify same-origin HTTPS cookie playback and session renewal in the hosted environment; container defaults now enable cookie mode, while local/demo overrides remain explicit.

## Honest public boundary

NiyamGuard is a synthetic sandbox. It does not verify government identity, Gazette, MeeSeva, DigiLocker, eSign, payment, messaging, or production model integrations. Demo users and synthetic mutation routes are available only when an operator explicitly enables demo mode. No pilot or government-production claim should be published from this state.

## Evidence

- Product Design audit: [`docs/design-audit/NIYAMGUARD_PRODUCT_DESIGN_AUDIT.md`](design-audit/NIYAMGUARD_PRODUCT_DESIGN_AUDIT.md)
- Ground-truth baseline and current deltas: [`docs/NIYAMGUARD_GROUND_TRUTH.md`](NIYAMGUARD_GROUND_TRUTH.md)
- Test report: [`docs/TEST_REPORT.md`](TEST_REPORT.md)
