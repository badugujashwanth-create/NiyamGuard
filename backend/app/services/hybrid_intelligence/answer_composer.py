from __future__ import annotations

from typing import Any


SAFE_FALLBACK = "Verified data is not available for this question."


def localize_fallback(language: str) -> str:
    if language == "telugu":
        return "Ee prashnaku verified NiyamGuard data available ledu."
    if language == "hindi":
        return "Is prashn ke liye verified NiyamGuard data available nahi hai."
    return SAFE_FALLBACK


def compose(
    *,
    answer: str,
    language: dict[str, Any],
    intent: str,
    service_id: str | None,
    method: str,
    confidence: float,
    verified: bool,
    sources: list[dict[str, Any]],
    fallback: bool = False,
    provider: str | None = None,
    limitations: str | None = None,
) -> dict[str, Any]:
    return {
        "success": True,
        "answer": answer,
        "language": language["language"],
        "language_code": language["language_code"],
        "intent": intent,
        "service_id": service_id,
        "method": method,
        "confidence": confidence,
        "verified": verified,
        "sources": sources,
        "fallback": fallback,
        "provider": provider or method,
        "limitations": limitations or "This answer is based on verified NiyamGuard data.",
    }


def fallback(language: dict[str, Any], intent: str = "unknown", service_id: str | None = None) -> dict[str, Any]:
    return compose(
        answer=localize_fallback(language["language"]),
        language=language,
        intent=intent,
        service_id=service_id,
        method="safe_fallback",
        confidence=0.0,
        verified=False,
        sources=[],
        fallback=True,
        provider="deterministic",
        limitations="No verified source matched this question.",
    )
