from typing import Literal

from pydantic import BaseModel, Field


CircularStatus = Literal[
    "uploaded",
    "extracted",
    "pending_review",
    "approved",
    "rejected",
    "superseded",
]
ExtractionStatus = Literal[
    "pending_review",
    "approved",
    "rejected",
    "needs_clarification",
]
VerifiedRuleStatus = Literal["active", "superseded", "retired"]


class Circular(BaseModel):
    id: str
    title: str
    circular_number: str
    department: str
    issue_date: str
    effective_date: str
    source_file_path: str | None = None
    source_text: str
    status: CircularStatus
    created_at: str
    updated_at: str


class ExtractedPolicyRule(BaseModel):
    id: str
    circular_id: str
    service_id: str
    rule_key: str
    rule_name: str
    old_value: str
    new_value: str
    unit: str | None = None
    effective_date: str
    affected_departments: list[str] = Field(default_factory=list)
    affected_forms: list[str] = Field(default_factory=list)
    affected_documents: list[str] = Field(default_factory=list)
    affected_faqs: list[str] = Field(default_factory=list)
    eligibility_changes: list[str] = Field(default_factory=list)
    document_changes: list[str] = Field(default_factory=list)
    deadline_changes: list[str] = Field(default_factory=list)
    extraction_confidence: float
    confidence_reason: str
    status: ExtractionStatus
    source_clause: str = ""
    created_at: str
    updated_at: str


class VerifiedPolicyRule(BaseModel):
    id: str
    source_extraction_id: str | None = None
    circular_id: str
    service_id: str
    rule_key: str
    rule_name: str
    current_value: str
    previous_value: str | None = None
    unit: str | None = None
    effective_date: str
    supersedes_rule_id: str | None = None
    status: VerifiedRuleStatus
    approved_by: str
    approved_at: str
    source_clause: str
    confidence: float
    created_at: str
    updated_at: str


class RuleSource(BaseModel):
    circular_id: str
    circular_number: str
    department: str
    effective_date: str
    confidence: float


class LatestRuleResponse(BaseModel):
    success: bool
    verified: bool
    service_id: str
    rule_key: str
    current_value: str | None = None
    unit: str | None = None
    previous_value: str | None = None
    source: RuleSource | None = None
    answer: str | None = None


class PublicRuleResponse(BaseModel):
    success: bool
    verified: bool
    answer: str
    source: RuleSource | None = None
