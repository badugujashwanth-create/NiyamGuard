# Integration Working Status

Verified against backend `http://127.0.0.1:8010` and frontend `http://127.0.0.1:5180` on 2026-07-10.

| Feature | Backend endpoint | Frontend section | Status | Tested? | Issue |
| --- | --- | --- | --- | --- | --- |
| Auth | `/api/auth/*` | Login, admin/officer routes | Working | Backend/frontend | Demo credentials only |
| Portal services | `/api/portal/services` | Citizen Portal, ServicePortal | Working | Smoke/E2E | Sandbox catalog |
| Applications | `/api/applications/*` | Apply, My Applications | Working | Unit/E2E | Demo applications |
| Officer review | `/api/officer/*` | Government Portal, `/officer` | Working | Backend/unit/E2E | Sandbox review |
| Certificates | `/api/certificates/verify/{query}` | Verify Certificate, Government certificates | Working | E2E | Sandbox signature |
| Public verification | `/api/certificates/verify/{query}` | `/verify-certificate` | Working | E2E | Official verifier not connected |
| Circular/policy update | `/api/circulars`, `/api/rule-candidates`, `/api/policy-updates/*` | Circulars & Policy Updates | Working | Unit/E2E | Sandbox circular feed |
| Compliance | `/api/compliance/run`, `/api/compliance/findings` | Compliance Drift | Working | Smoke/E2E | Demo connected-system data |
| Propagation | `/api/propagation/*`, `/api/mock-systems/*` | Connected Systems / Propagation | Working | Unit/E2E | Mock downstream systems |
| Audit | `/api/audit/*` | Audit Trail | Working | E2E/unit | Demo audit retention |
| Reports | `/api/reports/export`, `/api/demo/reports/export` | Reports | Working | Unit | Demo exports |
| Virtual government | `/api/virtual-gov/*` | Virtual Government Sandbox | Working | Smoke/E2E | Sandbox only |
| Hybrid answer | `POST /api/hybrid/answer` | Citizen and Government portals | Working | Smoke/E2E | Uses demo knowledge |
| AI/Ollama status | `GET /api/ai/status`, `POST /api/ai/verified-explanation` | Hybrid Answer Engine / Ollama | Working | Smoke/E2E | Requires local Ollama for online mode |
| Readiness/ops | `/api/ops/status`, `/api/readiness/*`, `/api/integration/health` | Readiness & Ops | Working | Smoke/E2E | Demo readiness only |
| Full end-to-end demo | `POST /api/demo/run-full-end-to-end` | Government Portal | Working | Backend/E2E | Sandbox flow |

Ollama verification:

```text
ollama list -> qwen2.5:7b-instruct present
GET /api/ai/status -> online
model -> qwen2.5:7b-instruct
fallback_available -> true
```

Official decisions remain deterministic:

```text
Verified rules and compliance engines decide policy behavior.
Ollama only explains verified context.
```
