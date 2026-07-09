from __future__ import annotations

from collections import Counter
from typing import Any

from sqlalchemy import delete, func, select

from app.database import SessionLocal, init_db
from app.models.dataset_models import NiyamGuardDatasetRecord


class DatasetRepository:
    def __init__(self) -> None:
        init_db()

    def replace_pack_records(self, pack_version: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
        with SessionLocal() as session:
            session.execute(
                delete(NiyamGuardDatasetRecord).where(
                    NiyamGuardDatasetRecord.pack_version == pack_version
                )
            )
            session.add_all(
                NiyamGuardDatasetRecord(
                    pack_version=pack_version,
                    collection=row["collection"],
                    item_id=row["item_id"],
                    source_file=row["source_file"],
                    payload=row["payload"],
                    imported_at=row["imported_at"],
                )
                for row in rows
            )
            session.commit()
        counts = Counter(row["collection"] for row in rows)
        return {"pack_version": pack_version, "total_records": len(rows), "collections": dict(counts)}

    def count(self, pack_version: str | None = None) -> int:
        with SessionLocal() as session:
            statement = select(func.count()).select_from(NiyamGuardDatasetRecord)
            if pack_version:
                statement = statement.where(NiyamGuardDatasetRecord.pack_version == pack_version)
            return int(session.scalar(statement) or 0)

    def collection_counts(self, pack_version: str | None = None) -> dict[str, int]:
        with SessionLocal() as session:
            statement = select(
                NiyamGuardDatasetRecord.collection,
                func.count(NiyamGuardDatasetRecord.id),
            ).group_by(NiyamGuardDatasetRecord.collection)
            if pack_version:
                statement = statement.where(NiyamGuardDatasetRecord.pack_version == pack_version)
            return {collection: int(count) for collection, count in session.execute(statement).all()}

    def list_records(
        self,
        collection: str,
        *,
        pack_version: str | None = None,
        limit: int = 50,
    ) -> list[dict[str, Any]]:
        with SessionLocal() as session:
            statement = (
                select(NiyamGuardDatasetRecord)
                .where(NiyamGuardDatasetRecord.collection == collection)
                .order_by(NiyamGuardDatasetRecord.item_id)
                .limit(max(1, min(limit, 500)))
            )
            if pack_version:
                statement = statement.where(NiyamGuardDatasetRecord.pack_version == pack_version)
            return [self._to_dict(record) for record in session.scalars(statement).all()]

    def all_records(
        self,
        collection: str,
        *,
        pack_version: str | None = None,
    ) -> list[dict[str, Any]]:
        with SessionLocal() as session:
            statement = select(NiyamGuardDatasetRecord).where(
                NiyamGuardDatasetRecord.collection == collection
            )
            if pack_version:
                statement = statement.where(NiyamGuardDatasetRecord.pack_version == pack_version)
            return [self._to_dict(record) for record in session.scalars(statement).all()]

    def get_record(
        self,
        collection: str,
        item_id: str,
        *,
        pack_version: str | None = None,
    ) -> dict[str, Any] | None:
        with SessionLocal() as session:
            statement = (
                select(NiyamGuardDatasetRecord)
                .where(NiyamGuardDatasetRecord.collection == collection)
                .where(NiyamGuardDatasetRecord.item_id == item_id)
            )
            if pack_version:
                statement = statement.where(NiyamGuardDatasetRecord.pack_version == pack_version)
            record = session.scalar(statement)
            return self._to_dict(record) if record else None

    @staticmethod
    def _to_dict(record: NiyamGuardDatasetRecord) -> dict[str, Any]:
        return {
            "pack_version": record.pack_version,
            "collection": record.collection,
            "item_id": record.item_id,
            "source_file": record.source_file,
            "payload": record.payload,
            "imported_at": record.imported_at,
        }


dataset_repository = DatasetRepository()
