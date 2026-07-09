# Threat Model

## Assets

- Regulatory circulars, obligations, policies, evidence, audit logs, and user accounts.
- Local vector/search indexes derived from the dataset.
- Optional AI provider credentials.

## Main Risks

- Hallucinated official guidance: mitigated by source-backed retrieval and safe fallback.
- Unauthorized policy changes: mitigated by RBAC and audit logging.
- Prompt injection through dataset text: mitigated by system prompts requiring dataset-only answers.
- PII exposure in retrieval: mitigated by redaction before indexing and limited demo data.
- Backup misuse: mitigated by explicit restore command and restricted filesystem access in deployment.

## Production Follow-Up

- Add external secrets manager.
- Add signed audit log export.
- Add real MFA provider and device binding.
- Add automated SAST/DAST gates in CI.
