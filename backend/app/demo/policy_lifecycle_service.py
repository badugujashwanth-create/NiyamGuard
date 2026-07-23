from __future__ import annotations

from typing import Any, Callable

from app.knowledge_base.platform_store import add_audit_event, read_store, reset_demo_store, write_store
from app.services import (
    circular_ingestion_service,
    circular_sync_service,
    compliance_service,
    conflict_detector,
    policy_publication_service,
    rule_extraction_service,
)
from app.services.ai import AIProviderFactory


StepRunner = Callable[[], dict[str, Any]]


def _step(key: str, label: str, details: str, payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "key": key,
        "label": label,
        "status": "success",
        "details": details,
        "payload": payload,
    }


def _safe(
    steps: list[dict[str, Any]],
    key: str,
    label: str,
    runner: StepRunner,
) -> dict[str, Any]:
    try:
        result = runner()
    except Exception as exc:  # pragma: no cover - defensive boundary for the public sandbox
        result = {
            "key": key,
            "label": label,
            "status": "failed",
            "details": str(exc),
            "payload": {},
        }
    steps.append(result)
    return result


def _source_evidence(document, excerpt: str) -> dict[str, Any]:
    start = document.raw_text.casefold().find(excerpt.casefold())
    if start < 0:
        start = 0
    return {
        "circular_id": document.id,
        "circular_number": document.circular_number,
        "department": document.department,
        "effective_date": document.effective_date,
        "expiry_date": document.expiry_date,
        "excerpt": excerpt,
        "character_range": [start, start + len(excerpt)],
        "content_hash": document.content_hash,
        "synthetic": True,
    }


def _impact_relationships(service_id: str) -> dict[str, list[dict[str, str]]]:
    store = read_store()
    schemes = []
    for service in store.service_definitions:
        dependencies = service.rule_bindings_json.get("depends_on", [])
        if service_id in dependencies:
            schemes.append({"id": service.service_id, "name": service.name})
    forms = [
        {"id": item.id, "name": f"{item.service_id} form v{item.version}"}
        for item in store.service_form_definitions
        if item.service_id == service_id
    ]
    systems = [
        {"id": item.id, "name": item.name, "type": item.system_type}
        for item in store.connected_systems
        if item.service_id == service_id
    ]
    return {
        "schemes": schemes,
        "forms": forms,
        "departments": [{"id": "revenue", "name": "Revenue"}],
        "workflows": [
            {"id": "officer_validation", "name": "Officer certificate validation"},
            {"id": "citizen_guidance", "name": "Citizen validity guidance"},
        ],
        "connected_systems": systems,
    }


def _eligibility_rerun(old_months: int, new_months: int) -> dict[str, Any]:
    scenarios = [
        {"id": "fresh_certificate", "certificate_age_months": 2},
        {"id": "boundary_certificate", "certificate_age_months": 6},
        {"id": "stale_under_new_rule", "certificate_age_months": 7},
        {"id": "stale_under_both", "certificate_age_months": 13},
    ]
    results = []
    for scenario in scenarios:
        age = scenario["certificate_age_months"]
        before = age <= old_months
        after = age <= new_months
        results.append(
            {
                **scenario,
                "eligible_before": before,
                "eligible_after": after,
                "changed": before != after,
                "reason": (
                    f"Certificate age {age} months compared with "
                    f"the previous {old_months}-month and current {new_months}-month limits."
                ),
            }
        )
    return {
        "old_limit_months": old_months,
        "new_limit_months": new_months,
        "scenario_count": len(results),
        "changed_count": sum(1 for item in results if item["changed"]),
        "results": results,
    }


def run_policy_lifecycle() -> dict[str, Any]:
    """Run one synthetic circular through the complete, source-grounded lifecycle."""

    steps: list[dict[str, Any]] = []
    state: dict[str, Any] = {}

    def reset() -> dict[str, Any]:
        reset_demo_store(persist=True)
        return _step("reset", "Reset synthetic sandbox", "Known synthetic baseline restored.", {})

    def ingest() -> dict[str, Any]:
        sync = circular_sync_service.sync_all(created_by="policy_lifecycle_demo")
        document = circular_ingestion_service.get_document("cirdoc_go_138")
        if document is None:
            raise RuntimeError("Synthetic GO-138 document was not created.")
        state["document"] = document
        return _step(
            "ingest",
            "Ingest synthetic circular",
            "Validated local synthetic text was ingested and hashed.",
            {"sync": sync, "document": document.model_dump()},
        )

    def extract() -> dict[str, Any]:
        document = state["document"]
        result = rule_extraction_service.extract_rules(document.id)
        if not result.get("success"):
            raise RuntimeError(result.get("message", "Rule extraction failed."))
        candidate = result["candidates"][0]
        state["candidate"] = candidate
        state["delta"] = result["deltas"][0]
        state["evidence"] = _source_evidence(document, candidate["source_excerpt"])
        return _step(
            "extract",
            "Extract metadata and clauses",
            "Effective/expiry dates, the changed clause, and its source range were extracted.",
            {
                "metadata": {
                    "circular_number": document.circular_number,
                    "department": document.department,
                    "effective_date": document.effective_date,
                    "expiry_date": document.expiry_date,
                },
                "candidate": candidate,
                "source_evidence": state["evidence"],
            },
        )

    def compare() -> dict[str, Any]:
        candidate = state["candidate"]
        versions = sorted(
            [
                item.model_dump()
                for item in policy_publication_service.versions_for_rule("rule_001")
            ],
            key=lambda item: item["version_number"],
        )
        previous = versions[-1] if versions else None
        comparison = {
            "change_type": state["delta"]["change_type"],
            "previous_version": previous,
            "proposed_value": f"{candidate['new_value']} {candidate['unit']}",
            "supersedes_version_id": previous["id"] if previous else None,
            "value_changed": bool(previous and previous["value"] != candidate["new_value"]),
        }
        state["comparison"] = comparison
        return _step(
            "compare",
            "Compare policy versions",
            "The proposed clause was compared with the linked earlier version.",
            comparison,
        )

    def detect_conflicts() -> dict[str, Any]:
        conflicts = [item.model_dump() for item in conflict_detector.scan_conflicts()]
        relevant = [
            item
            for item in conflicts
            if item["service_id"] == state["candidate"]["service_id"]
            and item["rule_key"] == state["candidate"]["rule_key"]
        ]
        state["conflicts"] = relevant
        return _step(
            "conflicts",
            "Detect conflicts",
            "Conflicting active values were identified with severity and resolution guidance.",
            {"conflicts": relevant, "count": len(relevant)},
        )

    def impact() -> dict[str, Any]:
        relationships = _impact_relationships(state["candidate"]["service_id"])
        state["impact"] = relationships
        return _step(
            "impact",
            "Trace downstream impact",
            "Linked schemes, forms, department, workflows, and mock systems were resolved from the store.",
            relationships,
        )

    def review() -> dict[str, Any]:
        candidate = state["candidate"]
        review_queue = {
            "candidate_id": candidate["id"],
            "status": candidate["status"],
            "requires_review": candidate["requires_review"],
            "available_decisions": ["approve", "reject", "request_revision"],
            "evidence": state["evidence"],
        }
        state["review_queue"] = review_queue
        return _step(
            "review",
            "Send to officer review",
            "The candidate entered a human review queue with evidence and three explicit decisions.",
            review_queue,
        )

    def approve_and_publish() -> dict[str, Any]:
        candidate_id = state["candidate"]["id"]
        approval = rule_extraction_service.approve_candidate(
            candidate_id,
            reviewer_user_id="demo_reviewer",
            notes="Synthetic lifecycle evidence reviewed.",
        )
        publication = policy_publication_service.publish_rule_candidate(
            candidate_id,
            reviewer_user_id="demo_reviewer",
            notes="Synthetic lifecycle publication.",
        )
        if not approval.get("success") or not publication.get("success"):
            raise RuntimeError("Review or publication did not complete.")
        state["publication"] = publication
        return _step(
            "publish",
            "Approve and publish",
            "Human approval created a linked immutable rule version and propagation plan.",
            {"approval": approval, "publication": publication},
        )

    def summarize() -> dict[str, Any]:
        candidate = state["candidate"]
        officer_summary = (
            f"{state['document'].circular_number} changes Income Certificate validity "
            f"from {candidate['old_value']} to {candidate['new_value']} {candidate['unit']}; "
            f"{len(state['conflicts'])} conflict(s) and "
            f"{len(state['impact']['connected_systems'])} connected system(s) require review."
        )
        fallback = (
            f"For this synthetic example, {state['document'].circular_number} changes the "
            f"Income Certificate validity to {candidate['new_value']} {candidate['unit']} "
            f"from {state['document'].effective_date}. Check the cited circular evidence before acting."
        )
        ai = AIProviderFactory.get_client().generate_text(
            "Explain only this verified synthetic policy context to a citizen: " + fallback,
            {"fallback_text": fallback},
        )
        citizen = {
            "text": ai.get("text") or fallback,
            "provider": ai.get("provider"),
            "model": ai.get("model"),
            "fallback": bool(ai.get("fallback")),
            "source_evidence": state["evidence"],
            "languages_available": ["English", "Telugu", "Hindi"],
        }
        state["officer_summary"] = officer_summary
        state["citizen_explanation"] = citizen
        return _step(
            "explain",
            "Generate officer and citizen views",
            "Both views remain tied to the same verified source evidence.",
            {"officer_summary": officer_summary, "citizen_explanation": citizen},
        )

    def rerun_eligibility() -> dict[str, Any]:
        candidate = state["candidate"]
        result = _eligibility_rerun(
            int(candidate["old_value"]),
            int(candidate["new_value"]),
        )
        state["eligibility"] = result
        return _step(
            "eligibility",
            "Rerun affected eligibility scenarios",
            "Four deterministic certificate-age fixtures were reevaluated against both versions.",
            result,
        )

    def audit() -> dict[str, Any]:
        store = read_store()
        add_audit_event(
            store,
            "policy_lifecycle_demo_completed",
            {
                "entity_type": "circular_document",
                "entity_id": state["document"].id,
                "candidate_id": state["candidate"]["id"],
            },
        )
        write_store(store)
        events = [
            dict(item)
            for item in read_store().audit_events
            if item.get("entity_id") in {state["document"].id, state["candidate"]["id"]}
            or item.get("action") == "policy_lifecycle_demo_completed"
        ]
        state["audit"] = events
        return _step(
            "audit",
            "Preserve audit history",
            "Ingestion, extraction, review, publication, and completion events remain traceable.",
            {"events": events, "count": len(events)},
        )

    runners: list[tuple[str, str, StepRunner]] = [
        ("reset", "Reset synthetic sandbox", reset),
        ("ingest", "Ingest synthetic circular", ingest),
        ("extract", "Extract metadata and clauses", extract),
        ("compare", "Compare policy versions", compare),
        ("conflicts", "Detect conflicts", detect_conflicts),
        ("impact", "Trace downstream impact", impact),
        ("review", "Send to officer review", review),
        ("publish", "Approve and publish", approve_and_publish),
        ("explain", "Generate officer and citizen views", summarize),
        ("eligibility", "Rerun eligibility scenarios", rerun_eligibility),
        ("audit", "Preserve audit history", audit),
    ]
    for key, label, runner in runners:
        _safe(steps, key, label, runner)
        if steps[-1]["status"] == "failed":
            break

    return {
        "success": len(steps) == len(runners)
        and all(item["status"] == "success" for item in steps),
        "synthetic_only": True,
        "circular": state.get("document").model_dump() if state.get("document") else None,
        "steps": steps,
        "source_evidence": state.get("evidence"),
        "comparison": state.get("comparison"),
        "conflicts": state.get("conflicts", []),
        "impact": state.get("impact", {}),
        "review_queue": state.get("review_queue"),
        "publication": state.get("publication"),
        "officer_summary": state.get("officer_summary"),
        "citizen_explanation": state.get("citizen_explanation"),
        "eligibility": state.get("eligibility"),
        "audit_events": state.get("audit", []),
    }
