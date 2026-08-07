# NiyamGuard productionization state

**State date:** 2026-08-07
**Canonical branch:** `main`
**Latest local change:** production boundary hardening and evidence-led landing update
**Public release:** `v1.1.0` (a new release is not claimed until the changes are committed and published)
**Classification:** synthetic policy-drift MVP; production-boundary work in progress

## Implemented in this pass

- Corrected the service-portal missing-field path to return HTTP 422 and retained its regression test.
- Made `DEMO_MODE` and startup demo seeding opt-in; production validation still rejects demo mode, debug mode, and placeholder secrets.
- Protected operational status and dataset import/RAG-build mutations with JWT role checks.
- Gated deterministic OTP endpoints behind explicit demo mode and removed absolute filesystem paths from ops status.
- Added STT upload size/format/MIME bounds and guaranteed temporary-file cleanup.
- Added TTS text limits, rate limiting, and bounded cache eviction.
- Added JWT issuer/audience checks and atomic refresh-token rotation.
- Serialized in-process audit appends and made chain verification ordering deterministic.
- Added Alembic execution to both container entrypoints and switched containers to a non-root runtime user.
- Refocused the landing screen on the GO-138 policy-drift incident, source evidence, impact chain, and reviewer/citizen workflow choices.
- Added visible focus treatment and reduced-motion handling; captured desktop/mobile Product Design evidence.

## Verification

| Check | Result |
|---|---|
| Focused backend correctness/security suites | Pass (service portal, auth/RBAC, readiness, dataset, speech, audit, and runtime boundaries) |
| Full backend suite | Pass: 250 tests execute successfully with third-party pytest plugin autoload disabled |
| Frontend tests | Pass: 60 tests |
| Frontend production build | Pass: Vite build |
| `npm audit --omit=dev` | Pass: 0 vulnerabilities |
| `pip-audit -r backend/requirements.txt` | Pass: no known vulnerabilities |
| `git diff --check` / Python compile | Pass |
| Product Design capture | Pass: landing and reviewer workflow captured at desktop and 390px mobile; no horizontal overflow |
| Docker image build | Not verified: Docker daemon unavailable in the current environment |
| Hosted Render deployment | Not verified: previous public hostname returned 404 |

## Remaining blockers

1. Run the updated containers against a fresh PostgreSQL database and verify `alembic upgrade head`, health, readiness, and the full policy lifecycle.
2. Confirm the Render service owner, database, CORS/trusted-host values, and public synthetic-sandbox intent before publishing a new release.
3. Add a database-backed audit append lock/sequence before any multi-worker pilot deployment; the current lock protects one application process.
4. Replace generic JSON policy storage with normalized relational records and foreign-key/optimistic-lock constraints for a true pilot.
5. Add quarantine/malware scanning and robust PDF/OCR processing before accepting real government documents.
6. Complete keyboard/screen-reader/contrast/reduced-motion testing with assistive technology; screenshots alone do not establish WCAG conformance.
7. Review owner/legal approval for licensing and credential policy; no license is intentionally published.

## Honest public boundary

NiyamGuard is a synthetic sandbox. It does not verify government identity, Gazette, MeeSeva, DigiLocker, eSign, payment, messaging, or production model integrations. Demo users and synthetic mutation routes are available only when an operator explicitly enables demo mode. No pilot or government-production claim should be published from this state.

## Evidence

- Product Design audit: [`docs/design-audit/NIYAMGUARD_PRODUCT_DESIGN_AUDIT.md`](design-audit/NIYAMGUARD_PRODUCT_DESIGN_AUDIT.md)
- Ground-truth baseline and current deltas: [`docs/NIYAMGUARD_GROUND_TRUTH.md`](NIYAMGUARD_GROUND_TRUTH.md)
- Test report: [`docs/TEST_REPORT.md`](TEST_REPORT.md)
