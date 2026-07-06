# NiyamGuard AI Call / Voice Assistant

NiyamGuard is a demo citizen-assistance application for completing a simplified
Income Certificate form. A citizen can ask questions by voice or text in
Telugu, Hindi, English, or common mixed/romanized forms. The assistant detects
the language and relevant form field, explains the field in everyday language,
calculates related income values, validates manually entered values, and speaks
its answer in the same language.

The assistant does not fill or submit the form. It only guides the citizen. The citizen remains in control.

## Problem and solution

Government forms can be difficult for citizens who do not understand formal
field labels such as Monthly Income, Purpose, or Mandal. Browser voice support
also differs by device, and Telugu or Hindi voices are often unavailable.

NiyamGuard combines:

- automatic Telugu/Hindi/English language detection
- citizen-friendly field explanations and form-context detection
- browser speech recognition and same-language browser speech output
- backend MP3 TTS fallback when the matching browser voice is missing
- optional pincode/village-based mandal guidance from local demo data
- manual validation and spoken review of citizen-entered values

## Safety boundary

The assistant never:

- auto-fills or controls form fields
- submits an application or claims government submission
- uploads documents
- handles OTP, CAPTCHA, payments, or government login
- accesses location without a user click and browser permission

All suggested values remain guidance. The citizen confirms, types, reviews, and
submits manually.

## Voice architecture

```text
Citizen speech
  → browser speech recognition
  → backend language, field, and location-intent detection
  → same-language text guidance
  → browser TTS when a matching language voice exists
  → backend gTTS MP3 fallback when that voice is missing
  → citizen hears the answer
  → citizen manually fills the form
```

Supported output languages are Telugu (`te-IN`), Hindi (`hi-IN`), and Indian
English (`en-IN`). Mixed Telugu-English and Hindi-English input uses the
dominant language markers.

## Technology

- Backend: Python, FastAPI, Pydantic, gTTS, JSON demo storage
- Frontend: React, Vite, Web Speech APIs, HTML audio
- Tests: pytest, Vitest, Testing Library

## Local setup

Backend:

```powershell
cd D:\niyam\niyamguard-call-assistant\backend
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

Frontend:

```powershell
cd D:\niyam\niyamguard-call-assistant\frontend
Copy-Item .env.example .env
npm install
npm run dev
```

Open `http://127.0.0.1:5173`.

## Demo flow

1. Click **Start Voice Help** or use the text fallback.
2. Ask `purpose lo scholarship ani rayacha`.
3. Listen to the Telugu reply. If Chrome has no Telugu voice, the backend
   generates and plays Telugu MP3 audio.
4. Ask `monthly income fifteen thousand what should I enter`.
5. Manually type the suggested values.
6. If the mandal is unknown, use the mandal quick-help or enter a pincode.
7. Click **Review My Details** and listen to the same-language review.
8. Use **Submit Manually (Demo)**. It makes no government submission request.

## Location-aware field help and privacy

If a citizen does not know their district, mandal, or village, the assistant
asks for a pincode or village name and suggests possible values using local
demo data. It never auto-fills the form and asks the citizen to confirm before
typing.

Location access is optional and only requested when the citizen clicks **Use My
Location**. The MVP does not claim precise GPS-to-mandal lookup and asks for a
pincode or village instead.

## Backend TTS

gTTS is the MVP backend provider and requires internet access for uncached
phrases. Generated MP3 files use SHA256-only cache names. Set
`VITE_FORCE_BACKEND_TTS=true` to test backend voice for every language.
Bhashini is represented only as a future provider option; credentials and
production integration are not included.

## Tests

```powershell
cd backend
pytest

cd ..\frontend
npm test
npm run build
```

## Not included and future scope

This demo does not connect to a government portal or perform document, identity,
login, payment, OTP, or CAPTCHA workflows. Future production work can replace
JSON session/location data, integrate Bhashini, add broader location datasets,
and add authenticated deployment controls without weakening the citizen-control
boundary.
