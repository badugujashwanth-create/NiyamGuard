# Platform Orchestrator Notes

The hackathon platform can be presented as three separate modules connected by HTTP contracts:

```text
Government Policy Backend: 8002
Citizen Chatbot Backend: 8001
Voice/Form Assistant Backend: 8000
Citizen Portal Frontend: 5173
Admin Portal Frontend: 5174
Demo Dashboard Frontend: 5175
```

This repository implements the Jashwanth voice/form assistant plus a local demo government-core surface. It does not import code from the other repositories. For a separate-repo presentation, use the scripts in `scripts/check-health.*` to verify local services and keep the limitation visible: the demo is an HTTP-level presentation, not a live government integration.

## Contracts

Shared demo contracts live in `shared-contracts/api-contracts.json`.
