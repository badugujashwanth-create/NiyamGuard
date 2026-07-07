from typing import Any, Literal

from pydantic import BaseModel, Field


LocalizedText = dict[Literal["english", "telugu", "hindi"], str]
FieldType = Literal[
    "text",
    "textarea",
    "number",
    "phone",
    "aadhaar",
    "date",
    "select",
    "radio",
    "file",
    "address_group",
    "location_group",
    "checkbox",
]
ServiceStatus = Literal["ready", "catalog_only"]


class FormField(BaseModel):
    key: str
    label: str
    type: FieldType
    required: bool
    help: LocalizedText
    simple_question: str | None = None
    validation: str | None = None
    placeholder: str | None = None
    options: list[str] = Field(default_factory=list)


class RequiredDocument(BaseModel):
    key: str
    label: str
    required: bool = True
    accepted_file_types: list[str]
    max_size_mb: int
    help: LocalizedText
    examples: list[str] = Field(default_factory=list)


class FormSchema(BaseModel):
    form_id: str
    service_name: str
    form_name: str | None = None
    department: str
    category: str
    description: str
    common_use_cases: list[str] = Field(default_factory=list)
    fields: list[FormField]
    required_documents: list[RequiredDocument] = Field(default_factory=list)
    assistant_examples: dict[str, list[str]] = Field(default_factory=dict)
    assistant_guidance: dict[str, str] = Field(default_factory=dict)
    translations: dict[str, dict[str, str]] = Field(default_factory=dict)
    status: ServiceStatus = "ready"


class FormCatalogItem(BaseModel):
    form_id: str
    service_name: str
    department: str
    category: str
    description: str
    common_use_cases: list[str] = Field(default_factory=list)
    required_document_count: int
    status: ServiceStatus = "ready"
    has_detailed_schema: bool = True


class FormResponse(BaseModel):
    success: bool = True
    form: FormSchema


class FormsResponse(BaseModel):
    success: bool = True
    forms: list[FormCatalogItem]


class ServicesResponse(BaseModel):
    success: bool = True
    services: list[FormCatalogItem]


class FormValues(BaseModel):
    """Loose frontend-owned values used only for validation and read-back."""

    values: dict[str, Any]
