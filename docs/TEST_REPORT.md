# Test report

Audited on 2026-07-17 from the `portfolio-polish` branch on Windows.

| Command | Result | Evidence / notes |
|---|---|---|
| `backend/.venv/Scripts/python -m pytest -q` | Pass | 226 tests passed; 2 Starlette/FastAPI deprecation warnings |
| `npm test` in `frontend` | Pass | 60 tests passed across 3 files |
| `npm run build` in `frontend` | Pass | Vite production bundle generated |

External identity, payment, government, messaging, and Ollama services were not treated as verified production integrations. The automated tests use local, mocked, sandboxed, or synthetic boundaries.
