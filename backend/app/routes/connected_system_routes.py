from fastapi import APIRouter, HTTPException

from app.models.connected_system_models import ConnectedSystemCreate, SnapshotCreate
from app.services import connected_system_service as service

router = APIRouter(prefix="/api/connected-systems", tags=["connected systems"])


@router.get("")
def list_systems() -> dict:
    return {"success": True, "systems": [item.model_dump() for item in service.list_connected_systems()]}


@router.post("")
def create_system(payload: ConnectedSystemCreate) -> dict:
    return {"success": True, "system": service.create_connected_system(payload).model_dump()}


@router.get("/{system_id}")
def get_system(system_id: str) -> dict:
    system = service.get_connected_system(system_id)
    if system is None:
        raise HTTPException(status_code=404, detail="Connected system not found.")
    return {"success": True, "system": system.model_dump()}


@router.post("/{system_id}/snapshots")
def create_snapshot(system_id: str, payload: SnapshotCreate) -> dict:
    snapshot = service.create_snapshot(system_id, payload)
    if snapshot is None:
        raise HTTPException(status_code=404, detail="Connected system not found.")
    return {"success": True, "snapshot": snapshot.model_dump()}


@router.get("/{system_id}/snapshots")
def list_snapshots(system_id: str) -> dict:
    if service.get_connected_system(system_id) is None:
        raise HTTPException(status_code=404, detail="Connected system not found.")
    return {"success": True, "snapshots": [item.model_dump() for item in service.list_snapshots(system_id)]}
