# Cleanup Report

Generated: 2026-07-10

## Files Removed

Removed generated, safe-to-recreate local artifacts:

- `backend/.pytest_cache`
- `backend/app/**/__pycache__`
- `frontend/dist`
- `frontend/test-results`
- `frontend/playwright-report`

## Files Kept Intentionally

- `frontend/node_modules/`: required for local test/build/demo commands.
- `apps/demo-dashboard/node_modules/`: ignored by root `apps/`; not touched because it is outside the active app path.
- `niyamguard.db` and `backend/niyamguard.db`: local demo databases; kept because the running backend uses local state.
- `docs/recording-assets/e2e-step-*.png`: local E2E screenshots generated for review.
- `docs/recording-assets/final-full-e2e-demo.webm`: local browser demo video generated for review.
- Existing committed recording assets under `docs/recording-assets/`: kept because they are part of prior demo evidence.
- `NIYAMGUARD_COMPLETE_PROJECT_AUDIT.md`: kept as requested.

## `.gitignore` Changes

Added ignore coverage for:

- `.env` and secret-like env files while preserving `.env.example`
- SQLite files
- backend storage/uploads
- frontend Playwright reports/test-results
- demo recordings
- generated final E2E screenshots/video

## Warnings

- Local DB files are still present but ignored. Do not commit them.
- Generated E2E assets are local evidence and ignored. Do not force-add them unless intentionally needed.
- The repo still contains many docs. They are not junk, but presentation should use `FINAL_DEMO_RUNBOOK.md` as the source of truth.

