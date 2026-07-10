# Final Folder Cleanup Report

Generated: 2026-07-10

## Removed Generated Files And Folders

- `frontend/dist`
- `frontend/playwright-report`
- `frontend/test-results`
- `backend/.pytest_cache`
- recursive `__pycache__` folders under `backend/app`

Only regenerateable junk was removed. No feature components, routes, services, models, tests, or docs were deleted.

## Kept Feature Files

- `VoiceAssistantPanel.jsx`
- `AdminPortal.jsx`
- `DemoDashboard.jsx`
- `VirtualGovernmentSandbox.jsx`
- `MockConnectedSystems.jsx`
- `ServicePortal.jsx`
- `ServiceCatalog.jsx`
- `SchemeFinder.jsx`
- `CitizenPortal.jsx`
- `GovernmentPortal.jsx`
- `UnifiedDemoPortal.jsx`
- backend routes, services, models, and tests

## Kept Demo Assets

Requested screenshots are kept under `docs/recording-assets`:

- `restored-01-home.png`
- `restored-02-citizen-voice-assistant.png`
- `restored-03-government-overview.png`
- `restored-04-circular-policy.png`
- `restored-05-compliance.png`
- `restored-06-virtual-gov.png`
- `restored-07-e2e-result.png`

## Ignored Local/Junk Files

- `.env` files except `.env.example`
- SQLite DB files
- generated uploads/certificates/documents
- `frontend/dist`
- `frontend/node_modules`
- `frontend/playwright-report`
- `frontend/test-results`
- local dataset/vector/search indexes
- local Codex helper logs: `backend/.codex-*.log`
- generated video/screenshot patterns not explicitly requested

## Files That Should Not Be Committed

- `.env` files containing local ports, tokens, or API keys.
- Local SQLite databases.
- Generated certificates and uploaded documents.
- Node modules and build folders.
- Playwright reports, traces, and videos.
- Local model files or vector indexes.
