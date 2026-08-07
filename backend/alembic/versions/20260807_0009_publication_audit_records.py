"""normalize publication and downstream audit records

Revision ID: 20260807_0009
Revises: 20260807_0008
Create Date: 2026-08-07
"""

from alembic import op
import sqlalchemy as sa


revision = "20260807_0009"
down_revision = "20260807_0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "policy_publication_events",
        sa.Column("id", sa.String(length=160), nullable=False),
        sa.Column("candidate_id", sa.String(length=160), nullable=False),
        sa.Column("rule_version_id", sa.String(length=160), nullable=False),
        sa.Column("service_id", sa.String(length=120), nullable=False),
        sa.Column("rule_key", sa.String(length=120), nullable=False),
        sa.Column("old_value", sa.String(length=200), nullable=True),
        sa.Column("new_value", sa.String(length=200), nullable=False),
        sa.Column("published_by", sa.String(length=160), nullable=True),
        sa.Column("created_at", sa.String(length=40), nullable=False),
        sa.ForeignKeyConstraint(["candidate_id"], ["policy_rule_candidates.id"]),
        sa.ForeignKeyConstraint(["rule_version_id"], ["policy_rule_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_policy_publication_events_candidate_id", "policy_publication_events", ["candidate_id"])
    op.create_index("ix_policy_publication_events_rule_version_id", "policy_publication_events", ["rule_version_id"])
    op.create_index("ix_policy_publication_events_service_id", "policy_publication_events", ["service_id"])
    op.create_index("ix_policy_publication_events_rule_key", "policy_publication_events", ["rule_key"])

    op.create_table(
        "knowledge_update_events",
        sa.Column("id", sa.String(length=160), nullable=False),
        sa.Column("rule_version_id", sa.String(length=160), nullable=False),
        sa.Column("service_id", sa.String(length=120), nullable=False),
        sa.Column("rule_key", sa.String(length=120), nullable=False),
        sa.Column("update_type", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("details", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.String(length=40), nullable=False),
        sa.ForeignKeyConstraint(["rule_version_id"], ["policy_rule_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_knowledge_update_events_rule_version_id", "knowledge_update_events", ["rule_version_id"])
    op.create_index("ix_knowledge_update_events_service_id", "knowledge_update_events", ["service_id"])
    op.create_index("ix_knowledge_update_events_rule_key", "knowledge_update_events", ["rule_key"])
    op.create_index("ix_knowledge_update_events_update_type", "knowledge_update_events", ["update_type"])
    op.create_index("ix_knowledge_update_events_status", "knowledge_update_events", ["status"])

    op.create_table(
        "compliance_runs",
        sa.Column("id", sa.String(length=160), nullable=False),
        sa.Column("trigger_type", sa.String(length=40), nullable=False),
        sa.Column("triggered_by", sa.String(length=160), nullable=True),
        sa.Column("affected_rule_id", sa.String(length=160), nullable=True),
        sa.Column("started_at", sa.String(length=40), nullable=False),
        sa.Column("completed_at", sa.String(length=40), nullable=True),
        sa.Column("finding_count", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_compliance_runs_trigger_type", "compliance_runs", ["trigger_type"])
    op.create_index("ix_compliance_runs_triggered_by", "compliance_runs", ["triggered_by"])
    op.create_index("ix_compliance_runs_affected_rule_id", "compliance_runs", ["affected_rule_id"])


def downgrade() -> None:
    op.drop_table("compliance_runs")
    op.drop_table("knowledge_update_events")
    op.drop_table("policy_publication_events")
