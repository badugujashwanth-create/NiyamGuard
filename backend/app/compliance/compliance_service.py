import re

from app.models.compliance_models import ComplianceFinding
from app.models.connected_system_models import ConnectedSystem, ConnectedSystemRuleSnapshot
from app.models.knowledge_models import VerifiedPolicyRule
from app.knowledge_base.platform_store import add_audit_event, now_iso, read_store, write_store


def normalize_rule_value(value: str | None, unit: str | None = None) -> str:
    if value is None:
        return ""
    text = str(value).strip().casefold()
    text = re.sub(r"\s+", " ", text)
    text = text.replace("month ", "months ").replace(" month", " months")
    text = text.rstrip(".")
    if unit and unit.casefold() not in text:
        text = f"{text} {unit.casefold()}".strip()
    text = text.replace(" month", " months")
    return text


def expected_display(rule: VerifiedPolicyRule) -> str:
    return f"{rule.current_value} {rule.unit or ''}".strip()


def _latest_active_rules(rules: list[VerifiedPolicyRule]) -> list[VerifiedPolicyRule]:
    latest: dict[tuple[str, str], VerifiedPolicyRule] = {}
    for rule in rules:
        if rule.status != "active":
            continue
        key = (rule.service_id, rule.rule_key)
        if key not in latest or rule.effective_date > latest[key].effective_date:
            latest[key] = rule
    return list(latest.values())


def _severity_for(system: ConnectedSystem, status: str, rule_key: str) -> str:
    if status == "compliant":
        return "low"
    if system.system_type == "portal" and rule_key in {"validity", "eligibility", "deadline"}:
        return "high"
    if system.system_type in {"sop", "form"}:
        return "high" if rule_key in {"validity", "eligibility", "deadline"} else "medium"
    if system.system_type == "faq":
        return "medium"
    return "low"


def _summary(system: ConnectedSystem, rule: VerifiedPolicyRule, snapshot: ConnectedSystemRuleSnapshot | None, status: str) -> str:
    expected = expected_display(rule)
    if status == "missing":
        return f"{system.name} has no snapshot for {rule.rule_name}."
    if status == "compliant":
        return f"{system.name} reflects the current verified rule of {expected}."
    actual = f"{snapshot.displayed_value} {snapshot.unit or ''}".strip() if snapshot else "unknown"
    return (
        f"{system.name} still shows {actual}, but current verified rule "
        f"requires {expected}."
    )


def run_compliance() -> list[ComplianceFinding]:
    store = read_store()
    timestamp = now_iso()
    findings: list[ComplianceFinding] = []
    retained = [
        finding
        for finding in store.compliance_findings
        if finding.status == "compliant" and finding.updated_at != finding.created_at
    ]

    for rule in _latest_active_rules(store.verified_rules):
        systems = [
            system
            for system in store.connected_systems
            if system.service_id == rule.service_id and system.status == "active"
        ]
        for system in systems:
            snapshot = next(
                (
                    item
                    for item in store.snapshots
                    if item.connected_system_id == system.id
                    and item.service_id == rule.service_id
                    and item.rule_key == rule.rule_key
                ),
                None,
            )
            if snapshot is None:
                status = "missing"
                actual = None
            elif normalize_rule_value(snapshot.displayed_value, snapshot.unit) == normalize_rule_value(
                rule.current_value, rule.unit
            ):
                status = "compliant"
                actual = f"{snapshot.displayed_value} {snapshot.unit or ''}".strip()
            else:
                status = "drifted"
                actual = f"{snapshot.displayed_value} {snapshot.unit or ''}".strip()

            finding = ComplianceFinding(
                id=f"find_{rule.id}_{system.id}",
                verified_rule_id=rule.id,
                connected_system_id=system.id,
                snapshot_id=snapshot.id if snapshot else None,
                service_id=rule.service_id,
                rule_key=rule.rule_key,
                expected_value=expected_display(rule),
                actual_value=actual,
                status=status,
                severity=_severity_for(system, status, rule.rule_key),
                finding_summary=_summary(system, rule, snapshot, status),
                source_clause=rule.source_clause,
                recommended_fix=(
                    f"Update {system.name} from {actual or 'missing value'} to {expected_display(rule)}."
                    if status != "compliant"
                    else "No fix required."
                ),
                citizen_impact_reason=(
                    "Citizens may follow an outdated requirement and face delay, wrong approval, or rejection."
                    if status != "compliant"
                    else "No current citizen impact detected."
                ),
                created_at=timestamp,
                updated_at=timestamp,
            )
            findings.append(finding)
            system.last_checked_at = timestamp
            system.updated_at = timestamp

    store.compliance_findings = retained + findings
    add_audit_event(store, "compliance_run_completed", {"findings": len(findings)})
    write_store(store)
    return store.compliance_findings


def list_findings() -> list[ComplianceFinding]:
    return read_store().compliance_findings


def get_finding(finding_id: str) -> ComplianceFinding | None:
    return next((item for item in read_store().compliance_findings if item.id == finding_id), None)


def findings_by_service(service_id: str) -> list[ComplianceFinding]:
    return [item for item in read_store().compliance_findings if item.service_id == service_id]


def findings_by_system(system_id: str) -> list[ComplianceFinding]:
    return [item for item in read_store().compliance_findings if item.connected_system_id == system_id]


def mark_fixed(finding_id: str) -> ComplianceFinding | None:
    store = read_store()
    finding = next((item for item in store.compliance_findings if item.id == finding_id), None)
    if finding is None:
        return None
    finding.status = "compliant"
    finding.severity = "low"
    finding.actual_value = finding.expected_value
    finding.finding_summary = "Finding marked fixed after officer confirmation."
    finding.recommended_fix = "No fix required."
    finding.citizen_impact_reason = "Officer marked the connected system as fixed."
    finding.updated_at = now_iso()
    add_audit_event(store, "compliance_finding_marked_fixed", {"finding_id": finding_id})
    write_store(store)
    return finding
