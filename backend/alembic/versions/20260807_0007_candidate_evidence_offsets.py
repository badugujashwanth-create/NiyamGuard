"""persist deterministic candidate evidence offsets

Revision ID: 20260807_0007
Revises: 20260807_0006
Create Date: 2026-08-07
"""

from alembic import op
import sqlalchemy as sa


revision = "20260807_0007"
down_revision = "20260807_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "policy_rule_candidates",
        sa.Column("source_start_offset", sa.Integer(), nullable=True),
    )
    op.add_column(
        "policy_rule_candidates",
        sa.Column("source_end_offset", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("policy_rule_candidates", "source_end_offset")
    op.drop_column("policy_rule_candidates", "source_start_offset")
