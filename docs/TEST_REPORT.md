# Test report

Audited on 2026-07-18 from the `product-completion-2026` branch on Windows.

| Command | Result | Evidence / notes |
|---|---|---|
| `backend/.venv/Scripts/python -m pytest -q` | Pass | 235 tests passed; 2 known Starlette/FastAPI deprecation warnings |
| `npm test` in `frontend` | Pass | 60 tests passed across 3 files |
| `npm run build` in `frontend` | Pass | Vite production bundle generated |
| Playwright recruiter walkthrough | Pass | Real browser simulation passed in 4.9 minutes |
| Demo media acceptance | Pass | 284.888 seconds, 1280×720, VP9 video, Opus audio, captions present |
| `npm audit --omit=dev` | Pass | 0 production dependency vulnerabilities |
| installed backend `pip-audit` | Pass | No known vulnerabilities after the Edge TTS migration |
| Gitleaks current tree and history | Pass | No leaks detected in the audited Git scope |

External identity, payment, government, messaging, and Ollama services were not treated as verified production integrations. The automated tests use local, mocked, sandboxed, or synthetic boundaries.

The published video SHA-256 is `aadd422b2dbe92c07d27be29b25a33a67fa242e6daf40297385a076a5873500b`. See [verification.json](demo/verification/verification.json) for the machine-readable record.
