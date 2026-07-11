from __future__ import annotations

from io import BytesIO

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from pypdf import PdfReader

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
def sync_all(actor: CurrentUser = Depends(require_roles("officer", "reviewer"))) -> dict:
    return circular_sync_service.sync_all(created_by=actor.id)


@router.post("/upload")
def upload_circular(
    payload: CircularUploadPayload,
    actor: CurrentUser = Depends(require_roles("officer", "reviewer")),
) -> dict:
    document, created = circular_ingestion_service.ingest_circular(
        {**payload.model_dump(exclude_none=True), "created_by": actor.id}
    )
    return {"success": True, "created": created, "document": document.model_dump()}


def _document_text(file_name: str, content_type: str | None, content: bytes) -> str:
    suffix = file_name.casefold().rsplit(".", 1)[-1] if "." in file_name else ""
    if suffix == "pdf" or content_type == "application/pdf":
        try:
            text = "\n".join(page.extract_text() or "" for page in PdfReader(BytesIO(content)).pages)
        except Exception as exc:
            raise HTTPException(status_code=422, detail="The PDF could not be read. Upload a text-based PDF or TXT file.") from exc
    elif suffix in {"txt", "md"} or (content_type or "").startswith("text/"):
        text = content.decode("utf-8", errors="replace")
    else:
        raise HTTPException(status_code=415, detail="Upload a PDF or UTF-8 text circular.")
    if not text.strip():
        raise HTTPException(status_code=422, detail="No extractable text was found in the circular.")
    return text.strip()


@router.post("/upload-file")
async def upload_circular_file(
    file: UploadFile = File(...),
    circular_number: str = Form(...),
    title: str = Form(...),
    department: str = Form(...),
    effective_date: str = Form(...),
    actor: CurrentUser = Depends(require_roles("officer", "reviewer")),
) -> dict:
    content = await file.read()
    if not content:
        raise HTTPException(status_code=422, detail="The uploaded circular is empty.")
    if len(content) > 10 * 1024 * 1024:
        raise HTTPException(status_code=413, detail="Circular files must be 10 MB or smaller.")
    raw_text = _document_text(file.filename or "circular", file.content_type, content)
    document, created = circular_ingestion_service.ingest_circular(
        {
            "source_id": "officer_upload",
            "circular_number": circular_number,
            "title": title,
            "department": department,
            "effective_date": effective_date,
            "document_url": None,
            "storage_path": file.filename,
            "raw_text": raw_text,
            "created_by": actor.id,
        }
    )
    extraction = rule_extraction_service.extract_rules(document.id, actor_user_id=actor.id)
    if not extraction.get("success"):
        raise HTTPException(status_code=422, detail=extraction.get("message") or "No rule change could be extracted.")
    extraction["reviewer_user_id"] = actor.id
    return {
        "success": True,
        "created": created,
        "document": circular_ingestion_service.get_document(document.id).model_dump(),
        **extraction,
    }


@router.get("", dependencies=[Depends(require_roles("officer", "reviewer"))])
def list_circulars() -> dict:
    return {
        "success": True,
        "circulars": [item.model_dump() for item in circular_ingestion_service.list_documents()],
    }


@router.get("/{circular_id}", dependencies=[Depends(require_roles("officer", "reviewer"))])
def get_circular(circular_id: str) -> dict:
    document = circular_ingestion_service.get_document(circular_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Circular not found.")
    return {"success": True, "circular": document.model_dump()}


@router.post("/{circular_id}/extract-rules")
def extract_rules(
    circular_id: str,
    actor: CurrentUser = Depends(require_roles("officer", "reviewer")),
) -> dict:
    result = rule_extraction_service.extract_rules(circular_id, actor_user_id=actor.id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("message", "Rule extraction failed."))
    result["reviewer_user_id"] = actor.id
    return result


@router.get("/{circular_id}/ai-summary", dependencies=[Depends(require_roles("officer", "reviewer"))])
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
