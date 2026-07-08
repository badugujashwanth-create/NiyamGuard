import csv
import io
from typing import Any

from app.services import priority_service
from app.services.platform_store import read_store


def summary() -> dict[str, int]:
    store = read_store()
    return {
        "circulars": len(store.circulars),
        "verified_rules": len(store.verified_rules),
        "connected_systems": len(store.connected_systems),
        "compliance_findings": len(store.compliance_findings),
        "conflicts": len(store.conflicts),
        "priority_scores": len(store.priority_scores),
    }


def compliance_report() -> list[dict[str, Any]]:
    return [item.model_dump() for item in read_store().compliance_findings]


def conflict_report() -> list[dict[str, Any]]:
    return [item.model_dump() for item in read_store().conflicts]


def priority_report() -> list[dict[str, Any]]:
    return [item.model_dump() for item in priority_service.list_priorities()]


def rules_report() -> list[dict[str, Any]]:
    return [item.model_dump() for item in read_store().verified_rules]


def to_csv(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return ""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()), extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue()
