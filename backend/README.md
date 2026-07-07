# NiyamGuard Backend

FastAPI backend for the NiyamGuard AI Voice/Form Assistant. It serves the form
catalog, dynamic form schemas, assistant guidance, validation, review summaries,
location help, and backend MP3 TTS fallback.

The assistant guides the citizen but does not submit the application. The citizen remains in control.

## Run

```powershell
cd D:\niyam\niyamguard-call-assistant\backend
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Swagger docs: `http://127.0.0.1:8000/docs`.

## Main APIs

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | Health |
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
summary language, and safety flags.
