from typing import Any, Literal

from pydantic import BaseModel


class FormField(BaseModel):
    key: str
    label: str
    type: Literal["text", "phone", "aadhaar", "number", "textarea"]
    required: bool
    help: str
    simple_question: str
    validation: str | None = None


class FormSchema(BaseModel):
    form_id: str
    form_name: str
    description: str
    fields: list[FormField]


class FormResponse(BaseModel):
    success: bool = True
    form: FormSchema


class FormValues(BaseModel):
    """Loose frontend-owned values used only for validation and read-back."""

    values: dict[str, Any]
