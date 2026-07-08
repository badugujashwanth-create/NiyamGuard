from app.services import report_service


class ReportRepository:
    def rows(self, report_type: str, filters: dict | None = None):
        return report_service.report_rows(report_type, filters)


report_repository = ReportRepository()
