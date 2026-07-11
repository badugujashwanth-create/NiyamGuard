from __future__ import annotations

from pathlib import Path

from app.services import circular_ingestion_service, policy_publication_service, rule_extraction_service
from app.knowledge_base.platform_store import add_audit_event, now_iso, read_store, write_store
from app.extraction.sandbox_circular_service import _load_records as load_sandbox_circulars

APP_DIR = Path(__file__).resolve().parents[1]


def _inbox_status(document_status: str, sandbox_delivery: str | None) -> str:
    mapping = {
        "ingested": "Received",
        "extracted": "Parsed",
        "pending_review": "Reviewed",
        "published": "Approved",
        "rejected": "Rejected",
    }
    if sandbox_delivery:
        if "Approved" in sandbox_delivery:
            return "Approved"
        if "Parsed" in sandbox_delivery:
            return "Parsed"
        if "Received" in sandbox_delivery:
            return "Received"
    return mapping.get(document_status, "Received")


def circular_inbox() -> dict:
    documents = circular_ingestion_service.list_documents()
    sandbox_records = {item.government_document_id: item for item in load_sandbox_circulars() if item.government_document_id}
    inbox = []
    for document in documents:
        sandbox = sandbox_records.get(document.id)
        inbox.append(
            {
                "id": document.id,
                "circular_number": document.circular_number,
                "title": document.title,
                "department": document.department,
                "affected_service": "Income Certificate"
                if "income" in document.title.casefold() or "income" in document.raw_text.casefold()
                else "General",
                "pdf_available": bool(document.storage_path or document.document_url),
                "pdf_url": document.document_url,
                "status": _inbox_status(document.status, sandbox.delivery_status if sandbox else None),
                "source": document.source_id,
                "effective_date": document.effective_date,
                "sandbox_circular_id": sandbox.id if sandbox else None,
                "document": document.model_dump(),
            }
        )
    inbox.sort(key=lambda item: item["document"]["created_at"], reverse=True)
    return {"success": True, "circulars": inbox}


def get_circular_pdf(circular_id: str) -> tuple[bytes, str] | None:
    document = circular_ingestion_service.get_document(circular_id)
    if document is None or not document.storage_path:
        return None
    path = (APP_DIR / document.storage_path).resolve()
    if APP_DIR.resolve() not in path.parents or not path.is_file():
        return None
    return path.read_bytes(), f"{document.circular_number}.pdf"


def parse_circular(circular_id: str, actor_id: str | None = None) -> dict:
    document = circular_ingestion_service.get_document(circular_id)
    if document is None:
        return {"success": False, "message": "Circular not found in inbox."}
    extraction = rule_extraction_service.extract_rules(circular_id, actor_user_id=actor_id)
    candidate = extraction.get("candidates", [{}])[0] if extraction.get("candidates") else None

    store = read_store()
    add_audit_event(
        store,
        "government_circular_parsed",
        {
            "entity_type": "circular_document",
            "entity_id": circular_id,
            "parsed_by": actor_id,
            "candidate_id": candidate.get("id") if candidate else None,
        },
    )
    write_store(store)

    detected_change = None
    if candidate:
        detected_change = {
            "summary": (
                f"{candidate.get('service_id', 'service').replace('_', ' ').title()} "
                f"{candidate.get('rule_key')} changed from "
                f"{candidate.get('old_value')} {candidate.get('unit', '')} to "
                f"{candidate.get('new_value')} {candidate.get('unit', '')}."
            ),
            "source": document.circular_number,
            "affected_service": candidate.get("service_id"),
            "affected_components": [
                "Citizen service form",
                "Officer workflow",
                "Certificate template",
                "Chatbot knowledge",
                "Connected public FAQ",
            ],
            "candidate": candidate,
        }

    return {
        "success": bool(extraction.get("success")),
        "extraction": extraction,
        "detected_change": detected_change,
        "circular": document.model_dump(),
    }


def approve_policy_update(update_id: str, actor_id: str | None = None, notes: str | None = None) -> dict:
    candidate_id = update_id
    if not candidate_id.startswith("cand_"):
        store = read_store()
        candidate = next((item for item in store.policy_rule_candidates if item.id == update_id), None)
        if candidate is None:
            candidate = next(
                (item for item in store.policy_rule_candidates if item.circular_id == update_id),
                None,
            )
        if candidate is None:
            return {"success": False, "message": "Policy update not found."}
        candidate_id = candidate.id

    approval = rule_extraction_service.approve_candidate(candidate_id, reviewer_user_id=actor_id, notes=notes)
    if not approval.get("success"):
        return approval
    publication = policy_publication_service.publish_rule_candidate(
        candidate_id,
        reviewer_user_id=actor_id,
        notes=notes or "Approved from Government Admin Portal.",
    )
    if not publication.get("success"):
        return publication

    store = read_store()
    candidate = rule_extraction_service.get_candidate(candidate_id)
    if candidate:
        for document in store.circular_documents:
            if document.id == candidate.circular_id:
                document.status = "published"
                document.updated_at = now_iso()
    add_audit_event(
        store,
        "government_policy_update_approved",
        {
            "entity_type": "rule_candidate",
            "entity_id": candidate_id,
            "approved_by": actor_id,
        },
    )
    write_store(store)

    verified_rule = publication.get("rule_version") or {}
    return {
        "success": True,
        "approval": approval,
        "publication": publication,
        "verified_rule": {
            "rule_key": candidate.rule_key if candidate else "validity",
            "value": f"{candidate.new_value} {candidate.unit}" if candidate else publication.get("value"),
            "source": candidate.circular_id if candidate else update_id,
            "status": "Verified",
            "circular_number": next(
                (
                    document.circular_number
                    for document in store.circular_documents
                    if candidate and document.id == candidate.circular_id
                ),
                "GO-138",
            ),
        },
    }


def portal_summary() -> dict:
    store = read_store()
    inbox = circular_inbox()
    return {
        "success": True,
        "portals": {
            "citizen": {"route": "/citizen", "status": "ready"},
            "government": {"route": "/government", "status": "ready", "inbox_count": len(inbox.get("circulars", []))},
            "sandbox": {"route": "/sandbox", "status": "ready"},
            "chatbot": {"route": "/chatbot", "status": "ready"},
        },
        "verified_rules": len(store.verified_rules),
        "audit_events": len(store.audit_events),
        "circular_inbox": inbox.get("circulars", [])[:5],
    }
