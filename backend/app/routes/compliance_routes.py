from fastapi import APIRouter, HTTPException

from app.services import compliance_service as service

router = APIRouter(prefix="/api/compliance", tags=["compliance"])


@router.post("/run")
def run_compliance() -> dict:
    return {"success": True, "findings": [item.model_dump() for item in service.run_compliance()]}


@router.get("/findings")
def list_findings() -> dict:
    return {"success": True, "findings": [item.model_dump() for item in service.list_findings()]}


@router.get("/findings/{finding_id}")
def get_finding(finding_id: str) -> dict:
    finding = service.get_finding(finding_id)
    if finding is None:
        raise HTTPException(status_code=404, detail="Finding not found.")
    return {"success": True, "finding": finding.model_dump()}


@router.get("/service/{service_id}")
def findings_by_service(service_id: str) -> dict:
    return {"success": True, "findings": [item.model_dump() for item in service.findings_by_service(service_id)]}


@router.get("/system/{connected_system_id}")
def findings_by_system(connected_system_id: str) -> dict:
    return {"success": True, "findings": [item.model_dump() for item in service.findings_by_system(connected_system_id)]}


@router.post("/findings/{finding_id}/mark-fixed")
def mark_fixed(finding_id: str) -> dict:
    finding = service.mark_fixed(finding_id)
    if finding is None:
        raise HTTPException(status_code=404, detail="Finding not found.")
    return {"success": True, "finding": finding.model_dump()}
