from __future__ import annotations

from app.models.self_update_models import ComplianceRunRecord
from app.services import compliance_service
from app.services.platform_store import add_audit_event, now_iso, read_store, write_store


def rerun_for_rule(rule_id: str, trigger_type: str = "manual", triggered_by: str | None = None) -> ComplianceRunRecord:
    store = read_store()
    started_at = now_iso()
    findings = compliance_service.run_compliance()
    store = read_store()
    run = ComplianceRunRecord(
        id=f"compliance_run_{len(store.compliance_runs) + 1:04d}",
        trigger_type=trigger_type,
        triggered_by=triggered_by,
        affected_rule_id=rule_id,
        started_at=started_at,
        completed_at=now_iso(),
        finding_count=len(findings),
    )
    store.compliance_runs.append(run)
    add_audit_event(store, "compliance_rerun", {"entity_type": "verified_rule", "entity_id": rule_id})
    write_store(store)
    return run


def list_runs() -> list[ComplianceRunRecord]:
    return read_store().compliance_runs


def get_run(run_id: str) -> ComplianceRunRecord | None:
    return next((item for item in read_store().compliance_runs if item.id == run_id), None)
