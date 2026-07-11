from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, model_validator

SandboxCircularStatus = Literal[
    "draft",
    "pdf_generated",
    "ready_for_manual_upload",
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
    department: str = Field(default="Revenue Department", min_length=1)
    circular_number: str = Field(default="GO-138", min_length=1)
    title: str = Field(default="Income Certificate Validity Update", min_length=1)
    service_affected: str = Field(default="Income Certificate", min_length=1)
    rule_key: str = Field(default="validity", min_length=1)
    old_value: str = Field(default="12 months", min_length=1)
    new_value: str = Field(default="6 months", min_length=1)
    effective_date: str | None = None
    body: str = Field(
        default=(
            "The Revenue Department hereby notifies that Income Certificate validity "
            "is revised from 12 months to 6 months for scholarship and fee reimbursement applications."
        )
    )

    @model_validator(mode="after")
    def changed_value_must_differ(self):
        if self.old_value.strip().casefold() == self.new_value.strip().casefold():
            raise ValueError("Old value and new value must be different.")
        return self


class ChatbotAskRequest(BaseModel):
    message: str = Field(min_length=1)
    language: str = "auto"
    mode: str | None = None
    context: dict = Field(default_factory=dict)
    profile: dict = Field(default_factory=dict)
