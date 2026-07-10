# NiyamGuard Backend

FastAPI backend for NiyamGuard AI. It serves the Voice/Form Assistant and the
government-core platform APIs for verified policy rules, connected systems,
compliance verification, cascade tracing, priority scoring, conflicts, reports,
public verified-rule lookup, and the synthetic full service portal workflow.

The assistant guides the citizen but does not submit the application. The citizen remains in control.

## Run

```powershell
cd D:\niyam\niyamguard-call-assistant\backend
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app.seed_demo
python -m app.data_pipeline.dataset_pack_loader --import-db --build-rag
uvicorn app.main:app --reload
```

Swagger docs: `http://127.0.0.1:8000/docs`.

## Main APIs

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | Health |
| `GET` | `/api/integration/health` | Government-core integration health |
| `GET` | `/api/forms` | Catalog of seeded forms |
| `GET` | `/api/forms/income-certificate` | Backward-compatible income form |
| `GET` | `/api/forms/{form_id}` | Dynamic form schema |
| `GET` | `/api/services` | Service catalog |
| `GET` | `/api/services/search?q=` | Service search |
| `POST` | `/api/sessions` | Create session for form or catalog |
| `GET` | `/api/sessions/{session_id}` | Read session context |
| `POST` | `/api/assistant/ask` | Language/field/document/location guidance |
| `POST` | `/api/assistant/validate` | Validate one manually entered value |
| `POST` | `/api/assistant/summary` | Review values and uploaded document status |
| `POST` | `/api/stt/transcribe` | Audio transcription with local Whisper provider or browser fallback transcript |
| `GET` | `/api/tts/health` | TTS status |
| `POST` | `/api/tts/speak` | MP3 TTS |
| `GET` | `/api/location/search?query=` | Location search |
| `GET` | `/api/location/search?pincode=` | Pincode lookup |
| `POST` | `/api/location/help` | Mandal/location guidance |
| `POST` | `/api/location/reverse` | Honest GPS MVP fallback |
| `GET` | `/api/knowledge/rules` | Verified policy rules |
| `GET` | `/api/knowledge/rules/latest` | Latest verified rule lookup |
| `GET` | `/api/connected-systems` | Connected systems registry |
| `POST` | `/api/compliance/run` | Run compliance drift detection |
| `GET` | `/api/compliance/findings` | Compliance findings |
| `GET` | `/api/cascade/finding/{finding_id}` | Cascade impact trace |
| `GET` | `/api/dashboard/summary` | Priority dashboard summary |
| `POST` | `/api/conflicts/scan` | Cross-circular conflict scan |
| `GET` | `/api/admin/summary` | Government admin summary |
| `GET` | `/api/reports/summary` | Reports summary |
| `GET` | `/api/reports/export` | CSV/JSON/HTML report export |
| `GET` | `/api/public/rules/latest` | Citizen-safe verified rule answer |
| `POST` | `/api/hybrid/answer` | Source-backed hybrid answer engine |
| `POST` | `/api/answer` | Public alias for hybrid answers |
| `GET` | `/api/search` | Hybrid searchable knowledge store |
| `GET` | `/api/search/status` | Search/index status |
| `POST` | `/api/search/reindex` | Rebuild searchable knowledge index |
| `GET` | `/api/ai/status` | Local Ollama/fallback and RAG status |
| `POST` | `/api/ai/chat` | Chat alias using local/fallback AI contract |
| `POST` | `/api/ai/circular-summary` | Circular summary using local/fallback AI |
| `POST` | `/api/ai/finding/{finding_id}/impact-summary` | Explanatory AI summary for verified compliance finding |
| `GET` | `/api/dataset/status` | Synthetic dataset pack import/index status |
| `POST` | `/api/dataset/qa` | Dataset-grounded regulatory Q&A |
| `GET` | `/api/dataset/obligations/search` | Obligation search |
| `GET` | `/api/dataset/gaps` | Policy-to-obligation gaps and mappings |
| `GET` | `/api/dataset/evidence` | Compliance evidence review records |
| `GET` | `/api/dataset/drift` | Regulatory drift cases |
| `GET` | `/api/dataset/risk/{org_id}` | Risk score explanation |
| `GET` | `/api/dataset/audit` | Synthetic dataset audit trail |
| `GET` | `/api/dataset/demo-flow` | End-to-end demo bundle |
| `GET` | `/api/sources` | Circular source registry |
| `POST` | `/api/sources/{source_id}/sync` | Sync one circular source |
| `GET` | `/api/circulars` | Ingested circular documents |
| `POST` | `/api/circulars/{circular_id}/extract-rules` | Extract policy rule candidates |
| `GET` | `/api/rule-candidates` | Officer review queue |
| `POST` | `/api/rule-candidates/{candidate_id}/approve` | Approve extracted candidate |
| `POST` | `/api/policy-updates/{candidate_id}/publish` | Publish verified rule version |
| `GET` | `/api/propagation/tasks` | Downstream update tasks |
| `POST` | `/api/demo/run-self-update-scenario` | End-to-end self-update demo |
| `POST` | `/api/scheme-finder/recommend` | Citizen scheme/service recommendations |
| `GET` | `/api/mock-systems` | Synthetic connected system state |
| `GET` | `/api/portal/services` | Synthetic service portal catalog |
| `GET` | `/api/portal/services/{service_id}` | Service definition and current form |
| `POST` | `/api/applications` | Create citizen application draft |
| `PATCH` | `/api/applications/{application_id}` | Update citizen application draft |
| `POST` | `/api/applications/{application_id}/documents` | Upload PDF/JPG/PNG evidence |
| `POST` | `/api/applications/{application_id}/submit` | Submit application for payment/review |
| `GET` | `/api/track/{application_number}` | Public application tracking |
| `POST` | `/api/payments/{application_id}/create` | Create sandbox payment |
| `POST` | `/api/payments/{payment_id}/simulate-success` | Mark sandbox payment as paid |
| `GET` | `/api/officer/applications` | Officer review queue |
| `POST` | `/api/officer/applications/{application_id}/approve` | Approve and issue demo certificate |
| `GET` | `/api/certificates/verify/{query}` | Public certificate verification |
| `GET` | `/api/notifications` | Current user's notifications |
| `GET` | `/api/ops/status` | Public ops status for pilot checks |
| `GET` | `/api/admin/readiness` | RBAC-protected pilot readiness matrix |
| `POST` | `/api/security/otp/request` | Sandbox OTP request |
| `POST` | `/api/security/otp/verify` | Sandbox OTP verification |
| `GET` | `/api/virtual-gov/status` | Virtual government sandbox status |
| `GET` | `/api/virtual-gov/scenarios` | Virtual government scenarios |
| `POST` | `/api/virtual-gov/run` | End-to-end regulation-to-certificate scenario |

Assistant responses always include `auto_fill: false` and
`should_submit: false`.

## Form Catalog

Schemas are one JSON file per form under `app/data/forms/`. Each schema
contains metadata, fields, localized help, required documents, file constraints,
and assistant examples.

`/api/services` returns 25+ catalog entries. Ten entries are ready detailed
forms, including EWS Certificate. Catalog-only entries such as Loan Eligibility
Card are marked `catalog_only` and `has_detailed_schema: false` so the frontend
can show "Detailed guided form coming soon" instead of opening an incomplete
form.

## STT

`POST /api/stt/transcribe` accepts multipart form data with an `audio` file and
optional `language_hint`, `form_id`, `session_id`, and `fallback_transcript`.
When `faster-whisper` is available, the backend uses a local Whisper provider.
When it is not installed, the endpoint returns a clear 503 so the frontend can
fall back to browser SpeechRecognition. Tests cover the browser fallback
transcript path without requiring the optional model.

## TTS

`POST /api/tts/speak` accepts:

```json
{
  "text": "నమస్తే",
  "language_code": "te-IN",
  "detected_language": "telugu",
  "provider": "auto"
}
```

It returns `audio/mpeg` with `X-TTS-Language-Code`, `X-TTS-Provider`, and
`X-TTS-Cache`. gTTS is used for `te-IN`, `hi-IN`, and `en-IN`; generated audio
is cached in `app/storage/tts_cache/`.

## Location Help

`app/data/telangana_locations.json` is a small MVP dataset. Responses use
cautious wording such as “may be” and ask the citizen to confirm. GPS reverse
lookup does not pretend to know the exact mandal.

## Tests

```powershell
pytest
```

Coverage includes endpoints, all seeded schemas, service search, language
detection/switching, localized field explanations, income calculation, mandal
help, document guidance, STT fallback behavior, TTS health/speak/errors,
summary language, safety flags, verified policy rules, connected systems,
compliance drift detection, cascade tracing, priority scoring, conflict
detection, admin summaries, reports/export, and public verified-rule APIs.

Dataset utilities:

```powershell
python -m app.data_pipeline.dataset_pack_loader --import-db --build-rag
python ..\scripts\evaluate_qa_dataset.py
python ..\scripts\test_intent_classifier.py
python ..\scripts\prepare_finetune_jsonl.py
```

Self-update and scheme finder tests:

```powershell
pytest app/tests/test_self_update_policy_engine.py app/tests/test_scheme_finder.py
```

Full service portal tests:

```powershell
pytest app/tests/test_service_portal.py
```

Hybrid/readiness/virtual sandbox tests:

```powershell
pytest app/tests/test_hybrid_intelligence.py app/tests/test_readiness.py app/tests/test_virtual_government.py
```

Final smoke test, after starting the backend:

```powershell
python ..\scripts\final_api_smoke_test.py --base-url http://127.0.0.1:8000
```

Demo accounts:

```text
admin@niyamguard.local / Admin@12345 / admin
reviewer@niyamguard.local / Reviewer@12345 / reviewer
officer@niyamguard.local / Officer@12345 / reviewer
viewer@niyamguard.local / Viewer@12345 / viewer
citizen@niyamguard.local / Citizen@12345 / citizen
```

## Independence and Safety

This repo is implemented independently. It does not import or merge code from the citizen chatbot or voice assistant repos. Those modules will integrate later through public APIs.

This is a demo MVP. It does not submit real applications to the government and does not replace official verification.
