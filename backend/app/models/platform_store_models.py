from typing import Any

from pydantic import BaseModel, Field

from app.models.cascade_models import CascadeTrace
from app.models.compliance_models import ComplianceFinding
from app.models.conflict_models import CircularConflict
from app.models.connected_system_models import ConnectedSystem, ConnectedSystemRuleSnapshot
from app.models.knowledge_models import Circular, ExtractedPolicyRule, VerifiedPolicyRule
from app.models.priority_models import PriorityScore
from app.models.self_update_models import (
    CircularDocument,
    CircularExtraction,
    CircularSyncJob,
    ComplianceRunRecord,
    ConnectedSystemPatch,
    KnowledgeUpdateEvent,
    MockConnectedSystemState,
    OfficialCircularSource,
    PolicyPublicationEvent,
    PolicyRuleCandidate,
    PolicyRuleDelta,
    PropagationPlan,
    PropagationTask,
    RollbackEvent,
    RuleApprovalWorkflow,
    VerifiedPolicyRuleVersion,
)
from app.models.service_portal_models import (
    Application,
    ApplicationAssignment,
    ApplicationComment,
    ApplicationDocument,
    ApplicationFieldValue,
    ApplicationStatusHistory,
    Certificate,
    CertificateVerificationLog,
    CitizenDocument,
    CitizenProfile,
    Notification,
    OfficerReview,
    PaymentRecord,
    ServiceDefinition,
    ServiceFormDefinition,
    ServiceSLA,
)


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
    official_circular_sources: list[OfficialCircularSource] = Field(default_factory=list)
    circular_sync_jobs: list[CircularSyncJob] = Field(default_factory=list)
    circular_documents: list[CircularDocument] = Field(default_factory=list)
    circular_extractions: list[CircularExtraction] = Field(default_factory=list)
    policy_rule_candidates: list[PolicyRuleCandidate] = Field(default_factory=list)
    policy_rule_deltas: list[PolicyRuleDelta] = Field(default_factory=list)
    rule_approval_workflows: list[RuleApprovalWorkflow] = Field(default_factory=list)
    verified_policy_rule_versions: list[VerifiedPolicyRuleVersion] = Field(default_factory=list)
    policy_publication_events: list[PolicyPublicationEvent] = Field(default_factory=list)
    knowledge_update_events: list[KnowledgeUpdateEvent] = Field(default_factory=list)
    propagation_plans: list[PropagationPlan] = Field(default_factory=list)
    propagation_tasks: list[PropagationTask] = Field(default_factory=list)
    connected_system_patches: list[ConnectedSystemPatch] = Field(default_factory=list)
    rollback_events: list[RollbackEvent] = Field(default_factory=list)
    compliance_runs: list[ComplianceRunRecord] = Field(default_factory=list)
    mock_connected_systems: list[MockConnectedSystemState] = Field(default_factory=list)
    citizen_profiles: list[CitizenProfile] = Field(default_factory=list)
    citizen_documents: list[CitizenDocument] = Field(default_factory=list)
    service_definitions: list[ServiceDefinition] = Field(default_factory=list)
    service_form_definitions: list[ServiceFormDefinition] = Field(default_factory=list)
    applications: list[Application] = Field(default_factory=list)
    application_field_values: list[ApplicationFieldValue] = Field(default_factory=list)
    application_documents: list[ApplicationDocument] = Field(default_factory=list)
    application_status_history: list[ApplicationStatusHistory] = Field(default_factory=list)
    officer_reviews: list[OfficerReview] = Field(default_factory=list)
    certificates: list[Certificate] = Field(default_factory=list)
    certificate_verification_logs: list[CertificateVerificationLog] = Field(default_factory=list)
    payment_records: list[PaymentRecord] = Field(default_factory=list)
    notifications: list[Notification] = Field(default_factory=list)
    service_slas: list[ServiceSLA] = Field(default_factory=list)
    application_comments: list[ApplicationComment] = Field(default_factory=list)
    application_assignments: list[ApplicationAssignment] = Field(default_factory=list)
