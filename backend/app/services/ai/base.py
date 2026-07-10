from __future__ import annotations

from typing import Any, Protocol


class AIProvider(Protocol):
    provider: str
    model: str

    def health_check(self) -> dict[str, Any]:
        ...

    def generate_text(self, prompt: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        ...

    def generate_json(self, prompt: str, context: dict[str, Any] | None = None) -> dict[str, Any]:
        ...

    def generate_impact_summary(self, payload: dict[str, Any]) -> dict[str, Any]:
        ...

    def answer_with_context(
        self,
        question: str,
        context_chunks: list[dict[str, Any]],
        language: str = "english",
    ) -> dict[str, Any]:
        ...
