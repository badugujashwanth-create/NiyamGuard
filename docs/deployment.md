# NiyamGuard deployment

The repository includes a same-origin full-stack container and a Render Blueprint. The hosted shape is one public FastAPI service that also serves the compiled React application, plus a private Render Postgres database. This avoids a frontend that points back to localhost and keeps database credentials off the public network.

## Local development

```powershell
cd backend
pip install -r requirements.txt
python -m app.seed_demo
uvicorn app.main:app --reload --port 8000

cd ../frontend
npm install
npm run dev
```

## Docker Compose

```powershell
docker compose up --build
docker compose exec backend python -m app.seed_demo
```

Compose provides PostgreSQL 16, FastAPI on port `8000`, and the Vite preview on port `5173`.

## One-click provisioning

[Provision NiyamGuard on Render](https://render.com/deploy?repo=https%3A%2F%2Fgithub.com%2Fbadugujashwanth-create%2FNiyamGuard)

Render authentication and confirmation of the free resources are required in the provider dashboard. The Blueprint generates `SECRET_KEY`, reads `DATABASE_URL` from the private database, seeds only synthetic data, disables external AI and server-side TTS, and binds the app to Render's runtime port.

## Local container verification

```powershell
docker build -f Dockerfile.fullstack -t niyamguard:local .
docker run --rm -p 8000:8000 `
  -e APP_ENV=staging `
  -e DEBUG=false `
  -e DEMO_MODE=true `
  -e SECRET_KEY=a-local-container-secret-with-32-characters `
  -e DATABASE_URL=sqlite:///./niyamguard.db `
  -e SEED_DEMO_ON_STARTUP=true `
  niyamguard:local
```

Open `http://127.0.0.1:8000`. The compiled frontend and `/api/*` requests share one origin. The provider health check uses `/api/integration/health`.

## Database URLs

Local SQLite uses `sqlite:///./niyamguard.db`. PostgreSQL uses the psycopg 3 form `postgresql+psycopg://user:password@host:5432/niyamguard`. Render's standard `postgresql://` connection string is normalized to that installed driver at runtime.

## Boundary

The hosted application remains a synthetic portfolio sandbox. Do not configure real identity, payment, messaging, government, citizen, or signing credentials without a separately authorized integration and security review.
