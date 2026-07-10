from __future__ import annotations

from app.models.self_update_models import PropagationPlan, PropagationTask, VerifiedPolicyRuleVersion
from app.knowledge_base.platform_store import add_audit_event, now_iso, read_store, write_store


TASK_TYPE_BY_SYSTEM = {
    "portal": "update_portal",
    "form": "update_form",
    "faq": "update_faq",
    "sop": "update_sop",
}


def create_plan(rule_version: VerifiedPolicyRuleVersion) -> PropagationPlan:
    store = read_store()
    systems = [
        system
        for system in store.connected_systems
        if system.service_id == rule_version.service_id and system.status == "active"
    ]
    task_ids: list[str] = []
    for system in systems:
        snapshot = next(
            (
                item
                for item in store.snapshots
                if item.connected_system_id == system.id
                and item.service_id == rule_version.service_id
                and item.rule_key == rule_version.rule_key
            ),
            None,
        )
        old_value = f"{snapshot.displayed_value} {snapshot.unit or ''}".strip() if snapshot else None
        task = PropagationTask(
            id=f"task_{rule_version.id}_{system.id}",
            rule_version_id=rule_version.id,
            connected_system_id=system.id,
            task_type=TASK_TYPE_BY_SYSTEM.get(system.system_type, "notify_owner"),
            status="pending",
            old_value=old_value,
            new_value=f"{rule_version.value} {rule_version.unit or ''}".strip(),
            patch_payload_json={
                "target": system.id,
                "field": f"{rule_version.service_id}.{rule_version.rule_key}",
                "old_value": old_value,
                "new_value": f"{rule_version.value} {rule_version.unit or ''}".strip(),
                "source": rule_version.source_circular_number,
            },
            assigned_to=system.owner,
            created_at=now_iso(),
        )
        store.propagation_tasks = [item for item in store.propagation_tasks if item.id != task.id]
        store.propagation_tasks.append(task)
        task_ids.append(task.id)
        add_audit_event(store, "propagation_task_created", {"entity_type": "propagation_task", "entity_id": task.id})

    plan = PropagationPlan(
        id=f"plan_{rule_version.id}",
        rule_version_id=rule_version.id,
        service_id=rule_version.service_id,
        rule_key=rule_version.rule_key,
        task_ids=task_ids,
        status="created",
        created_at=now_iso(),
    )
    store.propagation_plans = [item for item in store.propagation_plans if item.id != plan.id]
    store.propagation_plans.append(plan)
    write_store(store)
    return plan


def list_tasks() -> list[PropagationTask]:
    return read_store().propagation_tasks


def get_task(task_id: str) -> PropagationTask | None:
    return next((item for item in read_store().propagation_tasks if item.id == task_id), None)


def mark_completed(task_id: str) -> PropagationTask | None:
    store = read_store()
    task = next((item for item in store.propagation_tasks if item.id == task_id), None)
    if task is None:
        return None
    task.status = "completed"
    task.completed_at = now_iso()
    add_audit_event(store, "propagation_task_completed", {"entity_type": "propagation_task", "entity_id": task_id})
    write_store(store)
    return task


def mark_manual(task_id: str) -> PropagationTask | None:
    store = read_store()
    task = next((item for item in store.propagation_tasks if item.id == task_id), None)
    if task is None:
        return None
    task.status = "needs_manual_update"
    add_audit_event(store, "propagation_task_marked_manual", {"entity_type": "propagation_task", "entity_id": task_id})
    write_store(store)
    return task
