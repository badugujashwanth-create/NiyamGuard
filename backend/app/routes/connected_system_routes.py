from fastapi import APIRouter, Depends, HTTPException

from app.models.connected_system_models import ConnectedSystemCreate, SnapshotCreate
from app.security.rbac import require_roles
from app.services import connected_system_service as service

router = APIRouter(prefix="/api/connected-systems", tags=["Connected Systems"])


@router.get("", dependencies=[Depends(require_roles("admin", "reviewer", "viewer"))])
def list_systems() -> dict:
    return {"success": True, "systems": [item.model_dump() for item in service.list_connected_systems()]}


@router.post("", dependencies=[Depends(require_roles("admin", "reviewer"))])
def create_system(payload: ConnectedSystemCreate) -> dict:
    return {"success": True, "system": service.create_connected_system(payload).model_dump()}


@router.get("/{system_id}", dependencies=[Depends(require_roles("admin", "reviewer", "viewer"))])
def get_system(system_id: str) -> dict:
    system = service.get_connected_system(system_id)
    if system is None:
        raise HTTPException(status_code=404, detail="Connected system not found.")
    return {"success": True, "system": system.model_dump()}


@router.post("/{system_id}/snapshots", dependencies=[Depends(require_roles("admin", "reviewer"))])
def create_snapshot(system_id: str, payload: SnapshotCreate) -> dict:
    snapshot = service.create_snapshot(system_id, payload)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Connected system not found.")
    return {"success": True, "snapshot": snapshot.model_dump()}


@router.get("/{system_id}/snapshots", dependencies=[Depends(require_roles("admin", "reviewer", "viewer"))])
def list_snapshots(system_id: str) -> dict:
    if service.get_connected_system(system_id) is None:
        raise HTTPException(status_code=404, detail="Connected system not found.")
    return {"success": True, "snapshots": [item.model_dump() for item in service.list_snapshots(system_id)]}
