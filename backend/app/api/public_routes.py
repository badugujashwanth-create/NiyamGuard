from fastapi import APIRouter, Query

from app.config import APP_VERSION, APP_NAME, settings
from app.services import knowledge_base_service
from app.knowledge_base.platform_store import read_store

router = APIRouter(tags=["Public APIs"])


@router.get("/api/public/rules/latest")
def public_latest_rule(service_id: str = Query(...), rule_key: str = Query(...)) -> dict:
    return knowledge_base_service.citizen_safe_answer(service_id, rule_key)


@router.get("/api/public/services/{service_id}/documents")
def public_documents(service_id: str) -> dict:
    if service_id == "income_certificate":
        return {
            "success": True,
            "verified": True,
            "service_id": service_id,
            "documents": ["Aadhaar Card", "Income Proof", "Address Proof", "Passport Size Photo if requested"],
            "source": knowledge_base_service.latest_rule(service_id, "validity").source,
        }
    return {"success": False, "verified": False, "documents": [], "source": None}


@router.get("/api/public/services/{service_id}/eligibility")
def public_eligibility(service_id: str) -> dict:
    if service_id == "income_certificate":
        return {
            "success": True,
            "verified": True,
            "service_id": service_id,
            "eligibility": [
                "Citizen needs an income certificate for scholarship, pension, admission, or welfare service use.",
                "Final eligibility depends on the receiving scheme or department.",
            ],
            "source": knowledge_base_service.latest_rule(service_id, "validity").source,
        }
    return {"success": False, "verified": False, "eligibility": [], "source": None}


@router.get("/api/public/search")
def public_search(q: str = Query(default="")) -> dict:
    rules = knowledge_base_service.search_rules(q)
    return {
        "success": True,
        "verified": bool(rules),
        "results": [
            knowledge_base_service.citizen_safe_answer(rule.service_id, rule.rule_key)
            for rule in rules
        ],
    }


@router.get("/api/integration/health")
def integration_health() -> dict:
    store = read_store()
    return {
        "module": "niyamguard_government_core",
        "status": "online",
        "app": APP_NAME,
        "environment": settings.app_env,
        "version": APP_VERSION,
        "modules": [
            "knowledge_base",
            "connected_systems",
            "compliance",
            "cascade",
            "priority",
            "conflicts",
            "reports",
            "public_rules",
            "voice_assistant",
            "forms",
        ],
        "features": [
            "verified_knowledge_base",
            "connected_systems_registry",
            "compliance_verification",
            "cascade_tracing",
            "priority_dashboard",
            "conflict_detection",
            "reports_export",
            "public_rule_api",
        ],
        "counts": {
            "verified_rules": len(store.verified_rules),
            "connected_systems": len(store.connected_systems),
            "findings": len(store.compliance_findings),
        },
    }
