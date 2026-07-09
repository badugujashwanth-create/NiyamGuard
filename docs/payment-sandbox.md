# Payment Sandbox

NiyamGuard does not connect to a real payment gateway. Fee payment is a deterministic sandbox workflow for demos.

## Routes

- `POST /api/payments/{application_id}/create`
- `POST /api/payments/{payment_id}/simulate-success`
- `POST /api/payments/{payment_id}/simulate-failure`
- `GET /api/payments/{application_id}`

Frontend:

- `/payment/:applicationId`

## Behavior

If a service has `fee_amount > 0`, submission moves the application to:

```text
payment_pending
```

After `simulate-success`, the payment is marked `paid` and the application moves to:

```text
under_review
```

No real money, card details, UPI handles, bank credentials, OTPs, or gateway callbacks are used.
