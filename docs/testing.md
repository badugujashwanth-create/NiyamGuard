# Testing

## Backend

```powershell
cd backend
pytest
```

Coverage includes auth, RBAC, public API access, database seed, compliance, cascade, priority, conflicts, reports, audit logging, health/readiness, chat behavior, version aliases, and clean security errors.

## Frontend

```powershell
cd frontend
npm test
npm run build
```

Coverage includes public demo access, login, protected admin routing, admin pages, audit/users pages, report buttons, citizen portal, verified source cards, chatbot source metadata, and no raw JSON in the UI.

## Manual Smoke

1. Open `/demo`.
2. Open `/login` and sign in as `admin@niyamguard.local / Admin@12345`.
3. Open `/admin`, `/admin/compliance`, `/admin/conflicts`, `/admin/reports`, `/admin/audit`.
4. Export compliance CSV.
5. Open citizen portal and ask `income certificate validity entha`.
6. Ask `scholarship documents enti`.
7. Confirm public verified rule API works without auth.
8. Confirm protected admin APIs reject unauthenticated requests.
