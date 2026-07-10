# Final Demo Runbook

First screen:

```text
http://127.0.0.1:5180
```

Current live backend:

```text
http://127.0.0.1:8010
```

## 1. Optional Ollama Setup

```powershell
ollama serve
ollama pull qwen2.5:7b-instruct
```

If Ollama is unavailable, the app still works with deterministic fallback.

## 2. Start Backend

```powershell
cd D:\niyam\niyamguard-call-assistant\backend
$env:AI_ENABLED="true"
$env:AI_PROVIDER="ollama"
$env:OLLAMA_BASE_URL="http://127.0.0.1:11434"
$env:OLLAMA_MODEL="qwen2.5:7b-instruct"
python -m app.seed_demo
uvicorn app.main:app --host 127.0.0.1 --port 8010
```

## 3. Start Frontend

```powershell
cd D:\niyam\niyamguard-call-assistant\frontend
npm run dev -- --host 127.0.0.1 --port 5180
```

## 4. Demo Accounts

```text
admin@niyamguard.local / Admin@12345
reviewer@niyamguard.local / Reviewer@12345
officer@niyamguard.local / Officer@12345
citizen@niyamguard.local / Citizen@12345
```

The officer account now uses the separate role `officer`.

## 5. Citizen Portal

Open:

```text
http://127.0.0.1:5180/citizen
```

Show:

- Apply for Certificates with Voice Assistant.
- Text Assistant Fallback.
- Browse Services.
- Apply Income Certificate.
- My Applications.
- Track Application.
- Verify Certificate.
- Source-backed Citizen Q&A.

Ask:

```text
income certificate validity entha
```

Expected: source-backed GO-138 answer showing 6 months.

## 6. Government Portal

Open:

```text
http://127.0.0.1:5180/government
```

Show:

- Circulars & Policy Updates.
- Self-Updating Policy Engine.
- Compliance Drift.
- Connected Systems / Propagation.
- Virtual Government Sandbox.
- Officer Review.
- Certificates.
- Audit Trail.
- Reports.
- Hybrid Answer Engine / Ollama.
- Readiness & Ops.

Click:

```text
Run Full End-to-End Demo
```

Expected:

- Steps show Success or clear Fallback.
- Application number starts with `NGSP-`.
- Certificate number starts with `NGCERT-`.
- Verification hash is generated.
- Ollama status is Online or deterministic fallback is clear.

## 7. Verify Certificate

Open:

```text
http://127.0.0.1:5180/verify-certificate
```

Paste the generated certificate number or verification hash from Government Portal.

## 8. Useful Government Detail Routes

```text
http://127.0.0.1:5180/admin/compliance
http://127.0.0.1:5180/admin/policy-updates
http://127.0.0.1:5180/admin/propagation
http://127.0.0.1:5180/admin/audit
http://127.0.0.1:5180/admin/reports
http://127.0.0.1:5180/admin/readiness
http://127.0.0.1:5180/admin/regulatory-ai
http://127.0.0.1:5180/virtual-gov
http://127.0.0.1:5180/officer
```

## 9. Tests

Backend:

```powershell
cd D:\niyam\niyamguard-call-assistant
python -m pytest backend/app/tests -q
```

Frontend:

```powershell
cd D:\niyam\niyamguard-call-assistant\frontend
npm test -- --run
npm run build
```

Smoke:

```powershell
cd D:\niyam\niyamguard-call-assistant
python scripts/final_api_smoke_test.py --base-url http://127.0.0.1:8010
```

Browser E2E:

```powershell
cd D:\niyam\niyamguard-call-assistant\frontend
npx playwright test tests/e2e/final-full-feature-portal.spec.ts --headed
```
