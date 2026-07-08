# Admin Guide

## Login

Open `/login` and use:

```text
admin@niyamguard.local / Admin@12345
```

The admin portal shows the current email, role badge, and logout button.

## Pages

- `/admin`: dashboard, modules, priority and export shortcuts.
- `/admin/compliance`: connected-system drift findings.
- `/admin/cascade`: impact trace for a drifted finding.
- `/admin/conflicts`: circular conflicts and recommendations.
- `/admin/knowledge-base`: verified rules and module status.
- `/admin/reports`: authenticated report exports.
- `/admin/audit`: audit events and hash-chain verification status.
- `/admin/users`: admin-only user creation and user list.

## Roles

- Admin can manage users and all government operations.
- Reviewer can run compliance, resolve conflicts, and export reports.
- Viewer can read dashboards, findings, reports, and audit.
- Citizen uses public APIs only.
