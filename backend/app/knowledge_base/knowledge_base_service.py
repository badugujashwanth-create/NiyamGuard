from app.models.knowledge_models import (
    LatestRuleResponse,
    RuleSource,
    VerifiedPolicyRule,
)
from app.knowledge_base.platform_store import add_audit_event, now_iso, read_store, write_store


def _source_for_rule(rule: VerifiedPolicyRule) -> RuleSource | None:
    store = read_store()
    circular = next((item for item in store.circulars if item.id == rule.circular_id), None)
    if circular is not None:
        return RuleSource(
            circular_id=circular.id,
            circular_number=circular.circular_number,
            department=circular.department,
            effective_date=circular.effective_date,
            confidence=rule.confidence,
        )
    circular_document = next((item for item in store.circular_documents if item.id == rule.circular_id), None)
    if circular_document is None:
        return None
    return RuleSource(
        circular_id=circular_document.id,
        circular_number=circular_document.circular_number,
        department=circular_document.department,
        effective_date=circular_document.effective_date,
        confidence=rule.confidence,
    )


def list_rules() -> list[VerifiedPolicyRule]:
    return read_store().verified_rules


def get_rule(rule_id: str) -> VerifiedPolicyRule | None:
    return next((rule for rule in read_store().verified_rules if rule.id == rule_id), None)


def latest_rule(service_id: str, rule_key: str) -> LatestRuleResponse:
    candidates = [
        rule
        for rule in read_store().verified_rules
        if rule.service_id == service_id and rule.rule_key == rule_key and rule.status == "active"
    ]
    if not candidates:
        return LatestRuleResponse(
            success=False,
            verified=False,
            service_id=service_id,
            rule_key=rule_key,
            answer="Verified rule not found.",
        )
    rule = sorted(candidates, key=lambda item: item.effective_date, reverse=True)[0]
    return LatestRuleResponse(
        success=True,
        verified=True,
        service_id=rule.service_id,
        rule_key=rule.rule_key,
        current_value=rule.current_value,
        unit=rule.unit,
        previous_value=rule.previous_value,
        source=_source_for_rule(rule),
        answer=f"{rule.rule_name} is currently {rule.current_value} {rule.unit or ''}.".strip(),
    )


def rules_by_service(service_id: str) -> list[VerifiedPolicyRule]:
    return [rule for rule in read_store().verified_rules if rule.service_id == service_id]


def search_rules(query: str) -> list[VerifiedPolicyRule]:
    q = query.casefold().strip()
    if not q:
        return list_rules()
    return [
        rule
        for rule in read_store().verified_rules
        if q in " ".join(
            [
                rule.service_id,
                rule.rule_key,
                rule.rule_name,
                rule.current_value,
                rule.previous_value or "",
                rule.source_clause,
            ]
        ).casefold()
    ]


def supersede_older_rules(new_rule_id: str) -> VerifiedPolicyRule | None:
    store = read_store()
    new_rule = next((rule for rule in store.verified_rules if rule.id == new_rule_id), None)
    if new_rule is None:
        return None
    for rule in store.verified_rules:
        if (
            rule.id != new_rule.id
            and rule.service_id == new_rule.service_id
            and rule.rule_key == new_rule.rule_key
            and rule.status == "active"
            and rule.effective_date < new_rule.effective_date
        ):
            rule.status = "superseded"
            rule.updated_at = now_iso()
            new_rule.supersedes_rule_id = rule.id
    new_rule.updated_at = now_iso()
    add_audit_event(store, "verified_rule_superseded_older_rules", {"rule_id": new_rule.id})
    write_store(store)
    return new_rule


def citizen_safe_answer(service_id: str, rule_key: str) -> dict:
    result = latest_rule(service_id, rule_key)
    if not result.success:
        return {"success": False, "verified": False, "answer": "Verified rule not found.", "source": None}
    value = f"{result.current_value} {result.unit or ''}".strip()
    return {
        "success": True,
        "verified": True,
        "answer": f"Income Certificate validity is currently {value}."
        if service_id == "income_certificate" and rule_key == "validity"
        else f"{rule_key.replace('_', ' ').title()} is currently {value}.",
        "source": result.source.model_dump() if result.source else None,
    }


def source_circular_info(rule_id: str) -> dict | None:
    rule = get_rule(rule_id)
    if rule is None:
        return None
    store = read_store()
    circular = next((item for item in store.circulars if item.id == rule.circular_id), None)
    if circular:
        return circular.model_dump()
    circular_document = next((item for item in store.circular_documents if item.id == rule.circular_id), None)
    return circular_document.model_dump() if circular_document else None
