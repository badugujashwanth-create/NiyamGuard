from __future__ import annotations

from fastapi import APIRouter, Depends

from app.models.sandbox_models import ChatbotAskRequest
from app.security.rbac import CurrentUser, get_current_user
from app.services.hybrid_intelligence import hybrid_answer_service
from app.citizen_assistant.knowledge_chat_service import answer_chat

router = APIRouter(prefix="/api/chatbot", tags=["Chatbot / Help System"])


def _mode_for_role(role: str, requested: str | None) -> str:
    if requested in {"citizen", "government"}:
        return requested
    if role in {"officer", "reviewer", "admin"}:
        return "government"
    return "citizen"


@router.post("/ask")
def ask_chatbot(payload: ChatbotAskRequest, actor: CurrentUser = Depends(get_current_user)) -> dict:
    mode = _mode_for_role(actor.role, payload.mode)
    context = {
        **payload.context,
        "portal_mode": mode,
        "user_role": actor.role,
    }
    if mode == "government":
        hybrid = hybrid_answer_service.answer_question(
            payload.message,
            language=payload.language,
            context=context,
            profile=payload.profile,
        )
        return {
            "success": True,
            "mode": "government",
            "answer": hybrid.get("answer"),
            "method": hybrid.get("method"),
            "provider": hybrid.get("provider"),
            "verified": hybrid.get("verified"),
            "fallback": hybrid.get("fallback"),
            "source": hybrid.get("source"),
            "sources": hybrid.get("sources"),
            "language": hybrid.get("language"),
            "language_code": hybrid.get("language_code"),
        }
    chat = answer_chat(payload.message, language=payload.language, context=context, profile=payload.profile)
    return {
        "success": chat.success,
        "mode": "citizen",
        "answer": chat.answer,
        "method": chat.method,
        "provider": chat.provider,
        "verified": chat.verified,
        "fallback": chat.fallback,
        "source": chat.source,
        "sources": chat.sources,
        "language": chat.language,
        "language_code": chat.language_code,
    }
