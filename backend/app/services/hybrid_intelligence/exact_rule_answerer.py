from __future__ import annotations

from typing import Any

from app.services import knowledge_base_service
from app.services.hybrid_intelligence.confidence_scorer import score
from app.services.hybrid_intelligence.source_card_builder import source_card


def answer(question: str, language: dict[str, Any], intent: str, service_id: str | None) -> dict[str, Any] | None:
    if intent not in {"validity", "policy_update"}:
        return None
    service = service_id or "income_certificate"
    rule_key = "validity"
    rule = knowledge_base_service.latest_rule(service, rule_key)
    if not rule.success or not rule.verified:
        return None
    value = f"{rule.current_value} {rule.unit or ''}".strip()
    source = rule.source
    circular_number = source.circular_number if source else "Verified rule"
    service_name = service.replace("_", " ").title()
    if language["language"] == "telugu":
        text = f"{circular_number} prakaram {service_name} validity {value}."
    elif language["language"] == "hindi":
        text = f"{circular_number} ke anusaar {service_name} validity {value} hai."
    else:
        text = f"As per {circular_number}, {service_name} validity is {value}."
    sources = [
        source_card(
            "verified_rule",
            circular_number,
            verified=True,
            service_id=service,
            rule_key=rule_key,
            value=value,
            metadata=source.model_dump() if source else {},
        )
    ]
    return {
        "answer": text,
        "method": "exact_rule_engine",
        "confidence": score("exact_rule_engine", source_verified=True),
        "verified": True,
        "sources": sources,
        "service_id": service,
    }
