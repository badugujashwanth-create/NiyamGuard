from __future__ import annotations

from app.models.self_update_models import PolicyRuleCandidate, PolicyRuleDelta
from app.services import compliance_service
from app.services.platform_store import now_iso, read_store


def create_delta(candidate: PolicyRuleCandidate) -> PolicyRuleDelta:
    store = read_store()
    existing = next(
        (
            rule
            for rule in compliance_service._latest_active_rules(store.verified_rules)  # type: ignore[attr-defined]
            if rule.service_id == candidate.service_id and rule.rule_key == candidate.rule_key
        ),
        None,
    )
    previous = f"{existing.current_value} {existing.unit or ''}".strip() if existing else candidate.old_value
    proposed = f"{candidate.new_value} {candidate.unit or ''}".strip()
    if existing is None:
        change_type = "new_rule"
    elif previous == proposed:
        change_type = "no_change"
    else:
        change_type = "changed_value"
    return PolicyRuleDelta(
        id=f"delta_{candidate.id}",
        candidate_id=candidate.id,
        existing_rule_id=existing.id if existing else None,
        change_type=change_type,
        previous_value=previous,
        proposed_value=proposed,
        impact_level="high" if candidate.rule_key in {"validity", "eligibility", "deadline"} else "medium",
        reason=f"{candidate.rule_key} changes from {previous or 'none'} to {proposed}.",
        created_at=now_iso(),
    )
