from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response

from app.models.sandbox_models import SandboxCircularCreateRequest
from app.security.rbac import CurrentUser, require_roles
from app.services import sandbox_circular_service

router = APIRouter(prefix="/api/sandbox", tags=["Virtual Government Sandbox"])


@router.get("/status")
def status(actor: CurrentUser = Depends(require_roles("sandbox_admin", "admin"))) -> dict:
    return sandbox_circular_service.status()


@router.get("/circulars")
def list_circulars(actor: CurrentUser = Depends(require_roles("sandbox_admin", "admin"))) -> dict:
    return sandbox_circular_service.list_circulars()


@router.post("/circulars")
def create_circular(
    payload: SandboxCircularCreateRequest | None = None,
    actor: CurrentUser = Depends(require_roles("sandbox_admin", "admin")),
) -> dict:
    return sandbox_circular_service.create_circular(payload)


@router.post("/circulars/generate-pdf")
def generate_pdf_from_payload(
    payload: dict | None = None,
    actor: CurrentUser = Depends(require_roles("sandbox_admin", "admin")),
) -> dict:
    circular_id = (payload or {}).get("circular_id")
    if not circular_id:
        created = sandbox_circular_service.create_circular(
            SandboxCircularCreateRequest(**{k: v for k, v in (payload or {}).items() if k != "circular_id"})
            if payload
            else None
        )
        circular_id = created["circular"]["id"]
    result = sandbox_circular_service.generate_pdf(circular_id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("message", "PDF generation failed."))
    return result


@router.post("/circulars/{circular_id}/generate-pdf")
def generate_pdf(
    circular_id: str,
    actor: CurrentUser = Depends(require_roles("sandbox_admin", "admin")),
) -> dict:
    result = sandbox_circular_service.generate_pdf(circular_id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("message", "PDF generation failed."))
    return result


@router.get("/circulars/{circular_id}/pdf")
def download_pdf(
    circular_id: str,
    actor: CurrentUser = Depends(require_roles("sandbox_admin", "admin")),
) -> Response:
    payload = sandbox_circular_service.get_pdf_bytes(circular_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="PDF not found.")
    content, filename = payload
    return Response(
        content,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


@router.post("/circulars/{circular_id}/export")
def export_circular(
    circular_id: str,
    actor: CurrentUser = Depends(require_roles("sandbox_admin", "admin")),
) -> dict:
    result = sandbox_circular_service.export_for_manual_upload(circular_id, actor_id=actor.id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Export failed."))
    return result


@router.post("/circulars/{circular_id}/publish")
def publish_circular(
    circular_id: str,
    actor: CurrentUser = Depends(require_roles("sandbox_admin", "admin")),
) -> dict:
    result = sandbox_circular_service.publish_to_government(circular_id, actor_id=actor.id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Publish failed."))
    return result
