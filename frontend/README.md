# NiyamGuard Frontend

React/Vite citizen interface for an Income Certificate form and same-language
voice guidance.

The assistant does not fill or submit the form. It only guides the citizen. The citizen remains in control.

## Setup

Start the FastAPI backend first, then:

```powershell
cd D:\niyam\niyamguard-call-assistant\frontend
Copy-Item .env.example .env
npm install
npm run dev
```

Open `http://127.0.0.1:5173` in current Chrome or Edge.

## Configuration

```dotenv
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_FORCE_BACKEND_TTS=false
```

Set `VITE_FORCE_BACKEND_TTS=true` to route all voice output through backend MP3
TTS for testing.

## User experience

- No language or technical current-field selector is required.
- The focused form field is sent internally as context.
- Language is detected by the backend from Telugu, Hindi, English, or mixed text.
- The answer is displayed and spoken in the detected language.
- Voice recognition pauses during playback and resumes only while Voice Help is
  still active.
- Suggested values are never written into the form.
- Review uses only values the citizen manually entered.
- Demo submit makes no government submission API call.

## Voice output architecture

```text
Backend reply + language_code
  → load browser voices
  → exact/prefix language voice found: use SpeechSynthesis
  → matching voice missing: POST /api/tts/speak
  → play returned MP3 with HTML Audio
```

Telugu and Hindi are never silently spoken through an English browser voice.
If backend TTS fails, the localized text remains visible and a clear warning is
shown. gTTS requires internet for uncached phrases.

**Speak again** reuses the latest reply and latest backend language code.
Developer Diagnostics is collapsed by default and contains voice counts,
backend health, forced backend playback, and language test controls.

## Location help and privacy

The assistant includes:

- **I don't know my mandal** quick help
- a manual pincode helper
- optional **Use My Location to Help Find Mandal**

Location access is never requested on page load. It is requested only after the
citizen clicks the button. Because the MVP has no precise GPS reverse-geocoding
dataset, GPS guidance honestly asks for pincode or village details. District and
mandal suggestions are never auto-filled.

## Tests and build

```powershell
npm test
npm run build
```

Coverage includes auto-language payloads, focused-field context, browser voice
selection, backend audio fallback, forced backend playback, recognition
pause/resume, optional geolocation, location suggestions, manually controlled
form state, summary payloads, and absence of submission requests.
