from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

from app.schemas.chat_schemas import ChatRequest, ChatResponse
from app.services import cascade_trace_service, compliance_service, priority_service
from app.repositories.dataset_repository import dataset_repository
from app.services.ai import AIProviderFactory
from app.services.ai.prompt_builder import circular_summary_prompt
from app.citizen_assistant.knowledge_chat_service import answer_chat
from app.knowledge_base.platform_store import read_store

router = APIRouter(prefix="/api/ai", tags=["Local AI"])


@router.get("/status")
def ai_status() -> dict[str, Any]:
    return AIProviderFactory.status()


@router.post("/verified-explanation")
def verified_explanation(payload: dict[str, Any]) -> dict[str, Any]:
    question = str(payload.get("question") or "Explain GO-138 in simple words").strip()
    fallback_text = (
        "GO-138 means the demo Income Certificate validity is 6 months instead of 12 months. "
        "NiyamGuard uses the verified Revenue Department GO-138 context for this explanation."
    )
    prompt = (
        "Use only this verified NiyamGuard context. Do not invent government rules, dates, "
        "departments, eligibility, or official commitments.\n\n"
        "Verified context:\n"
        "- Circular: GO-138\n"
        "- Department: Revenue\n"
        "- Service: Income Certificate\n"
        "- Rule: validity\n"
        "- Previous value: 12 months\n"
        "- Current value: 6 months\n"
        "- Effective date: 2026-07-01\n\n"
        f"Question: {question}"
    )
    result = AIProviderFactory.get_client().generate_text(prompt, {"fallback_text": fallback_text})
    return {
        "success": True,
        "question": question,
        "provider": result.get("provider"),
        "model": result.get("model"),
        "fallback": bool(result.get("fallback")),
        "answer": result.get("text") or fallback_text,
        "source": {
            "type": "verified_rule",
            "circular_number": "GO-138",
            "department": "Revenue",
            "service_id": "income_certificate",
            "rule_key": "validity",
            "verified": True,
        },
    }


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
    return AIProviderFactory.get_client().generate_impact_summary(payload)


@router.post("/finding/{finding_id}/impact-summary")
def finding_impact_summary(finding_id: str) -> dict[str, Any]:
    payload = _finding_payload(finding_id)
    return AIProviderFactory.get_client().generate_impact_summary(payload)


def _circular_payload(identifier: str) -> dict[str, Any] | None:
    normalized = identifier.casefold()
    store = read_store()
    for circular in store.circulars:
        if circular.id.casefold() == normalized or circular.circular_number.casefold() == normalized:
            return circular.model_dump()
    record = dataset_repository.get_record("regulatory_circulars", identifier)
    if record:
        return record["payload"]
    for item in dataset_repository.all_records("regulatory_circulars"):
        payload = item["payload"]
        if normalized in {
            str(payload.get("circular_id", "")).casefold(),
            str(payload.get("title", "")).casefold(),
        }:
            return payload
    return None


@router.post("/circular-summary")
def circular_summary(payload: dict[str, Any]) -> dict[str, Any]:
    circular_id = str(payload.get("circular_id") or payload.get("circular_number") or "").strip()
    circular = _circular_payload(circular_id) if circular_id else payload.get("circular")
    if not isinstance(circular, dict) or not circular:
        raise HTTPException(status_code=404, detail="Circular not found in available dataset.")
    fallback_text = (
        f"{circular.get('circular_number') or circular.get('circular_id')}: {circular.get('title')}. "
        f"Effective date: {circular.get('effective_date')}. "
        f"Summary: {circular.get('summary') or circular.get('source_text') or circular.get('full_text') or 'Not found in available dataset.'}"
    )
    result = AIProviderFactory.get_client().generate_text(
        circular_summary_prompt(circular),
        {"fallback_text": fallback_text},
    )
    return {
        "success": True,
        "provider": result.get("provider"),
        "model": result.get("model"),
        "fallback": bool(result.get("fallback")),
        "summary": result.get("text") or fallback_text,
        "source": {
            "type": "regulatory_circular",
            "id": circular.get("id") or circular.get("circular_id"),
            "circular_number": circular.get("circular_number") or circular.get("circular_id"),
            "effective_date": circular.get("effective_date"),
            "verified": True,
        },
    }


@router.post("/chat", response_model=ChatResponse)
def ai_chat(payload: ChatRequest) -> ChatResponse:
    return answer_chat(
        payload.message,
        language=payload.language,
        context=payload.context,
        profile=payload.profile,
    )
