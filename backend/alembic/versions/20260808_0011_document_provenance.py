"""add OCR and page provenance to circular documents

Revision ID: 20260808_0011
Revises: 20260807_0010
Create Date: 2026-08-08
"""

from alembic import op
import sqlalchemy as sa


revision = "20260808_0011"
down_revision = "20260807_0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("circular_documents") as batch_op:
        batch_op.add_column(sa.Column("extraction_source", sa.String(length=20), nullable=False, server_default="NATIVE_TEXT"))
        batch_op.add_column(sa.Column("ocr_used", sa.Boolean(), nullable=False, server_default=sa.false()))
        batch_op.add_column(sa.Column("ocr_storage_path", sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column("page_provenance", sa.JSON(), nullable=False, server_default="[]"))


def downgrade() -> None:
    with op.batch_alter_table("circular_documents") as batch_op:
        batch_op.drop_column("page_provenance")
        batch_op.drop_column("ocr_storage_path")
        batch_op.drop_column("ocr_used")
        batch_op.drop_column("extraction_source")
