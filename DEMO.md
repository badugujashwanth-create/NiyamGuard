# NiyamGuard AI Demo

This is the acceptance demo for the two-portal NiyamGuard AI prototype.

## Start The App

Backend:

```bash
cd backend
python -m app.seed_demo
uvicorn app.main:app --reload --port 8010
```

Frontend:

```bash
cd frontend
npm run dev -- --host 127.0.0.1 --port 5180
```

Open:

```text
http://127.0.0.1:5180
```

## Demo Credentials

```text
admin@niyamguard.local / Admin@12345
reviewer@niyamguard.local / Reviewer@12345
officer@niyamguard.local / Officer@12345
citizen@niyamguard.local / Citizen@12345
```

## Seven-Step Acceptance Flow

### 1. Admin uploads or publishes GO-138

Open:

```text
http://127.0.0.1:5180/government
```

Click `Run Full End-to-End Demo` or open:

```text
http://127.0.0.1:5180/admin/policy-updates
```

The seeded scenario represents GO-138 changing Income Certificate validity from `12 months` to `6 months`.

### 2. System extracts the change

Open:

```text
http://127.0.0.1:5180/admin/rule-candidates
```

Expected:

- Service: Income Certificate.
- Old value: `12`.
- New value: `6`.
- Unit: `months`.
- Confidence score is visible.
- Status starts as pending review before approval.

### 3. Officer reviews and approves

Use:

```text
reviewer@niyamguard.local / Reviewer@12345
```

Approve the extracted rule from the rule candidate/policy update flow. The app must not silently auto-publish an extracted rule without this review step.

### 4. Compliance flags connected systems

Open:

```text
http://127.0.0.1:5180/admin/compliance
```

Expected:

- Mock MeeSeva portal, SOP, FAQ, or form entries that still show `12 months` are flagged.
- Findings point back to GO-138.
- Cascade/impact tracing is available.
- Priority dashboard explains citizen impact.

### 5. Citizen assistant answers from GO-138

Open:

```text
http://127.0.0.1:5180/citizen
```

Ask:

```text
income certificate validity entha
```

Expected:

- Answer says `6 months`.
- Source/citation shows GO-138.
- If the answer is not covered by verified data, the assistant should say it is not covered instead of guessing.

### 6. Citizen uses guided voice/form assistant

Open:

```text
http://127.0.0.1:5180/citizen
```

Use `Apply for Certificates with Voice Assistant`, or open:

```text
http://127.0.0.1:5180/citizen/assistant
```

Expected:

- Main voice assistant is visible.
- Text fallback is always available.
- The friendly fallback message is used when voice input is unavailable:

```text
Voice input is not available in this browser. You can continue using text.
```

### 7. Audit trail shows the chain

Open:

```text
http://127.0.0.1:5180/admin/audit
```

Expected audit chain:

- Circular uploaded/published.
- Rule extracted.
- Rule approved.
- Rule published/verified.
- Compliance check run.
- Citizen answer generated.
- Application/certificate events generated during the full demo.

## One-Click Backend Demo API

With the backend running:

```bash
curl -X POST http://127.0.0.1:8010/api/demo/run-full-end-to-end
```

Expected top-level fields:

```text
success
steps
circular_number
application_number
certificate_number
verification_hash
verified_rule
audit_event_count
```

## Verify Certificate

Open:

```text
http://127.0.0.1:5180/verify-certificate
```

Paste the generated certificate number or verification hash.

## Run Verification

```bash
python -m pytest backend/app/tests -q

cd frontend
npm test -- --run
npm run build
npx playwright test tests/e2e/final-full-feature-portal.spec.ts --headed
```

From the repo root, with the backend running:

```bash
python scripts/final_api_smoke_test.py --base-url http://127.0.0.1:8010
```
