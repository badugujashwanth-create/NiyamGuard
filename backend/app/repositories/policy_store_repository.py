from __future__ import annotations

from copy import deepcopy
import hashlib
from typing import Any

from fastapi import HTTPException
from sqlalchemy import delete, select
from sqlalchemy.exc import SQLAlchemyError

from app.database import SessionLocal, init_db
from app.models.database_models import (
    CircularDocumentRecord,
    ComplianceFindingRecord,
    ConnectedSystemSnapshotRecord,
    PolicyRecord,
    PolicyRuleCandidateRecord,
    PolicyRuleVersionRecord,
    PolicyStoreRevision,
)
from app.models.knowledge_models import Circular
from app.models.platform_store_models import PolicyDataStore
from app.services.time import now_iso


COLLECTIONS = (
    "circulars",
    "extracted_rules",
    "verified_rules",
    "connected_systems",
    "snapshots",
    "compliance_findings",
    "cascade_traces",
    "priority_scores",
    "conflicts",
    "audit_events",
    "official_circular_sources",
    "circular_sync_jobs",
    "circular_documents",
    "circular_extractions",
    "policy_rule_candidates",
    "policy_rule_deltas",
    "rule_approval_workflows",
    "verified_policy_rule_versions",
    "policy_publication_events",
    "knowledge_update_events",
    "propagation_plans",
    "propagation_tasks",
    "connected_system_patches",
    "rollback_events",
    "compliance_runs",
    "mock_connected_systems",
    "citizen_profiles",
    "citizen_documents",
    "service_definitions",
    "service_form_definitions",
    "applications",
    "application_field_values",
    "application_documents",
    "application_status_history",
    "officer_reviews",
    "certificates",
    "certificate_verification_logs",
    "payment_records",
    "notifications",
    "service_slas",
    "application_comments",
    "application_assignments",
)


def _legacy_document_payload(circular: Circular) -> dict[str, Any]:
    raw_text = circular.source_text or ""
    digest = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()
    status = {
        "uploaded": "ingested",
        "extracted": "extracted",
        "pending_review": "pending_review",
        "approved": "published",
        "rejected": "rejected",
        # A superseded legacy circular is still a published source artifact;
        # its version lineage carries the supersession state separately.
        "superseded": "published",
    }[circular.status]
    return {
        "id": circular.id,
        "source_id": "legacy_demo",
        "circular_number": circular.circular_number,
        "title": circular.title,
        "department": circular.department,
        "published_date": circular.issue_date,
        "effective_date": circular.effective_date,
        "expiry_date": None,
        "document_url": None,
        "storage_path": circular.source_file_path,
        "source_filename": None,
        "source_content_type": "text/plain",
        "source_size_bytes": len(raw_text.encode("utf-8")),
        "source_sha256": digest,
        "malware_scan_status": "synthetic_seed",
        "raw_text": raw_text,
        "content_hash": digest,
        "status": status,
        "created_at": circular.created_at,
        "updated_at": circular.updated_at,
    }


def _normalized_documents(store: PolicyDataStore) -> list[dict[str, Any]]:
    documents = [item.model_dump() for item in store.circular_documents]
    known_ids = {item["id"] for item in documents}
    for circular in store.circulars:
        if circular.id not in known_ids:
            documents.append(_legacy_document_payload(circular))
    return documents


def _replace_normalized_records(session, store: PolicyDataStore) -> None:
    """Write the flagship policy-drift entities into typed relational tables.

    The serialized PolicyRecord rows remain as a compatibility mirror until
    every non-flagship collection has a typed schema, but normalized rows are
    the preferred read source for these five core collections.
    """

    session.execute(delete(ComplianceFindingRecord))
    session.execute(delete(ConnectedSystemSnapshotRecord))
    session.execute(delete(PolicyRuleVersionRecord))
    session.execute(delete(PolicyRuleCandidateRecord))
    session.execute(delete(CircularDocumentRecord))

    documents = _normalized_documents(store)
    document_ids = {item["id"] for item in documents}
    for item in documents:
        session.add(CircularDocumentRecord(**item))

    for item in store.policy_rule_candidates:
        data = item.model_dump()
        if data["circular_id"] not in document_ids:
            continue
        session.add(PolicyRuleCandidateRecord(**data))

    version_ids: set[str] = set()
    for item in store.verified_policy_rule_versions:
        data = item.model_dump()
        if data["source_circular_id"] not in document_ids:
            continue
        session.add(PolicyRuleVersionRecord(**data))
        version_ids.add(data["id"])

    for item in store.snapshots:
        session.add(ConnectedSystemSnapshotRecord(**item.model_dump()))

    for item in store.compliance_findings:
        data = item.model_dump()
        if data["verified_rule_id"] not in version_ids:
            continue
        session.add(ComplianceFindingRecord(**data))


def _apply_normalized_payload(session, payload: dict[str, list[Any]]) -> None:
    def row_payload(item) -> dict[str, Any]:
        return {key: value for key, value in item.__dict__.items() if not key.startswith("_")}

    documents = session.scalars(select(CircularDocumentRecord)).all()
    candidates = session.scalars(select(PolicyRuleCandidateRecord)).all()
    versions = session.scalars(select(PolicyRuleVersionRecord)).all()
    snapshots = session.scalars(select(ConnectedSystemSnapshotRecord)).all()
    findings = session.scalars(select(ComplianceFindingRecord)).all()
    if documents:
        payload["circular_documents"] = [row_payload(item) for item in documents]
    if candidates:
        payload["policy_rule_candidates"] = [row_payload(item) for item in candidates]
    if versions:
        payload["verified_policy_rule_versions"] = [row_payload(item) for item in versions]
    if snapshots:
        payload["snapshots"] = [row_payload(item) for item in snapshots]
    if findings:
        payload["compliance_findings"] = [row_payload(item) for item in findings]


class PolicyStoreRepository:
    def __init__(self) -> None:
        init_db()

    def load(self) -> PolicyDataStore | None:
        try:
            with SessionLocal() as session:
                records = session.scalars(select(PolicyRecord)).all()
                revision_row = session.get(PolicyStoreRevision, 1)
                payload: dict[str, list[Any]] = {collection: [] for collection in COLLECTIONS}
                for record in records:
                    payload.setdefault(record.collection, []).append(deepcopy(record.payload))
                _apply_normalized_payload(session, payload)
                has_normalized_records = any(
                    payload[name]
                    for name in (
                        "circular_documents",
                        "policy_rule_candidates",
                        "verified_policy_rule_versions",
                        "snapshots",
                        "compliance_findings",
                    )
                )
        except SQLAlchemyError:
            return None
        if not records and not has_normalized_records:
            return None
        store = PolicyDataStore(**payload)
        store.revision = revision_row.revision if revision_row else 0
        return store

    def replace(self, store: PolicyDataStore) -> None:
        try:
            with SessionLocal() as session:
                revision_row = session.scalar(
                    select(PolicyStoreRevision).where(PolicyStoreRevision.id == 1).with_for_update()
                )
                if revision_row is None:
                    revision_row = PolicyStoreRevision(id=1, revision=0, updated_at=now_iso())
                    session.add(revision_row)
                    session.flush()
                expected_revision = getattr(store, "revision", None)
                if expected_revision is not None and expected_revision != revision_row.revision:
                    raise PolicyStoreConflict(expected_revision, revision_row.revision)
                session.execute(delete(PolicyRecord))
                for collection in COLLECTIONS:
                    for item in getattr(store, collection):
                        data = item.model_dump() if hasattr(item, "model_dump") else dict(item)
                        item_id = data.get("id") or f"{collection}_{len(data)}"
                        session.add(
                            PolicyRecord(
                                collection=collection,
                                item_id=str(item_id),
                                payload=data,
                            )
                        )
                _replace_normalized_records(session, store)
                revision_row.revision += 1
                revision_row.updated_at = now_iso()
                session.commit()
                store.revision = revision_row.revision
        except SQLAlchemyError:
            raise

    def has_records(self) -> bool:
        try:
            with SessionLocal() as session:
                if session.scalar(select(PolicyRecord.id).limit(1)) is not None:
                    return True
                return any(
                    session.scalar(select(model.id).limit(1)) is not None
                    for model in (
                        CircularDocumentRecord,
                        PolicyRuleCandidateRecord,
                        PolicyRuleVersionRecord,
                        ConnectedSystemSnapshotRecord,
                        ComplianceFindingRecord,
                    )
                )
        except SQLAlchemyError:
            return False


class PolicyStoreConflict(HTTPException):
    """A stale full-store write was rejected instead of losing another update."""

    def __init__(self, expected_revision: int, actual_revision: int) -> None:
        super().__init__(
            status_code=409,
            detail="Policy state changed since it was loaded; reload the current state and retry.",
            headers={"Cache-Control": "no-store"},
        )
