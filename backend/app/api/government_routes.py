from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.security.rbac import CurrentUser, require_roles
from app.services import government_inbox_service

router = APIRouter(prefix="/api/government", tags=["Government Admin Portal"])


class ApprovePolicyPayload(BaseModel):
    notes: str | None = None


@router.get("/circular-inbox")
def circular_inbox(actor: CurrentUser = Depends(require_roles("officer", "reviewer", "admin"))) -> dict:
    return government_inbox_service.circular_inbox()


@router.post("/circulars/{circular_id}/parse")
def parse_circular(
    circular_id: str,
    actor: CurrentUser = Depends(require_roles("officer", "reviewer", "admin")),
) -> dict:
    result = government_inbox_service.parse_circular(circular_id, actor_id=actor.id)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Parse failed."))
    return result


@router.post("/policy-updates/{update_id}/approve")
def approve_policy_update(
    update_id: str,
    payload: ApprovePolicyPayload | None = None,
    actor: CurrentUser = Depends(require_roles("officer", "reviewer", "admin")),
) -> dict:
    result = government_inbox_service.approve_policy_update(
        update_id,
        actor_id=actor.id,
        notes=payload.notes if payload else None,
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Approval failed."))
    return result
