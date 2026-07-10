from __future__ import annotations


BASE_CONFIDENCE = {
    "exact_rule_engine": 1.0,
    "certificate_lookup": 0.98,
    "application_lookup": 0.98,
    "decision_table": 0.95,
    "rag_search": 0.78,
    "local_llm": 0.76,
    "template_explanation": 0.72,
    "safe_fallback": 0.0,
}


def score(method: str, *, source_verified: bool = False, retrieval_score: float | None = None) -> float:
    base = BASE_CONFIDENCE.get(method, 0.5)
    if retrieval_score is not None:
        base = max(base, min(0.9, 0.55 + retrieval_score * 0.35))
    if source_verified:
        base = min(1.0, base + 0.05)
    return round(base, 2)

