"""add normalized policy-drift records

Revision ID: 20260807_0006
Revises: 20260807_0005
Create Date: 2026-08-07
"""

from alembic import op
import sqlalchemy as sa


revision = "20260807_0006"
down_revision = "20260807_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "circular_documents",
        sa.Column("id", sa.String(length=160), nullable=False),
        sa.Column("source_id", sa.String(length=160), nullable=False),
        sa.Column("circular_number", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("department", sa.String(length=160), nullable=False),
        sa.Column("published_date", sa.String(length=40), nullable=False),
        sa.Column("effective_date", sa.String(length=40), nullable=False),
        sa.Column("expiry_date", sa.String(length=40), nullable=True),
        sa.Column("document_url", sa.String(length=500), nullable=True),
        sa.Column("storage_path", sa.String(length=500), nullable=True),
        sa.Column("source_filename", sa.String(length=160), nullable=True),
        sa.Column("source_content_type", sa.String(length=120), nullable=True),
        sa.Column("source_size_bytes", sa.Integer(), nullable=True),
        sa.Column("source_sha256", sa.String(length=64), nullable=True),
        sa.Column("malware_scan_status", sa.String(length=40), nullable=True),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("content_hash", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.String(length=40), nullable=False),
        sa.Column("updated_at", sa.String(length=40), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_circular_documents_source_id", "circular_documents", ["source_id"])
    op.create_index("ix_circular_documents_circular_number", "circular_documents", ["circular_number"])
    op.create_index("ix_circular_documents_department", "circular_documents", ["department"])
    op.create_index("ix_circular_documents_effective_date", "circular_documents", ["effective_date"])
    op.create_index("ix_circular_documents_source_sha256", "circular_documents", ["source_sha256"])
    op.create_index("ix_circular_documents_content_hash", "circular_documents", ["content_hash"])
    op.create_index("ix_circular_documents_status", "circular_documents", ["status"])

    op.create_table(
        "policy_rule_candidates",
        sa.Column("id", sa.String(length=160), nullable=False),
        sa.Column("circular_id", sa.String(length=160), nullable=False),
        sa.Column("service_id", sa.String(length=120), nullable=False),
        sa.Column("rule_key", sa.String(length=120), nullable=False),
        sa.Column("old_value", sa.String(length=200), nullable=True),
        sa.Column("new_value", sa.String(length=200), nullable=False),
        sa.Column("unit", sa.String(length=80), nullable=True),
        sa.Column("effective_date", sa.String(length=40), nullable=False),
        sa.Column("expiry_date", sa.String(length=40), nullable=True),
        sa.Column("confidence_score", sa.Float(), nullable=False),
        sa.Column("extraction_method", sa.String(length=40), nullable=False),
        sa.Column("source_excerpt", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("requires_review", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.String(length=40), nullable=False),
        sa.ForeignKeyConstraint(["circular_id"], ["circular_documents.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_policy_rule_candidates_circular_id", "policy_rule_candidates", ["circular_id"])
    op.create_index("ix_policy_rule_candidates_service_id", "policy_rule_candidates", ["service_id"])
    op.create_index("ix_policy_rule_candidates_rule_key", "policy_rule_candidates", ["rule_key"])
    op.create_index("ix_policy_rule_candidates_effective_date", "policy_rule_candidates", ["effective_date"])
    op.create_index("ix_policy_rule_candidates_status", "policy_rule_candidates", ["status"])

    op.create_table(
        "policy_rule_versions",
        sa.Column("id", sa.String(length=160), nullable=False),
        sa.Column("rule_id", sa.String(length=160), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("service_id", sa.String(length=120), nullable=False),
        sa.Column("rule_key", sa.String(length=120), nullable=False),
        sa.Column("value", sa.String(length=200), nullable=False),
        sa.Column("unit", sa.String(length=80), nullable=True),
        sa.Column("source_circular_id", sa.String(length=160), nullable=False),
        sa.Column("source_circular_number", sa.String(length=80), nullable=False),
        sa.Column("effective_date", sa.String(length=40), nullable=False),
        sa.Column("expiry_date", sa.String(length=40), nullable=True),
        sa.Column("published_by", sa.String(length=160), nullable=True),
        sa.Column("published_at", sa.String(length=40), nullable=False),
        sa.Column("is_current", sa.Boolean(), nullable=False),
        sa.Column("previous_version_id", sa.String(length=160), nullable=True),
        sa.ForeignKeyConstraint(["source_circular_id"], ["circular_documents.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("rule_id", "version_number", name="uq_policy_rule_version_number"),
    )
    op.create_index("ix_policy_rule_versions_rule_id", "policy_rule_versions", ["rule_id"])
    op.create_index("ix_policy_rule_versions_service_id", "policy_rule_versions", ["service_id"])
    op.create_index("ix_policy_rule_versions_rule_key", "policy_rule_versions", ["rule_key"])
    op.create_index("ix_policy_rule_versions_source_circular_id", "policy_rule_versions", ["source_circular_id"])
    op.create_index("ix_policy_rule_versions_effective_date", "policy_rule_versions", ["effective_date"])
    op.create_index("ix_policy_rule_versions_is_current", "policy_rule_versions", ["is_current"])

    op.create_table(
        "connected_system_snapshots",
        sa.Column("id", sa.String(length=160), nullable=False),
        sa.Column("connected_system_id", sa.String(length=160), nullable=False),
        sa.Column("service_id", sa.String(length=120), nullable=False),
        sa.Column("rule_key", sa.String(length=120), nullable=False),
        sa.Column("displayed_value", sa.String(length=200), nullable=False),
        sa.Column("unit", sa.String(length=80), nullable=True),
        sa.Column("source_location", sa.String(length=500), nullable=False),
        sa.Column("last_synced_at", sa.String(length=40), nullable=True),
        sa.Column("snapshot_source", sa.String(length=40), nullable=False),
        sa.Column("created_at", sa.String(length=40), nullable=False),
        sa.Column("updated_at", sa.String(length=40), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_connected_system_snapshots_connected_system_id", "connected_system_snapshots", ["connected_system_id"])
    op.create_index("ix_connected_system_snapshots_service_id", "connected_system_snapshots", ["service_id"])
    op.create_index("ix_connected_system_snapshots_rule_key", "connected_system_snapshots", ["rule_key"])

    op.create_table(
        "compliance_findings",
        sa.Column("id", sa.String(length=160), nullable=False),
        sa.Column("verified_rule_id", sa.String(length=160), nullable=False),
        sa.Column("connected_system_id", sa.String(length=160), nullable=False),
        sa.Column("snapshot_id", sa.String(length=160), nullable=True),
        sa.Column("service_id", sa.String(length=120), nullable=False),
        sa.Column("rule_key", sa.String(length=120), nullable=False),
        sa.Column("expected_value", sa.String(length=200), nullable=False),
        sa.Column("actual_value", sa.String(length=200), nullable=True),
        sa.Column("status", sa.String(length=40), nullable=False),
        sa.Column("severity", sa.String(length=40), nullable=False),
        sa.Column("finding_summary", sa.Text(), nullable=False),
        sa.Column("source_clause", sa.Text(), nullable=False),
        sa.Column("recommended_fix", sa.Text(), nullable=False),
        sa.Column("citizen_impact_reason", sa.Text(), nullable=False),
        sa.Column("created_at", sa.String(length=40), nullable=False),
        sa.Column("updated_at", sa.String(length=40), nullable=False),
        sa.ForeignKeyConstraint(["verified_rule_id"], ["policy_rule_versions.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_compliance_findings_verified_rule_id", "compliance_findings", ["verified_rule_id"])
    op.create_index("ix_compliance_findings_connected_system_id", "compliance_findings", ["connected_system_id"])
    op.create_index("ix_compliance_findings_snapshot_id", "compliance_findings", ["snapshot_id"])
    op.create_index("ix_compliance_findings_service_id", "compliance_findings", ["service_id"])
    op.create_index("ix_compliance_findings_rule_key", "compliance_findings", ["rule_key"])
    op.create_index("ix_compliance_findings_status", "compliance_findings", ["status"])
    op.create_index("ix_compliance_findings_severity", "compliance_findings", ["severity"])


def downgrade() -> None:
    op.drop_table("compliance_findings")
    op.drop_table("connected_system_snapshots")
    op.drop_table("policy_rule_versions")
    op.drop_table("policy_rule_candidates")
    op.drop_table("circular_documents")
