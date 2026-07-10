from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.config import settings
from app.services import (
    circular_ingestion_service,
    circular_sync_service,
    compliance_orchestrator_service,
    mock_system_service,
    policy_publication_service,
    rule_extraction_service,
    system_patch_service,
)

router = APIRouter(prefix="/api/demo", tags=["Self Update Demo"])


class SelfUpdateScenarioPayload(BaseModel):
    apply_demo_patch: bool = False
    reset_mock_systems: bool = False


@router.post("/run-self-update-scenario")
def run_self_update_scenario(payload: SelfUpdateScenarioPayload | None = None) -> dict:
    payload = payload or SelfUpdateScenarioPayload()
    if payload.reset_mock_systems:
        mock_system_service.reset_demo_systems()

    sync = circular_sync_service.sync_all(created_by="demo_self_update")
    document = circular_ingestion_service.get_document("cirdoc_go_138")
    if document is None:
        document, _ = circular_ingestion_service.ingest_circular({"id": "cirdoc_go_138", "source_id": "src_revenue_demo"})

    extraction = rule_extraction_service.extract_rules(document.id)
    candidate_id = (
        extraction.get("candidates", [{}])[0].get("id")
        if extraction.get("candidates")
        else f"cand_{document.id}_income_validity"
    )
    approval = rule_extraction_service.approve_candidate(
        candidate_id,
        reviewer_user_id="demo_reviewer",
        notes="Demo scenario approval.",
    )
    publication = policy_publication_service.publish_rule_candidate(
        candidate_id,
        reviewer_user_id="demo_reviewer",
        notes="Demo scenario publication.",
    )

    patches = []
    should_patch = payload.apply_demo_patch or settings.auto_patch_demo_systems
    plan = publication.get("propagation_plan") or {}
    if should_patch:
        for task_id in plan.get("task_ids", []):
            patch = system_patch_service.apply_demo_patch(task_id)
            if patch.get("success"):
                patches.append(patch)
        mock_system_service.apply_demo_patch()
        rule_id = (publication.get("rule_version") or {}).get("rule_id") or "rule_001"
        compliance_orchestrator_service.rerun_for_rule(rule_id, trigger_type="patch_applied", triggered_by="demo")

    return {
        "success": True,
        "steps": {
            "sync": sync,
            "document": document.model_dump(),
            "extraction": extraction,
            "approval": approval,
            "publication": publication,
            "patches": patches,
            "mock_systems": mock_system_service.list_mock_systems(),
        },
    }
