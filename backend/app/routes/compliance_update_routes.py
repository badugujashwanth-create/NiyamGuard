from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.security.rbac import CurrentUser, require_roles
from app.services import compliance_orchestrator_service

router = APIRouter(prefix="/api/compliance", tags=["Compliance Runs"])


@router.post("/rerun-for-rule/{rule_id}")
def rerun_for_rule(
    rule_id: str,
    actor: CurrentUser = Depends(require_roles("admin", "reviewer")),
) -> dict:
    run = compliance_orchestrator_service.rerun_for_rule(rule_id, trigger_type="manual", triggered_by=actor.id)
    return {"success": True, "run": run.model_dump()}


@router.get("/runs", dependencies=[Depends(require_roles("admin", "reviewer", "viewer"))])
def list_runs() -> dict:
    return {"success": True, "runs": [item.model_dump() for item in compliance_orchestrator_service.list_runs()]}


@router.get("/runs/{run_id}", dependencies=[Depends(require_roles("admin", "reviewer", "viewer"))])
def get_run(run_id: str) -> dict:
    run = compliance_orchestrator_service.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Compliance run not found.")
    return {"success": True, "run": run.model_dump()}
