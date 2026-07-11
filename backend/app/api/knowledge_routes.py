from fastapi import APIRouter, Depends, HTTPException, Query

from app.security.rbac import require_roles
from app.knowledge_base import certificate_baseline_service
from app.services import knowledge_base_service as service

router = APIRouter(prefix="/api/knowledge", tags=["Knowledge Base"])


@router.get("/rules")
def list_rules() -> dict:
    return {"success": True, "rules": [item.model_dump() for item in service.list_rules()]}


@router.get("/rules/latest")
def latest_rule(service_id: str = Query(...), rule_key: str = Query(...)) -> dict:
    return service.latest_rule(service_id, rule_key).model_dump()


@router.get("/rules/{rule_id}")
def get_rule(rule_id: str) -> dict:
    rule = service.get_rule(rule_id)
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found.")
    return {"success": True, "rule": rule.model_dump(), "source": service.source_circular_info(rule_id)}


@router.get("/certificates")
def list_certificate_baselines() -> dict:
    return {"success": True, "certificates": certificate_baseline_service.list_baselines()}


@router.get("/certificates/{service_id}")
def get_certificate_baseline(service_id: str) -> dict:
    baseline = certificate_baseline_service.baseline_for_service(service_id)
    if baseline is None:
        raise HTTPException(status_code=404, detail="Certificate baseline not found.")
    return {"success": True, "certificate": baseline}


@router.get("/services/{service_id}/rules")
def rules_by_service(service_id: str) -> dict:
    return {"success": True, "rules": [item.model_dump() for item in service.rules_by_service(service_id)]}


@router.get("/search")
def search(q: str = Query(default="")) -> dict:
    return {"success": True, "rules": [item.model_dump() for item in service.search_rules(q)]}


@router.post("/rules/{rule_id}/supersede-older", dependencies=[Depends(require_roles("officer", "reviewer"))])
def supersede_older(rule_id: str) -> dict:
    rule = service.supersede_older_rules(rule_id)
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found.")
    return {"success": True, "rule": rule.model_dump()}
