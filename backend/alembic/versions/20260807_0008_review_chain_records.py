"""normalize candidate deltas and approval workflows

Revision ID: 20260807_0008
Revises: 20260807_0007
Create Date: 2026-08-07
"""

from alembic import op
import sqlalchemy as sa


revision = "20260807_0008"
down_revision = "20260807_0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "policy_rule_deltas",
        sa.Column("id", sa.String(length=160), nullable=False),
        sa.Column("candidate_id", sa.String(length=160), nullable=False),
        sa.Column("existing_rule_id", sa.String(length=160), nullable=True),
        sa.Column("change_type", sa.String(length=40), nullable=False),
        sa.Column("previous_value", sa.String(length=200), nullable=True),
        sa.Column("proposed_value", sa.String(length=200), nullable=False),
        sa.Column("impact_level", sa.String(length=40), nullable=False),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column("created_at", sa.String(length=40), nullable=False),
        sa.ForeignKeyConstraint(["candidate_id"], ["policy_rule_candidates.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_policy_rule_deltas_candidate_id", "policy_rule_deltas", ["candidate_id"])
    op.create_index("ix_policy_rule_deltas_existing_rule_id", "policy_rule_deltas", ["existing_rule_id"])
    op.create_index("ix_policy_rule_deltas_change_type", "policy_rule_deltas", ["change_type"])
    op.create_index("ix_policy_rule_deltas_impact_level", "policy_rule_deltas", ["impact_level"])

    op.create_table(
        "rule_approval_workflows",
        sa.Column("id", sa.String(length=160), nullable=False),
        sa.Column("candidate_id", sa.String(length=160), nullable=False),
        sa.Column("reviewer_user_id", sa.String(length=160), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("review_notes", sa.Text(), nullable=True),
        sa.Column("reviewed_at", sa.String(length=40), nullable=True),
        sa.Column("created_at", sa.String(length=40), nullable=False),
        sa.ForeignKeyConstraint(["candidate_id"], ["policy_rule_candidates.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_rule_approval_workflows_candidate_id", "rule_approval_workflows", ["candidate_id"])
    op.create_index("ix_rule_approval_workflows_reviewer_user_id", "rule_approval_workflows", ["reviewer_user_id"])
    op.create_index("ix_rule_approval_workflows_status", "rule_approval_workflows", ["status"])


def downgrade() -> None:
    op.drop_table("rule_approval_workflows")
    op.drop_table("policy_rule_deltas")
