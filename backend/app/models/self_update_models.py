from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

SourceType = Literal["url", "rss", "api", "manual_upload", "local_demo"]
SyncStatus = Literal["pending", "running", "success", "failed"]
CircularDocumentStatus = Literal["ingested", "extracted", "pending_review", "published", "rejected"]
CandidateStatus = Literal["candidate", "pending_review", "needs_revision", "approved", "rejected"]
ExtractionMethod = Literal["deterministic", "ollama", "manual"]
ChangeType = Literal["new_rule", "changed_value", "superseded", "no_change"]
ImpactLevel = Literal["low", "medium", "high", "critical"]
ReviewStatus = Literal["pending", "approved", "rejected", "needs_clarification"]
TaskType = Literal["update_portal", "update_form", "update_faq", "update_sop", "notify_owner"]
TaskStatus = Literal["pending", "auto_patched", "needs_manual_update", "completed", "failed"]
PatchStatus = Literal["drafted", "applied", "failed", "rolled_back"]
ComplianceRunTrigger = Literal["manual", "policy_update", "patch_applied", "scheduled"]


class OfficialCircularSource(BaseModel):
    id: str
    name: str
    department: str
    source_type: SourceType
    url: str | None = None
    enabled: bool = True
    last_checked_at: str | None = None
    last_success_at: str | None = None
    created_at: str
    updated_at: str


class CircularSyncJob(BaseModel):
    id: str
    source_id: str
    status: SyncStatus
    started_at: str | None = None
    completed_at: str | None = None
    new_documents_found: int = 0
    error_message: str | None = None
    created_by: str | None = None
    created_at: str


class CircularDocument(BaseModel):
    id: str
    source_id: str
    circular_number: str
    title: str
    department: str
    published_date: str
    effective_date: str
    expiry_date: str | None = None
    document_url: str | None = None
    storage_path: str | None = None
    raw_text: str
    content_hash: str
    status: CircularDocumentStatus
    created_at: str
    updated_at: str


class CircularExtraction(BaseModel):
    id: str
    circular_id: str
    status: str
    extraction_method: ExtractionMethod
    candidate_ids: list[str] = Field(default_factory=list)
    error_message: str | None = None
    created_at: str


class PolicyRuleCandidate(BaseModel):
    id: str
    circular_id: str
    service_id: str
    rule_key: str
    old_value: str | None = None
    new_value: str
    unit: str | None = None
    effective_date: str
    expiry_date: str | None = None
    confidence_score: float
    extraction_method: ExtractionMethod
    source_excerpt: str
    status: CandidateStatus
    requires_review: bool = True
    created_at: str


class PolicyRuleDelta(BaseModel):
    id: str
    candidate_id: str
    existing_rule_id: str | None = None
    change_type: ChangeType
    previous_value: str | None = None
    proposed_value: str
    impact_level: ImpactLevel
    reason: str
    created_at: str


class RuleApprovalWorkflow(BaseModel):
    id: str
    candidate_id: str
    reviewer_user_id: str | None = None
    status: ReviewStatus
    review_notes: str | None = None
    reviewed_at: str | None = None
    created_at: str


class VerifiedPolicyRuleVersion(BaseModel):
    id: str
    rule_id: str
    version_number: int
    service_id: str
    rule_key: str
    value: str
    unit: str | None = None
    source_circular_id: str
    source_circular_number: str
    effective_date: str
    expiry_date: str | None = None
    published_by: str | None = None
    published_at: str
    is_current: bool
    previous_version_id: str | None = None


class PolicyPublicationEvent(BaseModel):
    id: str
    candidate_id: str
    rule_version_id: str
    service_id: str
    rule_key: str
    old_value: str | None = None
    new_value: str
    published_by: str | None = None
    created_at: str


class KnowledgeUpdateEvent(BaseModel):
    id: str
    rule_version_id: str
    service_id: str
    rule_key: str
    update_type: str
    status: str
    details: dict[str, Any] = Field(default_factory=dict)
    created_at: str


class PropagationPlan(BaseModel):
    id: str
    rule_version_id: str
    service_id: str
    rule_key: str
    task_ids: list[str] = Field(default_factory=list)
    status: str
    created_at: str


class PropagationTask(BaseModel):
    id: str
    rule_version_id: str
    connected_system_id: str
    task_type: TaskType
    status: TaskStatus
    old_value: str | None = None
    new_value: str
    patch_payload_json: dict[str, Any] = Field(default_factory=dict)
    assigned_to: str | None = None
    created_at: str
    completed_at: str | None = None


class ConnectedSystemPatch(BaseModel):
    id: str
    propagation_task_id: str
    connected_system_id: str
    patch_type: str
    before_snapshot_json: dict[str, Any] = Field(default_factory=dict)
    after_snapshot_json: dict[str, Any] = Field(default_factory=dict)
    status: PatchStatus
    created_at: str
    applied_at: str | None = None


class RollbackEvent(BaseModel):
    id: str
    rule_id: str
    from_version_id: str
    to_version_id: str
    rolled_back_by: str | None = None
    reason: str | None = None
    created_at: str


class ComplianceRunRecord(BaseModel):
    id: str
    trigger_type: ComplianceRunTrigger
    triggered_by: str | None = None
    affected_rule_id: str | None = None
    started_at: str
    completed_at: str | None = None
    finding_count: int = 0


class MockConnectedSystemState(BaseModel):
    id: str
    system_name: str
    service_id: str
    rule_key: str
    expected_value: str
    source_circular: str
    sync_status: Literal["outdated", "updated"]
    last_updated_at: str | None = None
    displayed_value: str | None = None
    faq_value: str | None = None
    form_hint_value: str | None = None
