# Final Test And Video Report

Date: 2026-07-09

## Scope

This report covers the NiyamGuard synthetic dataset, hybrid answer engine, local AI fallback, government pilot readiness, virtual government sandbox, public service portal, admin regulatory AI explorer, and final demo evidence scripts.

## Commands To Run

Backend:

```powershell
cd D:\niyam\niyamguard-call-assistant
python -m pytest backend/app/tests -q
python scripts/final_api_smoke_test.py --base-url http://127.0.0.1:8000
```

Frontend:

```powershell
cd D:\niyam\niyamguard-call-assistant\frontend
npm test -- --run
npm run build
```

Recording assets:

```powershell
cd D:\niyam\niyamguard-call-assistant
python scripts/record_demo_assets.py --frontend-url http://127.0.0.1:5173
```

## Results

| Check | Result | Notes |
| --- | --- | --- |
| Backend tests | Passed | `python -m pytest backend/app/tests -q` |
| Frontend tests | Passed | `npm test -- --run` |
| Frontend build | Passed | `npm run build` |
| API smoke test | Passed | `python scripts/final_api_smoke_test.py --base-url http://127.0.0.1:8010` |
| Recording assets | Passed | `python scripts/record_demo_assets.py --frontend-url http://127.0.0.1:5180 --backend-url http://127.0.0.1:8010` |

## Demo Flow

1. Ask `income certificate validity entha`.
2. Show GO-138 exact-rule answer with source card.
3. Run `/virtual-gov` sandbox scenario.
4. Show application number, payment, certificate number, verification hash, and audit context.
5. Open `/admin/regulatory-ai` and ask `Why is ORG-0029 high risk?`.
6. Show circular, obligation, internal policy, gap, drift, risk score, evidence, and audit trail.
7. Open `/admin/readiness` and show all controls ready.

## Recording Files

Expected folder:

```text
docs/recording-assets/
```

Use `docs/recording-assets/manual-recording-checklist.md` if Playwright video capture is not available.

Generated assets in this run:

```text
docs/recording-assets/demo-dashboard.png
docs/recording-assets/admin-readiness.png
docs/recording-assets/regulatory-ai.png
docs/recording-assets/virtual-government-sandbox.png
docs/recording-assets/service-portal.png
docs/recording-assets/videos/842694a1b1108fb259c454df4d9b41fa.webm
docs/recording-assets/videos/aa6e436c8accfd7b513a55653dea7929.webm
docs/recording-assets/manual-recording-checklist.md
```

Fresh verification servers used:

```text
Backend: http://127.0.0.1:8010
Frontend: http://127.0.0.1:5180
```
