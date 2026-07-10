from __future__ import annotations

from typing import Any

from app.services.ollama_client import SAFE_MISSING_ANSWER


def validate_grounded_text(text: str, sources: list[dict[str, Any]] | None = None) -> str:
    cleaned = (text or "").strip()
    if not cleaned:
        return SAFE_MISSING_ANSWER
    if cleaned != SAFE_MISSING_ANSWER and not sources:
        return SAFE_MISSING_ANSWER
    return cleaned
