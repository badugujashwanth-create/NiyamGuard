from __future__ import annotations

from collections import defaultdict
from typing import Any

from app.knowledge_base.platform_store import read_store


ASSESSED_STATUSES = {"compliant", "drifted", "missing"}


def _percentage(numerator: int, denominator: int) -> float | None:
    if denominator <= 0:
        return None
    return round((numerator / denominator) * 100, 1)


def compliance_metrics() -> dict[str, int | float | None]:
    store = read_store()
    active_systems = [item for item in store.connected_systems if item.status == "active"]
    active_system_ids = {item.id for item in active_systems}
    assessed = [
        item
        for item in store.compliance_findings
        if item.status in ASSESSED_STATUSES and item.connected_system_id in active_system_ids
    ]
    compliant = [item for item in assessed if item.status == "compliant"]
    checked_system_ids = {item.connected_system_id for item in assessed}
    return {
        "compliant_findings": len(compliant),
        "assessed_findings": len(assessed),
        "compliance_score": _percentage(len(compliant), len(assessed)),
        "checked_systems": len(checked_system_ids),
        "coverage_score": _percentage(len(checked_system_ids), len(active_systems)),
    }


def department_readiness() -> list[dict[str, Any]]:
    store = read_store()
    systems_by_department: dict[str, list[Any]] = defaultdict(list)
    for system in store.connected_systems:
        if system.status == "active":
            systems_by_department[system.department or "Unassigned"].append(system)

    findings_by_system: dict[str, list[Any]] = defaultdict(list)
    for finding in store.compliance_findings:
        if finding.status in ASSESSED_STATUSES:
            findings_by_system[finding.connected_system_id].append(finding)

    priorities_by_finding = {item.finding_id: item for item in store.priority_scores}
    rows: list[dict[str, Any]] = []
    for department in sorted(systems_by_department):
        systems = systems_by_department[department]
        system_ids = {item.id for item in systems}
        findings = [finding for system_id in system_ids for finding in findings_by_system.get(system_id, [])]
        compliant = [item for item in findings if item.status == "compliant"]
        drifted = [item for item in findings if item.status in {"drifted", "missing"}]
        checked_systems = {item.connected_system_id for item in findings}
        critical = [
            item
            for item in findings
            if item.severity == "critical"
            or (
                priorities_by_finding.get(item.id)
                and priorities_by_finding[item.id].priority_level == "critical"
            )
        ]
        compliance_score = _percentage(len(compliant), len(findings))
        coverage_score = _percentage(len(checked_systems), len(systems))
        if compliance_score is None:
            readiness_status = "not_assessed"
        elif compliance_score == 100 and coverage_score == 100:
            readiness_status = "ready"
        elif compliance_score >= 75 and not critical:
            readiness_status = "attention"
        else:
            readiness_status = "at_risk"
        rows.append(
            {
                "department": department,
                "total_systems": len(systems),
                "checked_systems": len(checked_systems),
                "compliant_findings": len(compliant),
                "drifted_findings": len(drifted),
                "critical_findings": len(critical),
                "compliance_score": compliance_score,
                "coverage_score": coverage_score,
                "readiness_status": readiness_status,
            }
        )
    return rows
