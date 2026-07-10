from fastapi import APIRouter

from app.schemas.chat_schemas import ChatRequest, ChatResponse
from app.citizen_assistant.knowledge_chat_service import answer_chat

router = APIRouter(prefix="/api", tags=["Citizen Knowledge Chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest) -> ChatResponse:
    return answer_chat(
        payload.message,
        language=payload.language,
        context=payload.context,
        profile=payload.profile,
    )
