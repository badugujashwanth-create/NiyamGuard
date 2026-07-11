from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.security.rbac import CurrentUser, require_roles
from app.services import circular_sync_service, source_registry_service

router = APIRouter(prefix="/api/sources", tags=["Circular Sources"])


class SourcePayload(BaseModel):
    id: str | None = None
    name: str
    department: str | None = None
    source_type: str = "manual_upload"
    url: str | None = None
    enabled: bool = True


class SourcePatchPayload(BaseModel):
    name: str | None = None
    department: str | None = None
    source_type: str | None = None
    url: str | None = None
    enabled: bool | None = None


@router.get("", dependencies=[Depends(require_roles("officer", "reviewer"))])
def list_sources() -> dict:
    return {"success": True, "sources": [item.model_dump() for item in source_registry_service.list_sources()]}


@router.post("", dependencies=[Depends(require_roles("officer", "reviewer"))])
def create_source(payload: SourcePayload) -> dict:
    source = source_registry_service.create_source(payload.model_dump(exclude_none=True))
    return {"success": True, "source": source.model_dump()}


@router.get("/{source_id}", dependencies=[Depends(require_roles("officer", "reviewer"))])
def get_source(source_id: str) -> dict:
    source = source_registry_service.get_source(source_id)
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found.")
    return {"success": True, "source": source.model_dump()}


@router.patch("/{source_id}", dependencies=[Depends(require_roles("officer", "reviewer"))])
def update_source(source_id: str, payload: SourcePatchPayload) -> dict:
    source = source_registry_service.update_source(source_id, payload.model_dump(exclude_unset=True))
    if source is None:
        raise HTTPException(status_code=404, detail="Source not found.")
    return {"success": True, "source": source.model_dump()}


@router.post("/{source_id}/sync")
def sync_source(
    source_id: str,
    actor: CurrentUser = Depends(require_roles("officer", "reviewer")),
) -> dict:
    result = circular_sync_service.sync_source(source_id, created_by=actor.id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("message", "Source sync failed."))
    return result
