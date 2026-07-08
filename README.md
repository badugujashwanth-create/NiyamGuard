# NiyamGuard AI

NiyamGuard AI is a government-policy compliance and citizen assistance platform. The main product repo is the Jashwanth repo at `badugujashwanth-create/NiyamGuard`; the other repos reviewed during this work were used only as references and were not merged into this codebase.

This project does not submit real government applications and does not replace official verification.

## What It Provides

- Citizen voice/form assistant with Telugu, Hindi, and English guidance.
- Service catalog, dynamic forms, document guidance, and verified source cards.
- Admin portal at `/admin` with RBAC-protected government-core pages.
- Public demo dashboard at `/demo`.
- Verified policy rule knowledge base with public safe lookup APIs.
- Compliance drift detection, cascade tracing, priority scoring, conflict detection, reports, and audit logging.
- Database-backed persistence with SQLite for local development and PostgreSQL for production.
- Docker Compose and GitHub Actions CI.

## Architecture

```text
React/Vite frontend
  -> central API client with auth token injection
  -> citizen portal, demo dashboard, login, admin portal

FastAPI backend
  -> routes -> services -> repositories
  -> SQLAlchemy database layer with JSON/demo fallback
  -> auth, RBAC, audit, security middleware, health/readiness

SQLite local / PostgreSQL production
```

## Demo Credentials

```text
admin@niyamguard.local / Admin@12345 / admin
reviewer@niyamguard.local / Reviewer@12345 / reviewer
viewer@niyamguard.local / Viewer@12345 / viewer
```

## Local Run

Backend:

```powershell
cd D:\niyam\niyamguard-call-assistant\backend
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app.seed_demo
uvicorn app.main:app --reload --port 8000
```

Frontend:

```powershell
cd D:\niyam\niyamguard-call-assistant\frontend
npm install
npm run dev
```

Open:

```text
http://127.0.0.1:5173/demo
http://127.0.0.1:5173/login
http://127.0.0.1:5173/admin
http://127.0.0.1:5173
```

## Docker Run

```powershell
cd D:\niyam\niyamguard-call-assistant
docker compose up --build
docker compose exec backend python -m app.seed_demo
```

Docker starts PostgreSQL, FastAPI on `8000`, and the Vite preview server on `5173`.

## Environment

Copy examples when needed:

```text
.env.example
backend/.env.example
frontend/.env.example
```

Important backend variables:

```text
DATABASE_URL=sqlite:///./niyamguard.db
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/niyamguard
SECRET_KEY=change-this-secret-key
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
TRUSTED_HOSTS=localhost,127.0.0.1
```

Frontend:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## Key APIs

- `POST /api/auth/login`
- `GET /api/auth/me`
- `GET /api/health`
- `GET /api/ready`
- `GET /api/integration/health`
- `GET /api/dashboard/summary`
- `POST /api/compliance/run`
- `GET /api/conflicts`
- `GET /api/reports/export?type=compliance&format=csv`
- `GET /api/public/rules/latest?service_id=income_certificate&rule_key=validity`
- `POST /api/chat`
- `GET /api/audit/events`

Version aliases are also available under `/api/v1/...`.

## Tests

```powershell
cd D:\niyam\niyamguard-call-assistant\backend
pytest

cd D:\niyam\niyamguard-call-assistant\frontend
npm test
npm run build
```

## Security Notes

- Admin/government APIs require JWT authentication and RBAC.
- Public citizen and verified-rule APIs remain open.
- Passwords use bcrypt when available, with PBKDF2 verification retained for older local demo hashes.
- Audit events include a hash chain for important actions.
- Middleware adds request IDs, security headers, trusted host checks, CORS restrictions, rate limiting, structured errors, and request logging.

## Known Limitations

- Live MeeSeva integration, official government APIs, production cloud deployment, secrets manager, and full security audit are future steps.
- Circular extraction is still demo-oriented unless a verified extraction pipeline is added.
- The app guides citizens but never submits official applications, handles OTP, CAPTCHA, payments, or official portal login.
- Demo/local knowledge is useful for presentation and testing, but official deployments need verified government data feeds and legal approval.
