# NiyamGuard Call Assistant Frontend

React and Vite browser voice interface for the NiyamGuard Income Certificate
assistant. It presents a citizen-controlled form beside a voice/text guidance
panel and connects to the existing FastAPI backend.

## Safety boundary

The assistant never writes into a form field and never submits an application.
Suggested values appear only in the assistant panel. Every field value changes
only after the citizen types into that field. The demo submit button makes no
network request and clearly reports that no government application was
submitted.

## Features

- Income Certificate form loaded from the backend schema
- Backend session creation on page load
- Browser speech recognition with live transcript
- Text question fallback for unsupported browsers
- Spoken assistant replies with browser speech synthesis
- Current-field and language selectors
- Backend validation guidance when a manually entered field loses focus
- Summary/read-back of current citizen-entered values
- Clear conversation action that starts a fresh backend session
- Responsive citizen-service layout with large controls

## Prerequisites

- Node.js 20 or newer
- npm
- The FastAPI backend running at `http://127.0.0.1:8000`
- Chrome or Edge for the broadest Web Speech API support

Voice recognition availability depends on the browser and may require an
internet connection for the browser vendor's recognition service. Text input
always remains available.

## Run locally

First start the backend in one PowerShell terminal:

```powershell
cd D:\niyam\niyamguard-call-assistant\backend
uvicorn app.main:app --reload
```

Then start the frontend in another terminal:

```powershell
cd D:\niyam\niyamguard-call-assistant\frontend
Copy-Item .env.example .env
npm install
npm run dev
```

Open `http://127.0.0.1:5173`.

The default environment setting is:

```dotenv
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Restart Vite after changing environment variables.

## Demo

1. Open the frontend and wait for the green assistant status indicator.
2. Click **Start Voice Help** and allow microphone access.
   Voice help continues listening until **Stop Voice Help** is clicked. It
   automatically pauses while the assistant speaks and resumes afterward.
3. Say: `Monthly income fifteen thousand what should I enter?`
4. The transcript appears, the backend reply is displayed, and the browser
   speaks it.
5. Manually type `15000` into Monthly Income.
6. Ask: `Purpose lo scholarship ani rayacha?`
7. Listen to the guidance, then manually type `Scholarship`.
8. Complete other values and click **Review My Details**.
9. Listen to the summary and verify all values yourself.
10. **Submit Manually (Demo)** demonstrates the manual action but intentionally
    does not call a submission endpoint.

If the browser does not support speech recognition, type either question into
the assistant text box and click **Ask**.

## Voice troubleshooting

- Use the latest Chrome or Edge and open the app through
  `http://127.0.0.1:5173`, not directly as a local HTML file.
- Allow microphone access when the browser asks. If it was previously denied,
  open the site-permission icon beside the address bar and change Microphone to
  Allow, then reload.
- Check that the browser tab and system output device are not muted.
- After a reply appears, use **Speak again** to test text-to-speech directly.
- Keep both the backend on port 8000 and frontend on port 5173 running.
- Browser recognition may use an online browser service even though this
  project does not use a paid voice API.

## Tests and production build

```powershell
npm test
npm run build
```

The automated tests verify session creation, text fallback, voice transcript,
spoken replies, summary payloads, citizen-controlled form state, and the absence
of submission calls.

## Browser voice architecture

```text
Citizen speech
    -> Web Speech recognition
    -> POST /api/assistant/ask
    -> guidance text only
    -> Web Speech synthesis
    -> citizen manually types into the form
```

For a future real phone-call integration, the browser recognition/synthesis
adapters can be replaced by Vapi, Pipecat, LiveKit, or Twilio while keeping the
FastAPI guidance endpoints and the manual-entry safety policy.
