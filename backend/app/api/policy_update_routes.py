from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.security.rbac import CurrentUser, require_roles
from app.services import policy_publication_service

router = APIRouter(prefix="/api/policy-updates", tags=["Policy Updates"])


class PublishPayload(BaseModel):
    notes: str | None = None


class RollbackPayload(BaseModel):
    reason: str | None = None


@router.get("/history", dependencies=[Depends(require_roles("admin", "reviewer", "viewer"))])
def publication_history() -> dict:
    return {
        "success": True,
        "events": [item.model_dump() for item in policy_publication_service.publication_history()],
    }


@router.get("/versions", dependencies=[Depends(require_roles("admin", "reviewer", "viewer"))])
def list_versions() -> dict:
    return {"success": True, "versions": [item.model_dump() for item in policy_publication_service.list_versions()]}


@router.get("/rules/{rule_id}/versions", dependencies=[Depends(require_roles("admin", "reviewer", "viewer"))])
def versions_for_rule(rule_id: str) -> dict:
    return {
        "success": True,
        "versions": [item.model_dump() for item in policy_publication_service.versions_for_rule(rule_id)],
    }


@router.get("/rules/{rule_id}/lineage", dependencies=[Depends(require_roles("admin", "reviewer", "viewer"))])
def rule_lineage(rule_id: str) -> dict:
    lineage = policy_publication_service.lineage_for_rule(rule_id)
    if lineage is None:
        raise HTTPException(status_code=404, detail="Policy rule lineage not found.")
    return {"success": True, "lineage": lineage}


@router.post("/{candidate_id}/publish")
def publish_candidate(
    candidate_id: str,
    payload: PublishPayload | None = None,
    actor: CurrentUser = Depends(require_roles("admin", "reviewer")),
) -> dict:
    result = policy_publication_service.publish_rule_candidate(
        candidate_id,
        reviewer_user_id=actor.id,
        notes=payload.notes if payload else None,
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Policy publication failed."))
    return result


@router.post("/rules/{rule_id}/rollback")
def rollback_rule(
    rule_id: str,
    payload: RollbackPayload | None = None,
    actor: CurrentUser = Depends(require_roles("admin", "reviewer")),
) -> dict:
    result = policy_publication_service.rollback_rule(
        rule_id,
        actor=actor.id,
        reason=payload.reason if payload else None,
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Rollback failed."))
    return result
