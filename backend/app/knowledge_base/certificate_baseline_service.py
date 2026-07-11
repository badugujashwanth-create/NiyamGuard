from __future__ import annotations

import re
from typing import Any

from app.models.knowledge_models import CertificateReferenceDraft, VerifiedPolicyRule
from app.models.service_portal_models import ServiceDefinition
from app.knowledge_base.platform_store import add_audit_event, read_store, write_store
from app.services.time import now_iso


DEPARTMENT_BY_CATEGORY = {
    "Revenue Certificates": "Revenue Department",
    "Social Welfare Certificates": "Social Welfare Department",
    "Civil Registration": "Municipal / Panchayat Department",
    "Food Security": "Civil Supplies Department",
    "Welfare": "Social Welfare Department",
    "Education Welfare": "Education Welfare Department",
}


def _normalize_service_id(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "_", value.casefold()).strip("_")
    normalized = normalized.replace("_service", "").replace("_application", "")
    return normalized


def _department_for(service: ServiceDefinition) -> str:
    if service.department:
        return service.department
    return DEPARTMENT_BY_CATEGORY.get(service.category, service.category)


def _is_certificate_service(service: ServiceDefinition) -> bool:
    name = service.name.casefold()
    category = service.category.casefold()
    return (
        "certificate" in category
        or name.endswith("certificate")
        or service.service_id.endswith("_certificate")
    )


def _active_rule(service_id: str, rule_key: str) -> VerifiedPolicyRule | None:
    rules = [
        rule
        for rule in read_store().verified_rules
        if rule.service_id == service_id and rule.rule_key == rule_key and rule.status == "active"
    ]
    if not rules:
        return None
    return sorted(rules, key=lambda rule: rule.updated_at)[-1]


def _validity_reference(service: ServiceDefinition) -> dict[str, Any]:
    rule = _active_rule(service.service_id, "validity")
    if rule is None:
        return {
            "value": None,
            "verified": False,
            "answer": "Verified validity is not available for this service.",
            "source": None,
        }
    value = f"{rule.current_value} {rule.unit or ''}".strip()
    store = read_store()
    circular = next((item for item in store.circulars if item.id == rule.circular_id), None)
    return {
        "value": value,
        "verified": True,
        "answer": f"{service.name} validity is {value}.",
        "source": {
            "circular_id": rule.circular_id,
            "circular_number": circular.circular_number if circular else rule.circular_id,
            "department": circular.department if circular else _department_for(service),
            "rule_key": rule.rule_key,
            "effective_date": rule.effective_date,
            "confidence": rule.confidence,
        },
    }


def baseline_for_service(service_id: str) -> dict[str, Any] | None:
    store = read_store()
    normalized = _normalize_service_id(service_id)
    service = next(
        (
            item
            for item in store.service_definitions
            if item.enabled
            and (
                item.service_id == service_id
                or item.service_id == normalized
                or _normalize_service_id(item.name) == normalized
                or normalized.startswith(item.service_id)
            )
        ),
        None,
    )
    if service is None:
        return None
    if not _is_certificate_service(service):
        return None
    validity = _validity_reference(service)
    return {
        "service_id": service.service_id,
        "title": service.name,
        "purpose": service.description,
        "department": _department_for(service),
        "eligibility": service.eligibility_json,
        "required_documents": service.required_documents_json,
        "validity": validity,
        "processing_time": {
            "days": service.processing_days,
            "label": f"{service.processing_days} days",
            "verified": True,
        },
        "fee": {
            "amount": service.fee_amount,
            "currency": "INR",
            "verified": True,
        },
        "how_to_verify": {
            "route": "/verify-certificate",
            "accepted_inputs": ["certificate number", "verification hash"],
            "summary": "Use the certificate verification page to check a issued demo certificate or verification hash.",
        },
        "source": {
            "type": "service_definition",
            "label": "NiyamGuard service definitions with verified-rule overlay",
            "verified": validity["verified"],
        },
    }


def list_baselines() -> list[dict[str, Any]]:
    store = read_store()
    return [
        baseline
        for service in store.service_definitions
        if service.enabled
        for baseline in [baseline_for_service(service.service_id)]
        if baseline is not None
    ]


def has_baseline(service_id: str) -> bool:
    return baseline_for_service(service_id) is not None


def candidate_service_id(title: str) -> str:
    return _normalize_service_id(title)


def create_draft_if_missing(
    *,
    service_id: str,
    title: str,
    circular_id: str,
    circular_number: str | None = None,
    department: str | None = None,
    reason: str,
) -> CertificateReferenceDraft | None:
    if has_baseline(service_id):
        return None
    store = read_store()
    existing = next(
        (
            item
            for item in store.certificate_reference_drafts
            if item.service_id == service_id and item.source_circular_id == circular_id
        ),
        None,
    )
    if existing:
        return existing
    draft = CertificateReferenceDraft(
        id=f"certdraft_{service_id}_{len(store.certificate_reference_drafts) + 1:04d}",
        service_id=service_id,
        title=title,
        source_circular_id=circular_id,
        source_circular_number=circular_number,
        department=department,
        reason=reason,
        created_at=now_iso(),
    )
    store.certificate_reference_drafts.append(draft)
    add_audit_event(
        store,
        "certificate_reference_draft_created",
        {
            "entity_type": "certificate_reference_draft",
            "entity_id": draft.id,
            "service_id": service_id,
            "source_circular_id": circular_id,
        },
    )
    write_store(store)
    return draft
