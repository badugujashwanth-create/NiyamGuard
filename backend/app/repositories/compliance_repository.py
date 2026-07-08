from app.models.compliance_models import ComplianceFinding
from app.services.platform_store import read_store, write_store


class ComplianceRepository:
    def list_findings(
        self,
        service_id: str | None = None,
        status: str | None = None,
        severity: str | None = None,
    ) -> list[ComplianceFinding]:
        return [
            finding
            for finding in read_store().compliance_findings
            if service_id in {None, finding.service_id}
            and status in {None, finding.status}
            and severity in {None, finding.severity}
        ]

    def upsert_finding(self, finding: ComplianceFinding) -> ComplianceFinding:
        store = read_store()
        store.compliance_findings = [item for item in store.compliance_findings if item.id != finding.id]
        store.compliance_findings.append(finding)
        write_store(store)
        return finding

    def mark_fixed(self, finding_id: str) -> ComplianceFinding | None:
        return next((item for item in read_store().compliance_findings if item.id == finding_id), None)


compliance_repository = ComplianceRepository()
