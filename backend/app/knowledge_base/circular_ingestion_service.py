from __future__ import annotations

import hashlib
import re
from datetime import date

from app.models.self_update_models import CircularDocument
from app.knowledge_base.platform_store import add_audit_event, now_iso, read_store, write_store


DEMO_GO_138_TEXT = (
    "GO-138 Revenue Department circular: Income Certificate validity is changed "
    "from 12 months to 6 months. Income certificate must be issued within 6 months "
    "for scholarship and fee reimbursement applications. Effective 2026-07-01. "
    "This synthetic circular expires on 2027-06-30."
)


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def extract_temporal_metadata(
    text: str,
    *,
    effective_fallback: str | None = None,
    expiry_fallback: str | None = None,
) -> tuple[str, str | None]:
    effective_match = re.search(
        r"\beffective(?:\s+date)?(?:\s+is|\s+on|:)?\s*(\d{4}-\d{2}-\d{2})",
        text,
        flags=re.IGNORECASE,
    )
    expiry_match = re.search(
        r"\b(?:expires?|expiry(?:\s+date)?|valid\s+until)(?:\s+is|\s+on|:)?\s*(\d{4}-\d{2}-\d{2})",
        text,
        flags=re.IGNORECASE,
    )
    effective = effective_match.group(1) if effective_match else (effective_fallback or "")
    expiry = expiry_match.group(1) if expiry_match else expiry_fallback
    if not effective:
        raise ValueError("An effective date is required in ISO YYYY-MM-DD format.")
    effective_value = date.fromisoformat(effective)
    expiry_value = date.fromisoformat(expiry) if expiry else None
    if expiry_value and expiry_value < effective_value:
        raise ValueError("Expiry date cannot be earlier than the effective date.")
    return effective, expiry


def list_documents() -> list[CircularDocument]:
    return read_store().circular_documents


def get_document(circular_id: str) -> CircularDocument | None:
    return next((item for item in read_store().circular_documents if item.id == circular_id), None)


def ingest_circular(payload: dict) -> tuple[CircularDocument, bool]:
    store = read_store()
    timestamp = now_iso()
    raw_text = payload.get("raw_text") or payload.get("source_text") or DEMO_GO_138_TEXT
    effective_date, expiry_date = extract_temporal_metadata(
        raw_text,
        effective_fallback=payload.get("effective_date") or "2026-07-01",
        expiry_fallback=payload.get("expiry_date"),
    )
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
        effective_date=effective_date,
        expiry_date=expiry_date,
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
