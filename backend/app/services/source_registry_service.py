from __future__ import annotations

from app.models.self_update_models import OfficialCircularSource
from app.services.platform_store import add_audit_event, now_iso, read_store, write_store


def list_sources() -> list[OfficialCircularSource]:
    return read_store().official_circular_sources


def get_source(source_id: str) -> OfficialCircularSource | None:
    return next((item for item in read_store().official_circular_sources if item.id == source_id), None)


def create_source(payload: dict) -> OfficialCircularSource:
    store = read_store()
    timestamp = now_iso()
    source = OfficialCircularSource(
        id=payload.get("id") or f"src_{len(store.official_circular_sources) + 1:04d}",
        name=payload["name"],
        department=payload.get("department") or "Unknown",
        source_type=payload.get("source_type") or "manual_upload",
        url=payload.get("url"),
        enabled=bool(payload.get("enabled", True)),
        created_at=timestamp,
        updated_at=timestamp,
    )
    store.official_circular_sources = [item for item in store.official_circular_sources if item.id != source.id]
    store.official_circular_sources.append(source)
    add_audit_event(store, "source_created", {"entity_type": "source", "entity_id": source.id})
    write_store(store)
    return source


def update_source(source_id: str, payload: dict) -> OfficialCircularSource | None:
    store = read_store()
    source = next((item for item in store.official_circular_sources if item.id == source_id), None)
    if source is None:
        return None
    data = source.model_dump()
    data.update({key: value for key, value in payload.items() if value is not None})
    data["updated_at"] = now_iso()
    updated = OfficialCircularSource(**data)
    store.official_circular_sources = [
        updated if item.id == source_id else item for item in store.official_circular_sources
    ]
    add_audit_event(store, "source_updated", {"entity_type": "source", "entity_id": source_id})
    write_store(store)
    return updated
