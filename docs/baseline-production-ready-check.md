# Baseline Production-Ready Check

## Branch and Commit

- Requested baseline branch: `codex/language-matched-replies`
- Working hardening branch: `codex/production-ready-pro-version`
- Baseline commit: `3e42c21 Add final demo dashboard and presentation polish`
- Note: local `main` had one newer unrelated commit. The production-ready work was based on the requested MVP commit instead.

## Baseline Test Results Before Changes

- Backend: `pytest` reported `139 passed, 1 failed`.
- Existing backend failure: `test_catalog_only_suggestion_says_coming_soon` failed on Windows with `PermissionError` while replacing `backend/app/storage/sessions.tmp` with `sessions.json`.
- Frontend: `npm test` reported `34 passed`.
- Frontend build: `npm run build` passed.

## Currently Working MVP Features at Baseline

- `/demo` presentation dashboard
- `/admin`, `/admin/compliance`, `/admin/conflicts`, `/admin/reports`
- Citizen voice/form assistant
- Telugu/Hindi/English guidance
- Service catalog and dynamic forms
- Verified source card
- Public verified-rule API
- Verified policy rules and GO-138 seeded rule
- Connected systems registry
- Compliance drift detection
- Cascade tracing
- Priority scoring
- Conflict detection
- Reports/export

## Baseline API Checks

- `/api/integration/health`
- `/api/dashboard/summary`
- `/api/compliance/run`
- `/api/compliance/findings`
- `/api/public/rules/latest?service_id=income_certificate&rule_key=validity`
- `/api/reports/export?type=compliance&format=csv`

These existed before hardening. Some are now protected by auth according to production RBAC rules, with demo-safe public endpoints added where needed.
