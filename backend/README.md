# NiyamGuard Backend

FastAPI backend for language-aware Income Certificate guidance, manual-value
validation, location help, session context, summaries, and MP3 text-to-speech.

The assistant does not fill or submit the form. It only guides the citizen. The citizen remains in control.

## Setup

```powershell
cd D:\niyam\niyamguard-call-assistant\backend
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

Swagger documentation is available at `http://127.0.0.1:8000/docs`.

## Environment

```dotenv
APP_ENV=development
TTS_PROVIDER=auto
ENABLE_GTTS=true
ENABLE_BHASHINI=false
BHASHINI_API_KEY=
BHASHINI_USER_ID=
```

`auto` currently resolves to gTTS. gTTS requires internet for uncached text.
Bhashini is an intentionally non-breaking placeholder for future production
integration.

## Main endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/` | Backend health |
| `GET` | `/api/forms/income-certificate` | Form schema |
| `POST` | `/api/sessions` | Create an auto-language session |
| `POST` | `/api/assistant/ask` | Detect language/field and return guidance |
| `POST` | `/api/assistant/summary` | Validate and summarize manual values |
| `POST` | `/api/assistant/validate` | Validate one manually entered value |
| `GET` | `/api/tts/health` | TTS provider/language capability |
| `POST` | `/api/tts/speak` | Return same-language MP3 audio |
| `GET` | `/api/location/search` | Search local demo location data |
| `POST` | `/api/location/help` | Build cautious location guidance |
| `POST` | `/api/location/reverse` | Honest MVP GPS fallback response |

Every assistant and location-help response preserves:

```json
{
  "auto_fill": false,
  "should_submit": false
}
```

## TTS request

```json
{
  "text": "నమస్తే. ఇది NiyamGuard Telugu voice test.",
  "language_code": "te-IN",
  "detected_language": "telugu",
  "provider": "auto"
}
```

The response is `audio/mpeg` with:

- `X-TTS-Language-Code`
- `X-TTS-Provider`
- `X-TTS-Cache` (`HIT` or `MISS`)

Cached files are named only with a SHA256 hash of provider, language, and text.
Provider/network failure returns a clear `503` JSON response while the original
text reply remains available to the frontend.

## Language and conversation context

The frontend sends `language: "auto"`. The backend detects Telugu/Hindi Unicode,
romanized language markers, or English. Each session retains only conversation
messages, the last detected language, and last discussed field. It never stores
suggested values as filled form data.

Summary requests with `language: "auto"` reuse the session's last detected
language. Focused fields sent by the frontend and prior field context help with
questions such as “what should I enter here?”

## Location help

`app/data/telangana_locations.json` contains limited demonstration records.
Suggestions use cautious wording and require citizen confirmation. The reverse
location endpoint does not invent a precise mandal from GPS coordinates.

## Tests

```powershell
pytest
```

The tests mock gTTS to avoid network dependency and cover language detection,
localized guidance, session context, TTS audio/cache/errors, location searches,
manual-control safety flags, validation, and summaries.
