from typing import Literal

from pydantic import BaseModel


FindingStatus = Literal["compliant", "drifted", "missing", "unknown"]
Severity = Literal["low", "medium", "high", "critical"]


class ComplianceFinding(BaseModel):
    id: str
    verified_rule_id: str
    connected_system_id: str
    snapshot_id: str | None = None
    service_id: str
    rule_key: str
    expected_value: str
    actual_value: str | None = None
    status: FindingStatus
    severity: Severity
    finding_summary: str
    source_clause: str
    recommended_fix: str
    citizen_impact_reason: str
    created_at: str
    updated_at: str
