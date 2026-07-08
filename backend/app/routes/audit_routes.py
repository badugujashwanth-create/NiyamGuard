from fastapi import APIRouter, Depends, HTTPException, Query

from app.security.rbac import require_roles
from app.services import audit_service

router = APIRouter(
    prefix="/api/audit",
    tags=["Audit"],
    dependencies=[Depends(require_roles("admin", "reviewer", "viewer"))],
)


@router.get("/events")
def list_events(limit: int = Query(default=100, ge=1, le=500), action: str | None = None) -> dict:
    return {"success": True, "events": audit_service.list_events(limit=limit, action=action)}


@router.get("/events/{event_id}")
def get_event(event_id: str) -> dict:
    event = audit_service.get_event(event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Audit event not found.")
    return {"success": True, "event": event}


@router.get("/verify")
def verify_events() -> dict:
    return audit_service.verify_events()
