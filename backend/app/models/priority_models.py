from typing import Literal

from pydantic import BaseModel


PriorityLevel = Literal["low", "medium", "high", "critical"]


class PriorityScore(BaseModel):
    id: str
    finding_id: str
    score: int
    priority_level: PriorityLevel
    citizen_impact_score: int
    urgency_score: int
    service_volume_score: int
    deadline_score: int
    rule_type_score: int
    reason: str
    created_at: str
