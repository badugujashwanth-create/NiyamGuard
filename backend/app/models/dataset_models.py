from typing import Any

from sqlalchemy import JSON, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class NiyamGuardDatasetRecord(Base):
    __tablename__ = "niyamguard_dataset_records"
    __table_args__ = (
        UniqueConstraint(
            "pack_version",
            "collection",
            "item_id",
            name="uq_dataset_record_pack_collection_item",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    pack_version: Mapped[str] = mapped_column(String(80), index=True)
    collection: Mapped[str] = mapped_column(String(120), index=True)
    item_id: Mapped[str] = mapped_column(String(180), index=True)
    source_file: Mapped[str] = mapped_column(String(300), index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)
    imported_at: Mapped[str] = mapped_column(String(40), index=True)
