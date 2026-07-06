# NiyamGuard Call Assistant Backend

A Python 3.12 FastAPI MVP that gives citizens simple, text-based guidance while
they manually complete an Income Certificate application. The rule-based service
detects fields, understands common spoken income amounts, validates values,
calculates annual income, records conversation history, and reads back a summary.
It requires no database, LLM, paid API, or voice provider.

> This backend does not auto-fill or submit forms.
> It only provides guidance to the citizen.
> The citizen manually enters values and submits the form.

## Scope and safety

The assistant can explain fields, suggest a value for the citizen to type,
validate basic input, calculate monthly or annual income, and summarize
frontend-supplied values. Every assistant response explicitly returns
`auto_fill: false` and `should_submit: false`.

It does not control a frontend, save suggested values as filled fields, upload
documents, submit applications, handle OTP or CAPTCHA, process payments, log in
to government portals, claim government approval, or provide legal guarantees.
Session storage contains only session metadata and conversation messages.

## Tech stack

- Python 3.12
- FastAPI, Uvicorn, and Pydantic
- JSON files for the form definition and MVP session persistence
- pytest and HTTPX
- Docker (optional)

## Project structure

```text
backend/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── routes/                 # FastAPI endpoint modules
│   ├── models/                 # Pydantic request/response models
│   ├── services/               # Rule-based, voice-provider-neutral logic
│   ├── data/
│   │   └── income_certificate_form.json
│   ├── storage/
│   │   └── sessions.json
│   └── tests/
├── requirements.txt
├── .env.example
├── Dockerfile
└── README.md
```

## Local setup

Python 3.12 is required.

Linux or macOS:

```bash
cd niyamguard-call-assistant/backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Windows PowerShell:

```powershell
cd niyamguard-call-assistant\backend
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API runs at `http://127.0.0.1:8000`. Interactive Swagger documentation is
available at `http://127.0.0.1:8000/docs`.

## API endpoints

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/` | Health and version check |
| `GET` | `/api/forms/income-certificate` | Get the Income Certificate schema |
| `POST` | `/api/sessions` | Start an assistant session |
| `GET` | `/api/sessions/{session_id}` | Get metadata and conversation history |
| `POST` | `/api/assistant/ask` | Ask for field guidance |
| `POST` | `/api/assistant/validate` | Validate one proposed value |
| `POST` | `/api/assistant/summary` | Validate and read back frontend values |

Unsupported form IDs and languages are rejected by request validation. Supported
languages are `english`, `telugu`, `hindi`, and `mixed`. Full translation is out
of scope for this MVP, but common Telugu/Hindi transliterated phrases are
recognized.

## Example requests

Create a session:

```bash
curl -X POST http://127.0.0.1:8000/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"form_id":"income_certificate","language":"english"}'
```

Example response:

```json
{
  "success": true,
  "session_id": "generated-session-id",
  "form_id": "income_certificate",
  "language": "english",
  "message": "Assistant session created successfully."
}
```

Ask about monthly income, replacing `generated-session-id` with the returned ID:

```bash
curl -X POST http://127.0.0.1:8000/api/assistant/ask \
  -H "Content-Type: application/json" \
  -d '{
    "session_id":"generated-session-id",
    "message":"monthly income fifteen thousand what should I enter",
    "current_field":"monthly_income",
    "language":"english"
  }'
```

Example response:

```json
{
  "success": true,
  "field": "monthly_income",
  "reply": "You can enter 15000 in the Monthly Income field. If the form also asks Annual Income, you can enter 180000 because 15000 multiplied by 12 is 180000.",
  "suggested_value": "15000",
  "related_values": {"annual_income": "180000"},
  "warning": null,
  "auto_fill": false,
  "should_submit": false
}
```

Validate a mobile number:

```bash
curl -X POST http://127.0.0.1:8000/api/assistant/validate \
  -H "Content-Type: application/json" \
  -d '{"field":"mobile_number","value":"987654321"}'
```

Read back a completed form:

```bash
curl -X POST http://127.0.0.1:8000/api/assistant/summary \
  -H "Content-Type: application/json" \
  -d '{
    "session_id":"generated-session-id",
    "form_values":{
      "applicant_name":"Ravi Kumar",
      "father_name":"Suresh Kumar",
      "mobile_number":"9876543210",
      "aadhaar_number":"123456789012",
      "district":"Hyderabad",
      "mandal":"Ameerpet",
      "village":"Ameerpet",
      "monthly_income":"15000",
      "annual_income":"180000",
      "purpose":"Scholarship",
      "address":"House 1, Ameerpet, Hyderabad"
    }
  }'
```

The summary endpoint uses these frontend-provided values only for that response;
it does not persist them as filled or final values.

## Demo flow

1. Start the backend and open `/docs`.
2. Create a session with `/api/sessions`.
3. Ask `monthly income fifteen thousand what should I enter`.
   The assistant suggests `15000` for Monthly Income and `180000` for Annual
   Income, for the citizen to enter manually.
4. Ask `my mobile number is 987654321`.
   The assistant warns that a mobile number should contain 10 digits.
5. Ask `purpose lo scholarship ani rayacha`.
   The assistant explains that the citizen can enter `Scholarship`.
6. Send sample frontend values to `/api/assistant/summary`.
7. The assistant reads back key details and tells the citizen to review and
   submit the application themselves.

## Tests

From the `backend` directory:

```bash
pytest
```

The suite covers health, form schema, sessions and history, field detection,
spoken-number parsing, income calculations, validation, mixed-language examples,
summaries, missing fields, and the no-auto-fill/no-submit safety contract.

## Docker

```bash
docker build -t niyamguard-call-assistant .
docker run --rm -p 8000:8000 niyamguard-call-assistant
```

For multi-instance or production deployment, replace the JSON session store with
a transactional database or shared cache. JSON storage is intentionally limited
to a single-process MVP.

## Future frontend and voice integration

The HTTP API is already independent of any speech provider. A future browser,
Pipecat, Vapi, LiveKit, or Twilio adapter can transcribe speech, send the text to
`/api/assistant/ask`, and speak the returned `reply`. The adapter must preserve
the same safety boundary: display or speak suggestions only; never write fields,
upload documents, or submit on the citizen's behalf.

The service layer separates field detection, number interpretation, validation,
guidance, session persistence, and orchestration. A future LLM or RAG component
can replace or augment the rule-based guidance engine without changing the API
or granting it frontend control.
