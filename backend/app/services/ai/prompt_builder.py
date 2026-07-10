from __future__ import annotations

import json
from typing import Any

from app.services.ollama_client import SAFE_MISSING_ANSWER


SYSTEM_GROUNDED = (
    "You are NiyamGuard AI. Use only the supplied verified dataset context. "
    "Do not invent regulations, dates, regulators, departments, fees, eligibility, or audit events. "
    f"If the answer is missing, respond exactly: {SAFE_MISSING_ANSWER}"
)


def grounded_chat_prompt(question: str, context_chunks: list[dict[str, Any]], language: str = "english") -> str:
    return (
        f"Question language: {language}.\n"
        "Answer using only these context chunks.\n\n"
        f"Question: {question}\n\n"
        f"Context:\n{json.dumps(context_chunks, ensure_ascii=False, indent=2)}"
    )


def circular_summary_prompt(circular: dict[str, Any]) -> str:
    return (
        "Summarize this regulatory circular for compliance officers using only this JSON. "
        "Return concise bullets for regulator, effective date, obligations, risk, and action.\n\n"
        f"{json.dumps(circular, ensure_ascii=False, indent=2)}"
    )
