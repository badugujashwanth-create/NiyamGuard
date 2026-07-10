# Code Structure Final Report

## Frontend

- `frontend/src/components/UnifiedLanding.jsx` owns the first screen with only `Citizen Portal` and `Government Portal`.
- `frontend/src/components/CitizenPortal.jsx` owns citizen-facing links and the source-backed assistant demo.
- `frontend/src/components/GovernmentPortal.jsx` is the route-level government portal wrapper.
- `frontend/src/components/UnifiedDemoPortal.jsx` remains the government full-demo experience and calls the full-demo APIs.
- `frontend/src/services/speechService.js` keeps browser speech support detection and friendly fallback messaging separate from UI.
- `frontend/src/api/demoApi.js` keeps demo API calls separate from general API modules.
- `frontend/tests/e2e/final-two-portal-demo.spec.ts` covers the final two-portal browser path.

## Backend

- Routes remain separated by domain under `backend/app/routes`.
- Services remain separated under `backend/app/services`.
- `backend/app/services/full_demo_service.py` orchestrates the full demo but calls existing domain services instead of merging them.
- Models remain separated under `backend/app/models`, including auth, service portal, self-update, compliance, virtual government, and audit models.
- AI provider selection remains in `backend/app/services/ai/provider_factory.py`.

## Why This Structure Is Removable

- Citizen UI can be removed by deleting `CitizenPortal.jsx` and the `/citizen` route without touching backend policy/compliance services.
- Government UI can be removed by deleting `GovernmentPortal.jsx` and `UnifiedDemoPortal.jsx` route usage without deleting backend APIs.
- Full-demo orchestration is isolated in `full_demo_service.py`; individual modules still live in their own route/service/model files.
- Browser speech support is isolated in `speechService.js` and hooks, so text assistant behavior remains independent.
