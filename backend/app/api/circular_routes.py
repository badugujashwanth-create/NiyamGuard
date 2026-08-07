from __future__ import annotations

from io import BytesIO
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pypdf import PdfReader
from pypdf.errors import PdfReadError
from pydantic import BaseModel, Field

from app.security.rbac import CurrentUser, require_roles
from app.security.malware_scan import MalwareDetected, MalwareScanUnavailable, scan_bytes
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
    expiry_date: str | None = None
    raw_text: str = Field(min_length=20, max_length=250_000)


MAX_CIRCULAR_BYTES = 2 * 1024 * 1024
MAX_CIRCULAR_PAGES = 100
ALLOWED_CIRCULAR_UPLOADS = {
    ".pdf": {"application/pdf"},
    ".txt": {"text/plain"},
}


def _extract_uploaded_text(filename: str, content_type: str, content: bytes) -> str:
    suffix = Path(filename).suffix.casefold()
    if suffix not in ALLOWED_CIRCULAR_UPLOADS:
        raise HTTPException(status_code=415, detail="Only synthetic PDF and UTF-8 text circulars are accepted.")
    if content_type not in ALLOWED_CIRCULAR_UPLOADS[suffix]:
        raise HTTPException(status_code=415, detail="Circular file MIME type does not match its extension.")
    if not content or len(content) > MAX_CIRCULAR_BYTES:
        raise HTTPException(status_code=413, detail="Circular file must be between 1 byte and 2 MiB.")
    if suffix == ".txt":
        try:
            text = content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise HTTPException(status_code=400, detail="Text circular must use UTF-8.") from exc
    else:
        if not content.startswith(b"%PDF"):
            raise HTTPException(status_code=400, detail="PDF signature is invalid.")
        try:
            reader = PdfReader(BytesIO(content), strict=True)
            if reader.is_encrypted:
                raise HTTPException(status_code=422, detail="Encrypted PDFs are not accepted.")
            if len(reader.pages) > MAX_CIRCULAR_PAGES:
                raise HTTPException(status_code=413, detail="PDF contains too many pages.")
            text = "\n".join(
                (page.extract_text() or "").strip()
                for page in reader.pages
            ).strip()
        except HTTPException:
            raise
        except (PdfReadError, ValueError, OSError) as exc:
            raise HTTPException(status_code=400, detail="PDF could not be parsed safely.") from exc
    if len(text.strip()) < 20:
        raise HTTPException(
            status_code=422,
            detail="No usable text was found. Use the synthetic text path for scanned PDFs.",
        )
    return text[:250_000]


@router.post("/sync-all")
def sync_all(actor: CurrentUser = Depends(require_roles("admin", "reviewer"))) -> dict:
    return circular_sync_service.sync_all(created_by=actor.id)


@router.post("/upload", dependencies=[Depends(require_roles("admin", "reviewer"))])
def upload_circular(payload: CircularUploadPayload) -> dict:
    try:
        document, created = circular_ingestion_service.ingest_circular(payload.model_dump(exclude_none=True))
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"success": True, "created": created, "document": document.model_dump()}


@router.post("/upload-file", dependencies=[Depends(require_roles("admin", "reviewer"))])
async def upload_circular_file(
    file: UploadFile = File(...),
    circular_number: str = Form(..., min_length=2, max_length=80),
    title: str = Form(..., min_length=3, max_length=160),
    department: str = Form(..., min_length=2, max_length=120),
    published_date: str = Form(...),
    effective_date: str | None = Form(None),
    expiry_date: str | None = Form(None),
) -> dict:
    content = await file.read(MAX_CIRCULAR_BYTES + 1)
    try:
        scan = scan_bytes(content, file.filename or "")
    except MalwareDetected as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except MalwareScanUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    raw_text = _extract_uploaded_text(
        file.filename or "",
        (file.content_type or "").casefold(),
        content,
    )
    try:
        document, created = circular_ingestion_service.ingest_circular(
            {
                "source_id": "manual_upload",
                "circular_number": circular_number,
                "title": title,
                "department": department,
                "published_date": published_date,
                "effective_date": effective_date,
                "expiry_date": expiry_date,
                "raw_text": raw_text,
            }
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {
        "success": True,
        "created": created,
        "synthetic_only": True,
        "malware_scan": scan,
        "document": document.model_dump(),
    }


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
        if result.get("message") == "Circular not found.":
            raise HTTPException(status_code=404, detail=result["message"])
        raise HTTPException(
            status_code=422,
            detail=(result.get("extraction") or {}).get(
                "error_message", "No unambiguous rule candidate was found."
            ),
        )
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
