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
  -e APP_ENV=demo `
  -e DEBUG=false `
  -e DEMO_MODE=true `
  -e SECRET_KEY=a-local-container-secret-with-32-characters `
  -e DATABASE_URL=sqlite:///./niyamguard.db `
  -e SEED_DEMO_ON_STARTUP=true `
  niyamguard:local
```

Open `http://127.0.0.1:8000`. The compiled frontend and `/api/*` requests share one origin. The provider health check uses `/api/integration/health`.

## Production-shaped local stack

`docker-compose.production.yml` exercises the hardened path with PostgreSQL, an S3-compatible MinIO bucket, migrations, secure-cookie configuration, ClamAV CLI integration, and OCRmyPDF/Tesseract dependencies in the application image:

```powershell
docker compose -f docker-compose.production.yml up --build
```

This is a local integration harness, not a production deployment. It intentionally uses local-only credentials and `AUTH_COOKIE_SECURE=true`, so browser login requires an HTTPS reverse proxy; use `/api/health` for liveness and `/api/ready` for dependency readiness. MinIO persistence, ClamAV signature freshness, TLS, secret rotation, and hosted backups remain external verification gates.

## Database URLs

Local SQLite uses `sqlite:///./niyamguard.db`. PostgreSQL uses the psycopg 3 form `postgresql+psycopg://user:password@host:5432/niyamguard`. Render's standard `postgresql://` connection string is normalized to that installed driver at runtime. Hardened environments reject SQLite and every non-PostgreSQL scheme.

## Document-processing services

- Native PDF text extraction uses PyMuPDF first; pypdf is retained as a local compatibility fallback.
- Low-text/scanned PDFs require `OCR_ENABLED=true` and the configured `OCR_COMMAND` (OCRmyPDF). The original object is immutable; an OCR derivative is stored under a separate key with page provenance.
- Uploads are scanned before persistence. Production requires `MALWARE_SCAN_MODE=clamav`; an unavailable or indeterminate ClamAV result returns an error and never enters processing.
- Durable deployments require `OBJECT_STORAGE_BACKEND=s3`, a bucket, and provider credentials. Local/demo uses the filesystem backend explicitly.

## Boundary

The hosted application remains a synthetic portfolio sandbox. Do not configure real identity, payment, messaging, government, citizen, or signing credentials without a separately authorized integration and security review.
