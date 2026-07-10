from __future__ import annotations

from app.services.platform_store import add_audit_event, now_iso, read_store, reset_demo_store, write_store


def list_mock_systems() -> dict:
    store = read_store()
    return {item.id: item.model_dump() for item in store.mock_connected_systems}


def get_mock_system(system_id: str) -> dict | None:
    return list_mock_systems().get(system_id)


def reset_demo_systems() -> dict:
    store = read_store()
    defaults = reset_demo_store(persist=False).mock_connected_systems
    store.mock_connected_systems = defaults
    add_audit_event(store, "demo_system_reset", {"entity_type": "mock_connected_systems"})
    write_store(store)
    return list_mock_systems()


def apply_demo_patch() -> dict:
    store = read_store()
    for system in store.mock_connected_systems:
        if system.id == "meeseva":
            system.displayed_value = "6 months"
            system.source_circular = "GO-138"
            system.sync_status = "updated"
            system.last_updated_at = now_iso()
            add_audit_event(store, "mock_meeseva_patched", {"entity_type": "mock_system", "entity_id": system.id})
        elif system.id == "public_faq":
            system.faq_value = "6 months"
            system.form_hint_value = "6 months"
            system.source_circular = "GO-138"
            system.sync_status = "updated"
            system.last_updated_at = now_iso()
            add_audit_event(store, "mock_public_faq_patched", {"entity_type": "mock_system", "entity_id": system.id})
    write_store(store)
    return list_mock_systems()
