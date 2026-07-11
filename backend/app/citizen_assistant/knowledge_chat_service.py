from __future__ import annotations

import re
from typing import Any

from app.config import settings
from app.data_pipeline.rag_retriever import retrieve
from app.schemas.chat_schemas import ChatResponse, ChatSource
from app.knowledge_base import certificate_baseline_service
from app.services.hybrid_intelligence.hybrid_answer_service import answer_question
from app.services.hybrid_intelligence.source_card_builder import chat_source
from app.citizen_assistant.language_helper import detect_language
from app.citizen_assistant import scheme_rule_engine
from app.services.ollama_client import AIClientFactory


LOCAL_KNOWLEDGE: dict[str, dict[str, Any]] = {
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
    "purpose": ["purpose", "used for", "why need", "why do i need", "use case"],
    "department": ["department", "which office", "which dept", "office"],
    "process": ["process", "steps", "apply", "how to", "ela", "kaise"],
    "validity": ["validity", "valid", "months", "entha", "kitne"],
    "fee": ["fee", "fees", "cost", "charge"],
    "timeline": ["timeline", "time", "days", "processing"],
    "verification": ["verify", "verification", "certificate number", "hash"],
    "status": ["track application", "application status", "track my application", "tracking"],
    "old_vs_new": ["old vs new", "old rule", "new rule", "previous", "changed", "what changed"],
    "scheme_comparison": ["compare schemes", "which scheme", "scheme comparison", " vs ", "versus"],
    "which_service": ["which service", "what service", "which form"],
}


def _intent(message: str) -> str:
    normalized = message.casefold()
    if any(keyword in normalized for keyword in INTENT_KEYWORDS["verification"]):
        return "verification"
    if any(keyword in normalized for keyword in INTENT_KEYWORDS["status"]):
        return "status"
    for intent, keywords in INTENT_KEYWORDS.items():
        if any(keyword in normalized for keyword in keywords):
            return intent
    return "form_help" if "form" in normalized else "unknown"


def _certificate_aliases(baseline: dict[str, Any]) -> set[str]:
    title = str(baseline["title"]).casefold()
    service_id = str(baseline["service_id"]).replace("_", " ").casefold()
    aliases = {title, service_id}
    if title.endswith(" certificate"):
        aliases.add(title.removesuffix(" certificate").strip())
    return {alias for alias in aliases if len(alias) >= 4 and alias != "certificate"}


def _baseline_service_from_message(normalized: str) -> str | None:
    best: tuple[str, str] | None = None
    for baseline in certificate_baseline_service.list_baselines():
        for alias in _certificate_aliases(baseline):
            if alias in normalized and (best is None or len(alias) > len(best[1])):
                best = (str(baseline["service_id"]), alias)
    return best[0] if best else None


def _service_from_message(message: str, context: dict[str, Any]) -> tuple[str | None, dict[str, Any] | None]:
    normalized = message.casefold().replace("_", " ")
    baseline_service_id = _baseline_service_from_message(normalized)
    if baseline_service_id:
        return baseline_service_id, None

    best: tuple[str, dict[str, Any]] | None = None
    for service_id, item in LOCAL_KNOWLEDGE.items():
        if any(alias in normalized for alias in item["aliases"]):
            if best is None or len(item["name"]) > len(best[1]["name"]):
                best = (service_id, item)
    if best:
        return best
    context_service = context.get("service_id") or context.get("form_id")
    if context_service and certificate_baseline_service.has_baseline(str(context_service)):
        return str(context_service), None
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
            return f"{name} కోసం సాధారణంగా ఈ పత్రాలు కావాలి: {docs}."
        if language == "hindi":
            return f"{name} ke liye aam taur par ye documents chahiye: {docs}."
        return f"For {name}, the usual documents are: {docs}."
    if intent == "eligibility":
        if language == "telugu":
            return f"{name} అర్హత వివరాలు: {value}"
        if language == "hindi":
            return f"{name} eligibility: {value}"
        return f"{name} eligibility: {value}"
    if intent == "process":
        steps = " ".join(f"{index + 1}. {step}" for index, step in enumerate(value))
        if language == "telugu":
            return f"{name} దరఖాస్తు విధానం: {steps}"
        if language == "hindi":
            return f"{name} process: {steps}"
        return f"{name} process: {steps}"
    if intent == "fee":
        return f"{name} fee: {value}"
    if intent == "timeline":
        return f"{name} timeline: {value}"
    return str(value)


def _baseline_answer(
    intent: str,
    baseline: dict[str, Any],
    language: str = "english",
) -> tuple[str, bool] | None:
    name = baseline["title"]
    if intent == "documents":
        docs = ", ".join(
            str(document.get("label") or document.get("key"))
            for document in baseline["required_documents"]
        )
        if language == "telugu":
            return f"{name} కోసం అవసరమైన పత్రాలు: {docs}.", True
        return f"For {name}, the required documents are: {docs}.", True
    if intent == "eligibility":
        if language == "telugu":
            return f"{name} అర్హత వివరాలు: {' '.join(baseline['eligibility'])}", True
        return f"{name} eligibility: {' '.join(baseline['eligibility'])}", True
    if intent == "purpose":
        if language == "telugu":
            return f"{name} ఉద్దేశ్యం: {baseline['purpose']}", True
        return f"{name} purpose: {baseline['purpose']}", True
    if intent == "department":
        if language == "telugu":
            return f"{name} సేవను {baseline['department']} నిర్వహిస్తుంది.", True
        return f"{name} is handled by {baseline['department']}.", True
    if intent == "timeline":
        if language == "telugu":
            return f"{name} ప్రాసెసింగ్ సమయం: {baseline['processing_time']['label']}.", True
        return f"{name} processing time is {baseline['processing_time']['label']}.", True
    if intent == "fee":
        fee = baseline.get("fee") or {}
        amount = fee.get("amount")
        if amount in (None, ""):
            return f"{name} fee data is not available in the certificate baseline.", False
        return f"{name} fee is {amount} rupees in the service baseline.", True
    if intent == "verification":
        verify = baseline["how_to_verify"]
        if language == "telugu":
            return f"Certificate number లేదా verification hash ఉపయోగించి {verify['route']} వద్ద {name}ను ధృవీకరించండి.", True
        return f"Verify {name} at {verify['route']} using a certificate number or verification hash.", True
    if intent == "process":
        if language == "telugu":
            return f"{name} కోసం service form తెరిచి, అవసరమైన వివరాలు నింపి, పత్రాలు upload చేసి, పరిశీలించిన తరువాత మీరే submit చేయండి.", True
        return f"To apply for {name}, open the service form, fill required fields, upload the required documents, review, and submit manually.", True
    if intent in {"validity", "old_vs_new"}:
        validity = baseline["validity"]
        if not validity.get("verified"):
            return f"Verified validity is not available for {name}. Please check the official source before relying on a value.", False
        answer = validity["answer"]
        if intent == "old_vs_new" and validity.get("source"):
            answer = f"Current verified value: {validity['value']}. Previous value is available only when the verified rule source includes it."
        return answer, True
    return None


def _baseline_response(
    detected_language: str,
    language_code: str,
    intent: str,
    service_id: str | None,
) -> ChatResponse | None:
    if not service_id:
        return None
    baseline = certificate_baseline_service.baseline_for_service(service_id)
    if baseline is None:
        return None
    answer_payload = _baseline_answer(intent, baseline, detected_language)
    if answer_payload is None:
        return None
    answer, verified = answer_payload
    validity_source = baseline.get("validity", {}).get("source")
    references = [
        {
            "service_id": baseline["service_id"],
            "title": baseline["title"],
            "department": baseline["department"],
            "source_type": baseline["source"]["type"],
            "source_label": baseline["source"]["label"],
            "verified": verified,
            **({"circular_number": validity_source.get("circular_number")} if validity_source else {}),
            **({"effective_date": validity_source.get("effective_date")} if validity_source else {}),
        }
    ]
    return ChatResponse(
        success=True,
        answer=answer,
        language=detected_language,
        language_code=language_code,
        intent=intent,
        scheme_or_service=baseline["service_id"],
        source=_source("certificate_baseline", "NiyamGuard certificate baseline", references),
        method="certificate_baseline",
        confidence=0.86 if verified else 0.55,
        verified=verified,
        fallback=not verified,
        provider="deterministic",
    )


def _structured_source(service_id: str | None, circular: dict[str, Any] | None = None) -> ChatSource:
    reference = {
        "service_id": service_id,
        "source_type": "service_definition",
        "source_label": "NiyamGuard structured service rules",
        "verified": True,
    }
    if circular:
        reference.update(
            {
                "circular_number": circular.get("number"),
                "effective_date": circular.get("effective_date"),
                "title": circular.get("title"),
            }
        )
    return _source("deterministic_rule_engine", "NiyamGuard structured service rules", [reference])


def _format_documents(documents: list[dict[str, Any]]) -> str:
    parts = []
    for document in documents:
        name = document.get("name") or document.get("key")
        copies = document.get("copies_required") or 1
        notes = f" ({document['notes']})" if document.get("notes") else ""
        parts.append(f"{name} x{copies}{notes}")
    return ", ".join(parts) if parts else "None listed"


def _structured_documents_response(
    detected_language: str,
    language_code: str,
    service_id: str,
) -> ChatResponse | None:
    comparison = scheme_rule_engine.compare_with_previous(service_id)
    if comparison is None:
        return None
    docs = scheme_rule_engine.documents_for(service_id)
    if docs is None:
        return None
    mandatory = _format_documents(docs["mandatory_documents"])
    secondary = _format_documents(docs["secondary_documents"])
    answer = (
        f"For {docs['service_name']}, mandatory documents are: {mandatory}. "
        f"Secondary/supporting documents are: {secondary}."
    )
    if detected_language == "telugu":
        answer = (
            f"{docs['service_name']} కోసం తప్పనిసరి పత్రాలు: {mandatory}. "
            f"అదనపు లేదా సహాయక పత్రాలు: {secondary}."
        )
    return ChatResponse(
        success=True,
        answer=answer,
        language=detected_language,
        language_code=language_code,
        intent="documents",
        scheme_or_service=docs["service_id"],
        source=_structured_source(docs["service_id"], docs.get("circular")),
        method="deterministic_rule_engine",
        confidence=0.92,
        verified=True,
        fallback=False,
        provider="deterministic",
    )


def _structured_eligibility_response(
    message: str,
    detected_language: str,
    language_code: str,
    service_id: str,
    profile: dict[str, Any],
) -> ChatResponse | None:
    result = scheme_rule_engine.check_eligibility(service_id, profile, message)
    if result is None:
        return None
    if result["eligible"]:
        status = "Eligible based on the provided profile"
        details = " ".join(result["reasons_met"])
    else:
        status = "Not eligible or not fully verifiable based on the provided profile"
        details = " ".join(result["reasons_failed"])
    answer = f"{result['service_name']} eligibility check: {status}. {details}".strip()
    if detected_language == "telugu":
        telugu_status = (
            "మీరు ఇచ్చిన వివరాల ప్రకారం అర్హత ఉంది"
            if result["eligible"]
            else "మీరు ఇచ్చిన వివరాలతో అర్హతను పూర్తిగా నిర్ధారించలేము"
        )
        answer = f"{result['service_name']} అర్హత పరిశీలన: {telugu_status}. {details}".strip()
    return ChatResponse(
        success=True,
        answer=answer,
        language=detected_language,
        language_code=language_code,
        intent="eligibility",
        scheme_or_service=result["service_id"],
        source=_structured_source(result["service_id"], result.get("circular")),
        method="deterministic_rule_engine",
        confidence=0.92,
        verified=True,
        fallback=False,
        provider="deterministic",
    )


def _structured_process_response(
    detected_language: str,
    language_code: str,
    service_id: str,
) -> ChatResponse | None:
    result = scheme_rule_engine.process_for(service_id)
    if result is None:
        return None
    steps = " ".join(
        f"{step['step_number']}. {step['title']}: {step['description']}"
        for step in result["steps"]
    )
    answer = f"{result['service_name']} process: {steps}"
    if detected_language == "telugu":
        answer = f"{result['service_name']} దరఖాస్తు విధానం: {steps}"
    return ChatResponse(
        success=True,
        answer=answer,
        language=detected_language,
        language_code=language_code,
        intent="process",
        scheme_or_service=result["service_id"],
        source=_structured_source(result["service_id"], result.get("circular")),
        method="deterministic_rule_engine",
        confidence=0.91,
        verified=True,
        fallback=False,
        provider="deterministic",
    )


def _structured_change_response(
    detected_language: str,
    language_code: str,
    service_id: str,
) -> ChatResponse | None:
    result = scheme_rule_engine.compare_with_previous(service_id)
    if result is None:
        return None
    if not result["has_previous_version"]:
        answer = result["message"]
    else:
        changes = "; ".join(
            f"{item['field']}: {item['old_value']} -> {item['new_value']}"
            for item in result["changes"]
        ) or "No numeric rule changes."
        added_docs = ", ".join(result["document_changes"]["added"]) or "none"
        removed_docs = ", ".join(result["document_changes"]["removed"]) or "none"
        answer = (
            f"{result['service_name']} changed from {result['old_circular'].get('number')} "
            f"to {result['new_circular'].get('number')}. Rule changes: {changes}. "
            f"Documents added: {added_docs}. Documents removed: {removed_docs}."
        )
        if detected_language == "telugu":
            answer = (
                f"{result['service_name']} నియమం {result['old_circular'].get('number')} నుంచి "
                f"{result['new_circular'].get('number')}కి మారింది. నియమ మార్పులు: {changes}. "
                f"చేర్చిన పత్రాలు: {added_docs}. తొలగించిన పత్రాలు: {removed_docs}."
            )
    return ChatResponse(
        success=True,
        answer=answer,
        language=detected_language,
        language_code=language_code,
        intent="old_vs_new",
        scheme_or_service=result["service_id"],
        source=_structured_source(result["service_id"], result.get("new_circular")),
        method="deterministic_rule_engine",
        confidence=0.93,
        verified=True,
        fallback=False,
        provider="deterministic",
    )


def _structured_scheme_comparison_response(
    message: str,
    detected_language: str,
    language_code: str,
    context: dict[str, Any],
    profile: dict[str, Any],
) -> ChatResponse | None:
    service_ids = scheme_rule_engine.service_ids_from_text(message, context)
    if len(service_ids) < 2:
        return None
    result = scheme_rule_engine.compare_schemes(service_ids[:4], profile, message)
    rows = result["table"]
    answer_rows = []
    for row in rows:
        if row.get("error"):
            answer_rows.append(f"{row['service_id']}: {row['error']}")
            continue
        benefit = row.get("benefit_amount")
        income_limit = row.get("income_limit_annual")
        age_min = row.get("age_min")
        answer_rows.append(
            f"{row['service_name']}: benefit {benefit or 'not listed'}, "
            f"income limit {income_limit or 'not listed'}, minimum age {age_min or 'not listed'}, "
            f"processing {row.get('processing_time_days')} days, mandatory documents {row.get('mandatory_document_count')}."
        )
    answer = "Scheme comparison: " + " ".join(answer_rows)
    if detected_language == "telugu":
        answer = "పథకాల పోలిక: " + " ".join(answer_rows)
    return ChatResponse(
        success=True,
        answer=answer,
        language=detected_language,
        language_code=language_code,
        intent="scheme_comparison",
        scheme_or_service=None,
        source=_source(
            "deterministic_rule_engine",
            "NiyamGuard structured service rules",
            [{"service_id": row.get("service_id"), "verified": not bool(row.get("error"))} for row in rows],
        ),
        method="deterministic_rule_engine",
        sources=rows,
        confidence=0.9,
        verified=True,
        fallback=False,
        provider="deterministic",
    )


def _structured_response(
    message: str,
    detected_language: str,
    language_code: str,
    intent: str,
    service_id: str | None,
    context: dict[str, Any],
    profile: dict[str, Any],
) -> ChatResponse | None:
    if intent == "scheme_comparison":
        return _structured_scheme_comparison_response(message, detected_language, language_code, context, profile)
    if not service_id:
        return None
    if intent == "documents":
        return _structured_documents_response(detected_language, language_code, service_id)
    if intent == "eligibility":
        return _structured_eligibility_response(message, detected_language, language_code, service_id, profile)
    if intent == "process":
        return _structured_process_response(detected_language, language_code, service_id)
    if intent == "old_vs_new":
        return _structured_change_response(detected_language, language_code, service_id)
    return None


def _fallback(language: str, intent: str) -> ChatResponse:
    if language == "telugu":
        answer = "ఈ ప్రశ్నకు ధృవీకరించిన సమాచారం అందుబాటులో లేదు. దయచేసి అధికారిక ప్రభుత్వ మూలంలో పరిశీలించండి."
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


def _chat_source_from_hybrid(hybrid: dict[str, Any]) -> tuple[ChatSource, str | None, bool, bool]:
    method = str(hybrid.get("method") or "")
    sources = hybrid.get("sources") or []
    if method == "exact_rule_engine":
        return ChatSource(**chat_source("Verified NiyamGuard Knowledge Base", sources)), "deterministic", bool(hybrid["verified"]), False
    if method == "decision_table":
        references = [
            {
                "chunk_id": source.get("chunk_id") or f"svc_{source.get('service_id')}",
                "service_id": source.get("service_id"),
                "title": source.get("label"),
                "source_type": "seed_demo",
                "source_label": source.get("label"),
                "verified": False,
                "score": source.get("score"),
            }
            for source in sources
        ]
        return ChatSource(type="rag", label="NiyamGuard knowledge index", references=references), "fallback", False, True
    if method == "rag_search":
        references = [
            {
                "chunk_id": source.get("chunk_id"),
                "service_id": source.get("service_id"),
                "title": source.get("label"),
                "source_type": source.get("type"),
                "source_label": source.get("label"),
                "verified": bool(source.get("verified")),
                "score": source.get("score"),
            }
            for source in sources
        ]
        return ChatSource(type="rag", label="NiyamGuard knowledge index", references=references), hybrid.get("provider"), bool(hybrid["verified"]), bool(hybrid["fallback"])
    return ChatSource(**chat_source("NiyamGuard Hybrid Intelligence", sources)), hybrid.get("provider") or method, bool(hybrid["verified"]), bool(hybrid["fallback"])


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
    profile = profile or {}
    detected = detect_language(message, None if language == "auto" else language)
    detected_language = str(detected["detected_language"])
    language_code = str(detected["language_code"])
    intent = _intent(message)
    service_id, item = _service_from_message(message, context)
    if intent == "status":
        status_answer = "Open My Applications to view your records, or use Track Application with your NGSP application number."
        if detected_language == "telugu":
            status_answer = "మీ దరఖాస్తులను చూడటానికి My Applications తెరవండి లేదా NGSP దరఖాస్తు సంఖ్యతో Track Application ఉపయోగించండి."
        return ChatResponse(
            success=True,
            answer=status_answer,
            language=detected_language,
            language_code=language_code,
            intent=intent,
            source=_source(
                "service_portal_route",
                "NiyamGuard application tracking",
                [{"route": "/track", "label": "Track Application"}],
            ),
            confidence=1.0,
            verified=True,
            fallback=False,
            provider="deterministic",
            method="service_portal_route",
        )
    if intent in {"documents", "eligibility", "process", "old_vs_new", "scheme_comparison"}:
        structured_service_ids = scheme_rule_engine.service_ids_from_text(message, context)
        if structured_service_ids:
            service_id = structured_service_ids[0]
            item = LOCAL_KNOWLEDGE.get(service_id)

    structured = _structured_response(message, detected_language, language_code, intent, service_id, context, profile)
    if structured is not None:
        return structured

    if intent in {"documents", "eligibility", "purpose", "department", "process", "fee", "timeline", "verification"}:
        baseline_response = _baseline_response(detected_language, language_code, intent, service_id)
        if baseline_response is not None:
            return baseline_response

    hybrid = answer_question(message, language=language, context=context, profile=profile or {})
    if (
        hybrid.get("method")
        and hybrid.get("method") != "safe_fallback"
        and not bool(hybrid.get("fallback"))
    ):
        sources = hybrid.get("sources") or []
        source, provider, verified, fallback = _chat_source_from_hybrid(hybrid)
        return ChatResponse(
            success=True,
            answer=hybrid["answer"],
            language=hybrid["language"],
            language_code=hybrid["language_code"],
            intent=hybrid["intent"],
            scheme_or_service=hybrid.get("service_id"),
            source=source,
            method=hybrid.get("method"),
            sources=sources,
            confidence=hybrid["confidence"],
            verified=verified,
            fallback=fallback,
            provider=provider,
            limitations=hybrid.get("limitations"),
        )

    if intent in {"documents", "eligibility", "purpose", "department", "process", "validity", "fee", "timeline", "verification", "old_vs_new"}:
        baseline_response = _baseline_response(detected_language, language_code, intent, service_id or "income_certificate")
        if baseline_response is not None:
            return baseline_response

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
