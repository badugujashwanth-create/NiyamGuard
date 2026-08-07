from typing import Any

from sqlalchemy import JSON, Boolean, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PolicyRecord(Base):
    __tablename__ = "policy_records"
    __table_args__ = (
        UniqueConstraint("collection", "item_id", name="uq_policy_record_collection_item"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    collection: Mapped[str] = mapped_column(String(80), index=True)
    item_id: Mapped[str] = mapped_column(String(160), index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)


class PolicyStoreRevision(Base):
    """Singleton revision used to reject stale full-store replacements."""

    __tablename__ = "policy_store_revisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[str] = mapped_column(String(40), nullable=False)


class CircularDocumentRecord(Base):
    __tablename__ = "circular_documents"

    id: Mapped[str] = mapped_column(String(160), primary_key=True)
    source_id: Mapped[str] = mapped_column(String(160), index=True)
    circular_number: Mapped[str] = mapped_column(String(80), index=True)
    title: Mapped[str] = mapped_column(String(200))
    department: Mapped[str] = mapped_column(String(160), index=True)
    published_date: Mapped[str] = mapped_column(String(40))
    effective_date: Mapped[str] = mapped_column(String(40), index=True)
    expiry_date: Mapped[str | None] = mapped_column(String(40), nullable=True)
    document_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    storage_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_filename: Mapped[str | None] = mapped_column(String(160), nullable=True)
    source_content_type: Mapped[str | None] = mapped_column(String(120), nullable=True)
    source_size_bytes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    malware_scan_status: Mapped[str | None] = mapped_column(String(40), nullable=True)
    raw_text: Mapped[str] = mapped_column(Text)
    content_hash: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(40), index=True)
    created_at: Mapped[str] = mapped_column(String(40))
    updated_at: Mapped[str] = mapped_column(String(40))


class PolicyRuleCandidateRecord(Base):
    __tablename__ = "policy_rule_candidates"

    id: Mapped[str] = mapped_column(String(160), primary_key=True)
    circular_id: Mapped[str] = mapped_column(ForeignKey("circular_documents.id"), index=True)
    service_id: Mapped[str] = mapped_column(String(120), index=True)
    rule_key: Mapped[str] = mapped_column(String(120), index=True)
    old_value: Mapped[str | None] = mapped_column(String(200), nullable=True)
    new_value: Mapped[str] = mapped_column(String(200))
    unit: Mapped[str | None] = mapped_column(String(80), nullable=True)
    effective_date: Mapped[str] = mapped_column(String(40), index=True)
    expiry_date: Mapped[str | None] = mapped_column(String(40), nullable=True)
    confidence_score: Mapped[float] = mapped_column(Float)
    extraction_method: Mapped[str] = mapped_column(String(40))
    source_excerpt: Mapped[str] = mapped_column(Text)
    source_start_offset: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source_end_offset: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[str] = mapped_column(String(40), index=True)
    requires_review: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[str] = mapped_column(String(40))


class PolicyRuleDeltaRecord(Base):
    __tablename__ = "policy_rule_deltas"

    id: Mapped[str] = mapped_column(String(160), primary_key=True)
    candidate_id: Mapped[str] = mapped_column(ForeignKey("policy_rule_candidates.id"), index=True)
    existing_rule_id: Mapped[str | None] = mapped_column(String(160), nullable=True, index=True)
    change_type: Mapped[str] = mapped_column(String(40), index=True)
    previous_value: Mapped[str | None] = mapped_column(String(200), nullable=True)
    proposed_value: Mapped[str] = mapped_column(String(200))
    impact_level: Mapped[str] = mapped_column(String(40), index=True)
    reason: Mapped[str] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(String(40))


class RuleApprovalWorkflowRecord(Base):
    __tablename__ = "rule_approval_workflows"

    id: Mapped[str] = mapped_column(String(160), primary_key=True)
    candidate_id: Mapped[str] = mapped_column(ForeignKey("policy_rule_candidates.id"), index=True)
    reviewer_user_id: Mapped[str | None] = mapped_column(String(160), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(40), index=True)
    review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    created_at: Mapped[str] = mapped_column(String(40))


class PolicyPublicationEventRecord(Base):
    __tablename__ = "policy_publication_events"

    id: Mapped[str] = mapped_column(String(160), primary_key=True)
    candidate_id: Mapped[str] = mapped_column(ForeignKey("policy_rule_candidates.id"), index=True)
    rule_version_id: Mapped[str] = mapped_column(ForeignKey("policy_rule_versions.id"), index=True)
    service_id: Mapped[str] = mapped_column(String(120), index=True)
    rule_key: Mapped[str] = mapped_column(String(120), index=True)
    old_value: Mapped[str | None] = mapped_column(String(200), nullable=True)
    new_value: Mapped[str] = mapped_column(String(200))
    published_by: Mapped[str | None] = mapped_column(String(160), nullable=True)
    created_at: Mapped[str] = mapped_column(String(40))


class KnowledgeUpdateEventRecord(Base):
    __tablename__ = "knowledge_update_events"

    id: Mapped[str] = mapped_column(String(160), primary_key=True)
    rule_version_id: Mapped[str] = mapped_column(ForeignKey("policy_rule_versions.id"), index=True)
    service_id: Mapped[str] = mapped_column(String(120), index=True)
    rule_key: Mapped[str] = mapped_column(String(120), index=True)
    update_type: Mapped[str] = mapped_column(String(80), index=True)
    status: Mapped[str] = mapped_column(String(40), index=True)
    details: Mapped[dict[str, Any]] = mapped_column(JSON)
    created_at: Mapped[str] = mapped_column(String(40))


class ComplianceRunRecordModel(Base):
    __tablename__ = "compliance_runs"

    id: Mapped[str] = mapped_column(String(160), primary_key=True)
    trigger_type: Mapped[str] = mapped_column(String(40), index=True)
    triggered_by: Mapped[str | None] = mapped_column(String(160), nullable=True, index=True)
    affected_rule_id: Mapped[str | None] = mapped_column(String(160), nullable=True, index=True)
    started_at: Mapped[str] = mapped_column(String(40))
    completed_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    finding_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class PropagationPlanRecord(Base):
    __tablename__ = "propagation_plans"

    id: Mapped[str] = mapped_column(String(160), primary_key=True)
    rule_version_id: Mapped[str] = mapped_column(ForeignKey("policy_rule_versions.id"), index=True)
    service_id: Mapped[str] = mapped_column(String(120), index=True)
    rule_key: Mapped[str] = mapped_column(String(120), index=True)
    task_ids: Mapped[list[str]] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(40), index=True)
    created_at: Mapped[str] = mapped_column(String(40))


class PropagationTaskRecord(Base):
    __tablename__ = "propagation_tasks"

    id: Mapped[str] = mapped_column(String(160), primary_key=True)
    rule_version_id: Mapped[str] = mapped_column(ForeignKey("policy_rule_versions.id"), index=True)
    connected_system_id: Mapped[str] = mapped_column(String(160), index=True)
    task_type: Mapped[str] = mapped_column(String(40), index=True)
    status: Mapped[str] = mapped_column(String(40), index=True)
    old_value: Mapped[str | None] = mapped_column(String(200), nullable=True)
    new_value: Mapped[str] = mapped_column(String(200))
    patch_payload_json: Mapped[dict[str, Any]] = mapped_column(JSON)
    assigned_to: Mapped[str | None] = mapped_column(String(160), nullable=True, index=True)
    created_at: Mapped[str] = mapped_column(String(40))
    completed_at: Mapped[str | None] = mapped_column(String(40), nullable=True)


class ConnectedSystemPatchRecord(Base):
    __tablename__ = "connected_system_patches"

    id: Mapped[str] = mapped_column(String(160), primary_key=True)
    propagation_task_id: Mapped[str] = mapped_column(ForeignKey("propagation_tasks.id"), index=True)
    connected_system_id: Mapped[str] = mapped_column(String(160), index=True)
    patch_type: Mapped[str] = mapped_column(String(80), index=True)
    before_snapshot_json: Mapped[dict[str, Any]] = mapped_column(JSON)
    after_snapshot_json: Mapped[dict[str, Any]] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(40), index=True)
    created_at: Mapped[str] = mapped_column(String(40))
    applied_at: Mapped[str | None] = mapped_column(String(40), nullable=True)


class RollbackEventRecord(Base):
    __tablename__ = "rollback_events"

    id: Mapped[str] = mapped_column(String(160), primary_key=True)
    rule_id: Mapped[str] = mapped_column(String(160), index=True)
    from_version_id: Mapped[str] = mapped_column(ForeignKey("policy_rule_versions.id"), index=True)
    to_version_id: Mapped[str] = mapped_column(ForeignKey("policy_rule_versions.id"), index=True)
    rolled_back_by: Mapped[str | None] = mapped_column(String(160), nullable=True, index=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[str] = mapped_column(String(40))


class PolicyRuleVersionRecord(Base):
    __tablename__ = "policy_rule_versions"
    __table_args__ = (UniqueConstraint("rule_id", "version_number", name="uq_policy_rule_version_number"),)

    id: Mapped[str] = mapped_column(String(160), primary_key=True)
    rule_id: Mapped[str] = mapped_column(String(160), index=True)
    version_number: Mapped[int] = mapped_column(Integer)
    service_id: Mapped[str] = mapped_column(String(120), index=True)
    rule_key: Mapped[str] = mapped_column(String(120), index=True)
    value: Mapped[str] = mapped_column(String(200))
    unit: Mapped[str | None] = mapped_column(String(80), nullable=True)
    source_circular_id: Mapped[str] = mapped_column(ForeignKey("circular_documents.id"), index=True)
    source_circular_number: Mapped[str] = mapped_column(String(80))
    effective_date: Mapped[str] = mapped_column(String(40), index=True)
    expiry_date: Mapped[str | None] = mapped_column(String(40), nullable=True)
    published_by: Mapped[str | None] = mapped_column(String(160), nullable=True)
    published_at: Mapped[str] = mapped_column(String(40))
    is_current: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    previous_version_id: Mapped[str | None] = mapped_column(String(160), nullable=True)


class ConnectedSystemSnapshotRecord(Base):
    __tablename__ = "connected_system_snapshots"

    id: Mapped[str] = mapped_column(String(160), primary_key=True)
    connected_system_id: Mapped[str] = mapped_column(String(160), index=True)
    service_id: Mapped[str] = mapped_column(String(120), index=True)
    rule_key: Mapped[str] = mapped_column(String(120), index=True)
    displayed_value: Mapped[str] = mapped_column(String(200))
    unit: Mapped[str | None] = mapped_column(String(80), nullable=True)
    source_location: Mapped[str] = mapped_column(String(500))
    last_synced_at: Mapped[str | None] = mapped_column(String(40), nullable=True)
    snapshot_source: Mapped[str] = mapped_column(String(40))
    created_at: Mapped[str] = mapped_column(String(40))
    updated_at: Mapped[str] = mapped_column(String(40))


class ComplianceFindingRecord(Base):
    __tablename__ = "compliance_findings"

    id: Mapped[str] = mapped_column(String(160), primary_key=True)
    verified_rule_id: Mapped[str] = mapped_column(ForeignKey("policy_rule_versions.id"), index=True)
    connected_system_id: Mapped[str] = mapped_column(String(160), index=True)
    snapshot_id: Mapped[str | None] = mapped_column(String(160), nullable=True, index=True)
    service_id: Mapped[str] = mapped_column(String(120), index=True)
    rule_key: Mapped[str] = mapped_column(String(120), index=True)
    expected_value: Mapped[str] = mapped_column(String(200))
    actual_value: Mapped[str | None] = mapped_column(String(200), nullable=True)
    status: Mapped[str] = mapped_column(String(40), index=True)
    severity: Mapped[str] = mapped_column(String(40), index=True)
    finding_summary: Mapped[str] = mapped_column(Text)
    source_clause: Mapped[str] = mapped_column(Text)
    recommended_fix: Mapped[str] = mapped_column(Text)
    citizen_impact_reason: Mapped[str] = mapped_column(Text)
    created_at: Mapped[str] = mapped_column(String(40))
    updated_at: Mapped[str] = mapped_column(String(40))
