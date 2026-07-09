from __future__ import annotations

from typing import Any

from app.services.hybrid_intelligence.hybrid_answer_service import answer_question as _answer_question


def answer_question(
    question: str,
    *,
    language: str = "auto",
    context: dict[str, Any] | None = None,
    profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return _answer_question(question, language=language, context=context, profile=profile)
