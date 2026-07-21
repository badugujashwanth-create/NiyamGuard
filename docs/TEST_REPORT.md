# Test report

Release audit completed on 2026-07-19 from the `pilot-readiness-2026` branch on Windows. A fresh reconciliation rerun on 2026-07-21 from `phase5-niyamguard-reconciliation` preserved the same backend/frontend results and removed the application-owned deprecated HTTP 422 constant. The remaining TestClient warning is inside the installed FastAPI/Starlette compatibility layer. Full-stack container evidence was established on the v1.0.2 deployment baseline and remains applicable to the same packaging path.

| Command | Result | Evidence / notes |
|---|---|---|
| `backend/.venv/Scripts/python -m pytest -q` | Pass | 243 tests passed; 1 dependency-owned FastAPI/Starlette TestClient deprecation warning |
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

The recorded narration cites 242 backend tests because that was the passing count at capture time. A coverage-boundary regression test was added after review, bringing the final suite to 243 without changing the demonstrated product flow.
