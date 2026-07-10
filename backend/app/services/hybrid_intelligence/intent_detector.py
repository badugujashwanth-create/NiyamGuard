from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Any


ALIASES_PATH = Path(__file__).resolve().parents[2] / "data" / "hybrid_aliases.json"


@lru_cache(maxsize=1)
def aliases() -> dict[str, Any]:
    with ALIASES_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _contains_alias(text: str, values: list[str]) -> bool:
    normalized = text.casefold().replace("_", " ")
    return any(alias.casefold() in normalized for alias in values)


def detect_service_id(text: str, context: dict[str, Any] | None = None) -> str | None:
    context = context or {}
    context_service = context.get("service_id") or context.get("form_id")
    if context_service:
        return str(context_service)
    normalized = text.casefold().replace("_", " ")
    best: tuple[str, int] | None = None
    for service_id, service_aliases in aliases()["services"].items():
        for alias in service_aliases:
            alias_text = alias.casefold()
            if alias_text in normalized:
                score = len(alias_text)
                if best is None or score > best[1]:
                    best = (service_id, score)
    return best[0] if best else None


def detect_intent(text: str, context: dict[str, Any] | None = None) -> dict:
    normalized = text.casefold()
    if re.search(r"\bngsp-\d{4}-[a-z0-9]+-\d+\b", normalized):
        intent = "application_status"
    elif re.search(r"\bngcert-\d{4}-[a-z0-9]+-\d+\b", normalized) or "verification hash" in normalized:
        intent = "certificate_verification"
    else:
        intent = "unknown"
        for candidate, values in aliases()["intents"].items():
            if candidate == "unknown":
                continue
            if _contains_alias(text, values):
                intent = candidate
                break
    service_id = detect_service_id(text, context)
    if intent == "unknown" and service_id:
        intent = "general_service_question"
    confidence = 0.96 if intent in {"validity", "documents", "application_status", "certificate_verification"} else 0.76
    if intent == "unknown":
        confidence = 0.0
    return {
        "intent": intent,
        "service_id": service_id,
        "confidence": confidence,
        "method": "deterministic_intent",
    }

