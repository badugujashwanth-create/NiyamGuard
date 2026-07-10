from __future__ import annotations

from functools import lru_cache
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.config import settings
from app.knowledge_base.platform_store import read_store


def _chunk(chunk_id: str, title: str, text: str, source: dict[str, Any], service_id: str | None = None) -> dict[str, Any]:
    return {
        "chunk_id": chunk_id,
        "title": title,
        "text": text,
        "service_id": service_id,
        "source": source,
    }


def build_chunks() -> list[dict[str, Any]]:
    store = read_store()
    chunks: list[dict[str, Any]] = []
    for service in store.service_definitions:
        docs = ", ".join(item["label"] for item in service.required_documents_json)
        eligibility = "; ".join(service.eligibility_json)
        text = (
            f"Service: {service.name}. Category: {service.category}. Description: {service.description}. "
            f"Eligibility: {eligibility}. Required documents: {docs}. Fee: Rs {service.fee_amount}. "
            f"Processing days: {service.processing_days}."
        )
        chunks.append(
            _chunk(
                f"svc_{service.service_id}",
                service.name,
                text,
                {"type": "service_definition", "label": service.name, "verified": True},
                service.service_id,
            )
        )
    for rule in store.verified_rules:
        text = (
            f"Verified rule {rule.rule_name}. Service {rule.service_id}. Rule key {rule.rule_key}. "
            f"Current value {rule.current_value} {rule.unit or ''}. Previous value {rule.previous_value or 'none'}. "
            f"Effective date {rule.effective_date}. Source clause: {rule.source_clause}."
        )
        chunks.append(
            _chunk(
                f"rule_{rule.id}",
                rule.rule_name,
                text,
                {"type": "verified_rule", "label": rule.circular_id, "verified": rule.status == "active"},
                rule.service_id,
            )
        )
    for circular in store.circulars:
        chunks.append(
            _chunk(
                f"circular_{circular.id}",
                circular.title,
                f"{circular.circular_number}. {circular.title}. {circular.source_text}",
                {"type": "circular", "label": circular.circular_number, "verified": circular.status == "approved"},
            )
        )
    for finding in store.compliance_findings:
        chunks.append(
            _chunk(
                f"finding_{finding.id}",
                finding.finding_summary,
                f"{finding.finding_summary}. Expected {finding.expected_value}. Actual {finding.actual_value}. {finding.citizen_impact_reason} {finding.recommended_fix}",
                {"type": "compliance_finding", "label": finding.id, "verified": True},
                finding.service_id,
            )
        )
    return chunks


@lru_cache(maxsize=1)
def _index() -> dict[str, Any]:
    chunks = build_chunks()
    vectorizer = TfidfVectorizer(lowercase=True, ngram_range=(1, 2), max_features=12000)
    matrix = vectorizer.fit_transform([chunk["text"] for chunk in chunks])
    return {"chunks": chunks, "vectorizer": vectorizer, "matrix": matrix}


def reindex() -> dict[str, Any]:
    _index.cache_clear()
    index = _index()
    return {"indexed_chunks": len(index["chunks"])}


def status() -> dict[str, Any]:
    index = _index()
    return {
        "enabled": settings.search_engine_enabled,
        "bm25_enabled": settings.bm25_enabled,
        "semantic_search_enabled": settings.semantic_search_enabled,
        "indexed_chunks": len(index["chunks"]),
        "top_k": settings.search_top_k,
        "min_score": settings.search_min_score,
    }


def retrieve(query: str, top_k: int | None = None) -> list[dict[str, Any]]:
    if not settings.search_engine_enabled or not query.strip():
        return []
    index = _index()
    vectorizer = index["vectorizer"]
    matrix = index["matrix"]
    chunks = index["chunks"]
    scores = cosine_similarity(vectorizer.transform([query]), matrix)[0]
    ranked = sorted(enumerate(scores), key=lambda item: float(item[1]), reverse=True)
    results = []
    for chunk_index, raw_score in ranked[: top_k or settings.search_top_k]:
        score_value = float(raw_score)
        if score_value < settings.search_min_score:
            continue
        chunk = chunks[chunk_index]
        results.append({**chunk, "score": round(score_value, 4)})
    return results

