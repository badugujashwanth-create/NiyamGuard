from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.security.rbac import CurrentUser, require_roles
from app.services import circular_ingestion_service, circular_sync_service, rule_extraction_service
from app.services.ollama_client import AIClientFactory

router = APIRouter(prefix="/api/circulars", tags=["Circular Documents"])


class CircularUploadPayload(BaseModel):
    id: str | None = None
    source_id: str | None = None
    circular_number: str | None = None
    title: str | None = None
    department: str | None = None
    published_date: str | None = None
    effective_date: str | None = None
    document_url: str | None = None
    storage_path: str | None = None
    raw_text: str


@router.post("/sync-all")
def sync_all(actor: CurrentUser = Depends(require_roles("admin", "reviewer"))) -> dict:
    return circular_sync_service.sync_all(created_by=actor.id)


@router.post("/upload", dependencies=[Depends(require_roles("admin", "reviewer"))])
def upload_circular(payload: CircularUploadPayload) -> dict:
    document, created = circular_ingestion_service.ingest_circular(payload.model_dump(exclude_none=True))
    return {"success": True, "created": created, "document": document.model_dump()}


@router.get("", dependencies=[Depends(require_roles("admin", "reviewer", "viewer"))])
def list_circulars() -> dict:
    return {
        "success": True,
        "circulars": [item.model_dump() for item in circular_ingestion_service.list_documents()],
    }


@router.get("/{circular_id}", dependencies=[Depends(require_roles("admin", "reviewer", "viewer"))])
def get_circular(circular_id: str) -> dict:
    document = circular_ingestion_service.get_document(circular_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Circular not found.")
    return {"success": True, "circular": document.model_dump()}


@router.post("/{circular_id}/extract-rules")
def extract_rules(
    circular_id: str,
    actor: CurrentUser = Depends(require_roles("admin", "reviewer")),
) -> dict:
    result = rule_extraction_service.extract_rules(circular_id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("message", "Rule extraction failed."))
    result["reviewer_user_id"] = actor.id
    return result


@router.get("/{circular_id}/ai-summary", dependencies=[Depends(require_roles("admin", "reviewer", "viewer"))])
def circular_ai_summary(circular_id: str) -> dict:
    document = circular_ingestion_service.get_document(circular_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Circular not found.")
    fallback = (
        f"{document.circular_number} updates {document.title}. "
        f"Deterministic extraction should review obligations effective {document.effective_date}."
    )
    result = AIClientFactory.get_client().generate_text(
        f"Summarize this circular using only the text:\n\n{document.raw_text}",
        {"fallback_text": fallback},
    )
    return {"success": True, "summary": result.get("text"), "provider": result.get("provider"), "fallback": result.get("fallback")}
