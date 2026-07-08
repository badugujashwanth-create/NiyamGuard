from fastapi import APIRouter, HTTPException

from app.services import conflict_detector as service

router = APIRouter(prefix="/api/conflicts", tags=["conflicts"])


@router.post("/scan")
def scan_conflicts() -> dict:
    return {"success": True, "conflicts": [item.model_dump() for item in service.scan_conflicts()]}


@router.get("")
def list_conflicts() -> dict:
    return {"success": True, "conflicts": [item.model_dump() for item in service.list_conflicts()]}


@router.get("/{conflict_id}")
def get_conflict(conflict_id: str) -> dict:
    conflict = service.get_conflict(conflict_id)
    if conflict is None:
        raise HTTPException(status_code=404, detail="Conflict not found.")
    return {"success": True, "conflict": conflict.model_dump()}


@router.post("/{conflict_id}/resolve")
def resolve_conflict(conflict_id: str) -> dict:
    conflict = service.update_conflict_status(conflict_id, "resolved")
    if conflict is None:
        raise HTTPException(status_code=404, detail="Conflict not found.")
    return {"success": True, "conflict": conflict.model_dump()}


@router.post("/{conflict_id}/ignore")
def ignore_conflict(conflict_id: str) -> dict:
    conflict = service.update_conflict_status(conflict_id, "ignored")
    if conflict is None:
        raise HTTPException(status_code=404, detail="Conflict not found.")
    return {"success": True, "conflict": conflict.model_dump()}
