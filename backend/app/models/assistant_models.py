from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator

from app.models.session_models import Language, LanguagePreference


class AskRequest(BaseModel):
    session_id: str = Field(min_length=1)
    message: str = Field(min_length=1)
    current_field: str | None = None
    language: LanguagePreference = "auto"

    @field_validator("message")
    @classmethod
    def message_must_have_text(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("message must not be empty")
        return value.strip()


class AskResponse(BaseModel):
    success: bool = True
    field: str | None
    reply: str
    suggested_value: str | None = None
    related_values: dict[str, str] = Field(default_factory=dict)
    location_matches: list[dict[str, str]] = Field(default_factory=list)
    warning: str | None = None
    detected_language: Language
    language_code: Literal["te-IN", "hi-IN", "en-IN"]
    auto_fill: bool = False
    should_submit: bool = False


class ValidateRequest(BaseModel):
    field: str = Field(min_length=1)
    value: Any


class ValidateResponse(BaseModel):
    success: bool = True
    field: str
    valid: bool
    message: str
    auto_fill: bool = False
    should_submit: bool = False


class SummaryRequest(BaseModel):
    session_id: str = Field(min_length=1)
    form_values: dict[str, Any]
    language: LanguagePreference = "auto"


class SummaryResponse(BaseModel):
    success: bool = True
    summary: str
    missing_fields: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    detected_language: Language
    language_code: Literal["te-IN", "hi-IN", "en-IN"]
    auto_fill: bool = False
    should_submit: bool = False
