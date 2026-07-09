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
python -m app.data_pipeline.dataset_pack_loader --import-db --build-rag
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

## Dataset Pack

The synthetic dataset pack is extracted at:

```text
data/niyamguard_dataset_pack_v1/
```

It contains regulatory circulars, internal policies, obligations, policy mappings,
controls, compliance evidence, gap findings, drift cases, risk labels, audit logs,
organizations, users, RAG documents, QA pairs, intent data, instruction JSONL, and
API test cases. The data is synthetic demo data, not official regulatory advice.

Import and index it:

```powershell
cd D:\niyam\niyamguard-call-assistant\backend
python -m app.data_pipeline.dataset_pack_loader --import-db --build-rag
```

Useful dataset APIs:

```text
GET  /api/dataset/status
POST /api/dataset/qa
GET  /api/dataset/obligations/search?q=privacy
GET  /api/dataset/gaps?org_id=ORG-0029
GET  /api/dataset/evidence?org_id=ORG-0029
GET  /api/dataset/drift?org_id=ORG-0029
GET  /api/dataset/risk/ORG-0029
GET  /api/dataset/audit?org_id=ORG-0029
GET  /api/dataset/demo-flow?org_id=ORG-0029
```

Admin UI: open `/admin/regulatory-ai` to explore circulars, policies,
obligations, gaps, drift, risk, evidence, audit events, and dataset-grounded Q&A.

## Local LLM and RAG

AI is optional and safe by default:

```env
AI_PROVIDER=ollama
AI_ENABLED=false
OLLAMA_BASE_URL=http://127.0.0.1:11434
OLLAMA_MODEL=qwen2.5:7b-instruct
OLLAMA_FALLBACK_MODEL=llama3.2:3b
RAG_ENABLED=true
RAG_INDEX_PATH=./data/rag_index
DATASET_PACK_DIR=./data/niyamguard_dataset_pack_v1
```

Run Ollama only when available:

```powershell
ollama pull qwen2.5:7b-instruct
ollama run qwen2.5:7b-instruct
```

Without Ollama, deterministic fallbacks still answer from retrieved dataset
sources or return `Not found in available dataset.`.

## Evaluation and Fine-Tune Prep

These scripts use the dataset for testing and preparation only. They do not run
expensive model training.

```powershell
python scripts/evaluate_qa_dataset.py
python scripts/test_intent_classifier.py
python scripts/prepare_finetune_jsonl.py
```

## Hackathon Demo Flow

1. Open `/admin/regulatory-ai`.
2. Ask: `Why is ORG-0029 high risk?`
3. Show retrieved dataset references from QA/RAG.
4. Show the linked regulatory circular and extracted obligation.
5. Show the internal policy, policy gap, and drift alert.
6. Show risk score explanation, evidence records, and audit trail.
7. Point out that Ollama is optional and fallback is deterministic.

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
- `GET /api/ai/status`
- `POST /api/ai/finding/{finding_id}/impact-summary`
- `GET /api/dataset/status`
- `POST /api/dataset/qa`
- `GET /api/dataset/demo-flow`

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
- Dataset pack records are synthetic and useful for demos, RAG, tests, and model-prep only.
- Fine-tuning is future scope; current AI uses RAG plus local Ollama/fallback templates.
- The app guides citizens but never submits official applications, handles OTP, CAPTCHA, payments, or official portal login.
- Demo/local knowledge is useful for presentation and testing, but official deployments need verified government data feeds and legal approval.
