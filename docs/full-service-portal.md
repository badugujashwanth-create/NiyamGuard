# Full Service Portal

NiyamGuard Service Portal is a synthetic public-service workflow for demos and testing. It is not an official MeeSeva portal, does not collect real payments, and does not submit applications to any government system.

## Frontend Routes

Citizen/public routes:

- `/services`
- `/services/:serviceId`
- `/apply/:serviceId`
- `/applications`
- `/applications/:applicationId`
- `/track`
- `/verify-certificate`
- `/citizen/profile`
- `/citizen/documents`
- `/payment/:applicationId`

Officer routes:

- `/officer`
- `/officer/applications`
- `/officer/applications/:applicationId`
- `/officer/pending`
- `/officer/approved`
- `/officer/rejected`
- `/officer/escalations`

Admin routes:

- `/admin/services`
- `/admin/forms`
- `/admin/certificates`
- `/admin/users`
- `/admin/audit`
- `/admin/policy-updates`
- `/admin/propagation`

## Seeded Services

The demo store seeds ten services:

- Income Certificate
- Residence Certificate
- Caste Certificate
- EWS Certificate
- Birth Certificate
- Death Certificate
- Family Member Certificate
- Ration Card
- Old-Age Pension
- Post-Matric Scholarship

The service catalog is backed by `PolicyDataStore.service_definitions`, `service_form_definitions`, and `service_slas`.

## Backend APIs

Core service APIs:

- `GET /api/portal/services`
- `GET /api/portal/services/{service_id}`
- `POST /api/applications`
- `PATCH /api/applications/{application_id}`
- `POST /api/applications/{application_id}/documents`
- `POST /api/applications/{application_id}/submit`
- `GET /api/track/{application_number}`
- `POST /api/payments/{application_id}/create`
- `POST /api/payments/{payment_id}/simulate-success`
- `GET /api/officer/applications`
- `POST /api/officer/applications/{application_id}/approve`
- `GET /api/certificates/verify/{verification_hash}`
- `GET /api/notifications`

## Demo Flow

1. Sign in as `citizen@niyamguard.local / Citizen@12345`.
2. Open `/services` and choose Income Certificate.
3. Create a draft at `/apply/income_certificate`.
4. Upload required PDF/JPG/PNG files.
5. Submit the application.
6. Open `/payment/{application_id}` and simulate a successful payment.
7. Sign in as `officer@niyamguard.local / Officer@12345`.
8. Open `/officer/pending`, review the application, and approve it.
9. The system generates a demo certificate.
10. Verify the certificate on `/verify-certificate` and track the application on `/track`.

## Storage

Uploaded documents are stored under:

```text
backend/app/storage/documents/
```

Generated demo certificates are stored under:

```text
backend/app/storage/certificates/
```

Both folders are ignored by Git.
