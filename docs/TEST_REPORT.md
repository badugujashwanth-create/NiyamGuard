# Test report

Release audit refreshed on 2026-08-07 from the canonical `main` branch on Windows. The service-portal 422 failure was fixed, demo seeding is now opt-in, and the operational/dataset mutation boundaries are authenticated.

| Command | Result | Evidence / notes |
|---|---|---|
| `$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD="1"; python -m pytest backend/app/tests -q` | Pass | 276 collected tests execute successfully; the host's injected optional pytest plugins are excluded from this clean-environment gate. |
| Focused backend correctness/security suites | Pass | Service portal, auth/RBAC, readiness, dataset, speech, audit, and runtime-boundary tests pass. |
| Upload malware boundary | Pass | Circular and citizen service-document uploads scan before persistence and retain SHA-256/scanner provenance; synthetic mode reports an explicit skipped scan, while production configuration requires ClamAV and returns 503 when it cannot produce a trustworthy result. |
| `python -m app.evaluation.extraction_benchmark` | Pass | 20/20 frozen synthetic cases; exact candidate/evidence threshold 1.0. This is not a model-quality or legal-authority benchmark. |
| `npm test` in `frontend` | Pass | 61 tests passed across 3 files |
| `npm run build` in `frontend` | Pass | Vite production bundle generated |
| Playwright product walkthrough | Pass | Current branch landing and reviewer lifecycle were exercised locally; the checked-in walkthrough predates this code-only refresh. |
| Demo media acceptance | Pass | 337.408 seconds, 1280×720, VP9 video, Opus audio, captions present, 11 reviewed frames |
| Full-stack Docker image | Not verified | Docker daemon was unavailable in the current Windows environment; the Dockerfile runs migrations before Uvicorn and remains CI/deployment evidence only. |
| Render Blueprint schema | Pass | Validated against the current official Render schema |
| `npm audit --omit=dev` | Pass | 0 production dependency vulnerabilities |
| installed backend `pip-audit` | Pass | No known vulnerabilities after the Edge TTS migration |
| Fresh Alembic migration and normalized seed/load round trip | Pass | SQLite migrations through `20260807_0007`, readiness, typed row counts, and candidate evidence columns verified locally; PostgreSQL remains a CI/deployment gate |
| Gitleaks current tree and history | Not run locally | The Gitleaks CI job is configured; the binary was unavailable in this environment, so no local scan result is claimed. |

External identity, payment, government, messaging, and Ollama services were not treated as verified production integrations. The automated tests use local, mocked, sandboxed, or synthetic boundaries.

The release-candidate video SHA-256 is `859c36d0571f9b18ec32edf2520d500617ef5f595bdeeec7c460edd052f3aff2`. Its 13,708,739-byte size and hash were rechecked against [verification.json](demo/verification/verification.json).

The existing walkthrough predates this refresh and is not used as evidence for the current test count. A replacement recording is not required for this code-only verification; the media remains synthetic and the current branch/test boundary is documented above.
