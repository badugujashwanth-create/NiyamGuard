# OWASP API Mapping

| OWASP API Risk | Current Mitigation |
| --- | --- |
| Broken Object Level Authorization | JWT roles and route dependencies on admin/reviewer endpoints. |
| Broken Authentication | Password hashing, refresh tokens, rate limiting, sandbox OTP endpoint for pilot flows. |
| Broken Object Property Authorization | Pydantic schemas constrain request bodies on public routes. |
| Unrestricted Resource Consumption | Rate limiting and local-only AI fallback controls. |
| Broken Function Level Authorization | Admin readiness and reindex routes require privileged roles. |
| Server Side Request Forgery | AI providers use fixed endpoints from configuration. |
| Security Misconfiguration | Trusted host, CORS, and security headers middleware. |
| Improper Inventory Management | `/api/ops/status` and `/api/admin/readiness` expose environment/module status. |
| Unsafe Consumption of APIs | Deterministic fallback prevents demo dependence on external AI availability. |
