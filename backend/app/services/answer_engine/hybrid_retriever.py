from __future__ import annotations

from typing import Any

from app.services.answer_engine import bm25_search, semantic_search


def retrieve(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    by_key: dict[str, dict[str, Any]] = {}
    for result in [*semantic_search.search(query, top_k=top_k), *bm25_search.search(query, top_k=top_k)]:
        key = str(result.get("chunk_id") or result.get("title"))
        current = by_key.get(key)
        if current is None or float(result.get("score") or 0) > float(current.get("score") or 0):
            by_key[key] = result
    return sorted(by_key.values(), key=lambda item: float(item.get("score") or 0), reverse=True)[:top_k]
