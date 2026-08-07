from typing import Any

from sqlalchemy import JSON, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PolicyRecord(Base):
    __tablename__ = "policy_records"
    __table_args__ = (
        UniqueConstraint("collection", "item_id", name="uq_policy_record_collection_item"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    collection: Mapped[str] = mapped_column(String(80), index=True)
    item_id: Mapped[str] = mapped_column(String(160), index=True)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)


class PolicyStoreRevision(Base):
    """Singleton revision used to reject stale full-store replacements."""

    __tablename__ = "policy_store_revisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    updated_at: Mapped[str] = mapped_column(String(40), nullable=False)
