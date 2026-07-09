from __future__ import annotations

from app.config import settings
from app.models.knowledge_models import VerifiedPolicyRule
from app.models.self_update_models import PolicyPublicationEvent, VerifiedPolicyRuleVersion
from app.services import compliance_orchestrator_service, knowledge_update_service, propagation_service
from app.services.platform_store import add_audit_event, now_iso, read_store, write_store


def _version_number(rule_id: str) -> int:
    versions = [item for item in read_store().verified_policy_rule_versions if item.rule_id == rule_id]
    return max((item.version_number for item in versions), default=0) + 1


def _publication_response(
    event: PolicyPublicationEvent,
    rule_version: VerifiedPolicyRuleVersion | None,
    *,
    already_published: bool = False,
) -> dict:
    store = read_store()
    knowledge_event = next(
        (item for item in store.knowledge_update_events if rule_version and item.rule_version_id == rule_version.id),
        None,
    )
    plan = next(
        (item for item in store.propagation_plans if rule_version and item.rule_version_id == rule_version.id),
        None,
    )
    compliance_run = next(
        (item for item in reversed(store.compliance_runs) if rule_version and item.affected_rule_id == rule_version.rule_id),
        None,
    )
    return {
        "success": True,
        "already_published": already_published,
        "rule_version": rule_version.model_dump() if rule_version else None,
        "publication_event": event.model_dump(),
        "knowledge_update": knowledge_event.model_dump() if knowledge_event else None,
        "propagation_plan": plan.model_dump() if plan else None,
        "compliance_run": compliance_run.model_dump() if compliance_run else None,
    }


def publish_rule_candidate(candidate_id: str, reviewer_user_id: str | None = None, notes: str | None = None) -> dict:
    store = read_store()
    candidate = next((item for item in store.policy_rule_candidates if item.id == candidate_id), None)
    if candidate is None:
        return {"success": False, "message": "Candidate not found."}
    existing_event = next((item for item in store.policy_publication_events if item.candidate_id == candidate_id), None)
    if existing_event:
        existing_version = next(
            (item for item in store.verified_policy_rule_versions if item.id == existing_event.rule_version_id),
            None,
        )
        return _publication_response(existing_event, existing_version, already_published=True)
    if settings.policy_update_requires_approval and candidate.status != "approved":
        return {"success": False, "message": "Candidate approval is required before publication."}
    circular = next((item for item in store.circular_documents if item.id == candidate.circular_id), None)
    existing = next(
        (
            rule
            for rule in store.verified_rules
            if rule.service_id == candidate.service_id and rule.rule_key == candidate.rule_key and rule.status == "active"
        ),
        None,
    )
    timestamp = now_iso()
    rule_id = existing.id if existing else f"rule_{candidate.service_id}_{candidate.rule_key}"
    current_versions = [item for item in store.verified_policy_rule_versions if item.rule_id == rule_id and item.is_current]
    for version in current_versions:
        version.is_current = False
    previous_version_id = current_versions[0].id if current_versions else None
    next_version_number = _version_number(rule_id)
    version = VerifiedPolicyRuleVersion(
        id=f"version_{rule_id}_{next_version_number}",
        rule_id=rule_id,
        version_number=next_version_number,
        service_id=candidate.service_id,
        rule_key=candidate.rule_key,
        value=candidate.new_value,
        unit=candidate.unit,
        source_circular_id=candidate.circular_id,
        source_circular_number=circular.circular_number if circular else candidate.circular_id,
        effective_date=candidate.effective_date,
        published_by=reviewer_user_id,
        published_at=timestamp,
        is_current=True,
        previous_version_id=previous_version_id,
    )
    store.verified_policy_rule_versions.append(version)
    if existing:
        existing.current_value = candidate.new_value
        existing.previous_value = candidate.old_value
        existing.unit = candidate.unit
        existing.effective_date = candidate.effective_date
        existing.source_clause = candidate.source_excerpt
        existing.confidence = candidate.confidence_score
        existing.updated_at = timestamp
        existing.approved_by = reviewer_user_id or existing.approved_by
        existing.approved_at = timestamp
    else:
        store.verified_rules.append(
            VerifiedPolicyRule(
                id=rule_id,
                source_extraction_id=None,
                circular_id=candidate.circular_id,
                service_id=candidate.service_id,
                rule_key=candidate.rule_key,
                rule_name=candidate.rule_key.replace("_", " ").title(),
                current_value=candidate.new_value,
                previous_value=candidate.old_value,
                unit=candidate.unit,
                effective_date=candidate.effective_date,
                status="active",
                approved_by=reviewer_user_id or "system",
                approved_at=timestamp,
                source_clause=candidate.source_excerpt,
                confidence=candidate.confidence_score,
                created_at=timestamp,
                updated_at=timestamp,
            )
        )
    event = PolicyPublicationEvent(
        id=f"pub_{candidate_id}",
        candidate_id=candidate_id,
        rule_version_id=version.id,
        service_id=candidate.service_id,
        rule_key=candidate.rule_key,
        old_value=candidate.old_value,
        new_value=candidate.new_value,
        published_by=reviewer_user_id,
        created_at=timestamp,
    )
    store.policy_publication_events.append(event)
    add_audit_event(store, "rule_published", {"entity_type": "rule_candidate", "entity_id": candidate_id})
    write_store(store)
    knowledge_event = knowledge_update_service.update_for_rule(version)
    plan = propagation_service.create_plan(version)
    compliance_run = (
        compliance_orchestrator_service.rerun_for_rule(rule_id, trigger_type="policy_update", triggered_by=reviewer_user_id)
        if settings.compliance_rerun_on_policy_update
        else None
    )
    return {
        "success": True,
        "rule_version": version.model_dump(),
        "publication_event": event.model_dump(),
        "knowledge_update": knowledge_event.model_dump(),
        "propagation_plan": plan.model_dump(),
        "compliance_run": compliance_run.model_dump() if compliance_run else None,
    }


def publication_history() -> list[PolicyPublicationEvent]:
    return read_store().policy_publication_events


def list_versions() -> list[VerifiedPolicyRuleVersion]:
    return read_store().verified_policy_rule_versions


def versions_for_rule(rule_id: str) -> list[VerifiedPolicyRuleVersion]:
    return [item for item in read_store().verified_policy_rule_versions if item.rule_id == rule_id]


def rollback_rule(rule_id: str, actor: str | None = None, reason: str | None = None) -> dict:
    if not settings.policy_rollback_enabled:
        return {"success": False, "message": "Rollback is disabled."}
    store = read_store()
    versions = sorted(
        [item for item in store.verified_policy_rule_versions if item.rule_id == rule_id],
        key=lambda item: item.version_number,
    )
    current = next((item for item in versions if item.is_current), None)
    previous = next((item for item in reversed(versions) if not item.is_current), None)
    if current is None or previous is None:
        return {"success": False, "message": "Previous version not available."}
    current.is_current = False
    previous.is_current = True
    rule = next((item for item in store.verified_rules if item.id == rule_id), None)
    if rule:
        rule.current_value = previous.value
        rule.unit = previous.unit
        rule.effective_date = previous.effective_date
        rule.updated_at = now_iso()
    from app.models.self_update_models import RollbackEvent

    event = RollbackEvent(
        id=f"rollback_{rule_id}_{len(store.rollback_events) + 1:04d}",
        rule_id=rule_id,
        from_version_id=current.id,
        to_version_id=previous.id,
        rolled_back_by=actor,
        reason=reason,
        created_at=now_iso(),
    )
    store.rollback_events.append(event)
    add_audit_event(store, "rule_rolled_back", {"entity_type": "verified_rule", "entity_id": rule_id})
    write_store(store)
    compliance_run = compliance_orchestrator_service.rerun_for_rule(rule_id, trigger_type="policy_update", triggered_by=actor)
    return {"success": True, "rollback": event.model_dump(), "compliance_run": compliance_run.model_dump()}
