from __future__ import annotations

import hashlib

from app.models.self_update_models import CircularDocument
from app.services.platform_store import add_audit_event, now_iso, read_store, write_store


DEMO_GO_138_TEXT = (
    "GO-138 Revenue Department circular: Income Certificate validity is changed "
    "from 12 months to 6 months. Income certificate must be issued within 6 months "
    "for scholarship and fee reimbursement applications."
)


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def list_documents() -> list[CircularDocument]:
    return read_store().circular_documents


def get_document(circular_id: str) -> CircularDocument | None:
    return next((item for item in read_store().circular_documents if item.id == circular_id), None)


def ingest_circular(payload: dict) -> tuple[CircularDocument, bool]:
    store = read_store()
    timestamp = now_iso()
    raw_text = payload.get("raw_text") or payload.get("source_text") or DEMO_GO_138_TEXT
    digest = content_hash(raw_text)
    existing = next((item for item in store.circular_documents if item.content_hash == digest), None)
    if existing:
        return existing, False
    document = CircularDocument(
        id=payload.get("id") or f"cirdoc_{len(store.circular_documents) + 1:04d}",
        source_id=payload.get("source_id") or "manual",
        circular_number=payload.get("circular_number") or "GO-138",
        title=payload.get("title") or "Income Certificate Validity Amendment",
        department=payload.get("department") or "Revenue",
        published_date=payload.get("published_date") or "2026-06-20",
        effective_date=payload.get("effective_date") or "2026-07-01",
        document_url=payload.get("document_url"),
        storage_path=payload.get("storage_path"),
        raw_text=raw_text,
        content_hash=digest,
        status="ingested",
        created_at=timestamp,
        updated_at=timestamp,
    )
    store.circular_documents.append(document)
    add_audit_event(
        store,
        "circular_ingested",
        {"entity_type": "circular_document", "entity_id": document.id, "circular": document.circular_number},
    )
    write_store(store)
    return document, True
