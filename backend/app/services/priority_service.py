from datetime import date

from app.models.compliance_models import ComplianceFinding
from app.models.priority_models import PriorityScore
from app.services.platform_store import add_audit_event, now_iso, read_store, write_store


SYSTEM_TYPE_SCORE = {
    "portal": 30,
    "form": 25,
    "sop": 20,
    "faq": 15,
    "notification": 10,
    "manual": 10,
    "district_office": 15,
}
RULE_TYPE_SCORE = {
    "eligibility": 30,
    "validity": 25,
    "document_requirement": 20,
    "deadline": 30,
    "fee": 10,
}


def _level(score: int) -> str:
    if score >= 80:
        return "critical"
    if score >= 60:
        return "high"
    if score >= 30:
        return "medium"
    return "low"


def _urgency(effective_date: str) -> int:
    try:
        days = (date.fromisoformat(effective_date) - date.today()).days
    except ValueError:
        return 10
    if days <= 0:
        return 30
    if days <= 7:
        return 20
    if days <= 30:
        return 10
    return 0


def score_finding(finding: ComplianceFinding) -> PriorityScore:
    store = read_store()
    system = next(item for item in store.connected_systems if item.id == finding.connected_system_id)
    rule = next(item for item in store.verified_rules if item.id == finding.verified_rule_id)
    system_score = SYSTEM_TYPE_SCORE.get(system.system_type, 10)
    rule_score = RULE_TYPE_SCORE.get(finding.rule_key, 10)
    urgency_score = _urgency(rule.effective_date)
    service_volume_score = 10 if finding.service_id == "income_certificate" else 5
    deadline_score = 10 if finding.rule_key in {"deadline", "validity"} else 0
    status_penalty = 0 if finding.status == "compliant" else 10
    total = min(
        100,
        system_score
        + rule_score
        + urgency_score
        + service_volume_score
        + deadline_score
        + status_penalty,
    )
    if finding.status == "compliant":
        total = min(total, 25)
    return PriorityScore(
        id=f"prio_{finding.id}",
        finding_id=finding.id,
        score=total,
        priority_level=_level(total),
        citizen_impact_score=system_score,
        urgency_score=urgency_score,
        service_volume_score=service_volume_score,
        deadline_score=deadline_score,
        rule_type_score=rule_score,
        reason=(
            f"{system.name} is a {system.system_type}; {finding.rule_key} changes affect citizens, "
            f"and the rule is effective from {rule.effective_date}."
        ),
        created_at=now_iso(),
    )


def recalculate_priorities() -> list[PriorityScore]:
    store = read_store()
    scores = [score_finding(finding) for finding in store.compliance_findings]
    store.priority_scores = scores
    add_audit_event(store, "priority_scores_recalculated", {"scores": len(scores)})
    write_store(store)
    return scores


def list_priorities() -> list[PriorityScore]:
    store = read_store()
    if not store.priority_scores and store.compliance_findings:
        return recalculate_priorities()
    return store.priority_scores


def high_impact() -> list[PriorityScore]:
    return [score for score in list_priorities() if score.priority_level in {"high", "critical"}]


def service_priorities(service_id: str) -> list[PriorityScore]:
    store = read_store()
    finding_ids = {item.id for item in store.compliance_findings if item.service_id == service_id}
    return [score for score in list_priorities() if score.finding_id in finding_ids]
