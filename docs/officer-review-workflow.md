# Officer Review Workflow

Officer review is available to authenticated `reviewer` and `admin` roles. The demo officer account uses the existing reviewer role:

```text
officer@niyamguard.local / Officer@12345
```

## Queues

Frontend:

- `/officer`
- `/officer/pending`
- `/officer/approved`
- `/officer/rejected`
- `/officer/escalations`

Backend:

- `GET /api/officer/applications`
- `GET /api/officer/pending`
- `GET /api/officer/approved`
- `GET /api/officer/rejected`
- `GET /api/officer/escalations`

## Decisions

Officers can:

- assign an application
- request additional documents
- approve and issue a certificate
- reject with a reason
- add comments

Every decision writes application history, notification records, and audit events.

## SLA

Each seeded service has a processing SLA. Application SLA status is computed as:

- `not_started`
- `within_sla`
- `due_soon`
- `overdue`
- `completed`

The officer escalation route surfaces due-soon and overdue records.
