from __future__ import annotations

from fastapi import APIRouter, Depends

from app.security.rbac import require_roles
from app.services import knowledge_update_service
from app.services.platform_store import read_store

router = APIRouter(prefix="/api/knowledge", tags=["Knowledge Updates"])


@router.get("/update-events", dependencies=[Depends(require_roles("admin", "reviewer", "viewer"))])
def list_update_events() -> dict:
    return {"success": True, "events": [item.model_dump() for item in knowledge_update_service.list_update_events()]}


@router.post("/reindex", dependencies=[Depends(require_roles("admin", "reviewer"))])
def reindex_knowledge() -> dict:
    current_versions = [item for item in read_store().verified_policy_rule_versions if item.is_current]
    events = [knowledge_update_service.update_for_rule(version).model_dump() for version in current_versions]
    return {
        "success": True,
        "events": events,
        "message": "Knowledge update events recorded." if events else "No current rule versions found to reindex.",
    }
