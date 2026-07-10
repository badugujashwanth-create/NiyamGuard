from __future__ import annotations

from typing import Any

from app.services.hybrid_intelligence.confidence_scorer import score
from app.services.hybrid_intelligence.source_card_builder import source_card
from app.services.ollama_client import AIClientFactory


def answer(question: str, language: dict[str, Any], intent: str, chunks: list[dict[str, Any]]) -> dict[str, Any] | None:
    if intent not in {"circular_summary", "compliance_impact", "officer_next_action"}:
        return None
    if not chunks:
        return None
    ai = AIClientFactory.get_client().answer_with_context(question, chunks, language["language"])
    best = chunks[0]
    references = [
        source_card(
            (chunk.get("source") or {}).get("type", "retrieved_context"),
            (chunk.get("source") or {}).get("label", chunk.get("title") or "Retrieved context"),
            verified=bool((chunk.get("source") or {}).get("verified")),
            service_id=chunk.get("service_id"),
            metadata={"chunk_id": chunk.get("chunk_id"), "score": chunk.get("score")},
        )
        for chunk in chunks
    ]
    method = "local_llm" if ai.get("provider") == "ollama" and not ai.get("fallback") else "template_explanation"
    return {
        "answer": ai.get("answer") or best.get("text") or "Verified data is not available for this question.",
        "method": method,
        "confidence": score(method, source_verified=any(item["verified"] for item in references), retrieval_score=best.get("score")),
        "verified": bool(references),
        "sources": references,
        "service_id": best.get("service_id"),
        "provider": ai.get("provider"),
    }

