from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

SandboxCircularStatus = Literal[
    "draft",
    "pdf_generated",
    "published",
    "received",
    "parsed",
    "approved",
]


class SandboxCircular(BaseModel):
    id: str
    department: str
    circular_number: str
    title: str
    service_affected: str
    rule_key: str
    old_value: str
    new_value: str
    effective_date: str
    body: str
    status: SandboxCircularStatus = "draft"
    pdf_path: str | None = None
    pdf_url: str | None = None
    government_document_id: str | None = None
    delivery_status: str = "draft"
    created_at: str
    updated_at: str
    published_at: str | None = None


class SandboxCircularCreateRequest(BaseModel):
    department: str = "Revenue Department"
    circular_number: str = "GO-138"
    title: str = "Income Certificate Validity Update"
    service_affected: str = "Income Certificate"
    rule_key: str = "validity"
    old_value: str = "12 months"
    new_value: str = "6 months"
    effective_date: str | None = None
    body: str = Field(
        default=(
            "The Revenue Department hereby notifies that Income Certificate validity "
            "is revised from 12 months to 6 months for scholarship and fee reimbursement applications."
        )
    )


class ChatbotAskRequest(BaseModel):
    message: str = Field(min_length=1)
    language: str = "auto"
    mode: str | None = None
    context: dict = Field(default_factory=dict)
    profile: dict = Field(default_factory=dict)
