# Certificate Generation

Certificate generation is synthetic and local to NiyamGuard. It is suitable for hackathon demos and automated tests only.

## Numbering

Certificate numbers use:

```text
NGCERT-YYYY-SERVICECODE-000001
```

## Verification

Each certificate gets a SHA-256 verification hash and QR-style value:

```text
NGSP_VERIFY:{verification_hash}
```

Public verification endpoints:

- `GET /api/certificates/verify/{query}`
- `GET /api/verify-certificate/{query}`

The query can be a certificate number or verification hash.

## Income Certificate Rule Binding

Income Certificate expiry is bound to the latest verified policy rule version for:

```text
service_id=income_certificate
rule_key=validity
```

In the demo seed, GO-138 sets the current value to `6 months`, so generated income certificates expire six months after issue.

## Output File

The generated demo certificate is saved under:

```text
backend/app/storage/certificates/
```

Download endpoint:

```text
GET /api/certificates/{certificate_id}/download
```
