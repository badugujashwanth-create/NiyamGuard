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


def _change_summary(old_value: str | None, new_value: str, unit: str | None = None) -> str:
    old_label = old_value or "Current"
    unit_label = f" {unit}" if unit else ""
    return f"{old_label} -> {new_value}{unit_label}"


def _event_payload(event) -> dict:
    return {
        **event.model_dump(),
        "change_summary": _change_summary(event.old_value, event.new_value),
    }


def _version_payload(version) -> dict:
    return {
        **version.model_dump(),
        "change_summary": _change_summary(None, version.value, version.unit),
    }


@router.get("/history", dependencies=[Depends(require_roles("officer", "reviewer"))])
def publication_history() -> dict:
    return {
        "success": True,
        "events": [_event_payload(item) for item in policy_publication_service.publication_history()],
    }


@router.get("/versions", dependencies=[Depends(require_roles("officer", "reviewer"))])
def list_versions() -> dict:
    return {"success": True, "versions": [_version_payload(item) for item in policy_publication_service.list_versions()]}


@router.get("/rules/{rule_id}/versions", dependencies=[Depends(require_roles("officer", "reviewer"))])
def versions_for_rule(rule_id: str) -> dict:
    return {
        "success": True,
        "versions": [_version_payload(item) for item in policy_publication_service.versions_for_rule(rule_id)],
    }


@router.post("/{candidate_id}/publish")
def publish_candidate(
    candidate_id: str,
    payload: PublishPayload | None = None,
    actor: CurrentUser = Depends(require_roles("officer", "reviewer")),
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
    actor: CurrentUser = Depends(require_roles("officer", "reviewer")),
) -> dict:
    result = policy_publication_service.rollback_rule(
        rule_id,
        actor=actor.id,
        reason=payload.reason if payload else None,
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Rollback failed."))
    return result
