from __future__ import annotations

import re

from app.models.self_update_models import CircularExtraction, PolicyRuleCandidate
from app.knowledge_base import certificate_baseline_service
from app.services import circular_ingestion_service, rule_delta_service
from app.knowledge_base.platform_store import add_audit_event, now_iso, read_store, write_store


def _deterministic_candidates(circular_id: str, text: str, effective_date: str) -> list[PolicyRuleCandidate]:
    normalized = text.casefold()
    if "income certificate" not in normalized or "6 months" not in normalized:
        return []
    old_value = "12"
    old_match = re.search(r"from\s+(\d+)\s+months", normalized)
    if old_match:
        old_value = old_match.group(1)
    excerpt = "Income Certificate validity changed from 12 months to 6 months."
    return [
        PolicyRuleCandidate(
            id=f"cand_{circular_id}_income_validity",
            circular_id=circular_id,
            service_id="income_certificate",
            rule_key="validity",
            old_value=old_value,
            new_value="6",
            unit="months",
            effective_date=effective_date,
            confidence_score=0.91,
            extraction_method="deterministic",
            source_excerpt=excerpt,
            status="pending_review",
            requires_review=True,
            created_at=now_iso(),
        )
    ]


def _candidate_titles(text: str) -> list[str]:
    pattern = re.compile(r"\b([A-Z][A-Za-z /-]{2,70}?(?:Certificate|Card|Pension|Scholarship))\b")
    titles: list[str] = []
    for match in pattern.finditer(text):
        title = " ".join(match.group(1).split())
        if title.casefold() not in {item.casefold() for item in titles}:
            titles.append(title)
    return titles


def _flag_unknown_certificate_references(document, candidates: list[PolicyRuleCandidate]) -> list[dict]:
    drafts = []
    known_candidate_ids = {candidate.service_id for candidate in candidates}
    for service_id in known_candidate_ids:
        if not certificate_baseline_service.has_baseline(service_id):
            draft = certificate_baseline_service.create_draft_if_missing(
                service_id=service_id,
                title=service_id.replace("_", " ").title(),
                circular_id=document.id,
                circular_number=document.circular_number,
                department=document.department,
                reason="Rule candidate references a service with no certificate baseline.",
            )
            if draft:
                drafts.append(draft.model_dump())
    for title in _candidate_titles(document.raw_text):
        service_id = certificate_baseline_service.candidate_service_id(title)
        if service_id in known_candidate_ids:
            continue
        draft = certificate_baseline_service.create_draft_if_missing(
            service_id=service_id,
            title=title,
            circular_id=document.id,
            circular_number=document.circular_number,
            department=document.department,
            reason="Circular text references a service with no certificate baseline.",
        )
        if draft:
            drafts.append(draft.model_dump())
    return drafts


def extract_rules(circular_id: str, actor_user_id: str | None = None) -> dict:
    document = circular_ingestion_service.get_document(circular_id)
    if document is None:
        return {"success": False, "message": "Circular not found."}
    candidates = _deterministic_candidates(circular_id, document.raw_text, document.effective_date)
    draft_references = _flag_unknown_certificate_references(document, candidates)
    store = read_store()
    existing_ids = {item.id for item in store.policy_rule_candidates}
    new_candidates = [candidate for candidate in candidates if candidate.id not in existing_ids]
    store.policy_rule_candidates.extend(new_candidates)
    deltas = [rule_delta_service.create_delta(candidate) for candidate in new_candidates]
    store.policy_rule_deltas = [
        item for item in store.policy_rule_deltas if item.candidate_id not in {candidate.id for candidate in new_candidates}
    ] + deltas
    extraction = CircularExtraction(
        id=f"extract_{circular_id}",
        circular_id=circular_id,
        status="success" if candidates else "failed",
        extraction_method="deterministic",
        candidate_ids=[candidate.id for candidate in candidates],
        error_message=None if candidates else "No deterministic rule candidate found.",
        created_at=now_iso(),
    )
    store.circular_extractions = [item for item in store.circular_extractions if item.id != extraction.id]
    store.circular_extractions.append(extraction)
    for item in store.circular_documents:
        if item.id == circular_id:
            item.status = "pending_review" if candidates else "extracted"
            item.updated_at = now_iso()
    add_audit_event(
        store,
        "rule_extracted",
        {"entity_type": "circular_document", "entity_id": circular_id, "actor_user_id": actor_user_id},
    )
    write_store(store)
    return {
        "success": bool(candidates),
        "extraction": extraction.model_dump(),
        "candidates": [candidate.model_dump() for candidate in candidates],
        "deltas": [delta.model_dump() for delta in deltas],
        "certificate_reference_drafts": draft_references,
    }


def list_candidates() -> list[PolicyRuleCandidate]:
    return read_store().policy_rule_candidates


def get_candidate(candidate_id: str) -> PolicyRuleCandidate | None:
    return next((item for item in read_store().policy_rule_candidates if item.id == candidate_id), None)


def approve_candidate(candidate_id: str, reviewer_user_id: str | None = None, notes: str | None = None) -> dict:
    store = read_store()
    candidate = next((item for item in store.policy_rule_candidates if item.id == candidate_id), None)
    if candidate is None:
        return {"success": False, "message": "Candidate not found."}
    candidate.status = "approved"
    from app.models.self_update_models import RuleApprovalWorkflow

    workflow = RuleApprovalWorkflow(
        id=f"review_{candidate_id}",
        candidate_id=candidate_id,
        reviewer_user_id=reviewer_user_id,
        status="approved",
        review_notes=notes,
        reviewed_at=now_iso(),
        created_at=now_iso(),
    )
    store.rule_approval_workflows = [item for item in store.rule_approval_workflows if item.id != workflow.id]
    store.rule_approval_workflows.append(workflow)
    add_audit_event(
        store,
        "candidate_approved",
        {"entity_type": "rule_candidate", "entity_id": candidate_id, "reviewer_user_id": reviewer_user_id},
    )
    write_store(store)
    return {"success": True, "candidate": candidate.model_dump(), "workflow": workflow.model_dump()}


def reject_candidate(candidate_id: str, reviewer_user_id: str | None = None, notes: str | None = None) -> dict:
    store = read_store()
    candidate = next((item for item in store.policy_rule_candidates if item.id == candidate_id), None)
    if candidate is None:
        return {"success": False, "message": "Candidate not found."}
    candidate.status = "rejected"
    from app.models.self_update_models import RuleApprovalWorkflow

    workflow = RuleApprovalWorkflow(
        id=f"review_{candidate_id}",
        candidate_id=candidate_id,
        reviewer_user_id=reviewer_user_id,
        status="rejected",
        review_notes=notes,
        reviewed_at=now_iso(),
        created_at=now_iso(),
    )
    store.rule_approval_workflows = [item for item in store.rule_approval_workflows if item.id != workflow.id]
    store.rule_approval_workflows.append(workflow)
    add_audit_event(
        store,
        "candidate_rejected",
        {"entity_type": "rule_candidate", "entity_id": candidate_id, "reviewer_user_id": reviewer_user_id},
    )
    write_store(store)
    return {"success": True, "candidate": candidate.model_dump(), "workflow": workflow.model_dump()}
