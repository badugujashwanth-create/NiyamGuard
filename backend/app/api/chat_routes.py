from fastapi import APIRouter, Depends

from app.schemas.chat_schemas import ChatRequest, ChatResponse
from app.citizen_assistant.knowledge_chat_service import answer_chat
from app.security.rbac import require_roles

router = APIRouter(prefix="/api", tags=["Citizen Knowledge Chat"])


@router.post("/chat", response_model=ChatResponse, dependencies=[Depends(require_roles("citizen"))])
def chat(payload: ChatRequest) -> ChatResponse:
    return answer_chat(
        payload.message,
        language=payload.language,
        context=payload.context,
        profile=payload.profile,
    )
