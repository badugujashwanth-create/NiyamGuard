from __future__ import annotations

from typing import Any

from app.services.hybrid_intelligence.rag_retriever import retrieve


def search(query: str, top_k: int | None = None) -> list[dict[str, Any]]:
    return retrieve(query, top_k=top_k)
