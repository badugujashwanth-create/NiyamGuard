from fastapi import APIRouter, Depends

from app.security.rbac import require_roles
from app.services import priority_service
from app.knowledge_base.platform_store import read_store

router = APIRouter(prefix="/api/dashboard", tags=["Priority Dashboard"])


@router.get("/summary")
def summary() -> dict:
    store = read_store()
    priorities = priority_service.list_priorities()
    return {
        "success": True,
        "summary": {
            "total_circulars": len(store.circulars),
            "pending_extractions": len([item for item in store.extracted_rules if item.status == "pending_review"]),
            "verified_rules": len(store.verified_rules),
            "connected_systems": len(store.connected_systems),
            "compliance_findings": len(store.compliance_findings),
            "drifted_findings": len([item for item in store.compliance_findings if item.status == "drifted"]),
            "critical_findings": len([item for item in priorities if item.priority_level == "critical"]),
            "open_conflicts": len([item for item in store.conflicts if item.status == "open"]),
        },
    }


@router.get("/priority-findings", dependencies=[Depends(require_roles("admin", "reviewer", "viewer"))])
def priority_findings() -> dict:
    return {"success": True, "priority_findings": [item.model_dump() for item in priority_service.list_priorities()]}


@router.get("/high-impact", dependencies=[Depends(require_roles("admin", "reviewer", "viewer"))])
def high_impact() -> dict:
    return {"success": True, "priority_findings": [item.model_dump() for item in priority_service.high_impact()]}


@router.get("/service/{service_id}", dependencies=[Depends(require_roles("admin", "reviewer", "viewer"))])
def service_dashboard(service_id: str) -> dict:
    return {"success": True, "priority_findings": [item.model_dump() for item in priority_service.service_priorities(service_id)]}


@router.post("/recalculate-priority", dependencies=[Depends(require_roles("admin", "reviewer"))])
def recalculate_priority() -> dict:
    return {"success": True, "priority_findings": [item.model_dump() for item in priority_service.recalculate_priorities()]}
