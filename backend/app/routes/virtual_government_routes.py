from __future__ import annotations

from fastapi import APIRouter

from app.models.virtual_gov_models import VirtualScenarioRequest
from app.services import virtual_government_service

router = APIRouter(prefix="/api/virtual-gov", tags=["Virtual Government Sandbox"])


@router.get("/status")
def status() -> dict:
    return virtual_government_service.status()


@router.get("/scenarios")
def scenarios() -> dict:
    return virtual_government_service.catalog()


@router.post("/run")
def run(payload: VirtualScenarioRequest) -> dict:
    return virtual_government_service.run_scenario(
        payload.scenario_id,
        reset_before_run=payload.reset_before_run,
    )
