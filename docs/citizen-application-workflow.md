# Citizen Application Workflow

The citizen workflow is a synthetic NiyamGuard demo. It helps judges see a complete service journey while keeping real government submission out of scope.

## Steps

1. Browse `/services`.
2. Open a service detail page.
3. Start `/apply/:serviceId`.
4. Fill the seeded form fields.
5. Create a draft application.
6. Upload required evidence files.
7. Submit the application.
8. Complete sandbox payment when a fee is configured.
9. Track status from `/applications`, `/applications/:applicationId`, or `/track`.
10. Download or verify a certificate after officer approval.

## Application Number

Application numbers use:

```text
NGSP-YYYY-SERVICECODE-000001
```

Example:

```text
NGSP-2026-INC-000001
```

## File Rules

Accepted upload types:

- PDF
- JPG
- JPEG
- PNG

Maximum size:

```text
5 MB
```

The backend validates file extension, MIME type, and size before writing to local storage.

## Missing Data Behavior

If an application, service, certificate, or tracking number is not in the available demo dataset, the API returns a clear not-found response instead of inventing data.
