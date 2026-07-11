from __future__ import annotations

from fastapi import APIRouter, Depends

from app.models.virtual_gov_models import VirtualScenarioRequest
from app.security.rbac import CurrentUser, require_roles
from app.services import virtual_government_service

router = APIRouter(prefix="/api/virtual-gov", tags=["Virtual Government Sandbox"])


@router.get("/status")
def status(actor: CurrentUser = Depends(require_roles("sandbox_admin", "admin"))) -> dict:
    return virtual_government_service.status()


@router.get("/scenarios")
def scenarios(actor: CurrentUser = Depends(require_roles("sandbox_admin", "admin"))) -> dict:
    return virtual_government_service.catalog()


@router.post("/run")
def run(
    payload: VirtualScenarioRequest,
    actor: CurrentUser = Depends(require_roles("sandbox_admin", "admin")),
) -> dict:
    return virtual_government_service.run_scenario(
        payload.scenario_id,
        reset_before_run=payload.reset_before_run,
    )
