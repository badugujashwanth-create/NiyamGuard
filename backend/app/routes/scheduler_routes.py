from __future__ import annotations

from fastapi import APIRouter, Depends

from app.security.rbac import require_roles
from app.services import scheduler_service

router = APIRouter(prefix="/api/scheduler", tags=["Circular Scheduler"])


@router.get("/status", dependencies=[Depends(require_roles("admin", "reviewer", "viewer"))])
def scheduler_status() -> dict:
    return {"success": True, "scheduler": scheduler_service.status()}


@router.post("/run-now", dependencies=[Depends(require_roles("admin", "reviewer"))])
def scheduler_run_now() -> dict:
    return scheduler_service.run_now()
