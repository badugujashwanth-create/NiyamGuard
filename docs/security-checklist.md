# Security Checklist

- Use HTTPS and trusted host allowlists outside local demos.
- Keep `SECRET_KEY` unique per environment.
- Keep paid provider keys optional and out of source control.
- Require admin/reviewer roles for policy updates, RAG reindex, and readiness details.
- Preserve audit logs for login, policy, user, and compliance actions.
- Replace sandbox OTP with a government-approved SMS/email provider before production.
- Run dependency, container, and secret scans before deployment.
- Keep database backups encrypted and access-controlled.
