from __future__ import annotations

import re
from typing import Any

from app.knowledge_base.platform_store import read_store
from app.models.service_portal_models import ServiceDefinition
from app.services.hybrid_intelligence import intent_detector


COMPARABLE_FIELD_LABELS = {
    "validity_period_months": "Validity period (months)",
    "income_limit_annual": "Annual income limit",
    "age_min": "Minimum age",
    "age_max": "Maximum age",
    "benefit_amount": "Benefit amount",
    "processing_time_days": "Processing time (days)",
}

OPERATORS = {
    "==": lambda user, expected: user == expected,
    "!=": lambda user, expected: user != expected,
    "<": lambda user, expected: user is not None and user < expected,
    "<=": lambda user, expected: user is not None and user <= expected,
    ">": lambda user, expected: user is not None and user > expected,
    ">=": lambda user, expected: user is not None and user >= expected,
    "in": lambda user, expected: user in expected,
    "not_in": lambda user, expected: user not in expected,
    "contains": lambda user, expected: isinstance(user, (list, tuple, set)) and expected in user,
}


def service_by_id(service_id: str | None) -> ServiceDefinition | None:
    if not service_id:
        return None
    return next(
        (service for service in read_store().service_definitions if service.service_id == service_id and service.enabled),
        None,
    )


def service_ids_from_text(text: str, context: dict[str, Any] | None = None) -> list[str]:
    found: list[tuple[str, int]] = []
    enabled_service_ids = {
        service.service_id for service in read_store().service_definitions if service.enabled
    }
    context_service = (context or {}).get("service_id") or (context or {}).get("form_id")
    if context_service and str(context_service) in enabled_service_ids:
        found.append((str(context_service), 1))
    normalized = text.casefold().replace("_", " ")
    for service_id, aliases in intent_detector.aliases()["services"].items():
        if service_id not in enabled_service_ids:
            continue
        best_score = max((len(alias) for alias in aliases if alias.casefold() in normalized), default=0)
        if best_score:
            found.append((service_id, best_score))
    found.sort(key=lambda item: item[1], reverse=True)
    unique: list[str] = []
    for service_id, _score in found:
        if service_id not in unique:
            unique.append(service_id)
    return unique


def service_id_from_text(text: str, context: dict[str, Any] | None = None) -> str | None:
    ids = service_ids_from_text(text, context)
    if ids:
        return ids[0]
    return intent_detector.detect_service_id(text, context)


def _bindings(service: ServiceDefinition) -> dict[str, Any]:
    return service.rule_bindings_json or {}


def _current_version(service: ServiceDefinition) -> dict[str, Any] | None:
    version = _bindings(service).get("current_version")
    return version if isinstance(version, dict) else None


def _previous_version(service: ServiceDefinition) -> dict[str, Any] | None:
    version = _bindings(service).get("previous_version")
    return version if isinstance(version, dict) else None


def _normalize_profile(profile: dict[str, Any] | None, message: str = "") -> dict[str, Any]:
    normalized = dict(profile or {})
    text = message.casefold()

    def set_number(field: str, patterns: list[str]) -> None:
        if normalized.get(field) not in (None, ""):
            normalized[field] = _to_number(normalized.get(field))
            return
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                value = _to_number(match.group(1))
                if value is not None:
                    normalized[field] = value
                    return

    set_number("age", [r"\bage\s*(?:is|=|:)?\s*(\d{1,3})\b", r"\b(\d{1,3})\s*(?:years|yrs|year old)\b"])
    set_number(
        "annual_income",
        [
            r"\bannual income\s*(?:is|=|:)?\s*(?:rs\.?|inr)?\s*([\d,]+)\b",
            r"\bincome\s*(?:is|=|:)?\s*(?:rs\.?|inr)?\s*([\d,]+)\b",
            r"\b([\d.]+)\s*lakh\b",
        ],
    )
    if "lakh" in text and isinstance(normalized.get("annual_income"), (int, float)) and normalized["annual_income"] < 1000:
        normalized["annual_income"] = int(float(normalized["annual_income"]) * 100000)

    if normalized.get("category") in (None, ""):
        for category in ("sc", "st", "obc", "general", "minority"):
            if re.search(rf"\b{category}\b", text):
                normalized["category"] = category.upper() if category != "general" else "General"
                break

    if normalized.get("currently_enrolled") in (None, ""):
        if any(word in text for word in ("student", "studying", "enrolled", "college", "school")):
            normalized["currently_enrolled"] = True
    return normalized


def _to_number(value: Any) -> float | int | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        return value
    try:
        parsed = float(str(value).replace(",", "").strip())
    except (TypeError, ValueError):
        return None
    return int(parsed) if parsed.is_integer() else parsed


def _evaluate_rule(rule: dict[str, Any], profile: dict[str, Any]) -> tuple[bool, str]:
    field = str(rule.get("field_name") or "")
    operator = str(rule.get("operator") or "")
    expected = rule.get("value")
    user_value = profile.get(field)
    op_fn = OPERATORS.get(operator)
    explanation = str(rule.get("explanation") or field.replace("_", " ").title())
    if op_fn is None:
        return False, f"{explanation} - unsupported operator {operator}."
    if isinstance(expected, (int, float)):
        user_value = _to_number(user_value)
    try:
        passed = bool(op_fn(user_value, expected))
    except TypeError:
        return False, f"{explanation} - value was not provided in a comparable format."
    if passed:
        return True, explanation
    if user_value is None:
        return False, f"{explanation} - this could not be verified because {field.replace('_', ' ')} was not provided."
    if isinstance(expected, (int, float)) and isinstance(user_value, (int, float)):
        if operator in ("<=", "<") and user_value > expected:
            return False, f"{explanation} - your value ({user_value:,.0f}) exceeds this by {user_value - expected:,.0f}."
        if operator in (">=", ">") and user_value < expected:
            return False, f"{explanation} - your value ({user_value:,.0f}) is short by {expected - user_value:,.0f}."
    if operator == "in":
        return False, f"{explanation} - your value '{user_value}' is not in the allowed list."
    return False, explanation


def check_eligibility(service_id: str, profile: dict[str, Any] | None = None, message: str = "") -> dict[str, Any] | None:
    service = service_by_id(service_id)
    if service is None:
        return None
    version = _current_version(service)
    rules = list((version or {}).get("eligibility_rules") or [])
    if not rules:
        return None
    normalized_profile = _normalize_profile(profile, message)
    reasons_met: list[str] = []
    reasons_failed: list[str] = []
    for rule in rules:
        passed, reason = _evaluate_rule(rule, normalized_profile)
        if passed:
            reasons_met.append(reason)
        else:
            reasons_failed.append(reason)
    circular = (version or {}).get("circular") or {}
    return {
        "service_id": service.service_id,
        "service_name": service.name,
        "eligible": len(reasons_failed) == 0,
        "reasons_met": reasons_met,
        "reasons_failed": reasons_failed,
        "required_fields": sorted({str(rule.get("field_name")) for rule in rules if rule.get("field_name")}),
        "profile_used": normalized_profile,
        "circular": circular,
    }


def documents_for(service_id: str) -> dict[str, Any] | None:
    service = service_by_id(service_id)
    if service is None:
        return None
    version = _current_version(service)
    docs = list((version or {}).get("documents") or [])
    if not docs:
        docs = [
            {
                "key": item.get("key"),
                "name": item.get("label") or item.get("key"),
                "mandatory": bool(item.get("required")),
                "copies_required": item.get("copies_required", 1),
                "notes": item.get("notes"),
            }
            for item in service.required_documents_json
        ]
    circular = (version or {}).get("circular") or {}
    return {
        "service_id": service.service_id,
        "service_name": service.name,
        "circular": circular,
        "mandatory_documents": [_format_document(doc) for doc in docs if doc.get("mandatory", doc.get("required", True))],
        "secondary_documents": [_format_document(doc) for doc in docs if not doc.get("mandatory", doc.get("required", True))],
    }


def _format_document(doc: dict[str, Any]) -> dict[str, Any]:
    return {
        "key": doc.get("key"),
        "name": doc.get("name") or doc.get("label") or doc.get("key"),
        "copies_required": int(doc.get("copies_required") or 1),
        "notes": doc.get("notes"),
    }


def process_for(service_id: str) -> dict[str, Any] | None:
    service = service_by_id(service_id)
    if service is None:
        return None
    version = _current_version(service)
    steps = list((version or {}).get("process_steps") or [])
    if not steps:
        return None
    circular = (version or {}).get("circular") or {}
    return {
        "service_id": service.service_id,
        "service_name": service.name,
        "circular": circular,
        "steps": sorted(steps, key=lambda item: int(item.get("step_number") or 0)),
    }


def compare_with_previous(service_id: str) -> dict[str, Any] | None:
    service = service_by_id(service_id)
    if service is None:
        return None
    current = _current_version(service)
    previous = _previous_version(service)
    if not current:
        return None
    current_circular = current.get("circular") or {}
    if not previous:
        return {
            "service_id": service.service_id,
            "service_name": service.name,
            "has_previous_version": False,
            "message": f"{service.name} has no earlier structured version on record.",
            "new_circular": current_circular,
        }
    changes: list[dict[str, Any]] = []
    old_fields = previous.get("comparable_fields") or {}
    new_fields = current.get("comparable_fields") or {}
    for field in sorted(set(old_fields) | set(new_fields)):
        old_value = old_fields.get(field)
        new_value = new_fields.get(field)
        if old_value != new_value:
            changes.append(
                {
                    "field": COMPARABLE_FIELD_LABELS.get(field, field.replace("_", " ").title()),
                    "old_value": old_value,
                    "new_value": new_value,
                }
            )
    old_docs = {str(doc.get("name") or doc.get("label")) for doc in previous.get("documents") or []}
    new_docs = {str(doc.get("name") or doc.get("label")) for doc in current.get("documents") or []}
    return {
        "service_id": service.service_id,
        "service_name": service.name,
        "has_previous_version": True,
        "old_circular": previous.get("circular") or {},
        "new_circular": current_circular,
        "changes": changes,
        "document_changes": {
            "added": sorted(new_docs - old_docs),
            "removed": sorted(old_docs - new_docs),
        },
    }


def compare_schemes(service_ids: list[str], profile: dict[str, Any] | None = None, message: str = "") -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for service_id in service_ids:
        service = service_by_id(service_id)
        if service is None:
            rows.append({"service_id": service_id, "error": "Service not found"})
            continue
        version = _current_version(service) or {}
        fields = version.get("comparable_fields") or {}
        docs = documents_for(service.service_id) or {}
        row = {
            "service_id": service.service_id,
            "service_name": service.name,
            "department": service.department,
            "category": service.category,
            "circular": (version.get("circular") or {}).get("number"),
            "income_limit_annual": fields.get("income_limit_annual"),
            "age_min": fields.get("age_min"),
            "age_max": fields.get("age_max"),
            "benefit_amount": fields.get("benefit_amount"),
            "processing_time_days": fields.get("processing_time_days", service.processing_days),
            "mandatory_document_count": len(docs.get("mandatory_documents") or []),
        }
        eligibility = check_eligibility(service.service_id, profile, message)
        if eligibility is not None:
            row["eligible_for_user"] = eligibility["eligible"]
            row["reasons_failed"] = eligibility["reasons_failed"]
        rows.append(row)
    return {"table": rows}


def find_circulars(query: str, limit: int = 5) -> list[dict[str, Any]]:
    normalized = query.casefold()
    results: list[dict[str, Any]] = []
    store = read_store()
    for circular in store.circulars:
        haystack = f"{circular.circular_number} {circular.title} {circular.department} {circular.source_text}".casefold()
        if normalized in haystack:
            results.append(
                {
                    "id": circular.id,
                    "doc_number": circular.circular_number,
                    "title": circular.title,
                    "issued_date": circular.issue_date,
                    "effective_date": circular.effective_date,
                    "needs_human_review": circular.status != "approved",
                }
            )
    if len(results) < limit:
        for service in store.service_definitions:
            if normalized in service.name.casefold():
                version = _current_version(service)
                circular = (version or {}).get("circular") or {}
                if circular:
                    results.append(
                        {
                            "id": circular.get("id") or service.service_id,
                            "doc_number": circular.get("number"),
                            "title": circular.get("title"),
                            "issued_date": circular.get("issue_date"),
                            "effective_date": circular.get("effective_date"),
                            "needs_human_review": False,
                        }
                    )
    return results[:limit]
