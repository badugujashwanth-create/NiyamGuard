from __future__ import annotations

from fastapi import APIRouter, Depends

from app.models.sandbox_models import ChatbotAskRequest
from app.security.rbac import CurrentUser, require_roles
from app.services.hybrid_intelligence import hybrid_answer_service
from app.citizen_assistant.knowledge_chat_service import answer_chat
from app.services import compliance_service, connected_system_service, government_inbox_service, service_portal_service

router = APIRouter(prefix="/api/chatbot", tags=["Chatbot / Help System"])


def _government_operational_answer(message: str, actor: CurrentUser) -> dict | None:
    normalized = message.casefold()
    if "system" in normalized and ("affected" in normalized or "go-138" in normalized):
        systems = connected_system_service.list_connected_systems()
        names = [item.name for item in systems]
        return {
            "answer": "GO-138 is checked against these connected systems: " + ", ".join(names) + ".",
            "method": "connected_system_registry",
            "verified": True,
            "fallback": False,
            "source": {"type": "connected_system_registry", "label": "NiyamGuard Connected Systems", "references": [{"system_id": item.id, "label": item.name} for item in systems]},
        }
    if "compliance" in normalized and ("drift" in normalized or "mismatch" in normalized):
        findings = compliance_service.list_findings()
        drifted = [item for item in findings if item.status == "drifted"]
        return {
            "answer": f"Compliance currently shows {len(drifted)} drifted finding(s) out of {len(findings)} total finding(s). Open Government > Compliance for details.",
            "method": "compliance_engine",
            "verified": True,
            "fallback": False,
            "source": {"type": "compliance_engine", "label": "Latest compliance findings", "references": [{"finding_id": item.id, "status": item.status} for item in drifted]},
        }
    if "pending" in normalized and ("officer" in normalized or "review" in normalized):
        applications = service_portal_service.pending_officer_queue(actor)
        circulars = [item for item in government_inbox_service.circular_inbox()["circulars"] if item["status"] in {"Received", "Parsed", "Reviewed"}]
        return {
            "answer": f"Pending officer review: {len(applications)} application(s) and {len(circulars)} circular(s).",
            "method": "officer_review_queue",
            "verified": True,
            "fallback": False,
            "source": {"type": "officer_review_queue", "label": "Live officer review queues", "references": [{"application_id": item["id"], "label": item["application_number"]} for item in applications]},
        }
    return None


def _mode_for_role(role: str, requested: str | None) -> str:
    if requested in {"citizen", "government"}:
        return requested
    if role in {"officer", "reviewer", "admin"}:
        return "government"
    return "citizen"


@router.post("/ask")
def ask_chatbot(payload: ChatbotAskRequest, actor: CurrentUser = Depends(require_roles("citizen"))) -> dict:
    mode = _mode_for_role(actor.role, payload.mode)
    context = {
        **payload.context,
        "portal_mode": mode,
        "user_role": actor.role,
    }
    if mode == "government":
        operational = _government_operational_answer(payload.message, actor)
        if operational is not None:
            return {
                "success": True,
                "mode": "government",
                **operational,
                "provider": "deterministic",
                "sources": operational["source"].get("references", []),
                "language": "english",
                "language_code": "en-IN",
            }
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
