from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


Language = Literal["english", "telugu", "hindi", "mixed"]


class ConversationEntry(BaseModel):
    role: Literal["user", "assistant"]
    message: str
    timestamp: datetime


class Session(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str
    form_id: str
    language: Language
    created_at: datetime
    conversation: list[ConversationEntry] = Field(default_factory=list)


class CreateSessionRequest(BaseModel):
    form_id: Literal["income_certificate"] = "income_certificate"
    language: Language = "english"


class CreateSessionResponse(BaseModel):
    success: bool = True
    session_id: str
    form_id: str
    language: Language
    message: str = "Assistant session created successfully."


class GetSessionResponse(BaseModel):
    success: bool = True
    session: Session
