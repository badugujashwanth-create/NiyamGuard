from typing import Literal

from pydantic import BaseModel

from app.models.compliance_models import Severity


ConflictType = Literal[
    "active_value_conflict",
    "supersession_conflict",
    "effective_date_overlap",
    "document_requirement_conflict",
    "eligibility_conflict",
]
ConflictStatus = Literal["open", "resolved", "ignored"]


class CircularConflict(BaseModel):
    id: str
    service_id: str
    rule_key: str
    conflict_type: ConflictType
    rule_a_id: str
    rule_b_id: str
    severity: Severity
    summary: str
    recommendation: str
    status: ConflictStatus
    created_at: str
    resolved_at: str | None = None
