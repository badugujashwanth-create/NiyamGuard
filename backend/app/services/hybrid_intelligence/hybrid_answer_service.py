from __future__ import annotations

import re
from typing import Any

from app.services.hybrid_intelligence import (
    answer_composer,
    answer_validator,
    decision_table_answerer,
    exact_rule_answerer,
    intent_detector,
    language_detector,
    local_llm_answerer,
    question_router,
    rag_retriever,
)
from app.services.hybrid_intelligence.confidence_scorer import score
from app.services.hybrid_intelligence.source_card_builder import source_card
from app.forms.service_portal_service import track_application, verify_certificate


def _application_answer(question: str, language: dict[str, Any]) -> dict[str, Any] | None:
    match = re.search(r"\b(NGSP-\d{4}-[A-Z0-9]+-\d+)\b", question, flags=re.IGNORECASE)
    if not match:
        return None
    tracking = track_application(match.group(1).upper())
    answer = (
        f"Application {tracking['application_number']} is at {tracking['current_stage']} "
        f"with SLA status {tracking['sla']['status']}."
    )
    return {
        "answer": answer,
        "method": "application_lookup",
        "confidence": score("application_lookup", source_verified=True),
        "verified": True,
        "sources": [
            source_card(
                "application",
                tracking["application_number"],
                verified=True,
                value=tracking["status"],
                metadata={"sla": tracking["sla"]},
            )
        ],
        "service_id": None,
    }


def _certificate_answer(question: str, language: dict[str, Any]) -> dict[str, Any] | None:
    match = re.search(r"\b(NGCERT-\d{4}-[A-Z0-9]+-\d+|[a-f0-9]{32,64})\b", question, flags=re.IGNORECASE)
    if not match:
        return None
    result = verify_certificate(match.group(1))
    if not result.get("valid"):
        return None
    certificate = result["certificate"]
    return {
        "answer": f"Certificate {certificate['certificate_number']} is valid for {result.get('service_name')}.",
        "method": "certificate_lookup",
        "confidence": score("certificate_lookup", source_verified=True),
        "verified": True,
        "sources": [
            source_card(
                "certificate",
                certificate["certificate_number"],
                verified=True,
                value=certificate["status"],
                metadata={"issued_at": certificate["issued_at"], "expires_at": certificate.get("expires_at")},
            )
        ],
        "service_id": certificate.get("service_id"),
    }


def answer_question(
    question: str,
    *,
    language: str = "auto",
    context: dict[str, Any] | None = None,
    profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    context = context or {}
    detected_language = language_detector.detect_language(question, language)
    detected_intent = intent_detector.detect_intent(question, context)
    intent = detected_intent["intent"]
    service_id = detected_intent.get("service_id")
    route = question_router.route(intent)
    candidate: dict[str, Any] | None = None

    if route == "exact_rule_engine":
        candidate = exact_rule_answerer.answer(question, detected_language, intent, service_id)
    elif route == "application_lookup":
        candidate = _application_answer(question, detected_language)
    elif route == "certificate_lookup":
        candidate = _certificate_answer(question, detected_language)
    elif route == "decision_table":
        candidate = decision_table_answerer.answer(question, detected_language, intent, service_id)
        if candidate is None:
            chunks = rag_retriever.retrieve(question)
            if chunks:
                best = chunks[0]
                candidate = {
                    "answer": f"From {best['title']}: {best['text'][:700]}",
                    "method": "rag_search",
                    "confidence": score("rag_search", source_verified=True, retrieval_score=best["score"]),
                    "verified": True,
                    "sources": [
                        source_card(
                            (chunk.get("source") or {}).get("type", "retrieved_context"),
                            (chunk.get("source") or {}).get("label", chunk.get("title")),
                            verified=bool((chunk.get("source") or {}).get("verified")),
                            service_id=chunk.get("service_id"),
                            metadata={"chunk_id": chunk.get("chunk_id"), "score": chunk.get("score")},
                        )
                        for chunk in chunks
                    ],
                    "service_id": best.get("service_id") or service_id,
                }
    elif route in {"local_llm", "rag_search"}:
        chunks = rag_retriever.retrieve(question)
        candidate = local_llm_answerer.answer(question, detected_language, intent, chunks)

    if not answer_validator.validate(candidate or {}):
        return answer_composer.fallback(detected_language, intent, service_id)
    return answer_composer.compose(
        answer=candidate["answer"],
        language=detected_language,
        intent=intent,
        service_id=candidate.get("service_id") or service_id,
        method=candidate["method"],
        confidence=candidate["confidence"],
        verified=bool(candidate["verified"]),
        sources=candidate["sources"],
        fallback=False,
        provider=candidate.get("provider"),
    )


def search(query: str, top_k: int | None = None) -> dict[str, Any]:
    return {"success": True, "query": query, "results": rag_retriever.retrieve(query, top_k=top_k)}


def reindex() -> dict[str, Any]:
    result = rag_retriever.reindex()
    return {"success": True, **result}


def status() -> dict[str, Any]:
    index_status = rag_retriever.status()
    alias_data = intent_detector.aliases()
    return {
        "success": True,
        "engine": "hybrid_intelligence",
        "methods": {
            "exact_rule_engine": True,
            "decision_tables": True,
            "rag": True,
            "ollama_optional": True,
            "safe_fallback": True,
        },
        "service_alias_count": sum(len(value) for value in alias_data["services"].values()),
        "intent_alias_count": sum(len(value) for value in alias_data["intents"].values()),
        **index_status,
    }
