# Security

## Authentication And RBAC

Admin users authenticate through `/api/auth/login`. The backend returns a short-lived JWT access token and a refresh token. Roles are:

- `admin`: full access, user management, audit, settings.
- `reviewer`: compliance runs, conflict resolution, report export, rule review.
- `viewer`: read dashboards, findings, reports, and audit.
- `citizen`: public citizen APIs only.

## Protections

- bcrypt password hashing for new hashes.
- PBKDF2 verification retained for older local demo hashes.
- JWT validation for protected routes.
- Request ID middleware and `X-Request-ID` response header.
- Security headers: `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`.
- CORS and trusted hosts loaded from environment.
- Rate limiting for sensitive endpoints.
- Standard JSON error shape with readable messages and request IDs.
- Audit logging with previous/current hash values.

## Production Notes

Use a real `SECRET_KEY`, HTTPS termination, restricted CORS, managed PostgreSQL, centralized logs, a secrets manager, and an external security review before official deployment.
