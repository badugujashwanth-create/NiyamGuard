from __future__ import annotations

from typing import Any

from app.services.hybrid_intelligence.confidence_scorer import score
from app.services.hybrid_intelligence.source_card_builder import source_card
from app.services.platform_store import read_store


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


def answer(question: str, language: dict[str, Any], intent: str, service_id: str | None) -> dict[str, Any] | None:
    if intent not in {"documents", "eligibility", "process", "fee", "timeline", "general_service_question"}:
        return None
    if not service_id:
        return None
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
