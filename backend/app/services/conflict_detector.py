from app.models.conflict_models import CircularConflict
from app.models.knowledge_models import VerifiedPolicyRule
from app.services.platform_store import add_audit_event, now_iso, read_store, write_store


def _conflict_for(rule_a: VerifiedPolicyRule, rule_b: VerifiedPolicyRule) -> CircularConflict:
    return CircularConflict(
        id=f"conf_{rule_a.id}_{rule_b.id}",
        service_id=rule_a.service_id,
        rule_key=rule_a.rule_key,
        conflict_type="active_value_conflict",
        rule_a_id=rule_a.id,
        rule_b_id=rule_b.id,
        severity="high",
        summary=(
            f"Two active verified rules for {rule_a.service_id}/{rule_a.rule_key} "
            f"have different values: {rule_a.current_value} {rule_a.unit or ''} and "
            f"{rule_b.current_value} {rule_b.unit or ''}."
        ),
        recommendation="Resolve by superseding the older rule or recording an officer decision.",
        status="open",
        created_at=now_iso(),
    )


def scan_conflicts() -> list[CircularConflict]:
    store = read_store()
    conflicts: list[CircularConflict] = []
    active = [rule for rule in store.verified_rules if rule.status == "active"]
    for index, rule_a in enumerate(active):
        for rule_b in active[index + 1 :]:
            if rule_a.service_id != rule_b.service_id or rule_a.rule_key != rule_b.rule_key:
                continue
            if (rule_a.current_value, rule_a.unit) != (rule_b.current_value, rule_b.unit):
                conflicts.append(_conflict_for(rule_a, rule_b))
    existing_resolved = [
        conflict for conflict in store.conflicts if conflict.status in {"resolved", "ignored"}
    ]
    store.conflicts = existing_resolved + conflicts
    add_audit_event(store, "conflict_scan_completed", {"conflicts": len(conflicts)})
    write_store(store)
    return store.conflicts


def list_conflicts() -> list[CircularConflict]:
    return read_store().conflicts


def get_conflict(conflict_id: str) -> CircularConflict | None:
    return next((item for item in read_store().conflicts if item.id == conflict_id), None)


def update_conflict_status(conflict_id: str, status: str) -> CircularConflict | None:
    store = read_store()
    conflict = next((item for item in store.conflicts if item.id == conflict_id), None)
    if conflict is None:
        return None
    conflict.status = status
    conflict.resolved_at = now_iso()
    add_audit_event(store, f"conflict_{status}", {"conflict_id": conflict_id})
    write_store(store)
    return conflict
