from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel, Field

from app.config import settings
from app.documents.processing import (
    DocumentProcessingError,
    OCRProcessingError,
    OCRRequiredError,
    extract_document,
)
from app.security.rbac import CurrentUser, require_roles
from app.security.malware_scan import MalwareDetected, MalwareScanUnavailable, scan_bytes
from app.security.source_artifacts import (
    SourceArtifactStorageUnavailable,
    delete_circular_artifact,
    persist_circular_ocr_derivative,
    persist_circular_source,
)
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
    if suffix == ".pdf" and not content.startswith(b"%PDF"):
        raise HTTPException(status_code=400, detail="PDF signature is invalid.")
    try:
        return extract_document(content, filename, content_type).text
    except OCRRequiredError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except OCRProcessingError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except DocumentProcessingError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


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
    filename = file.filename or ""
    content_type = (file.content_type or "").casefold()
    suffix = Path(filename).suffix.casefold()
    if suffix not in ALLOWED_CIRCULAR_UPLOADS:
        raise HTTPException(status_code=415, detail="Only synthetic PDF and UTF-8 text circulars are accepted.")
    if content_type not in ALLOWED_CIRCULAR_UPLOADS[suffix]:
        raise HTTPException(status_code=415, detail="Circular file MIME type does not match its extension.")
    if not content or len(content) > MAX_CIRCULAR_BYTES:
        raise HTTPException(status_code=413, detail="Circular file must be between 1 byte and 2 MiB.")
    if suffix == ".pdf" and not content.startswith(b"%PDF"):
        raise HTTPException(status_code=400, detail="PDF signature is invalid.")
    if suffix == ".txt":
        try:
            content.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise HTTPException(status_code=400, detail="Text circular must use UTF-8.") from exc
    try:
        scan = scan_bytes(content, filename)
    except MalwareDetected as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except MalwareScanUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    if not settings.circular_artifact_storage_enabled:
        raise HTTPException(status_code=503, detail="Source artifact storage is disabled.")
    try:
        artifact = persist_circular_source(content, filename or "source", content_type)
    except SourceArtifactStorageUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    artifact_created = bool(artifact.pop("_storage_created", True))

    def cleanup_original() -> None:
        if artifact_created:
            delete_circular_artifact(str(artifact.get("storage_path")))

    try:
        extraction = extract_document(content, filename, content_type)
    except OCRRequiredError as exc:
        cleanup_original()
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except OCRProcessingError as exc:
        cleanup_original()
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except DocumentProcessingError as exc:
        cleanup_original()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    ocr_storage_path = None
    if extraction.ocr_derivative is not None:
        try:
            ocr_storage_path = persist_circular_ocr_derivative(
                extraction.ocr_derivative,
                source_sha256=str(artifact["source_sha256"]),
            )
        except SourceArtifactStorageUnavailable as exc:
            cleanup_original()
            raise HTTPException(status_code=503, detail=str(exc)) from exc
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
                "raw_text": extraction.text,
                **artifact,
                "malware_scan_status": scan["status"],
                "extraction_source": extraction.extraction_source,
                "ocr_used": extraction.ocr_used,
                "ocr_storage_path": ocr_storage_path,
                "page_provenance": extraction.page_provenance,
            }
        )
    except ValueError as exc:
        cleanup_original()
        delete_circular_artifact(ocr_storage_path)
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {
        "success": True,
        "created": created,
        "synthetic_only": True,
        "malware_scan": scan,
        "source_artifact": {
            "storage_path": document.storage_path,
            "source_sha256": document.source_sha256,
            "source_size_bytes": document.source_size_bytes,
            "extraction_source": document.extraction_source,
            "ocr_used": document.ocr_used,
            "ocr_storage_path": document.ocr_storage_path,
            "page_provenance": document.page_provenance,
        },
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
