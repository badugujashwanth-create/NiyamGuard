"""Compatibility surface for shared service imports.

Domain modules live in sorted packages such as app.knowledge_base, app.compliance,
app.forms, and app.citizen_assistant. This package keeps older grouped imports
like `from app.services import compliance_service` working without eager imports.
"""

from importlib import import_module


_ALIASES = {
    "audit_service": "app.audit.audit_service",
    "cascade_trace_service": "app.compliance.cascade_trace_service",
    "compliance_orchestrator_service": "app.compliance.compliance_orchestrator_service",
    "compliance_service": "app.compliance.compliance_service",
    "conflict_detector": "app.compliance.conflict_detector",
    "connected_system_service": "app.compliance.connected_system_service",
    "mock_system_service": "app.compliance.mock_system_service",
    "priority_service": "app.compliance.priority_service",
    "propagation_service": "app.compliance.propagation_service",
    "report_service": "app.compliance.report_service",
    "system_patch_service": "app.compliance.system_patch_service",
    "assistant_service": "app.citizen_assistant.assistant_service",
    "field_detector": "app.citizen_assistant.field_detector",
    "guidance_engine": "app.citizen_assistant.guidance_engine",
    "income_calculator": "app.citizen_assistant.income_calculator",
    "knowledge_chat_service": "app.citizen_assistant.knowledge_chat_service",
    "language_helper": "app.citizen_assistant.language_helper",
    "location_helper": "app.citizen_assistant.location_helper",
    "scheme_finder_service": "app.citizen_assistant.scheme_finder_service",
    "session_service": "app.citizen_assistant.session_service",
    "validator": "app.citizen_assistant.validator",
    "dataset_service": "app.demo.dataset_service",
    "full_demo_service": "app.demo.full_demo_service",
    "policy_lifecycle_service": "app.demo.policy_lifecycle_service",
    "government_inbox_service": "app.demo.government_inbox_service",
    "pdf_generator": "app.demo.pdf_generator",
    "readiness_service": "app.demo.readiness_service",
    "virtual_government_service": "app.demo.virtual_government_service",
    "rule_delta_service": "app.extraction.rule_delta_service",
    "rule_extraction_service": "app.extraction.rule_extraction_service",
    "sandbox_circular_service": "app.extraction.sandbox_circular_service",
    "form_catalog_service": "app.forms.form_catalog_service",
    "form_service": "app.forms.form_service",
    "service_portal_service": "app.forms.service_portal_service",
    "circular_ingestion_service": "app.knowledge_base.circular_ingestion_service",
    "circular_sync_service": "app.knowledge_base.circular_sync_service",
    "knowledge_base_service": "app.knowledge_base.knowledge_base_service",
    "knowledge_update_service": "app.knowledge_base.knowledge_update_service",
    "platform_store": "app.knowledge_base.platform_store",
    "policy_publication_service": "app.knowledge_base.policy_publication_service",
    "scheduler_service": "app.knowledge_base.scheduler_service",
    "source_registry_service": "app.knowledge_base.source_registry_service",
    "stt_service": "app.stt.stt_service",
    "tts_service": "app.tts.tts_service",
}

__all__ = sorted(_ALIASES)


def __getattr__(name: str):
    if name not in _ALIASES:
        raise AttributeError(name)
    module = import_module(_ALIASES[name])
    globals()[name] = module
    return module
