from __future__ import annotations

import re
from typing import Any

from app.config import settings
from app.data_pipeline.rag_retriever import retrieve
from app.schemas.chat_schemas import ChatResponse, ChatSource
from app.services import knowledge_base_service
from app.services.language_helper import detect_language
from app.services.ollama_client import AIClientFactory


LOCAL_KNOWLEDGE: dict[str, dict[str, Any]] = {
    "income_certificate": {
        "name": "Income Certificate",
        "aliases": ["income certificate", "income", "income-cert"],
        "documents": ["Aadhaar Card", "Income Proof", "Address Proof", "Passport size photo if requested"],
        "eligibility": "Citizens usually need it to prove family income for scholarships, fee reimbursement, pensions, admission, or welfare services.",
        "process": [
            "Choose Income Certificate in the citizen portal.",
            "Enter personal, address, income, and purpose details.",
            "Upload required proof documents.",
            "Review the details and submit manually through the official government channel.",
        ],
        "fee": "Verified fee data is not available in this demo.",
        "timeline": "Processing timeline depends on the official department workflow.",
        "source": "NiyamGuard seeded service catalog and verified GO-138 rule.",
    },
    "residence_certificate": {
        "name": "Residence Certificate",
        "aliases": ["residence certificate", "residence", "resident"],
        "documents": ["Aadhaar Card", "Address Proof", "Ration Card if available"],
        "eligibility": "Citizens generally need proof of residence in the relevant locality.",
        "process": ["Fill residence details.", "Attach address proof.", "Submit through the official service channel."],
        "fee": "Verified fee data is not available.",
        "timeline": "Official processing timeline is not available in verified data.",
        "source": "NiyamGuard local service knowledge.",
    },
    "caste_certificate": {
        "name": "Caste Certificate",
        "aliases": ["caste certificate", "community certificate", "caste", "community"],
        "documents": ["Aadhaar Card", "Parent caste proof if available", "Address Proof", "School record if requested"],
        "eligibility": "Applicant must belong to the claimed community and provide supporting proof requested by the department.",
        "process": ["Enter applicant and family details.", "Attach community proof.", "Officer verifies and approves or rejects."],
        "fee": "Verified fee data is not available.",
        "timeline": "Official processing timeline is not available in verified data.",
        "source": "NiyamGuard local service knowledge.",
    },
    "ews_certificate": {
        "name": "EWS Certificate",
        "aliases": ["ews certificate", "ews"],
        "documents": ["Aadhaar Card", "Income Proof", "Asset declaration if requested", "Address Proof"],
        "eligibility": "Eligibility depends on official EWS income and asset criteria; this demo does not have a verified current threshold.",
        "process": ["Provide identity, income, and residence details.", "Attach supporting documents.", "Submit through official channel."],
        "fee": "Verified fee data is not available.",
        "timeline": "Official processing timeline is not available in verified data.",
        "source": "NiyamGuard local service knowledge.",
    },
    "post_matric_scholarship": {
        "name": "Post-Matric Scholarship",
        "aliases": ["post matric scholarship", "post-matric scholarship", "scholarship", "fee reimbursement"],
        "documents": ["Valid Income Certificate", "Caste Certificate if applicable", "Previous year mark sheet", "Bonafide certificate", "Bank passbook copy"],
        "eligibility": "Student should be pursuing post-Class-10 education and meet the income/category rules of the receiving scholarship scheme.",
        "process": ["Register on the scholarship portal.", "Fill student, institution, income, and bank details.", "Upload required documents.", "Institution and department verify before benefit release."],
        "fee": "No verified application fee data is available in this demo.",
        "timeline": "Timeline depends on institution and department verification.",
        "source": "NiyamGuard local scholarship knowledge linked to Income Certificate GO-138.",
    },
    "old_age_pension": {
        "name": "Old-Age Pension",
        "aliases": ["old age pension", "old-age pension", "pension", "senior citizen pension"],
        "documents": ["Aadhaar Card", "Age Proof", "Income Certificate", "Bank passbook copy"],
        "eligibility": "Applicant generally must be a senior citizen and meet income criteria. Verified current thresholds are not available in this demo.",
        "process": ["Submit application through local office or official portal.", "Officer verifies age and income.", "Approved pension is paid through the official benefit channel."],
        "fee": "Verified fee data is not available.",
        "timeline": "Official processing timeline is not available in verified data.",
        "source": "NiyamGuard local pension knowledge.",
    },
    "widow_pension": {
        "name": "Widow Pension",
        "aliases": ["widow pension"],
        "documents": ["Aadhaar Card", "Death Certificate of spouse", "Income Certificate", "Bank passbook copy"],
        "eligibility": "Eligibility depends on official widow pension criteria; verified current rules are not available in this demo.",
        "process": ["Provide identity and spouse details.", "Attach death and income proof.", "Submit through official channel."],
        "fee": "Verified fee data is not available.",
        "timeline": "Official processing timeline is not available.",
        "source": "NiyamGuard local pension knowledge.",
    },
    "disability_pension": {
        "name": "Disability Pension",
        "aliases": ["disability pension", "disabled pension"],
        "documents": ["Aadhaar Card", "Disability certificate", "Income Certificate", "Bank passbook copy"],
        "eligibility": "Eligibility depends on official disability and income criteria; verified current thresholds are not available in this demo.",
        "process": ["Provide identity, disability, and income details.", "Attach proof documents.", "Submit through official channel."],
        "fee": "Verified fee data is not available.",
        "timeline": "Official processing timeline is not available.",
        "source": "NiyamGuard local pension knowledge.",
    },
    "birth_certificate": {
        "name": "Birth Certificate",
        "aliases": ["birth certificate", "birth"],
        "documents": ["Hospital birth record if available", "Parent identity proof", "Address proof"],
        "eligibility": "A birth event must be registered through the competent local body.",
        "process": ["Provide child and parent details.", "Attach hospital/local proof.", "Submit to the local body or official portal."],
        "fee": "Verified fee data is not available.",
        "timeline": "Timeline depends on registration timing and local body workflow.",
        "source": "NiyamGuard local certificate knowledge.",
    },
    "death_certificate": {
        "name": "Death Certificate",
        "aliases": ["death certificate", "death"],
        "documents": ["Medical death record if available", "Identity proof of deceased", "Applicant identity proof"],
        "eligibility": "A death event must be registered through the competent local body.",
        "process": ["Provide deceased and applicant details.", "Attach medical/local proof.", "Submit to the local body or official portal."],
        "fee": "Verified fee data is not available.",
        "timeline": "Timeline depends on registration timing and local body workflow.",
        "source": "NiyamGuard local certificate knowledge.",
    },
    "family_member_certificate": {
        "name": "Family Member Certificate",
        "aliases": ["family member certificate", "family certificate"],
        "documents": ["Aadhaar Card", "Ration Card if available", "Death Certificate if applicable", "Address Proof"],
        "eligibility": "Applicant must provide family relationship details and supporting proof requested by the department.",
        "process": ["Enter family relationship details.", "Attach supporting documents.", "Officer verifies and issues certificate if approved."],
        "fee": "Verified fee data is not available.",
        "timeline": "Official processing timeline is not available.",
        "source": "NiyamGuard local certificate knowledge.",
    },
    "ration_card": {
        "name": "Ration Card / Food Security Card",
        "aliases": ["ration card", "food security card", "food card"],
        "documents": ["Aadhaar Cards of family members", "Address Proof", "Income proof if requested"],
        "eligibility": "Eligibility depends on official household income and food security criteria; verified current thresholds are not available in this demo.",
        "process": ["Provide household details.", "Attach identity and address documents.", "Submit through the official food security channel."],
        "fee": "Verified fee data is not available.",
        "timeline": "Official processing timeline is not available.",
        "source": "NiyamGuard local food security knowledge.",
    },
}


INTENT_KEYWORDS = {
    "documents": ["document", "documents", "upload", "proof", "docs", "patralu", "documents enti"],
    "eligibility": ["eligible", "eligibility", "qualify", "am i", "arhata", "eligible aa", "yogyata"],
    "process": ["process", "steps", "apply", "how to", "ela", "kaise"],
    "validity": ["validity", "valid", "months", "entha", "kitne"],
    "fee": ["fee", "fees", "cost", "charge"],
    "timeline": ["timeline", "time", "days", "processing"],
    "old_vs_new": ["old vs new", "old rule", "new rule", "previous", "changed", "compare"],
    "scheme_comparison": ["compare schemes", "which scheme"],
    "which_service": ["which service", "what service", "which form"],
}


def _intent(message: str) -> str:
    normalized = message.casefold()
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(keyword in normalized for keyword in keywords):
            return intent
    return "form_help" if "form" in normalized else "unknown"


def _service_from_message(message: str, context: dict[str, Any]) -> tuple[str | None, dict[str, Any] | None]:
    normalized = message.casefold().replace("_", " ")
    best: tuple[str, dict[str, Any]] | None = None
    for service_id, item in LOCAL_KNOWLEDGE.items():
        if any(alias in normalized for alias in item["aliases"]):
            if best is None or len(item["name"]) > len(best[1]["name"]):
                best = (service_id, item)
    if best:
        return best
    context_service = context.get("service_id") or context.get("form_id")
    if context_service in LOCAL_KNOWLEDGE:
        return context_service, LOCAL_KNOWLEDGE[context_service]
    return None, None


def _source(source_type: str, label: str, references: list[dict[str, Any]] | None = None) -> ChatSource:
    return ChatSource(type=source_type, label=label, references=references or [])


def _localized(language: str, intent: str, item: dict[str, Any], value: Any) -> str:
    name = item["name"]
    if intent == "documents":
        docs = ", ".join(value)
        if language == "telugu":
            return f"{name} kosam usually ee documents kavali: {docs}."
        if language == "hindi":
            return f"{name} ke liye aam taur par ye documents chahiye: {docs}."
        return f"For {name}, the usual documents are: {docs}."
    if intent == "eligibility":
        if language == "telugu":
            return f"{name} eligibility: {value}"
        if language == "hindi":
            return f"{name} eligibility: {value}"
        return f"{name} eligibility: {value}"
    if intent == "process":
        steps = " ".join(f"{index + 1}. {step}" for index, step in enumerate(value))
        if language == "telugu":
            return f"{name} process: {steps}"
        if language == "hindi":
            return f"{name} process: {steps}"
        return f"{name} process: {steps}"
    if intent == "fee":
        return f"{name} fee: {value}"
    if intent == "timeline":
        return f"{name} timeline: {value}"
    return str(value)


def _fallback(language: str, intent: str) -> ChatResponse:
    if language == "telugu":
        answer = "Verified data available ledu. Official government source nunchi verify cheyyandi."
    elif language == "hindi":
        answer = "Verified data available nahi hai. Kripya official government source se verify karein."
    else:
        answer = "Verified data is not available for this question."
    return ChatResponse(
        success=True,
        answer=answer,
        language=language,
        language_code={"telugu": "te-IN", "hindi": "hi-IN"}.get(language, "en-IN"),
        intent=intent,
        scheme_or_service=None,
        source=_source("none", "No verified NiyamGuard source", []),
        confidence=0.35,
        verified=False,
        fallback=True,
        provider="deterministic",
    )


def _references_from_chunks(chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    references = []
    for chunk in chunks:
        source = chunk.get("source") or {}
        references.append(
            {
                "chunk_id": chunk.get("chunk_id"),
                "service_id": chunk.get("service_id"),
                "title": chunk.get("title"),
                "source_type": source.get("type"),
                "source_label": source.get("label"),
                "verified": bool(source.get("verified", False)),
                "score": chunk.get("score"),
            }
        )
    return references


def _rag_answer(
    message: str,
    detected_language: str,
    language_code: str,
    intent: str,
    service_id: str | None,
) -> ChatResponse | None:
    if not settings.rag_enabled:
        return None
    chunks = retrieve(message, top_k=settings.rag_top_k)
    if not chunks:
        return _fallback(detected_language, intent)
    client = AIClientFactory.get_client()
    ai_result = client.answer_with_context(message, chunks, detected_language)
    references = ai_result.get("references") or _references_from_chunks(chunks)
    best_service = service_id or chunks[0].get("service_id")
    best_score = max(float(chunk.get("score") or 0) for chunk in chunks)
    verified = bool(references) and all(bool(reference.get("verified")) for reference in references)
    return ChatResponse(
        success=True,
        answer=str(ai_result.get("answer") or "Verified data is not available for this question."),
        language=detected_language,
        language_code=language_code,
        intent=intent,
        scheme_or_service=str(best_service) if best_service else None,
        source=_source(
            "rag",
            "NiyamGuard knowledge index",
            references,
        ),
        confidence=round(best_score, 2),
        verified=verified,
        fallback=bool(ai_result.get("fallback", True)),
        provider=str(ai_result.get("provider") or "fallback"),
    )


def answer_chat(message: str, language: str = "auto", context: dict[str, Any] | None = None, profile: dict[str, Any] | None = None) -> ChatResponse:
    context = context or {}
    detected = detect_language(message, None if language == "auto" else language)
    detected_language = str(detected["detected_language"])
    language_code = str(detected["language_code"])
    intent = _intent(message)
    service_id, item = _service_from_message(message, context)

    if intent in {"validity", "old_vs_new"} and (service_id in {None, "income_certificate"}):
        rule = knowledge_base_service.citizen_safe_answer("income_certificate", "validity")
        if not rule.get("verified"):
            return _fallback(detected_language, intent)
        source = rule["source"] or {}
        answer = rule["answer"]
        if intent == "old_vs_new":
            answer = "Old rule was 12 months. Current verified rule is 6 months under GO-138."
            if detected_language == "telugu":
                answer = "Old rule 12 months. Current verified rule GO-138 prakaram 6 months."
            elif detected_language == "hindi":
                answer = "Old rule 12 months tha. Current verified rule GO-138 ke anusaar 6 months hai."
        return ChatResponse(
            success=True,
            answer=answer,
            language=detected_language,
            language_code=language_code,
            intent=intent,
            scheme_or_service="income_certificate",
            source=_source(
                "verified_rule",
                "Verified NiyamGuard Knowledge Base",
                [source],
            ),
            confidence=0.91,
            verified=True,
            fallback=False,
            provider="deterministic",
        )

    if intent in {"documents", "eligibility", "process", "fee", "timeline"}:
        rag_response = _rag_answer(message, detected_language, language_code, intent, service_id)
        if rag_response is not None:
            return rag_response

    if item is None:
        return _fallback(detected_language, intent)

    if intent == "documents":
        value = item["documents"]
    elif intent == "eligibility":
        value = item["eligibility"]
    elif intent == "process":
        value = item["process"]
    elif intent == "fee":
        value = item["fee"]
    elif intent == "timeline":
        value = item["timeline"]
    elif intent == "which_service":
        value = f"You may need {item['name']}."
    else:
        return _fallback(detected_language, intent)

    return ChatResponse(
        success=True,
        answer=_localized(detected_language, intent, item, value),
        language=detected_language,
        language_code=language_code,
        intent=intent,
        scheme_or_service=service_id,
        source=_source(
            "local_knowledge",
            "NiyamGuard seeded citizen knowledge",
            [{"service_id": service_id, "label": item["source"]}],
        ),
        confidence=0.78,
        verified=True,
        fallback=False,
        provider="deterministic",
    )
