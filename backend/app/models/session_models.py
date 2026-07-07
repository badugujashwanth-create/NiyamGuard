from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


Language = Literal["english", "telugu", "hindi", "mixed"]
LanguagePreference = Literal["auto", "english", "telugu", "hindi", "mixed"]


class ConversationEntry(BaseModel):
    role: Literal["user", "assistant"]
    message: str
    timestamp: datetime


class Session(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str
    form_id: str
    language: LanguagePreference
    created_at: datetime
    conversation: list[ConversationEntry] = Field(default_factory=list)
    last_detected_language: Language | None = None
    last_field: str | None = None


class CreateSessionRequest(BaseModel):
    form_id: str = "income_certificate"
    language: LanguagePreference = "auto"


class CreateSessionResponse(BaseModel):
    success: bool = True
    session_id: str
    form_id: str
    language: LanguagePreference
    message: str = "Assistant session created successfully."


class GetSessionResponse(BaseModel):
    success: bool = True
    session: Session
