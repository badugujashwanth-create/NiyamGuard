from fastapi import APIRouter, Depends

from app.security.rbac import require_roles
from app.knowledge_base.platform_store import read_store

router = APIRouter(
    prefix="/api/admin",
    tags=["Admin"],
    dependencies=[Depends(require_roles("admin"))],
)


MODULES = [
    "central_verified_knowledge_base",
    "connected_systems_registry",
    "compliance_verification_engine",
    "cascade_tracing_impact_analysis",
    "priority_dashboard",
    "cross_circular_conflict_detection",
    "government_admin_apis",
    "reports_export_module",
    "public_verified_rule_apis",
]


@router.get("/summary")
def summary() -> dict:
    store = read_store()
    return {
        "success": True,
        "summary": {
            "total_circulars": len(store.circulars),
            "pending_extractions": len([item for item in store.extracted_rules if item.status == "pending_review"]),
            "verified_rules": len(store.verified_rules),
            "connected_systems": len(store.connected_systems),
            "compliance_findings": len(store.compliance_findings),
            "drifted_findings": len([item for item in store.compliance_findings if item.status == "drifted"]),
            "critical_findings": len([item for item in store.priority_scores if item.priority_level == "critical"]),
            "open_conflicts": len([item for item in store.conflicts if item.status == "open"]),
            "recent_audit_events": len(store.audit_events[-10:]),
        },
    }


@router.get("/recent-activity")
def recent_activity() -> dict:
    return {"success": True, "events": read_store().audit_events[-10:]}


@router.get("/module-status")
def module_status() -> dict:
    return {
        "success": True,
        "modules": [{"name": module, "status": "ready"} for module in MODULES],
    }
