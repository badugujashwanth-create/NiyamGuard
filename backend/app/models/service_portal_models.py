from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

ApplicationStatus = Literal[
    "draft",
    "submitted",
    "payment_pending",
    "under_review",
    "documents_required",
    "approved",
    "rejected",
    "certificate_issued",
    "closed",
]
FeeStatus = Literal["not_required", "pending", "paid", "failed"]
DocumentVerificationStatus = Literal["pending", "accepted", "rejected"]
CertificateStatus = Literal["valid", "revoked", "expired"]
PaymentStatus = Literal["created", "paid", "failed"]
NotificationType = Literal[
    "application_submitted",
    "payment_success",
    "application_assigned",
    "documents_requested",
    "application_approved",
    "application_rejected",
    "certificate_issued",
    "certificate_revoked",
]


class CitizenProfile(BaseModel):
    id: str
    user_id: str
    full_name: str
    date_of_birth: str | None = None
    gender: str | None = None
    mobile: str | None = None
    email: str | None = None
    address_line1: str | None = None
    address_line2: str | None = None
    district: str | None = None
    mandal: str | None = None
    village: str | None = None
    pincode: str | None = None
    created_at: str
    updated_at: str


class CitizenDocument(BaseModel):
    id: str
    citizen_user_id: str
    document_type: str
    file_name: str
    storage_path: str
    mime_type: str
    file_size: int
    created_at: str


class ServiceDefinition(BaseModel):
    id: str
    service_id: str
    name: str
    department: str = ""
    category: str
    description: str
    eligibility_json: list[str] = Field(default_factory=list)
    required_documents_json: list[dict[str, Any]] = Field(default_factory=list)
    fee_amount: int = 0
    processing_days: int = 7
    enabled: bool = True
    rule_bindings_json: dict[str, Any] = Field(default_factory=dict)
    created_at: str
    updated_at: str


class ServiceFormDefinition(BaseModel):
    id: str
    service_id: str
    version: int
    fields_json: list[dict[str, Any]] = Field(default_factory=list)
    validation_rules_json: dict[str, Any] = Field(default_factory=dict)
    is_current: bool = True
    created_at: str
    updated_at: str


class Application(BaseModel):
    id: str
    application_number: str
    citizen_user_id: str
    service_id: str
    status: ApplicationStatus
    current_stage: str
    submitted_at: str | None = None
    assigned_officer_id: str | None = None
    district: str | None = None
    mandal: str | None = None
    fee_status: FeeStatus = "not_required"
    certificate_id: str | None = None
    source_rule_version_id: str | None = None
    form_values_json: dict[str, Any] = Field(default_factory=dict)
    rejection_reason: str | None = None
    due_date: str | None = None
    created_at: str
    updated_at: str


class ApplicationFieldValue(BaseModel):
    id: str
    application_id: str
    field_key: str
    value_json: Any
    created_at: str
    updated_at: str


class ApplicationDocument(BaseModel):
    id: str
    application_id: str
    document_type: str
    file_name: str
    storage_path: str
    mime_type: str
    file_size: int
    verification_status: DocumentVerificationStatus = "pending"
    uploaded_at: str


class ApplicationStatusHistory(BaseModel):
    id: str
    application_id: str
    status: ApplicationStatus
    note: str | None = None
    actor_user_id: str | None = None
    created_at: str


class OfficerReview(BaseModel):
    id: str
    application_id: str
    officer_user_id: str
    decision: Literal["approved", "rejected", "documents_required"]
    notes: str | None = None
    requested_documents_json: list[str] = Field(default_factory=list)
    reviewed_at: str


class Certificate(BaseModel):
    id: str
    certificate_number: str
    application_id: str
    service_id: str
    citizen_user_id: str
    issued_at: str
    expires_at: str | None = None
    status: CertificateStatus = "valid"
    pdf_path: str | None = None
    qr_code_value: str
    verification_hash: str
    source_rule_version_id: str | None = None
    created_at: str


class CertificateVerificationLog(BaseModel):
    id: str
    certificate_id: str | None = None
    query: str
    success: bool
    created_at: str


class PaymentRecord(BaseModel):
    id: str
    application_id: str
    amount: int
    payment_status: PaymentStatus
    payment_reference: str
    payment_mode: str = "sandbox"
    paid_at: str | None = None
    created_at: str


class Notification(BaseModel):
    id: str
    user_id: str
    notification_type: NotificationType
    title: str
    message: str
    read: bool = False
    entity_type: str | None = None
    entity_id: str | None = None
    created_at: str


class ServiceSLA(BaseModel):
    id: str
    service_id: str
    processing_days: int
    escalation_days: int
    created_at: str


class ApplicationComment(BaseModel):
    id: str
    application_id: str
    user_id: str
    comment: str
    created_at: str


class ApplicationAssignment(BaseModel):
    id: str
    application_id: str
    officer_user_id: str
    assigned_by: str | None = None
    assigned_at: str
