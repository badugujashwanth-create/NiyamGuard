from __future__ import annotations

from typing import Any

from app.services.knowledge_chat_service import LOCAL_KNOWLEDGE


class SchemeRepository:
    def list_schemes(self) -> list[dict[str, Any]]:
        return [
            {"id": scheme_id, **scheme}
            for scheme_id, scheme in sorted(LOCAL_KNOWLEDGE.items())
        ]

    def get_scheme(self, scheme_id: str) -> dict[str, Any] | None:
        scheme = LOCAL_KNOWLEDGE.get(scheme_id)
        return {"id": scheme_id, **scheme} if scheme else None

    def find_by_alias(self, text: str) -> dict[str, Any] | None:
        normalized = text.casefold().replace("_", " ")
        for scheme_id, scheme in LOCAL_KNOWLEDGE.items():
            if any(alias in normalized for alias in scheme["aliases"]):
                return {"id": scheme_id, **scheme}
        return None


scheme_repository = SchemeRepository()
