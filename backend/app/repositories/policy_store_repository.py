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
    "connected_systems",
    "snapshots",
    "compliance_findings",
    "cascade_traces",
    "priority_scores",
    "conflicts",
    "audit_events",
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
