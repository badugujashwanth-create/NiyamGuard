from fastapi import APIRouter, HTTPException, Query, Response

from app.services import report_service

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/summary")
def summary() -> dict:
    return {"success": True, "summary": report_service.summary()}


@router.get("/compliance")
def compliance_report() -> dict:
    return {"success": True, "report": report_service.compliance_report()}


@router.get("/conflicts")
def conflicts_report() -> dict:
    return {"success": True, "report": report_service.conflict_report()}


@router.get("/priority")
def priority_report() -> dict:
    return {"success": True, "report": report_service.priority_report()}


@router.get("/rules")
def rules_report() -> dict:
    return {"success": True, "report": report_service.rules_report()}


@router.get("/export")
def export_report(type: str = Query(...), format: str = Query(...)):
    reports = {
        "compliance": report_service.compliance_report,
        "conflicts": report_service.conflict_report,
        "priority": report_service.priority_report,
        "rules": report_service.rules_report,
    }
    if type not in reports:
        raise HTTPException(status_code=400, detail="Unsupported report type.")
    rows = reports[type]()
    if format == "json":
        return {"success": True, "type": type, "rows": rows}
    if format == "csv":
        return Response(
            report_service.to_csv(rows),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={type}.csv"},
        )
    if format == "html":
        body = "<html><body><pre>" + report_service.to_csv(rows) + "</pre></body></html>"
        return Response(body, media_type="text/html")
    raise HTTPException(status_code=400, detail="Unsupported export format.")
