# Policy Publication Workflow

Policy publication is intentionally review-first:

1. Sync or upload a circular.
2. Extract candidates.
3. Review the candidate and delta.
4. Approve or reject.
5. Publish approved candidates.

Publishing is idempotent per candidate. Re-running publication for the same candidate returns the existing publication instead of creating duplicate rule versions.

Published rule versions are stored in `verified_policy_rule_versions`. Rollback is available when an older version exists and `POLICY_ROLLBACK_ENABLED=true`.
