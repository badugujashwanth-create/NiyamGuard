# Code Organization Audit

Generated: 2026-07-10

## Current Model Structure

The backend models remain modular under `backend/app/models/`:

- `auth_models.py`
- `audit_models.py`
- `assistant_models.py`
- `cascade_models.py`
- `compliance_models.py`
- `conflict_models.py`
- `connected_system_models.py`
- `database_models.py`
- `dataset_models.py`
- `form_models.py`
- `knowledge_models.py`
- `platform_store_models.py`
- `priority_models.py`
- `self_update_models.py`
- `service_portal_models.py`
- `session_models.py`
- `virtual_gov_models.py`

No giant `backend/app/models.py` file was created.

## Current Service Structure

The service layer remains domain-oriented:

- Auth: `auth_service.py`
- Citizen/service portal: `service_portal_service.py`
- Policy update: `circular_*`, `rule_*`, `policy_publication_service.py`, `propagation_service.py`
- Compliance: `compliance_service.py`, `compliance_orchestrator_service.py`
- Virtual government: `virtual_government_service.py`
- Final demo orchestration: `full_demo_service.py`
- AI: `services/ai/*`, `services/hybrid_intelligence/*`
- Readiness and audit: `readiness_service.py`, `audit_service.py`

The new `full_demo_service.py` is intentionally an orchestrator. It calls existing domain services and does not merge their internals.

## Duplicate Or Confusing Areas

- `services/answer_engine/` and `services/hybrid_intelligence/` both exist. The active public hybrid route uses `hybrid_intelligence`.
- `services/ollama_client.py` and `services/ai/ollama_provider.py` both exist. `ollama_provider.py` is a thin adapter over `OllamaClient`.
- Demo functions exist in both `demo_routes.py` and `demo_self_update_routes.py`. This is acceptable because they serve different scopes: compliance/report demo versus self-update/full-demo flows.

## Files Left Untouched Because Moving Them Is Risky

- Existing model modules were not moved because imports are already spread across routes, services, and tests.
- Existing admin pages were not split further because they are working and heavily covered by tests.
- Existing dataset/RAG services were not reorganized because the demo depends on stable import paths.

## Final Recommended Structure

Keep the current modular layout. If cleanup is done later, do it with a separate migration:

- `models/auth.py`, `models/portal.py`, `models/policy.py`, `models/compliance.py`, `models/audit.py`, `models/virtual_government.py`, `models/answer_engine.py`
- `services/demo/full_demo_service.py` if demo orchestration grows
- `services/ai/` and `services/hybrid_intelligence/` can remain separate because provider execution and answer routing are different concerns

