from __future__ import annotations

import re
from typing import Any

try:
    from rank_bm25 import BM25Okapi
except Exception:  # pragma: no cover - exercised only when optional package is missing.
    BM25Okapi = None

from app.services.hybrid_intelligence.rag_retriever import build_chunks


def _tokens(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.casefold())


def search(query: str, top_k: int = 5) -> list[dict[str, Any]]:
    chunks = build_chunks()
    query_tokens = _tokens(query)
    if not chunks or not query_tokens:
        return []
    documents = [_tokens(str(chunk.get("text") or "")) for chunk in chunks]
    if BM25Okapi is None:
        query_set = set(query_tokens)
        scored = [(index, len(query_set & set(document))) for index, document in enumerate(documents)]
    else:
        bm25 = BM25Okapi(documents)
        scored = list(enumerate(bm25.get_scores(query_tokens)))
    results = []
    for index, raw_score in sorted(scored, key=lambda item: float(item[1]), reverse=True)[:top_k]:
        if float(raw_score) <= 0:
            continue
        results.append({**chunks[index], "score": round(float(raw_score), 4), "retrieval": "bm25"})
    return results
