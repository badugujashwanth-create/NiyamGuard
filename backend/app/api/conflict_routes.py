from fastapi import APIRouter, Depends, HTTPException, Request

from app.security.rbac import CurrentUser, require_roles
from app.services import conflict_detector as service
from app.services import audit_service

router = APIRouter(prefix="/api/conflicts", tags=["Conflicts"])


@router.post("/scan")
def scan_conflicts(
    request: Request,
    actor: CurrentUser = Depends(require_roles("officer", "reviewer")),
) -> dict:
    conflicts = service.scan_conflicts()
    audit_service.record_event(
        action="conflicts_scanned_by_user",
        actor=actor,
        request=request,
        entity_type="conflict",
        details={"conflicts": len(conflicts)},
    )
    return {"success": True, "conflicts": [item.model_dump() for item in conflicts]}


@router.get("", dependencies=[Depends(require_roles("officer", "reviewer"))])
def list_conflicts() -> dict:
    return {"success": True, "conflicts": [item.model_dump() for item in service.list_conflicts()]}


@router.get("/{conflict_id}", dependencies=[Depends(require_roles("officer", "reviewer"))])
def get_conflict(conflict_id: str) -> dict:
    conflict = service.get_conflict(conflict_id)
    if conflict is None:
        raise HTTPException(status_code=404, detail="Conflict not found.")
    return {"success": True, "conflict": conflict.model_dump()}


@router.post("/{conflict_id}/resolve")
def resolve_conflict(
    conflict_id: str,
    request: Request,
    actor: CurrentUser = Depends(require_roles("officer", "reviewer")),
) -> dict:
    conflict = service.update_conflict_status(conflict_id, "resolved")
    if conflict is None:
        raise HTTPException(status_code=404, detail="Conflict not found.")
    audit_service.record_event(
        action="conflict_resolved_by_user",
        actor=actor,
        request=request,
        entity_type="conflict",
        entity_id=conflict_id,
    )
    return {"success": True, "conflict": conflict.model_dump()}


@router.post("/{conflict_id}/ignore")
def ignore_conflict(
    conflict_id: str,
    request: Request,
    actor: CurrentUser = Depends(require_roles("officer", "reviewer")),
) -> dict:
    conflict = service.update_conflict_status(conflict_id, "ignored")
    if conflict is None:
        raise HTTPException(status_code=404, detail="Conflict not found.")
    audit_service.record_event(
        action="conflict_ignored_by_user",
        actor=actor,
        request=request,
        entity_type="conflict",
        entity_id=conflict_id,
    )
    return {"success": True, "conflict": conflict.model_dump()}
