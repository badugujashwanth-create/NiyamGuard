"""add revocable session linkage to auth records

Revision ID: 20260807_0003
Revises: 20260709_0002
Create Date: 2026-08-07
"""
from alembic import op
import sqlalchemy as sa


revision = "20260807_0003"
down_revision = "20260709_0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "refresh_tokens",
        sa.Column("session_id", sa.String(length=120), nullable=True),
    )
    op.create_index("ix_refresh_tokens_session_id", "refresh_tokens", ["session_id"])
    op.add_column(
        "user_sessions",
        sa.Column("revoked_at", sa.String(length=40), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("user_sessions", "revoked_at")
    op.drop_index("ix_refresh_tokens_session_id", table_name="refresh_tokens")
    op.drop_column("refresh_tokens", "session_id")
