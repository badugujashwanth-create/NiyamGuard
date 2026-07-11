from __future__ import annotations

from typing import Any

from app.services.hybrid_intelligence.confidence_scorer import score
from app.services.hybrid_intelligence.source_card_builder import source_card
from app.knowledge_base.platform_store import read_store
from app.citizen_assistant import scheme_rule_engine


PROCESS_STEPS = [
    "Open the service in the NiyamGuard Service Portal.",
    "Fill required citizen, address, and purpose details.",
    "Upload the required evidence documents.",
    "Submit the application and complete sandbox payment if applicable.",
    "Officer reviews the application and issues a demo certificate if approved.",
]


def _service(service_id: str):
    store = read_store()
    return next((item for item in store.service_definitions if item.service_id == service_id), None)


def _source(service_id: str, label: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
    return source_card(
        "service_definition",
        label,
        verified=True,
        service_id=service_id,
        value=label,
        metadata=metadata or {},
    )


def _structured_documents(question: str, language: dict[str, Any], service_id: str) -> dict[str, Any] | None:
    docs = scheme_rule_engine.documents_for(service_id)
    comparison = scheme_rule_engine.compare_with_previous(service_id)
    if docs is None or comparison is None:
        return None
    mandatory = ", ".join(item["name"] for item in docs["mandatory_documents"]) or "none"
    secondary = ", ".join(item["name"] for item in docs["secondary_documents"]) or "none"
    text = f"For {docs['service_name']}, mandatory documents are: {mandatory}. Secondary/supporting documents are: {secondary}."
    return {
        "answer": text,
        "method": "decision_table",
        "confidence": score("decision_table", source_verified=True),
        "verified": True,
        "sources": [_source(service_id, docs["service_name"], docs.get("circular"))],
        "service_id": service_id,
    }


def _structured_eligibility(question: str, language: dict[str, Any], service_id: str, profile: dict[str, Any] | None = None) -> dict[str, Any] | None:
    result = scheme_rule_engine.check_eligibility(service_id, profile or {}, question)
    if result is None:
        return None
    details = result["reasons_met"] if result["eligible"] else result["reasons_failed"]
    text = f"{result['service_name']} eligibility: {'Eligible' if result['eligible'] else 'Not eligible or missing data'}. {' '.join(details)}"
    return {
        "answer": text,
        "method": "decision_table",
        "confidence": score("decision_table", source_verified=True),
        "verified": True,
        "sources": [_source(service_id, result["service_name"], result.get("circular"))],
        "service_id": service_id,
    }


def _structured_process(question: str, language: dict[str, Any], service_id: str) -> dict[str, Any] | None:
    result = scheme_rule_engine.process_for(service_id)
    if result is None:
        return None
    text = f"{result['service_name']} process: " + " ".join(
        f"{step['step_number']}. {step['title']}: {step['description']}" for step in result["steps"]
    )
    return {
        "answer": text,
        "method": "decision_table",
        "confidence": score("decision_table", source_verified=True),
        "verified": True,
        "sources": [_source(service_id, result["service_name"], result.get("circular"))],
        "service_id": service_id,
    }


def _structured_change(question: str, language: dict[str, Any], service_id: str) -> dict[str, Any] | None:
    result = scheme_rule_engine.compare_with_previous(service_id)
    if result is None:
        return None
    if not result["has_previous_version"]:
        text = result["message"]
    else:
        changes = "; ".join(f"{item['field']}: {item['old_value']} -> {item['new_value']}" for item in result["changes"])
        added = ", ".join(result["document_changes"]["added"]) or "none"
        removed = ", ".join(result["document_changes"]["removed"]) or "none"
        text = f"{result['service_name']} changes: {changes}. Documents added: {added}. Documents removed: {removed}."
    return {
        "answer": text,
        "method": "decision_table",
        "confidence": score("decision_table", source_verified=True),
        "verified": True,
        "sources": [_source(service_id, result["service_name"], result.get("new_circular"))],
        "service_id": service_id,
    }


def _structured_scheme_comparison(question: str, language: dict[str, Any]) -> dict[str, Any] | None:
    service_ids = scheme_rule_engine.service_ids_from_text(question)
    if len(service_ids) < 2:
        return None
    result = scheme_rule_engine.compare_schemes(service_ids[:4], message=question)
    text = "Scheme comparison: " + " ".join(
        f"{row.get('service_name', row.get('service_id'))}: benefit {row.get('benefit_amount') or 'not listed'}, "
        f"income limit {row.get('income_limit_annual') or 'not listed'}, processing {row.get('processing_time_days')} days."
        for row in result["table"]
    )
    return {
        "answer": text,
        "method": "decision_table",
        "confidence": score("decision_table", source_verified=True),
        "verified": True,
        "sources": [_source(row["service_id"], row.get("service_name") or row["service_id"]) for row in result["table"] if not row.get("error")],
        "service_id": None,
    }


def answer(question: str, language: dict[str, Any], intent: str, service_id: str | None) -> dict[str, Any] | None:
    if intent not in {"documents", "eligibility", "process", "fee", "timeline", "general_service_question", "old_vs_new", "scheme_comparison"}:
        return None
    if not service_id:
        if intent == "scheme_comparison":
            return _structured_scheme_comparison(question, language)
        return None
    if intent == "documents":
        structured = _structured_documents(question, language, service_id)
        if structured is not None:
            return structured
    if intent == "eligibility":
        structured = _structured_eligibility(question, language, service_id)
        if structured is not None:
            return structured
    if intent == "process":
        structured = _structured_process(question, language, service_id)
        if structured is not None:
            return structured
    if intent == "old_vs_new":
        structured = _structured_change(question, language, service_id)
        if structured is not None:
            return structured
    if intent == "scheme_comparison":
        structured = _structured_scheme_comparison(question, language)
        if structured is not None:
            return structured
    service = _service(service_id)
    if service is None:
        return None
    name = service.name
    if intent == "documents":
        docs = [item["label"] for item in service.required_documents_json if item.get("required")]
        detail = ", ".join(docs) or "No required documents found in available dataset."
        if language["language"] == "telugu":
            text = f"{name} kosam required documents: {detail}."
        elif language["language"] == "hindi":
            text = f"{name} ke liye required documents: {detail}."
        else:
            text = f"For {name}, required documents are: {detail}."
    elif intent == "eligibility":
        detail = "; ".join(service.eligibility_json) or "Eligibility data is not available."
        text = f"{name} eligibility criteria in the available dataset: {detail}"
    elif intent == "fee":
        text = f"{name} fee is Rs {service.fee_amount} in the NiyamGuard demo service catalog."
    elif intent == "timeline":
        text = f"{name} processing timeline is {service.processing_days} days in the NiyamGuard demo SLA."
    elif intent == "process":
        text = f"{name} process: " + " ".join(f"{index + 1}. {step}" for index, step in enumerate(PROCESS_STEPS))
    else:
        text = f"{name}: {service.description}"
    sources = [
        source_card(
            "service_definition",
            name,
            verified=True,
            service_id=service.service_id,
            value=name,
            metadata={"category": service.category, "processing_days": service.processing_days},
        )
    ]
    return {
        "answer": text,
        "method": "decision_table",
        "confidence": score("decision_table", source_verified=True),
        "verified": True,
        "sources": sources,
        "service_id": service.service_id,
    }
