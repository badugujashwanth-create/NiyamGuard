# What NiyamGuard Does Now

NiyamGuard has two main portals, but all major features are still available.

## Citizen Portal

- Main voice assistant.
- Text assistant fallback when voice is unavailable.
- Browse services.
- Apply for Income Certificate.
- My Applications.
- Track Application.
- Verify Certificate.
- Source-backed Citizen Q&A.

The visible voice fallback message is:

```text
Voice input is not available in this browser. You can continue using text.
```

## Government Portal

- Circular updates.
- Self-updating policy engine.
- Compliance drift.
- Connected system propagation.
- Virtual government sandbox.
- Officer review.
- Certificate authority and public verification.
- Audit trail.
- Reports.
- Readiness and ops.
- Ollama/local AI explanation.

## Full Demo Flow

The Government Portal button `Run Full End-to-End Demo` calls `POST /api/demo/run-full-end-to-end` and runs:

1. Publish circular.
2. Ingest circular.
3. Extract/update verified rule.
4. Update service portal.
5. Create citizen identity.
6. Submit application.
7. Verify OTP.
8. Complete payment.
9. Officer approval.
10. Generate certificate.
11. Sign certificate.
12. Verify certificate.
13. Patch connected systems.
14. Rerun compliance.
15. Write audit trail.
16. Ask hybrid answer engine.
17. Generate Ollama explanation or deterministic fallback.

The API returns direct identifiers:

- `circular_number`
- `application_number`
- `certificate_number`
- `verification_hash`
- `verified_rule`
- `audit_event_count`

## What Is Real In The Project

- FastAPI backend.
- React frontend.
- Local Ollama call when Ollama is running.
- Deterministic verified rule engine.
- Automated backend, frontend, smoke, and browser tests.

## What Is Sandbox/Mock

- Government circular feed.
- Citizen identity.
- OTP.
- Payment.
- Officer review.
- Certificate signing.
- Connected systems.
- Compliance data.

## First Screen

Open:

```text
http://127.0.0.1:5180
```
