from app.models.connected_system_models import (
    ConnectedSystem,
    ConnectedSystemCreate,
    ConnectedSystemRuleSnapshot,
    SnapshotCreate,
)
from app.knowledge_base.platform_store import add_audit_event, now_iso, read_store, write_store


def list_connected_systems() -> list[ConnectedSystem]:
    return read_store().connected_systems


def get_connected_system(system_id: str) -> ConnectedSystem | None:
    return next((item for item in read_store().connected_systems if item.id == system_id), None)


def create_connected_system(payload: ConnectedSystemCreate) -> ConnectedSystem:
    store = read_store()
    timestamp = now_iso()
    system = ConnectedSystem(
        id=f"sys_custom_{len(store.connected_systems) + 1:03d}",
        created_at=timestamp,
        updated_at=timestamp,
        last_checked_at=None,
        **payload.model_dump(),
    )
    store.connected_systems.append(system)
    add_audit_event(store, "connected_system_created", {"system_id": system.id})
    write_store(store)
    return system


def list_snapshots(system_id: str) -> list[ConnectedSystemRuleSnapshot]:
    return [
        snapshot
        for snapshot in read_store().snapshots
        if snapshot.connected_system_id == system_id
    ]


def create_snapshot(system_id: str, payload: SnapshotCreate) -> ConnectedSystemRuleSnapshot | None:
    store = read_store()
    if not any(system.id == system_id for system in store.connected_systems):
        return None
    timestamp = now_iso()
    snapshot = ConnectedSystemRuleSnapshot(
        id=f"snap_custom_{len(store.snapshots) + 1:03d}",
        connected_system_id=system_id,
        created_at=timestamp,
        updated_at=timestamp,
        last_synced_at=timestamp,
        **payload.model_dump(),
    )
    store.snapshots.append(snapshot)
    add_audit_event(store, "connected_system_snapshot_created", {"snapshot_id": snapshot.id})
    write_store(store)
    return snapshot
