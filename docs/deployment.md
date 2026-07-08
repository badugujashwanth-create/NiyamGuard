# Deployment

## Local Development

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

Services:

- `postgres`: PostgreSQL 16.
- `backend`: FastAPI on port `8000`.
- `frontend`: Vite preview on port `5173`.

## Environment

Local SQLite:

```text
DATABASE_URL=sqlite:///./niyamguard.db
```

PostgreSQL:

```text
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/niyamguard
```

Production deployment still needs managed secrets, HTTPS, backup/restore, log retention, and a reviewed infrastructure plan.
