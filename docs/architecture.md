# Architecture

NiyamGuard AI is organized around one verified knowledge base shared by two portals.

```text
                    Central Verified Knowledge Base
                    circulars, extracted rules, versions,
                    confidence scores, audit trail
                              |
              +---------------+---------------+
              |                               |
      Government Portal                Citizen Portal
 upload, review, compliance      ask, apply, guided help
```

## Runtime Shape

The repository has one backend app and one frontend app:

```text
backend/app/main.py        FastAPI entrypoint
frontend/src/app/App.jsx   React route composition
```

The backend is grouped by API surface, domain service packages, and storage boundaries:

```text
backend/app/api                 HTTP API modules
backend/app/knowledge_base      verified rules, circulars, source sync, publication
backend/app/extraction          rule extraction, deltas, sandbox circulars
backend/app/compliance          drift checks, cascade, priority, propagation
backend/app/audit               audit logging
backend/app/citizen_assistant   guidance, chat, language, validation, schemes
backend/app/forms               form catalog and service portal logic
backend/app/stt                 speech-to-text boundary
backend/app/tts                 text-to-speech boundary
backend/app/demo                full demo, virtual government, certificates, datasets
backend/app/services            shared compatibility helpers and AI subpackages
backend/app/repositories        storage access
backend/app/models              domain/persistence models
backend/app/schemas             request/response schemas
backend/app/security            JWT, password, RBAC, rate limit
backend/app/middleware          request IDs, security headers, logging, errors
backend/app/data                seeded JSON data
```

| Product concern | Current code location |
| --- | --- |
| Knowledge base | `backend/app/knowledge_base` |
| Circular storage | `backend/app/knowledge_base` and `backend/app/extraction` |
| Extraction | `backend/app/extraction` |
| Compliance | `backend/app/compliance` |
| Cascade tracing | `backend/app/compliance` and `backend/app/api/cascade_routes.py` |
| Priority | `backend/app/compliance/priority_service.py` and dashboard APIs |
| Audit | `backend/app/audit`, audit APIs, audit repositories |
| Citizen assistant | `backend/app/citizen_assistant`, AI services, chat APIs |
| Forms | `backend/app/forms` and citizen portal form components |
| STT/TTS | `backend/app/stt`, `backend/app/tts`, speech hooks |
| API grouping | route modules under `backend/app/api` |

## Backend Flow

1. Circular source is synced or uploaded.
2. Rule extraction creates a structured rule candidate with confidence.
3. Officer/reviewer approval is required.
4. Approved candidate is published into verified rule versions.
5. Compliance compares verified rules against mock connected systems.
6. Cascade and priority services explain impact.
7. Audit events record every write/action.
8. Citizen assistant answers from verified rules and citations.

## Frontend Flow

```text
/                       public landing
/citizen                citizen-facing portal
/government             government/admin/officer overview
/admin/*                detailed government tools
/services, /apply/*     synthetic citizen service portal
/officer                officer review
/verify-certificate     public certificate verification
/virtual-gov            virtual government sandbox
```

Core frontend locations:

```text
frontend/src/app/App.jsx
frontend/src/shared/components/UnifiedLanding.jsx
frontend/src/citizen-portal/components/CitizenPortal.jsx
frontend/src/citizen-portal/components/ServicePortal.jsx
frontend/src/citizen-portal/components/VoiceAssistantPanel.jsx
frontend/src/government-portal/components/GovernmentPortal.jsx
frontend/src/government-portal/components/UnifiedDemoPortal.jsx
frontend/src/government-portal/components/AdminPortal.jsx
frontend/src/services/api.js
```

## Knowledge And AI Rule

Official behavior comes from deterministic verified rules and compliance services. Optional Ollama/local AI is used only to explain verified context. If Ollama is unavailable, deterministic fallback remains active.

## Storage

Local development defaults to SQLite and JSON-backed demo store helpers. PostgreSQL is supported through `DATABASE_URL` for production-style deployments. The project should not mix multiple authoritative stores for the same concern in one flow; seeded/demo JSON exists to support local scenarios.

## Sandbox Boundary

The following are mock/demo implementations:

- connected systems
- MeeSeva/public FAQ pages
- payment
- OTP
- certificate signing
- citizen identity
- official circular source feed

Production would require official APIs, secrets management, security audit, accessibility review, department sign-off, and real certificate/signature infrastructure.
