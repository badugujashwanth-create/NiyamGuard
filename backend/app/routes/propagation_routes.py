from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.security.rbac import require_roles
from app.services import propagation_service, system_patch_service
from app.services.platform_store import read_store

router = APIRouter(prefix="/api/propagation", tags=["Propagation"])


@router.get("/plans", dependencies=[Depends(require_roles("admin", "reviewer", "viewer"))])
def list_plans() -> dict:
    return {"success": True, "plans": [item.model_dump() for item in read_store().propagation_plans]}


@router.get("/tasks", dependencies=[Depends(require_roles("admin", "reviewer", "viewer"))])
def list_tasks() -> dict:
    return {"success": True, "tasks": [item.model_dump() for item in propagation_service.list_tasks()]}


@router.get("/tasks/{task_id}", dependencies=[Depends(require_roles("admin", "reviewer", "viewer"))])
def get_task(task_id: str) -> dict:
    task = propagation_service.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Propagation task not found.")
    return {"success": True, "task": task.model_dump()}


@router.post("/tasks/{task_id}/apply-demo-patch", dependencies=[Depends(require_roles("admin", "reviewer"))])
def apply_demo_patch(task_id: str) -> dict:
    result = system_patch_service.apply_demo_patch(task_id)
    if not result.get("success"):
        raise HTTPException(status_code=404, detail=result.get("message", "Demo patch failed."))
    return result


@router.post("/tasks/{task_id}/mark-completed", dependencies=[Depends(require_roles("admin", "reviewer"))])
def mark_completed(task_id: str) -> dict:
    task = propagation_service.mark_completed(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Propagation task not found.")
    return {"success": True, "task": task.model_dump()}


@router.post("/tasks/{task_id}/mark-manual", dependencies=[Depends(require_roles("admin", "reviewer"))])
def mark_manual(task_id: str) -> dict:
    task = propagation_service.mark_manual(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Propagation task not found.")
    return {"success": True, "task": task.model_dump()}
