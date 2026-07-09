from __future__ import annotations


def route(intent: str) -> str:
    if intent in {"validity", "policy_update"}:
        return "exact_rule_engine"
    if intent in {"application_status"}:
        return "application_lookup"
    if intent in {"certificate_verification"}:
        return "certificate_lookup"
    if intent in {"documents", "eligibility", "process", "fee", "timeline", "general_service_question"}:
        return "decision_table"
    if intent in {"circular_summary", "compliance_impact", "officer_next_action"}:
        return "local_llm"
    if intent == "service_recommendation":
        return "rag_search"
    return "safe_fallback"

