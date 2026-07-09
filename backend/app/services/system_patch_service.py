from __future__ import annotations

from app.models.self_update_models import ConnectedSystemPatch
from app.services import propagation_service
from app.services.platform_store import add_audit_event, now_iso, read_store, write_store


MOCK_SYSTEM_BY_CONNECTED_SYSTEM = {
    "sys_meeseva_portal": "meeseva",
    "sys_public_faq": "public_faq",
    "sys_simplified_form": "public_faq",
}


def apply_demo_patch(task_id: str) -> dict:
    task = propagation_service.get_task(task_id)
    if task is None:
        return {"success": False, "message": "Propagation task not found."}
    store = read_store()
    snapshot = next(
        (item for item in store.snapshots if item.connected_system_id == task.connected_system_id),
        None,
    )
    before = snapshot.model_dump() if snapshot else {}
    if snapshot:
        parts = task.new_value.split(" ", 1)
        snapshot.displayed_value = parts[0]
        snapshot.unit = parts[1] if len(parts) > 1 else snapshot.unit
        snapshot.last_synced_at = now_iso()
        snapshot.updated_at = now_iso()
    mock_id = MOCK_SYSTEM_BY_CONNECTED_SYSTEM.get(task.connected_system_id)
    for system in store.mock_connected_systems:
        if system.id != mock_id:
            continue
        if system.id == "meeseva":
            system.displayed_value = task.new_value
        if system.id == "public_faq":
            system.faq_value = task.new_value
            system.form_hint_value = task.new_value
        system.source_circular = task.patch_payload_json.get("source") or system.source_circular
        system.sync_status = "updated"
        system.last_updated_at = now_iso()
    patch = ConnectedSystemPatch(
        id=f"patch_{task_id}",
        propagation_task_id=task_id,
        connected_system_id=task.connected_system_id,
        patch_type="demo_snapshot_update",
        before_snapshot_json=before,
        after_snapshot_json=snapshot.model_dump() if snapshot else {},
        status="applied",
        created_at=now_iso(),
        applied_at=now_iso(),
    )
    store.connected_system_patches = [item for item in store.connected_system_patches if item.id != patch.id]
    store.connected_system_patches.append(patch)
    task = next(item for item in store.propagation_tasks if item.id == task_id)
    task.status = "auto_patched"
    task.completed_at = now_iso()
    add_audit_event(store, "demo_patch_applied", {"entity_type": "propagation_task", "entity_id": task_id})
    write_store(store)
    return {"success": True, "task": task.model_dump(), "patch": patch.model_dump()}
