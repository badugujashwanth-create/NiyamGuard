from fastapi import APIRouter, HTTPException

from app.services import cascade_trace_service as service

router = APIRouter(prefix="/api/cascade", tags=["cascade"])


@router.get("/finding/{finding_id}")
def get_trace(finding_id: str) -> dict:
    trace = service.get_trace_for_finding(finding_id)
    if trace is None:
        raise HTTPException(status_code=404, detail="Finding not found.")
    return {"success": True, "trace": trace.model_dump()}


@router.post("/generate/{finding_id}")
def generate_trace(finding_id: str) -> dict:
    trace = service.generate_trace(finding_id)
    if trace is None:
        raise HTTPException(status_code=404, detail="Finding not found.")
    return {"success": True, "trace": trace.model_dump()}


@router.get("/service/{service_id}")
def traces_by_service(service_id: str) -> dict:
    return {"success": True, "traces": [item.model_dump() for item in service.traces_by_service(service_id)]}
