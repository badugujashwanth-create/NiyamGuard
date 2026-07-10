from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from app.config import settings
from app.data_pipeline.dataset_pack_loader import (
    PACK_VERSION,
    build_dataset_pack_index,
    import_dataset_pack,
)
from app.data_pipeline.rag_indexer import INDEX_FILE, METADATA_FILE
from app.data_pipeline.rag_retriever import RagRetriever
from app.repositories.dataset_repository import dataset_repository
from app.services.ollama_client import AIClientFactory

NOT_FOUND = "Not found in available dataset."


def _payload(record: dict[str, Any] | None) -> dict[str, Any]:
    return record.get("payload", {}) if record else {}


def _matches(payload: dict[str, Any], **filters: str | None) -> bool:
    for key, value in filters.items():
        if value is None or value == "":
            continue
        if str(payload.get(key, "")).casefold() != str(value).casefold():
            return False
    return True


def _contains(payload: dict[str, Any], query: str | None) -> bool:
    if not query:
        return True
    haystack = " ".join(str(value) for value in payload.values()).casefold()
    return query.casefold() in haystack


def ensure_dataset_loaded() -> dict[str, Any]:
    if dataset_repository.count(PACK_VERSION) == 0 and settings.dataset_pack_dir.exists():
        return import_dataset_pack(settings.dataset_pack_dir)
    return {
        "pack_version": PACK_VERSION,
        "total_records": dataset_repository.count(PACK_VERSION),
        "collections": dataset_repository.collection_counts(PACK_VERSION),
    }


def _should_build_index(index_path: Path) -> bool:
    if not (index_path / INDEX_FILE).exists():
        return True
    metadata_path = index_path / METADATA_FILE
    if not metadata_path.exists():
        return True
    return False


def ensure_dataset_rag_index() -> dict[str, Any]:
    if _should_build_index(settings.rag_index_path):
        return build_dataset_pack_index(settings.dataset_pack_dir, settings.rag_index_path)
    return {"status": "ready", "output": str(settings.rag_index_path)}


def dataset_status() -> dict[str, Any]:
    summary = ensure_dataset_loaded()
    return {
        "success": True,
        "pack_version": PACK_VERSION,
        "pack_dir": str(settings.dataset_pack_dir),
        "pack_available": settings.dataset_pack_dir.exists(),
        "loaded_records": summary["total_records"],
        "collections": summary["collections"],
        "rag_index_path": str(settings.rag_index_path),
        "rag_index_ready": (settings.rag_index_path / INDEX_FILE).exists(),
    }


def list_collection(collection: str, limit: int = 50, q: str | None = None, **filters: str | None) -> dict[str, Any]:
    ensure_dataset_loaded()
    rows = dataset_repository.all_records(collection, pack_version=PACK_VERSION)
    filtered = [
        row
        for row in rows
        if _contains(_payload(row), q) and _matches(_payload(row), **filters)
    ]
    return {
        "success": True,
        "collection": collection,
        "count": len(filtered),
        "records": filtered[: max(1, min(limit, 500))],
    }


def get_record(collection: str, item_id: str) -> dict[str, Any]:
    ensure_dataset_loaded()
    record = dataset_repository.get_record(collection, item_id, pack_version=PACK_VERSION)
    if record is None:
        return {"success": False, "message": NOT_FOUND, "record": None}
    return {"success": True, "record": record}


def rag_search(question: str, top_k: int = 5) -> list[dict[str, Any]]:
    ensure_dataset_loaded()
    ensure_dataset_rag_index()
    return RagRetriever(settings.rag_index_path, min_score=0.12).retrieve(question, top_k=top_k)


def _answer_from_qa_chunk(text: str) -> str | None:
    match = re.search(r"Answer:\s*(.+)", text, flags=re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else None


def regulatory_qa(question: str, top_k: int = 5) -> dict[str, Any]:
    chunks = rag_search(question, top_k=top_k)
    if not chunks:
        return {
            "success": False,
            "answer": NOT_FOUND,
            "references": [],
            "fallback": True,
            "provider": "deterministic",
        }
    top = chunks[0]
    source_type = (top.get("source") or {}).get("type")
    if source_type == "policy_qa_pair":
        answer = _answer_from_qa_chunk(str(top.get("text") or "")) or NOT_FOUND
        provider = "dataset"
        fallback = False
    else:
        ai_result = AIClientFactory.get_client().answer_with_context(question, chunks, "english")
        answer = str(ai_result.get("answer") or NOT_FOUND)
        provider = str(ai_result.get("provider") or "fallback")
        fallback = bool(ai_result.get("fallback", True))
    return {
        "success": True,
        "answer": answer,
        "references": [
            {
                "chunk_id": chunk.get("chunk_id"),
                "title": chunk.get("title"),
                "service_id": chunk.get("service_id"),
                "score": chunk.get("score"),
                "source": chunk.get("source"),
                "metadata": chunk.get("metadata", {}),
            }
            for chunk in chunks
        ],
        "fallback": fallback,
        "provider": provider,
    }


def search_obligations(
    q: str | None = None,
    regulator_code: str | None = None,
    sector: str | None = None,
    limit: int = 25,
) -> dict[str, Any]:
    return list_collection(
        "obligations",
        limit=limit,
        q=q,
        regulator_code=regulator_code,
        sector=sector,
    )


def detect_gaps(
    org_id: str | None = None,
    policy_id: str | None = None,
    obligation_id: str | None = None,
    limit: int = 25,
) -> dict[str, Any]:
    gaps = list_collection(
        "gap_findings",
        limit=limit,
        org_id=org_id,
        policy_id=policy_id,
        obligation_id=obligation_id,
    )
    mappings = list_collection(
        "policy_obligation_mapping",
        limit=limit,
        org_id=org_id,
        policy_id=policy_id,
        obligation_id=obligation_id,
    )
    return {
        "success": True,
        "message": NOT_FOUND if not gaps["records"] and not mappings["records"] else "Dataset records found.",
        "gaps": gaps["records"],
        "mappings": mappings["records"],
    }


def review_evidence(
    org_id: str | None = None,
    obligation_id: str | None = None,
    status: str | None = None,
    limit: int = 25,
) -> dict[str, Any]:
    evidence = list_collection(
        "compliance_evidence",
        limit=limit,
        org_id=org_id,
        obligation_id=obligation_id,
        status=status,
    )
    return {
        "success": True,
        "message": NOT_FOUND if not evidence["records"] else "Evidence records found.",
        "evidence": evidence["records"],
    }


def detect_drift(org_id: str | None = None, limit: int = 25) -> dict[str, Any]:
    drift = list_collection("regulatory_drift_cases", limit=limit, org_id=org_id)
    return {
        "success": True,
        "message": NOT_FOUND if not drift["records"] else "Drift cases found.",
        "drift_cases": drift["records"],
    }


def explain_risk(org_id: str) -> dict[str, Any]:
    risk = list_collection("risk_scoring_labels", limit=1, org_id=org_id)
    if not risk["records"]:
        return {"success": False, "message": NOT_FOUND, "risk": None, "explanation": NOT_FOUND}
    payload = _payload(risk["records"][0])
    explanation = (
        f"{org_id} has risk band {payload.get('risk_band')} with score {payload.get('risk_score')}. "
        f"Top factors: {payload.get('top_risk_factors')}. "
        f"Open findings: {payload.get('open_findings_count')}; bad evidence: {payload.get('bad_evidence_count')}."
    )
    return {"success": True, "risk": risk["records"][0], "explanation": explanation}


def audit_trail(
    org_id: str | None = None,
    entity_id: str | None = None,
    limit: int = 25,
) -> dict[str, Any]:
    audit = list_collection(
        "dataset_audit_events",
        limit=limit,
        org_id=org_id,
        entity_id=entity_id,
    )
    return {
        "success": True,
        "message": NOT_FOUND if not audit["records"] else "Audit records found.",
        "events": audit["records"],
    }


def demo_flow(org_id: str | None = None) -> dict[str, Any]:
    ensure_dataset_loaded()
    risk_rows = dataset_repository.all_records("risk_scoring_labels", pack_version=PACK_VERSION)
    if not risk_rows:
        return {"success": False, "message": NOT_FOUND}
    selected_risk = (
        next((row for row in risk_rows if _payload(row).get("org_id") == org_id), None)
        if org_id
        else None
    )
    selected_risk = selected_risk or sorted(
        risk_rows,
        key=lambda row: float(_payload(row).get("risk_score") or 0),
        reverse=True,
    )[0]
    selected_org = _payload(selected_risk)["org_id"]

    gap = detect_gaps(org_id=selected_org, limit=1)["gaps"]
    drift = detect_drift(org_id=selected_org, limit=1)["drift_cases"]
    risk = explain_risk(selected_org)
    obligation_id = _payload(gap[0]).get("obligation_id") if gap else None
    policy_id = _payload(gap[0]).get("policy_id") if gap else None
    obligation = (
        dataset_repository.get_record("obligations", obligation_id, pack_version=PACK_VERSION)
        if obligation_id
        else None
    )
    circular_id = _payload(obligation).get("circular_id") if obligation else None
    circular = (
        dataset_repository.get_record("regulatory_circulars", circular_id, pack_version=PACK_VERSION)
        if circular_id
        else None
    )
    policy = (
        dataset_repository.get_record("internal_policies", policy_id, pack_version=PACK_VERSION)
        if policy_id
        else None
    )
    evidence = review_evidence(org_id=selected_org, obligation_id=obligation_id, limit=3)["evidence"]
    audit = audit_trail(org_id=selected_org, limit=5)["events"]
    return {
        "success": True,
        "org_id": selected_org,
        "question": f"What changed for {selected_org} and what should compliance fix first?",
        "regulation": circular,
        "obligation": obligation,
        "internal_policy": policy,
        "gap": gap[0] if gap else None,
        "drift": drift[0] if drift else None,
        "risk": risk.get("risk"),
        "risk_explanation": risk.get("explanation"),
        "evidence": evidence,
        "audit_trail": audit,
    }
