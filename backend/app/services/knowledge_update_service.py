from __future__ import annotations

from app.models.self_update_models import KnowledgeUpdateEvent, VerifiedPolicyRuleVersion
from app.services.platform_store import add_audit_event, now_iso, read_store, write_store


def update_for_rule(rule_version: VerifiedPolicyRuleVersion) -> KnowledgeUpdateEvent:
    store = read_store()
    event = KnowledgeUpdateEvent(
        id=f"knowledge_{rule_version.id}",
        rule_version_id=rule_version.id,
        service_id=rule_version.service_id,
        rule_key=rule_version.rule_key,
        update_type="verified_rule_public_api_and_rag",
        status="completed",
        details={
            "public_rule_api": "updated",
            "citizen_assistant": "uses latest verified rule lookup",
            "rag_reindex": "scheduled_or_small_index",
        },
        created_at=now_iso(),
    )
    store.knowledge_update_events = [item for item in store.knowledge_update_events if item.id != event.id]
    store.knowledge_update_events.append(event)
    add_audit_event(store, "knowledge_base_updated", {"entity_type": "rule_version", "entity_id": rule_version.id})
    write_store(store)
    return event


def list_update_events() -> list[KnowledgeUpdateEvent]:
    return read_store().knowledge_update_events
