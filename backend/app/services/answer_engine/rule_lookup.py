from __future__ import annotations

from typing import Any

from app.services.hybrid_intelligence import exact_rule_answerer


def lookup_rule(question: str, language: dict[str, Any], intent: str, service_id: str | None = None) -> dict[str, Any] | None:
    return exact_rule_answerer.answer(question, language, intent, service_id)
