from typing import Any

from pydantic import BaseModel, Field

from app.models.cascade_models import CascadeTrace
from app.models.compliance_models import ComplianceFinding
from app.models.conflict_models import CircularConflict
from app.models.connected_system_models import ConnectedSystem, ConnectedSystemRuleSnapshot
from app.models.knowledge_models import Circular, ExtractedPolicyRule, VerifiedPolicyRule
from app.models.priority_models import PriorityScore


class PolicyDataStore(BaseModel):
    circulars: list[Circular] = Field(default_factory=list)
    extracted_rules: list[ExtractedPolicyRule] = Field(default_factory=list)
    verified_rules: list[VerifiedPolicyRule] = Field(default_factory=list)
    connected_systems: list[ConnectedSystem] = Field(default_factory=list)
    snapshots: list[ConnectedSystemRuleSnapshot] = Field(default_factory=list)
    compliance_findings: list[ComplianceFinding] = Field(default_factory=list)
    cascade_traces: list[CascadeTrace] = Field(default_factory=list)
    priority_scores: list[PriorityScore] = Field(default_factory=list)
    conflicts: list[CircularConflict] = Field(default_factory=list)
    audit_events: list[dict[str, Any]] = Field(default_factory=list)
