from __future__ import annotations

from typing import Any


def source_card(
    source_type: str,
    label: str,
    *,
    verified: bool,
    service_id: str | None = None,
    rule_key: str | None = None,
    value: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    card = {
        "type": source_type,
        "label": label,
        "service_id": service_id,
        "rule_key": rule_key,
        "value": value,
        "verified": verified,
        "metadata": metadata or {},
    }
    for key, item in (metadata or {}).items():
        card.setdefault(key, item)
    return card


def chat_source(label: str, sources: list[dict[str, Any]]) -> dict[str, Any]:
    first_type = sources[0]["type"] if sources else "none"
    return {"type": first_type, "label": label, "references": sources}
