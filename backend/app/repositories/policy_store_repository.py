from __future__ import annotations

from copy import deepcopy
from typing import Any

from sqlalchemy import delete, select
from sqlalchemy.exc import SQLAlchemyError

from app.database import SessionLocal, init_db
from app.models.database_models import PolicyRecord
from app.models.platform_store_models import PolicyDataStore


COLLECTIONS = (
    "circulars",
    "extracted_rules",
    "verified_rules",
    "certificate_reference_drafts",
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


class PolicyStoreRepository:
    def __init__(self) -> None:
        init_db()

    def load(self) -> PolicyDataStore | None:
        try:
            with SessionLocal() as session:
                records = session.scalars(select(PolicyRecord)).all()
        except SQLAlchemyError:
            return None
        if not records:
            return None
        payload: dict[str, list[Any]] = {collection: [] for collection in COLLECTIONS}
        for record in records:
            payload.setdefault(record.collection, []).append(deepcopy(record.payload))
        return PolicyDataStore(**payload)

    def replace(self, store: PolicyDataStore) -> None:
        try:
            with SessionLocal() as session:
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
                session.commit()
        except SQLAlchemyError:
            raise

    def has_records(self) -> bool:
        try:
            with SessionLocal() as session:
                return session.scalar(select(PolicyRecord.id).limit(1)) is not None
        except SQLAlchemyError:
            return False
