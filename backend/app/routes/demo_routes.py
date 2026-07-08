from fastapi import APIRouter, HTTPException, Query, Response

from app.services import compliance_service, conflict_detector, priority_service, report_service

router = APIRouter(prefix="/api/demo", tags=["Demo"])


@router.post("/run")
def run_demo() -> dict:
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


@router.get("/reports/export")
def export_demo_report(type: str = Query(...), format: str = Query(...)):
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
