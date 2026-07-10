from __future__ import annotations

from app.models.self_update_models import CircularSyncJob
from app.services import circular_ingestion_service, source_registry_service
from app.services.platform_store import add_audit_event, now_iso, read_store, write_store


def sync_source(source_id: str, created_by: str | None = None) -> dict:
    source = source_registry_service.get_source(source_id)
    if source is None:
        return {"success": False, "message": "Source not found."}
    store = read_store()
    timestamp = now_iso()
    job = CircularSyncJob(
        id=f"sync_{len(store.circular_sync_jobs) + 1:04d}",
        source_id=source.id,
        status="running",
        started_at=timestamp,
        created_by=created_by,
        created_at=timestamp,
    )
    store.circular_sync_jobs.append(job)
    write_store(store)

    try:
        if source.source_type == "local_demo":
            document, created = circular_ingestion_service.ingest_circular(
                {
                    "source_id": source.id,
                    "id": "cirdoc_go_138",
                    "circular_number": "GO-138",
                    "title": "Income Certificate Validity Amendment",
                    "department": "Revenue",
                    "published_date": "2026-06-20",
                    "effective_date": "2026-07-01",
                }
            )
            new_count = 1 if created else 0
        else:
            document = None
            new_count = 0
        store = read_store()
        job = next(item for item in store.circular_sync_jobs if item.id == job.id)
        job.status = "success"
        job.completed_at = now_iso()
        job.new_documents_found = new_count
        source = next(item for item in store.official_circular_sources if item.id == source_id)
        source.last_checked_at = job.completed_at
        source.last_success_at = job.completed_at
        source.updated_at = job.completed_at
        add_audit_event(store, "source_synced", {"entity_type": "source", "entity_id": source_id})
        write_store(store)
        return {"success": True, "job": job.model_dump(), "document": document.model_dump() if document else None}
    except Exception as exc:
        store = read_store()
        job = next(item for item in store.circular_sync_jobs if item.id == job.id)
        job.status = "failed"
        job.completed_at = now_iso()
        job.error_message = "Circular sync failed."
        add_audit_event(store, "source_sync_failed", {"entity_type": "source", "entity_id": source_id})
        write_store(store)
        return {"success": False, "message": "Circular sync failed.", "error": str(exc)}


def sync_all(created_by: str | None = None) -> dict:
    results = [
        sync_source(source.id, created_by=created_by)
        for source in source_registry_service.list_sources()
        if source.enabled
    ]
    return {"success": True, "results": results}
