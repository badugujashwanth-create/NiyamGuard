from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response

from app.services import report_service
from app.services import audit_service
from app.security.rbac import CurrentUser, require_roles

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("/summary", dependencies=[Depends(require_roles("officer", "reviewer"))])
def summary() -> dict:
    return {"success": True, "summary": report_service.summary()}


@router.get("/compliance", dependencies=[Depends(require_roles("officer", "reviewer"))])
def compliance_report(
    service_id: str | None = None,
    severity: str | None = None,
    status: str | None = None,
) -> dict:
    return {
        "success": True,
        "report": report_service.compliance_report(
            service_id=service_id,
            severity=severity,
            status=status,
        ),
    }


@router.get("/conflicts", dependencies=[Depends(require_roles("officer", "reviewer"))])
def conflicts_report(status: str | None = None, severity: str | None = None) -> dict:
    return {"success": True, "report": report_service.conflict_report(status=status, severity=severity)}


@router.get("/priority", dependencies=[Depends(require_roles("officer", "reviewer"))])
def priority_report(priority_level: str | None = None) -> dict:
    return {"success": True, "report": report_service.priority_report(priority_level=priority_level)}


@router.get("/rules", dependencies=[Depends(require_roles("officer", "reviewer"))])
def rules_report(service_id: str | None = None, status: str | None = None) -> dict:
    return {"success": True, "report": report_service.rules_report(service_id=service_id, status=status)}


@router.get("/export", dependencies=[Depends(require_roles("officer", "reviewer"))])
def export_report(
    request: Request,
    type: str = Query(...),
    format: str = Query(...),
    service_id: str | None = None,
    severity: str | None = None,
    status: str | None = None,
    priority_level: str | None = None,
    actor: CurrentUser = Depends(require_roles("officer", "reviewer")),
):
    filters = {
        "service_id": service_id,
        "severity": severity,
        "status": status,
        "priority_level": priority_level,
    }
    rows = report_service.report_rows(type, filters)
    if rows is None:
        raise HTTPException(status_code=400, detail="Unsupported report type.")
    metadata = report_service.report_metadata(type, filters, generated_by=actor.email)
    audit_service.record_event(
        action="report_exported",
        actor=actor,
        request=request,
        entity_type="report",
        entity_id=type,
        details={"format": format, "filters": metadata["filters"], "total_records": len(rows)},
    )
    if format == "json":
        return {"success": True, "type": type, "metadata": metadata, "rows": rows}
    if format == "csv":
        return Response(
            report_service.to_csv(report_service.rows_with_metadata(rows, metadata)),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={type}.csv"},
        )
    if format == "html":
        return Response(report_service.to_html(rows, metadata), media_type="text/html")
    raise HTTPException(status_code=400, detail="Unsupported export format.")
