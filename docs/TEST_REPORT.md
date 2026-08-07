# Test report

Release audit refreshed on 2026-08-07 from the canonical `main` branch on Windows. The service-portal 422 failure was fixed, demo seeding is now opt-in, and the operational/dataset mutation boundaries are authenticated.

| Command | Result | Evidence / notes |
|---|---|---|
| `$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD="1"; python -m pytest backend/app/tests -q` | Pass | 250 collected tests execute successfully; the host's injected optional pytest plugins are excluded from this clean-environment gate. |
| Focused backend correctness/security suites | Pass | Service portal, auth/RBAC, readiness, dataset, speech, audit, and runtime-boundary tests pass. |
| `npm test` in `frontend` | Pass | 60 tests passed across 3 files |
| `npm run build` in `frontend` | Pass | Vite production bundle generated |
| Playwright product walkthrough | Pass | Real browser simulation completed and recorded end to end |
| Demo media acceptance | Pass | 337.408 seconds, 1280×720, VP9 video, Opus audio, captions present, 11 reviewed frames |
| Full-stack Docker image | Pass | React SPA and live API served on one origin; deep route 200; missing API 404 |
| Render Blueprint schema | Pass | Validated against the current official Render schema |
| `npm audit --omit=dev` | Pass | 0 production dependency vulnerabilities |
| installed backend `pip-audit` | Pass | No known vulnerabilities after the Edge TTS migration |
| Gitleaks current tree and history | Pass | No leaks detected in the audited Git scope |

External identity, payment, government, messaging, and Ollama services were not treated as verified production integrations. The automated tests use local, mocked, sandboxed, or synthetic boundaries.

The release-candidate video SHA-256 is `859c36d0571f9b18ec32edf2520d500617ef5f595bdeeec7c460edd052f3aff2`. Its 13,708,739-byte size and hash were rechecked against [verification.json](demo/verification/verification.json).

The existing walkthrough predates this refresh and is not used as evidence for the current test count. A replacement recording is not required for this code-only verification; the media remains synthetic and the current branch/test boundary is documented above.
