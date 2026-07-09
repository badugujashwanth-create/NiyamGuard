# NiyamGuard AI

NiyamGuard AI is a government-policy compliance and citizen assistance platform. The main product repo is the Jashwanth repo at `badugujashwanth-create/NiyamGuard`; the other repos reviewed during this work were used only as references and were not merged into this codebase.

This project does not submit real government applications and does not replace official verification.

## What It Provides

- Citizen voice/form assistant with Telugu, Hindi, and English guidance.
- Service catalog, dynamic forms, document guidance, and verified source cards.
- Admin portal at `/admin` with RBAC-protected government-core pages.
- Public demo dashboard at `/demo`.
- Citizen scheme finder at `/scheme-finder`.
- Hybrid verified answer engine at `/api/hybrid/answer`, `/api/answer`, and `/api/search`.
- Full synthetic public service portal at `/services` with application submission, document upload, sandbox payment, officer review, certificate generation, public tracking, and certificate verification.
- Government pilot readiness at `/admin/readiness` and virtual sandbox at `/virtual-gov`.
- Self-updating policy workflow with circular source sync, extraction, approval, publication, propagation, rollback, scheduler controls, and demo patching.
- Mock connected system pages at `/mock/meeseva` and `/mock/public-faq`.
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
officer@niyamguard.local / Officer@12345 / reviewer
viewer@niyamguard.local / Viewer@12345 / viewer
citizen@niyamguard.local / Citizen@12345 / citizen
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
http://127.0.0.1:5173/services
http://127.0.0.1:5173/track
http://127.0.0.1:5173/verify-certificate
http://127.0.0.1:5173/officer
http://127.0.0.1:5173/scheme-finder
http://127.0.0.1:5173/virtual-gov
http://127.0.0.1:5173/mock/meeseva
http://127.0.0.1:5173/mock/public-faq
http://127.0.0.1:5173/login
http://127.0.0.1:5173/admin
http://127.0.0.1:5173/admin/readiness
http://127.0.0.1:5173
```

## Self-Updating Policy Demo

Use this flow for the GO-138 income-certificate scenario:

```text
/demo -> Reset Mock Systems -> Run Update Workflow -> Run and Patch
```

Admin pages:

```text
/admin/sources
/admin/circulars
/admin/rule-candidates
/admin/policy-updates
/admin/propagation
/admin/scheduler
/admin/scale-view
/admin/impact
```

Important self-update APIs:

```text
GET  /api/sources
POST /api/sources/{source_id}/sync
GET  /api/circulars
POST /api/circulars/{circular_id}/extract-rules
GET  /api/rule-candidates
POST /api/rule-candidates/{candidate_id}/approve
POST /api/policy-updates/{candidate_id}/publish
GET  /api/propagation/tasks
POST /api/propagation/tasks/{task_id}/apply-demo-patch
POST /api/demo/run-self-update-scenario
GET  /api/mock-systems
```

The mock pages are synthetic connected systems only. They do not connect to real MeeSeva, OTP, CAPTCHA, payments, or official government submission.

## Full Service Portal Demo

The `/services` portal is a synthetic NiyamGuard public-service platform, not an official MeeSeva site. It supports the seeded services in `PolicyDataStore`: Income Certificate, Residence Certificate, Caste Certificate, EWS Certificate, Birth Certificate, Death Certificate, Family Member Certificate, Ration Card, Old-Age Pension, and Post-Matric Scholarship.

Core demo flow:

```text
/services -> /apply/income_certificate -> upload documents -> submit
-> /payment/{application_id} -> /officer/pending -> approve
-> /applications/{application_id} -> /verify-certificate -> /track
```

Useful APIs:

```text
GET  /api/portal/services
GET  /api/portal/services/{service_id}
POST /api/applications
POST /api/applications/{application_id}/documents
POST /api/applications/{application_id}/submit
POST /api/payments/{application_id}/create
POST /api/payments/{payment_id}/simulate-success
GET  /api/officer/pending
POST /api/officer/applications/{application_id}/approve
GET  /api/certificates/verify/{verification_hash}
GET  /api/track/{application_number}
```

Generated local files are ignored under:

```text
backend/app/storage/documents/
backend/app/storage/certificates/
```

Docs:

```text
docs/full-service-portal.md
docs/citizen-application-workflow.md
docs/officer-review-workflow.md
docs/certificate-generation.md
docs/payment-sandbox.md
docs/access-control.md
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

## Hybrid Search And Answer Engine

The verified answer engine uses exact rules, service decision tables, local RAG
retrieval, optional Ollama, and deterministic fallback. It never invents official
answers when a source is missing.

```text
POST /api/hybrid/answer
POST /api/answer
GET  /api/hybrid/status
POST /api/hybrid/reindex
GET  /api/search?q=income%20certificate%20validity
GET  /api/search/status
POST /api/search/reindex
```

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

Optional provider settings:

```env
ANSWER_ENGINE=hybrid_intelligence
SEARCH_ENGINE_ENABLED=true
BM25_ENABLED=true
SEMANTIC_SEARCH_ENABLED=true
ANSWER_TEMPLATES_ENABLED=true
LLM_OPTIONAL=true
LLM_REQUIRED=false
HF_API_TOKEN=
GROQ_API_KEY=
GEMINI_API_KEY=
```

## Government Pilot Readiness And Sandbox

Readiness and operations:

```text
GET  /api/ops/status
GET  /api/admin/readiness
POST /api/security/otp/request
POST /api/security/otp/verify
```

Virtual government sandbox:

```text
GET  /api/virtual-gov/status
GET  /api/virtual-gov/scenarios
POST /api/virtual-gov/run
```

Docs:

```text
docs/government-pilot-readiness.md
docs/virtual-government-sandbox.md
docs/security-checklist.md
docs/threat-model.md
docs/privacy-checklist.md
docs/owasp-mapping.md
docs/backup-restore.md
docs/uat-checklist.md
```

## Evaluation and Fine-Tune Prep

These scripts use the dataset for testing and preparation only. They do not run
expensive model training.

```powershell
python scripts/evaluate_qa_dataset.py
python scripts/test_intent_classifier.py
python scripts/prepare_finetune_jsonl.py
```

## Hackathon Demo Flow

1. Open `/demo`.
2. Reset mock systems and show `/mock/meeseva` still says `12 months`.
3. Run the self-update scenario.
4. Show `/admin/rule-candidates`, `/admin/policy-updates`, and `/admin/propagation`.
5. Patch mock systems and show `/mock/meeseva` plus `/mock/public-faq` now say `6 months`.
6. Open `/admin/impact` to explain citizen impact and priority.
7. Open `/admin/regulatory-ai`, ask `Why is ORG-0029 high risk?`, and show dataset-grounded citations.
8. Open `/admin/readiness` and show the pilot controls.
9. Open `/virtual-gov`, run the sandbox, and show application/certificate artifacts.
10. Open `/scheme-finder`, select student/scholarship, and show cautious service recommendations.
11. Open `/services`, apply for Income Certificate, simulate payment, approve from `/officer/pending`, then verify the generated certificate.
12. Open `/`, ask `income certificate validity entha`, then open the Income Certificate form and ask `purpose lo scholarship ani rayacha`.
13. Point out that Ollama is optional and fallback is deterministic.

## Platform Contracts

Shared demo contracts are in:

```text
shared-contracts/api-contracts.json
docs/platform-orchestrator.md
scripts/check-health.ps1
scripts/check-health.sh
```

The three-module presentation keeps modules separate and connects through HTTP contracts. This repo does not import internal code from the other repositories.

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
- `POST /api/scheme-finder/recommend`
- `GET /api/portal/services`
- `POST /api/applications`
- `POST /api/applications/{application_id}/submit`
- `POST /api/payments/{application_id}/create`
- `GET /api/officer/pending`
- `POST /api/officer/applications/{application_id}/approve`
- `GET /api/certificates/verify/{verification_hash}`
- `POST /api/demo/run-self-update-scenario`
- `GET /api/mock-systems`
- `POST /api/chat`
- `GET /api/audit/events`
- `GET /api/ai/status`
- `POST /api/ai/finding/{finding_id}/impact-summary`
- `GET /api/dataset/status`
- `POST /api/dataset/qa`
- `GET /api/dataset/demo-flow`
- `POST /api/hybrid/answer`
- `GET /api/search/status`
- `GET /api/ops/status`
- `GET /api/admin/readiness`
- `POST /api/virtual-gov/run`

Version aliases are also available under `/api/v1/...`.

## Tests

```powershell
cd D:\niyam\niyamguard-call-assistant\backend
pytest

cd D:\niyam\niyamguard-call-assistant\frontend
npm test
npm run build

cd D:\niyam\niyamguard-call-assistant
python scripts/final_api_smoke_test.py --base-url http://127.0.0.1:8000
python scripts/record_demo_assets.py --frontend-url http://127.0.0.1:5173 --backend-url http://127.0.0.1:8000
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
