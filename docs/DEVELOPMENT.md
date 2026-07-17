# Development guide

## Purpose

Compliance and public-service prototype combining citizen workflows, government administration, explainable policy retrieval, and synthetic demo data.

## Prerequisites

React/Vite, FastAPI, SQLAlchemy, scikit-learn, PostgreSQL/SQLite, optional Ollama.

## Install

```powershell
Backend: pip install -r backend/requirements.txt; frontend: npm ci --prefix frontend
```

## Run

```powershell
Use `scripts/start-demo.ps1` or run backend and frontend separately
```

## Verify

- Tests: `Backend pytest; frontend Vitest`
- Build: `npm run build --prefix frontend`

See [TEST_REPORT.md](TEST_REPORT.md) for the latest audited results. Copy example environment files instead of committing real values. Generated dependencies, caches, logs, databases, and build output must remain untracked.

