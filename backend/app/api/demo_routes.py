from fastapi import APIRouter, Depends, HTTPException, Query, Response

from app.security.rbac import CurrentUser, require_roles
from app.services import compliance_service, conflict_detector, full_demo_service, government_inbox_service, priority_service, report_service

router = APIRouter(prefix="/api/demo", tags=["Demo"])


@router.post("/run")
def run_demo(actor: CurrentUser = Depends(require_roles("officer", "reviewer"))) -> dict:
    findings = compliance_service.run_compliance()
    priorities = priority_service.recalculate_priorities()
    conflicts = conflict_detector.scan_conflicts()
    return {
        "success": True,
        "summary": {
            "findings": len(findings),
            "priority_scores": len(priorities),
            "conflicts": len(conflicts),
        },
    }


@router.post("/run-full-end-to-end")
def run_full_end_to_end_demo(actor: CurrentUser = Depends(require_roles("admin"))) -> dict:
    return full_demo_service.run_full_end_to_end_demo()


@router.get("/portal-summary")
def portal_summary(actor: CurrentUser = Depends(require_roles("officer", "reviewer"))) -> dict:
    return government_inbox_service.portal_summary()


@router.get("/reports/export")
def export_demo_report(
    type: str = Query(...),
    format: str = Query(...),
    actor: CurrentUser = Depends(require_roles("officer", "reviewer")),
):
    rows = report_service.report_rows(type)
    if rows is None:
        raise HTTPException(status_code=400, detail="Unsupported report type.")
    metadata = report_service.report_metadata(type, {}, generated_by="demo")
    if format == "json":
        return {"success": True, "type": type, "metadata": metadata, "rows": rows}
    if format == "csv":
        return Response(
            report_service.to_csv(report_service.rows_with_metadata(rows, metadata)),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=demo-{type}.csv"},
        )
    if format == "html":
        return Response(report_service.to_html(rows, metadata), media_type="text/html")
    raise HTTPException(status_code=400, detail="Unsupported export format.")
