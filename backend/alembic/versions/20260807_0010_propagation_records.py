"""normalize propagation and rollback records

Revision ID: 20260807_0010
Revises: 20260807_0009
Create Date: 2026-08-07
"""

from alembic import op
import sqlalchemy as sa


revision = "20260807_0010"
down_revision = "20260807_0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "propagation_plans",
        sa.Column("id", sa.String(length=160), nullable=False),
        sa.Column("rule_version_id", sa.String(length=160), nullable=False),
        sa.Column("service_id", sa.String(length=120), nullable=False),
        sa.Column("rule_key", sa.String(length=120), nullable=False),
        sa.Column("task_ids", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.String(length=40), nullable=False),
        sa.ForeignKeyConstraint(["rule_version_id"], ["policy_rule_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_propagation_plans_rule_version_id", "propagation_plans", ["rule_version_id"])
    op.create_index("ix_propagation_plans_service_id", "propagation_plans", ["service_id"])
    op.create_index("ix_propagation_plans_rule_key", "propagation_plans", ["rule_key"])
    op.create_index("ix_propagation_plans_status", "propagation_plans", ["status"])

    op.create_table(
        "propagation_tasks",
        sa.Column("id", sa.String(length=160), nullable=False),
        sa.Column("rule_version_id", sa.String(length=160), nullable=False),
        sa.Column("connected_system_id", sa.String(length=160), nullable=False),
        sa.Column("task_type", sa.String(length=40), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("old_value", sa.String(length=200), nullable=True),
        sa.Column("new_value", sa.String(length=200), nullable=False),
        sa.Column("patch_payload_json", sa.JSON(), nullable=False),
        sa.Column("assigned_to", sa.String(length=160), nullable=True),
        sa.Column("created_at", sa.String(length=40), nullable=False),
        sa.Column("completed_at", sa.String(length=40), nullable=True),
        sa.ForeignKeyConstraint(["rule_version_id"], ["policy_rule_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_propagation_tasks_rule_version_id", "propagation_tasks", ["rule_version_id"])
    op.create_index("ix_propagation_tasks_connected_system_id", "propagation_tasks", ["connected_system_id"])
    op.create_index("ix_propagation_tasks_task_type", "propagation_tasks", ["task_type"])
    op.create_index("ix_propagation_tasks_status", "propagation_tasks", ["status"])
    op.create_index("ix_propagation_tasks_assigned_to", "propagation_tasks", ["assigned_to"])

    op.create_table(
        "connected_system_patches",
        sa.Column("id", sa.String(length=160), nullable=False),
        sa.Column("propagation_task_id", sa.String(length=160), nullable=False),
        sa.Column("connected_system_id", sa.String(length=160), nullable=False),
        sa.Column("patch_type", sa.String(length=80), nullable=False),
        sa.Column("before_snapshot_json", sa.JSON(), nullable=False),
        sa.Column("after_snapshot_json", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.String(length=40), nullable=False),
        sa.Column("applied_at", sa.String(length=40), nullable=True),
        sa.ForeignKeyConstraint(["propagation_task_id"], ["propagation_tasks.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_connected_system_patches_propagation_task_id", "connected_system_patches", ["propagation_task_id"])
    op.create_index("ix_connected_system_patches_connected_system_id", "connected_system_patches", ["connected_system_id"])
    op.create_index("ix_connected_system_patches_patch_type", "connected_system_patches", ["patch_type"])
    op.create_index("ix_connected_system_patches_status", "connected_system_patches", ["status"])

    op.create_table(
        "rollback_events",
        sa.Column("id", sa.String(length=160), nullable=False),
        sa.Column("rule_id", sa.String(length=160), nullable=False),
        sa.Column("from_version_id", sa.String(length=160), nullable=False),
        sa.Column("to_version_id", sa.String(length=160), nullable=False),
        sa.Column("rolled_back_by", sa.String(length=160), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("created_at", sa.String(length=40), nullable=False),
        sa.ForeignKeyConstraint(["from_version_id"], ["policy_rule_versions.id"]),
        sa.ForeignKeyConstraint(["to_version_id"], ["policy_rule_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_rollback_events_rule_id", "rollback_events", ["rule_id"])
    op.create_index("ix_rollback_events_from_version_id", "rollback_events", ["from_version_id"])
    op.create_index("ix_rollback_events_to_version_id", "rollback_events", ["to_version_id"])
    op.create_index("ix_rollback_events_rolled_back_by", "rollback_events", ["rolled_back_by"])


def downgrade() -> None:
    op.drop_table("rollback_events")
    op.drop_table("connected_system_patches")
    op.drop_table("propagation_tasks")
    op.drop_table("propagation_plans")
