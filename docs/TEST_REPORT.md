# Test report

Audited on 2026-07-18 from the `product-completion-2026` branch on Windows.

| Command | Result | Evidence / notes |
|---|---|---|
| `backend/.venv/Scripts/python -m pytest -q` | Pass | 239 tests passed; 2 known Starlette/FastAPI deprecation warnings |
| `npm test` in `frontend` | Pass | 60 tests passed across 3 files |
| `npm run build` in `frontend` | Pass | Vite production bundle generated |
| Playwright recruiter walkthrough | Pass | Real browser simulation passed in 4.9 minutes |
| Demo media acceptance | Pass | 283.648 seconds, 1280×720, VP9 video, Opus audio, captions present |
| Full-stack Docker image | Pass | React SPA and live API served on one origin; deep route 200; missing API 404 |
| Render Blueprint schema | Pass | Validated against the current official Render schema |
| `npm audit --omit=dev` | Pass | 0 production dependency vulnerabilities |
| installed backend `pip-audit` | Pass | No known vulnerabilities after the Edge TTS migration |
| Gitleaks current tree and history | Pass | No leaks detected in the audited Git scope |

External identity, payment, government, messaging, and Ollama services were not treated as verified production integrations. The automated tests use local, mocked, sandboxed, or synthetic boundaries.

The published video SHA-256 is `5802108062397c3e95d234d58832672589d1b027d908a82c680318e6e2e0c633`. See [verification.json](demo/verification/verification.json) for the machine-readable record.
