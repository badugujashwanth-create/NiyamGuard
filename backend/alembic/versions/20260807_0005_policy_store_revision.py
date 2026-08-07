"""add optimistic revision for serialized policy-store writes

Revision ID: 20260807_0005
Revises: 20260807_0004
Create Date: 2026-08-07
"""

from alembic import op
import sqlalchemy as sa


revision = "20260807_0005"
down_revision = "20260807_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "policy_store_revisions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("revision", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("updated_at", sa.String(length=40), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.execute(
        sa.text(
            "INSERT INTO policy_store_revisions (id, revision, updated_at) "
            "VALUES (1, 0, '1970-01-01T00:00:00+00:00')"
        )
    )


def downgrade() -> None:
    op.drop_table("policy_store_revisions")
