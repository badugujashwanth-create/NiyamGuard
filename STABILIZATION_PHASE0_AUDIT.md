# NiyamGuard Stabilization — Phase 0 Regression Audit

Date: 2026-07-11  
Branch: `feature/global-citizen-voice-assistant`

This audit was completed before stabilization edits. The dirty worktree contains substantial earlier work, which must be preserved unless a phase explicitly requires changing its behavior.

## 1. Admin portal regression

### Current evidence

- A real top-level Admin component still exists: `frontend/src/app/App.jsx` renders `AdminPortal` for `/admin`.
- `AdminPortal` has a dedicated shell and a visible four-item navigation: Dashboard, Sandbox, Audit, and Users.
- Despite that component existing, `frontend/src/utils/authUtils.js` sends the `admin` role to `/government`, so normal login bypasses the dedicated Admin portal.
- The public landing advertises only Citizen and Government and describes government/admin/sandbox work together.
- Hidden render branches remain inside `AdminPortal` for officer/policy features such as compliance, cascade, circulars, rule candidates, propagation, services, forms, certificates, and reports. They are absent from the four-item nav but still directly reachable under `/admin/...`.

### Why the earlier separation did not hold

- Commit `c14fa64` intentionally restructured the product into a two-portal landing and grouped sandbox and policy operations into Government.
- Commit `45876ea` globalized the citizen voice assistant but retained the generalized role mapping in which admin lands in Government and sandbox admin lands at a standalone `/sandbox`.
- The current dirty tree partially restored separate Government and Admin components, but did not correct those role homes or remove legacy cross-portal render branches. Tests were updated to expect the regressed routing, so the regression became protected by tests.

## 2. Sandbox location and data

### Current evidence

- The correct embedded route `/admin/sandbox` exists and renders inside `AdminPortal`.
- Two regressed aliases bypass Admin: sandbox admin lands at `/sandbox`, and `App.jsx` renders `VirtualGovernmentSandbox` as a standalone top-level route.
- `/virtual-gov` already redirects to `/admin/sandbox`.
- The sandbox header links to `/admin/policy-updates`, an officer/policy workflow that should not be inside the isolated Admin portal.

### Data/PDF status

- The configured department, circular number, title, service, changed field, old/new values, effective date, and body are posted and persisted.
- Generated PDFs contain those actual values, and publish uses the same PDF-backed record to create the Government inbox item with audit events.
- The earlier real-data PDF fix has not regressed. It needs broader multi-service regression coverage, not another PDF implementation.

## 3. Circular Intake clumsiness

- The same `CircularUploadPanel` appears in both Overview and Circular Intake. Phase 5 explicitly requires removing it from Overview.
- In Intake, the upload form appears before the page heading/flow explanation.
- The panel uses layout class names that have no matching CSS rules, producing inconsistent layout.
- Officers must enter the file plus circular number, title, department, and effective date before seeing extraction output.
- Upload and global circular/candidate tables are not visually linked into an upload → extraction result/confidence → approve/reject flow.
- Only approval is wired in this UI although the existing backend already supports rejection.
- No clear PDF/open-document action appears in the intake table.
- Initial page load can automatically run compliance and priority mutations when lists are empty; loading a dashboard should be read-only.

## 4. Voice assistant baseline and multilingual status

### What is working

- Real audio is recorded with `MediaRecorder`, posted to `/api/stt/transcribe`, and the returned transcript goes through the same `processTranscript`/`onAsk` path as browser speech and typed input.
- Browser final transcripts also enter that same path unchanged.
- Form help, verified-rule lookup, and knowledge/chat questions route to real deterministic or verified services; runtime probes returned distinct answers. The globally hardcoded-response bug has not regressed.
- The backend logs the exact assistant request text.

### What is incomplete

- `faster-whisper` is not in `backend/requirements.txt` and is not installed. The live backend STT route returns 503 without a caller-supplied fallback transcript, so the standard install relies entirely on browser speech recognition.
- First-turn recognition starts as `en-IN`; there is no English/Telugu language selector. Telugu is selected only after text has already been recognized and answered.
- Backend recording waits for a fixed 4.5-second chunk and uses synchronous CPU transcription; this is not low-latency/real-time behavior.
- Several deterministic replies force English for Telugu questions, including occupation/mandal and verified validity. Telugu TTS can therefore read English text with a Telugu voice.
- gTTS supports English/Telugu output but requires network. Bhashini is configurable but explicitly unimplemented.
- Duplicate suppression persists across completed turns, so repeating the same legitimate utterance is treated as a failed capture.
- If `onAsk` fails, the panel can remain in “Thinking” instead of resuming or surfacing a clear recoverable state.
- Existing voice tests inject fake transcripts and monkeypatched audio; they do not prove real English/Telugu audio transcription, provider readiness, or latency.

## 5. Scheme Finder category regression

- `scheme_finder_service.py` builds recommendations from the certificate/form catalog rather than a scheme dataset.
- Student profiles return Income Certificate and Caste/Community Certificate; pension can return No Earning Member Certificate; farmers can receive Loan Eligibility Card; EWS returns EWS Certificate; the default is Residence Certificate.
- The UI title says “Find services,” its purpose list includes “Certificate” and “EWS certificate,” and result actions call `onStartForm(form_id)`.
- There is no scheme-vs-certificate type discriminator in the Scheme Finder data model because there is no dedicated scheme model/data file.
- Only a few genuine welfare entries exist in `LOCAL_KNOWLEDGE`; the repository merely re-exports that dictionary and does not drive the current matcher.
- Therefore the reported category confusion is confirmed: current recommendations are mostly certificates, not benefit schemes.

## 6. Portal/RBAC isolation gaps

- Frontend role homes/routes allow admin across citizen, government, and sandbox, and unknown authenticated paths default to allowed.
- Citizen application/profile/payment APIs accept admin.
- Government/officer application, circular, compliance, priority, and cascade APIs generally accept admin.
- Several nominally admin APIs accept reviewer/viewer.
- `/api/dashboard/summary` is unauthenticated.
- Government audit returns the global audit list instead of filtering to the current officer’s actions.
- Application Review navigates out of the Government layout to a separate officer `ServicePortal`, producing a second officer nav rather than one coherent portal.

The RBAC primitive correctly rejects roles not listed; the endpoint role lists and frontend mappings are the source of the isolation weakness.

## 7. Additional Phase 4/8 risk found during audit

- Circular extraction is hardcoded to one case: Income Certificate validity changing to 6 months. Sandbox PDFs for other services are real, but uploading those documents cannot produce a rule candidate through the same pipeline.
- Current automated tests encode several regressed expectations: upload on Overview, admin landing in Government, standalone `/sandbox`, and broad admin access.
- Current E2E uses typed assistant input and fake/unit speech transcripts; it does not satisfy real bilingual audio verification.

## Stabilization work implied by this audit

1. Make `/admin` the real admin landing, keep sandbox only at `/admin/sandbox`, and make Admin render only dashboard/sandbox/global audit/users.
2. Keep officer operations in one Government layout, make Overview read-only, and rebuild Circular Intake as a linked review flow with approve/reject.
3. Tighten route and endpoint roles so citizen/officer/admin portals are disjoint, while public verification remains public.
4. Install/document a real bilingual STT provider, add language selection and language-matched deterministic output, reduce capture latency, and add real-audio tests.
5. Add a dedicated raw scheme dataset and scheme model/type, expand it across departments, and make the matcher return schemes only.
6. Generalize deterministic extraction enough for the three-department sandbox demo while preserving human approval.
7. Update tests and docs to prove the intended architecture rather than the regressed one.
