from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from app.security.rbac import CurrentUser, require_roles
from app.services import government_inbox_service
from app.services import service_portal_service as portal

router = APIRouter(prefix="/api/government", tags=["Government Admin Portal"])


class ApprovePolicyPayload(BaseModel):
    notes: str | None = None


class ApplicationApprovalPayload(BaseModel):
    notes: str | None = None


class ApplicationRejectionPayload(BaseModel):
    reason: str


def _application_error(exc: portal.ServicePortalError) -> None:
    raise HTTPException(status_code=exc.status_code, detail=exc.detail) from exc


@router.get("/applications/pending")
def pending_applications(
    actor: CurrentUser = Depends(require_roles("officer", "reviewer")),
) -> dict:
    try:
        return {"success": True, "applications": portal.pending_officer_queue(actor)}
    except portal.ServicePortalError as exc:
        _application_error(exc)


@router.get("/applications")
def applications(
    actor: CurrentUser = Depends(require_roles("officer", "reviewer")),
) -> dict:
    try:
        return {"success": True, "applications": portal.officer_queue(actor)}
    except portal.ServicePortalError as exc:
        _application_error(exc)


@router.post("/applications/{application_id}/approve")
def approve_application(
    application_id: str,
    payload: ApplicationApprovalPayload,
    actor: CurrentUser = Depends(require_roles("officer", "reviewer")),
) -> dict:
    try:
        return {"success": True, "application": portal.approve_application(actor, application_id, payload.notes)}
    except portal.ServicePortalError as exc:
        _application_error(exc)


@router.post("/applications/{application_id}/reject")
def reject_application(
    application_id: str,
    payload: ApplicationRejectionPayload,
    actor: CurrentUser = Depends(require_roles("officer", "reviewer")),
) -> dict:
    try:
        return {"success": True, "application": portal.reject_application(actor, application_id, payload.reason)}
    except portal.ServicePortalError as exc:
        _application_error(exc)


@router.get("/circular-inbox")
def circular_inbox(actor: CurrentUser = Depends(require_roles("officer", "reviewer"))) -> dict:
    return government_inbox_service.circular_inbox()


@router.get("/circulars/{circular_id}/pdf")
def circular_pdf(
    circular_id: str,
    actor: CurrentUser = Depends(require_roles("officer", "reviewer")),
) -> Response:
    payload = government_inbox_service.get_circular_pdf(circular_id)
    if payload is None:
        raise HTTPException(status_code=404, detail="Circular PDF not found.")
    content, filename = payload
    return Response(
        content,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{filename}"'},
    )


@router.post("/circulars/{circular_id}/parse")
def parse_circular(
    circular_id: str,
    actor: CurrentUser = Depends(require_roles("officer", "reviewer")),
) -> dict:
    result = government_inbox_service.parse_circular(circular_id, actor_id=actor.id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Parse failed."))
    return result


@router.post("/policy-updates/{update_id}/approve")
def approve_policy_update(
    update_id: str,
    payload: ApprovePolicyPayload | None = None,
    actor: CurrentUser = Depends(require_roles("officer", "reviewer")),
) -> dict:
    result = government_inbox_service.approve_policy_update(
        update_id,
        actor_id=actor.id,
        notes=payload.notes if payload else None,
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Approval failed."))
    return result
