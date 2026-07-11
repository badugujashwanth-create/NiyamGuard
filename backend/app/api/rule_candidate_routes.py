from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.security.rbac import CurrentUser, require_roles
from app.services import policy_publication_service, rule_extraction_service
from app.knowledge_base.platform_store import read_store

router = APIRouter(prefix="/api/rule-candidates", tags=["Rule Candidates"])


class ReviewPayload(BaseModel):
    notes: str | None = None


def _delta_by_candidate() -> dict[str, dict]:
    return {item.candidate_id: item.model_dump() for item in read_store().policy_rule_deltas}


def _change_summary(old_value: str | None, new_value: str, unit: str | None) -> str:
    old_label = old_value or "New rule"
    unit_label = f" {unit}" if unit else ""
    return f"{old_label} -> {new_value}{unit_label}"


def _candidate_payload(candidate) -> dict:
    return {
        **candidate.model_dump(),
        "change_summary": _change_summary(candidate.old_value, candidate.new_value, candidate.unit),
    }


@router.get("", dependencies=[Depends(require_roles("officer", "reviewer"))])
def list_candidates() -> dict:
    deltas = _delta_by_candidate()
    candidates = [
        {**_candidate_payload(candidate), "delta": deltas.get(candidate.id)}
        for candidate in rule_extraction_service.list_candidates()
    ]
    return {"success": True, "candidates": candidates}


@router.get("/{candidate_id}", dependencies=[Depends(require_roles("officer", "reviewer"))])
def get_candidate(candidate_id: str) -> dict:
    candidate = rule_extraction_service.get_candidate(candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="Candidate not found.")
    return {"success": True, "candidate": _candidate_payload(candidate), "delta": _delta_by_candidate().get(candidate_id)}


@router.post("/{candidate_id}/approve")
def approve_candidate(
    candidate_id: str,
    payload: ReviewPayload | None = None,
    actor: CurrentUser = Depends(require_roles("officer", "reviewer")),
) -> dict:
    result = rule_extraction_service.approve_candidate(
        candidate_id,
        reviewer_user_id=actor.id,
        notes=payload.notes if payload else None,
    )
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("message", "Candidate not found."))
    publication = policy_publication_service.publish_rule_candidate(
        candidate_id,
        reviewer_user_id=actor.id,
        notes=payload.notes if payload else None,
    )
    if not publication.get("success"):
        raise HTTPException(status_code=400, detail=publication.get("message", "Approved rule publication failed."))
    result["publication"] = publication
    return result


@router.post("/{candidate_id}/reject")
def reject_candidate(
    candidate_id: str,
    payload: ReviewPayload | None = None,
    actor: CurrentUser = Depends(require_roles("officer", "reviewer")),
) -> dict:
    result = rule_extraction_service.reject_candidate(
        candidate_id,
        reviewer_user_id=actor.id,
        notes=payload.notes if payload else None,
    )
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("message", "Candidate not found."))
    return result
