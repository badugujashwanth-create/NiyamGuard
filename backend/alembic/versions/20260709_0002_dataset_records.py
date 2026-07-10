"""add synthetic dataset records

Revision ID: 20260709_0002
Revises: 20260709_0001
Create Date: 2026-07-09
"""
from alembic import op
import sqlalchemy as sa

revision = "20260709_0002"
down_revision = "20260709_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "niyamguard_dataset_records",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("pack_version", sa.String(length=80), nullable=False),
        sa.Column("collection", sa.String(length=120), nullable=False),
        sa.Column("item_id", sa.String(length=180), nullable=False),
        sa.Column("source_file", sa.String(length=300), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("imported_at", sa.String(length=40), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "pack_version",
            "collection",
            "item_id",
            name="uq_dataset_record_pack_collection_item",
        ),
    )
    op.create_index("ix_niyamguard_dataset_records_pack_version", "niyamguard_dataset_records", ["pack_version"])
    op.create_index("ix_niyamguard_dataset_records_collection", "niyamguard_dataset_records", ["collection"])
    op.create_index("ix_niyamguard_dataset_records_item_id", "niyamguard_dataset_records", ["item_id"])
    op.create_index("ix_niyamguard_dataset_records_source_file", "niyamguard_dataset_records", ["source_file"])
    op.create_index("ix_niyamguard_dataset_records_imported_at", "niyamguard_dataset_records", ["imported_at"])


def downgrade() -> None:
    op.drop_table("niyamguard_dataset_records")
