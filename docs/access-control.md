# Access Control

The service portal uses the same JWT and RBAC stack as the rest of NiyamGuard.

## Demo Accounts

```text
admin@niyamguard.local / Admin@12345 / admin
reviewer@niyamguard.local / Reviewer@12345 / reviewer
officer@niyamguard.local / Officer@12345 / reviewer
viewer@niyamguard.local / Viewer@12345 / viewer
citizen@niyamguard.local / Citizen@12345 / citizen
```

## Rules

- Public users can list services, track an application by number, and verify a certificate.
- Citizens can create, update, submit, and view only their own applications.
- Citizens can view only their own uploaded document records and notifications.
- Reviewers and admins can view officer queues and make review decisions.
- Viewers cannot access citizen-owned applications unless granted a reviewer/admin role.
- Admin pages remain protected by the existing admin portal authentication guard.

## Audit

Application creation, updates, document upload, submission, payment events, officer decisions, certificate issuance, comments, and revocation write audit events.
