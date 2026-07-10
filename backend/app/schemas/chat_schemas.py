from typing import Any

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    language: str = "auto"
    context: dict[str, Any] = Field(default_factory=dict)
    profile: dict[str, Any] = Field(default_factory=dict)


class ChatSource(BaseModel):
    type: str
    label: str
    references: list[dict[str, Any]] = Field(default_factory=list)


class ChatResponse(BaseModel):
    success: bool
    answer: str
    language: str
    language_code: str
    intent: str
    scheme_or_service: str | None = None
    source: ChatSource
    method: str | None = None
    sources: list[dict[str, Any]] = Field(default_factory=list)
    confidence: float
    verified: bool
    fallback: bool
    provider: str | None = None
    limitations: str | None = None
