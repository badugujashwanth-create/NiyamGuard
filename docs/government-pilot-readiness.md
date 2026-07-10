# Government Pilot Readiness Matrix

NiyamGuard is demo-ready for a controlled government pilot when all controls below are green in `/api/admin/readiness`.

| Control | Status Source | Evidence |
| --- | --- | --- |
| Verified answers | `/api/hybrid/answer` | Exact rules, decision tables, RAG, and safe fallback. |
| Dataset grounding | `/api/dataset/status` | Synthetic regulatory pack imported and indexed. |
| No paid AI dependency | `/api/ai/status` | Ollama optional, deterministic fallback always available. |
| RBAC | `/api/auth/login`, admin routes | Admin, reviewer, viewer, citizen roles. |
| Audit trail | `/api/dataset/audit`, `/api/admin/recent-activity` | User/system events retained for review. |
| MFA sandbox | `/api/security/otp/request` | Deterministic OTP for demo only. |
| PII handling | RAG cleaner | Sensitive identifiers redacted before index creation. |
| Backup/restore | `scripts/backup_restore.py` | Timestamped SQLite backup and explicit restore. |

## Pilot Go/No-Go

Run:

```bash
python -m pytest backend/app/tests/test_hybrid_intelligence.py backend/app/tests/test_readiness.py -q
python scripts/backup_restore.py backup
```

Then verify:

```bash
curl http://127.0.0.1:8000/api/ops/status
curl -H "Authorization: Bearer <admin-token>" http://127.0.0.1:8000/api/admin/readiness
```
