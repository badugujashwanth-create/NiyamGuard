from fastapi import APIRouter, Depends, HTTPException, Request

from app.security.rbac import CurrentUser, require_roles
from app.services import compliance_service as service
from app.services import audit_service

router = APIRouter(prefix="/api/compliance", tags=["Compliance"])


@router.post("/run")
def run_compliance(
    request: Request,
    actor: CurrentUser = Depends(require_roles("admin", "reviewer")),
) -> dict:
    findings = service.run_compliance()
    audit_service.record_event(
        action="compliance_run",
        actor=actor,
        request=request,
        entity_type="compliance",
        details={"findings": len(findings)},
    )
    return {"success": True, "findings": [item.model_dump() for item in findings]}


@router.get("/findings", dependencies=[Depends(require_roles("admin", "reviewer", "viewer"))])
def list_findings() -> dict:
    return {"success": True, "findings": [item.model_dump() for item in service.list_findings()]}


@router.get("/findings/{finding_id}", dependencies=[Depends(require_roles("admin", "reviewer", "viewer"))])
def get_finding(finding_id: str) -> dict:
    finding = service.get_finding(finding_id)
    if finding is None:
        raise HTTPException(status_code=404, detail="Finding not found.")
    return {"success": True, "finding": finding.model_dump()}


@router.get("/service/{service_id}", dependencies=[Depends(require_roles("admin", "reviewer", "viewer"))])
def findings_by_service(service_id: str) -> dict:
    return {"success": True, "findings": [item.model_dump() for item in service.findings_by_service(service_id)]}


@router.get("/system/{connected_system_id}", dependencies=[Depends(require_roles("admin", "reviewer", "viewer"))])
def findings_by_system(connected_system_id: str) -> dict:
    return {"success": True, "findings": [item.model_dump() for item in service.findings_by_system(connected_system_id)]}


@router.post("/findings/{finding_id}/mark-fixed")
def mark_fixed(
    finding_id: str,
    request: Request,
    actor: CurrentUser = Depends(require_roles("admin", "reviewer")),
) -> dict:
    finding = service.mark_fixed(finding_id)
    if finding is None:
        raise HTTPException(status_code=404, detail="Finding not found.")
    audit_service.record_event(
        action="compliance_finding_marked_fixed_by_user",
        actor=actor,
        request=request,
        entity_type="compliance_finding",
        entity_id=finding_id,
    )
    return {"success": True, "finding": finding.model_dump()}
