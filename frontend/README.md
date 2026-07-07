# NiyamGuard Frontend

React/Vite frontend for the NiyamGuard AI Voice/Form Assistant. The first screen
is a service catalog; selected services render dynamically from backend JSON
schemas.

The assistant guides the citizen but does not submit the application. The citizen remains in control.

## Run

Start FastAPI first, then:

```powershell
cd D:\niyam\niyamguard-call-assistant\frontend
npm install
npm run dev
```

Open `http://127.0.0.1:5173`.

Optional `.env`:

```dotenv
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_FORCE_BACKEND_TTS=false
```

## UI Flow

1. Service catalog appears with search, category filter, service cards, and Ask
   Assistant.
2. Citizen starts a service.
3. Dynamic form fields and document upload guidance render from backend schema.
4. Citizen clicks **Start**; assistant speaks an introduction first.
5. User can ask by voice or text in Telugu, Hindi, English, or mixed phrasing.
6. Assistant replies in the detected language and speaks in that language.
7. Citizen manually fills fields and selects files.
8. **Review My Details** reads back values and missing documents.
9. **Submit Manually (Demo)** shows demo-only notice.

## Voice Behavior

- Only Start and Stop are visible as the main voice controls.
- No language dropdown.
- No visible current-field selector.
- Focused field is sent internally as context.
- MediaRecorder sends short audio chunks to backend STT first.
- Browser SpeechRecognition is used as fallback if backend STT is unavailable.
- Listening pauses while assistant audio plays and resumes only while Start is active.
- Telugu/Hindi are never silently spoken through an English browser voice.
- If a matching browser voice is missing, the frontend calls backend
  `/api/tts/speak` and plays MP3 audio.
- If backend TTS fails, text guidance stays visible with a warning.

## Dynamic Forms and Documents

`DynamicFormPage`, `DynamicFieldRenderer`, and `DocumentUploadSection` render
fields and upload guidance from schema. File validation is local/demo-only:
accepted extension, max size, and required document status. The assistant never
uploads files.

## Safety

Suggested values are shown with a copy action only. They are not written into
fields automatically. Demo submit does not call a government endpoint.

## Tests and Build

```powershell
npm test
npm run build
```

Tests cover catalog rendering, dynamic form rendering, hidden technical
selectors, Start/Stop assistant controls, voice intro, listening status changes,
auto-language payloads, focused field/document context, Telugu and Hindi backend
TTS fallback, document upload validation, no auto-fill, review payloads,
demo-only submit, and optional location permission behavior.
