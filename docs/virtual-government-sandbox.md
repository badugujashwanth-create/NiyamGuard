# Virtual Government Sandbox

The sandbox is a synthetic end-to-end government service environment for demos and UAT.

## API Flow

List scenarios:

```bash
curl http://127.0.0.1:8000/api/virtual-gov/scenarios
```

Run the main scenario:

```bash
curl -X POST http://127.0.0.1:8000/api/virtual-gov/run \
  -H "Content-Type: application/json" \
  -d '{"scenario_id":"income_certificate_full_flow","reset_before_run":true}'
```

The scenario:

1. Answers an income certificate validity question from GO-138.
2. Creates a synthetic citizen application.
3. Attaches synthetic evidence metadata.
4. Submits the application.
5. Completes sandbox payment.
6. Approves officer review.
7. Issues and verifies a demo certificate.
8. Retrieves dataset gap, drift, risk, evidence, and audit context.

## Important Limits

- No real application is submitted to a government system.
- No real payment is processed.
- No real SMS/email OTP is sent.
- Generated certificates are synthetic demo artifacts.
