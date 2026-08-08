from __future__ import annotations

from typing import Any

from app.services.hybrid_intelligence.confidence_scorer import score
from app.services.hybrid_intelligence.source_card_builder import source_card
from app.knowledge_base.platform_store import read_store


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
    if intent not in {"documents", "eligibility", "process", "form_help", "fee", "timeline", "general_service_question"}:
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
    elif intent in {"process", "form_help"}:
        if language["language"] == "telugu":
            text = (
                f"{name} \u0c2b\u0c3e\u0c30\u0c4d\u0c2e\u0c4d \u0c28\u0c3f\u0c02\u0c2a\u0c21\u0c3e\u0c28\u0c3f\u0c15\u0c3f: "
                "1. \u0c2a\u0c4c\u0c30\u0c41\u0c32, \u0c1a\u0c3f\u0c30\u0c41\u0c28\u0c3e\u0c2e\u0c3e, \u0c05\u0c2d\u0c4d\u0c2f\u0c3f\u0c2a\u0c4d\u0c30\u0c3e\u0c2f\u0c02 \u0c35\u0c3f\u0c35\u0c30\u0c3e\u0c32\u0c41 \u0c28\u0c3f\u0c02\u0c2a\u0c02\u0c21\u0c3f. "
                "2. \u0c05\u0c35\u0c38\u0c30\u0c2e\u0c48\u0c28 \u0c2a\u0c24\u0c4d\u0c30\u0c3e\u0c32\u0c28\u0c41 \u0c05\u0c2a\u0c4d\u0c32\u0c4b\u0c21\u0c4d \u0c1a\u0c47\u0c2f\u0c02\u0c21\u0c3f. "
                "3. \u0c35\u0c3f\u0c35\u0c30\u0c3e\u0c32\u0c28\u0c41 \u0c24\u0c28\u0c3f\u0c16\u0c40 \u0c1a\u0c47\u0c38\u0c3f \u0c38\u0c2c\u0c4d\u0c2e\u0c3f\u0c1f\u0c4d \u0c1a\u0c47\u0c2f\u0c02\u0c21\u0c3f. "
                "4. \u0c05\u0c27\u0c3f\u0c15\u0c3e\u0c30\u0c3f \u0c2a\u0c30\u0c3f\u0c36\u0c40\u0c32\u0c28 \u0c15\u0c4b\u0c38\u0c02 \u0c35\u0c47\u0c1a\u0c3f \u0c09\u0c02\u0c1f\u0c41\u0c02\u0c26\u0c3f."
            )
        elif language["language"] == "hindi":
            text = (
                f"{name} \u092b\u093c\u0949\u0930\u094d\u092e \u092d\u0930\u0928\u0947 \u0915\u0947 \u0932\u093f\u090f: "
                "1. \u0928\u093e\u0917\u0930\u093f\u0915, \u092a\u0924\u093e \u0914\u0930 \u0909\u0926\u094d\u0926\u0947\u0936\u094d\u092f \u0935\u093f\u0935\u0930\u0923 \u092d\u0930\u0947\u0902। "
                "2. \u0906\u0935\u0936\u094d\u092f\u0915 \u0926\u0938\u094d\u0924\u093e\u0935\u0947\u091c\u093c \u0905\u092a\u0932\u094b\u0921 \u0915\u0930\u0947\u0902। "
                "3. \u0935\u093f\u0935\u0930\u0923 \u0915\u0940 \u091c\u093e\u0901\u091a \u0915\u0930\u0915\u0947 \u0938\u092c\u092e\u093f\u091f \u0915\u0930\u0947\u0902। "
                "4. \u0905\u0927\u093f\u0915\u0943\u0924 \u0905\u0927\u093f\u0915\u093e\u0930\u0940 \u0926\u094d\u0935\u093e\u0930\u093e \u0938\u092e\u0940\u0915\u094d\u0937\u093e \u0915\u093e \u0907\u0902\u0924\u091c\u093c\u093e\u0930 \u0915\u0930\u0947\u0902।"
            )
        else:
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
