from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from app.schemas.chat_schemas import ChatRequest, ChatResponse
from app.services import cascade_trace_service, compliance_service, priority_service
from app.services.knowledge_chat_service import answer_chat
from app.services.ollama_client import AIClientFactory
from app.services.platform_store import read_store

router = APIRouter(prefix="/api/ai", tags=["Local AI"])


@router.get("/status")
def ai_status() -> dict[str, Any]:
    return AIClientFactory.status()


def _finding_payload(finding_id: str) -> dict[str, Any]:
    finding = compliance_service.get_finding(finding_id)
    if finding is None:
        raise HTTPException(status_code=404, detail="Finding not found.")
    store = read_store()
    rule = next((item for item in store.verified_rules if item.id == finding.verified_rule_id), None)
    circular = next((item for item in store.circulars if rule and item.id == rule.circular_id), None)
    system = next((item for item in store.connected_systems if item.id == finding.connected_system_id), None)
    snapshot = next((item for item in store.snapshots if item.id == finding.snapshot_id), None)
    trace = cascade_trace_service.get_trace_for_finding(finding.id)
    priority = next(
        (item for item in priority_service.list_priorities() if item.finding_id == finding.id),
        None,
    )
    return {
        "finding": finding.model_dump(),
        "rule": rule.model_dump() if rule else None,
        "circular": circular.model_dump() if circular else None,
        "connected_system": system.model_dump() if system else None,
        "snapshot": snapshot.model_dump() if snapshot else None,
        "cascade_trace": trace.model_dump() if trace else None,
        "priority_score": priority.model_dump() if priority else None,
    }


@router.post("/impact-summary")
def generate_impact_summary(payload: dict[str, Any]) -> dict[str, Any]:
    return AIClientFactory.get_client().generate_impact_summary(payload)


@router.post("/finding/{finding_id}/impact-summary")
def finding_impact_summary(finding_id: str) -> dict[str, Any]:
    payload = _finding_payload(finding_id)
    return AIClientFactory.get_client().generate_impact_summary(payload)


@router.post("/chat", response_model=ChatResponse)
def ai_chat(payload: ChatRequest) -> ChatResponse:
    return answer_chat(
        payload.message,
        language=payload.language,
        context=payload.context,
        profile=payload.profile,
    )
