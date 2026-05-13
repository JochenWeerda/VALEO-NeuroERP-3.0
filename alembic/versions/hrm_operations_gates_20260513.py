"""HRM operations gates persistence and evidence workflow.

Revision ID: hrm_operations_gates_20260513
Revises: faf00a6bfc11
Create Date: 2026-05-13
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "hrm_operations_gates_20260513"
down_revision = "faf00a6bfc11"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(sa.text("CREATE SCHEMA IF NOT EXISTS domain_hr"))

    op.create_table(
        "hrm_operations_gates",
        sa.Column("tenant_id", sa.String(length=80), nullable=False),
        sa.Column("gate_id", sa.String(length=80), nullable=False),
        sa.Column("status", sa.String(length=40), nullable=False, server_default=sa.text("'external_evidence_required'")),
        sa.Column("owner_role", sa.String(length=160), nullable=False),
        sa.Column("go_live_blocking", sa.Boolean(), nullable=False, server_default=sa.text("TRUE")),
        sa.Column("last_probe_status", sa.String(length=40), nullable=True),
        sa.Column("last_probe_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("approved_by", sa.String(length=160), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("rejection_reason", sa.Text(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("tenant_id", "gate_id", name="pk_hrm_operations_gates"),
        sa.CheckConstraint(
            "status IN ('external_evidence_required','evidence_submitted','probe_passed','approved','rejected')",
            name="ck_hrm_operations_gates_status",
        ),
        sa.CheckConstraint(
            "last_probe_status IS NULL OR last_probe_status IN ('passed','failed','manual','not_configured')",
            name="ck_hrm_operations_gates_probe_status",
        ),
        schema="domain_hr",
    )
    op.create_index(
        "idx_hrm_operations_gates_tenant_status",
        "hrm_operations_gates",
        ["tenant_id", "status"],
        schema="domain_hr",
    )

    op.create_table(
        "hrm_operations_gate_evidence",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=80), nullable=False),
        sa.Column("gate_id", sa.String(length=80), nullable=False),
        sa.Column("evidence_type", sa.String(length=80), nullable=False),
        sa.Column("title", sa.String(length=220), nullable=False),
        sa.Column("artifact_ref", sa.String(length=500), nullable=False),
        sa.Column("submitted_by", sa.String(length=160), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.ForeignKeyConstraint(
            ["tenant_id", "gate_id"],
            ["domain_hr.hrm_operations_gates.tenant_id", "domain_hr.hrm_operations_gates.gate_id"],
            ondelete="CASCADE",
            name="fk_hrm_gate_evidence_gate",
        ),
        sa.PrimaryKeyConstraint("id"),
        schema="domain_hr",
    )
    op.create_index(
        "idx_hrm_gate_evidence_tenant_gate",
        "hrm_operations_gate_evidence",
        ["tenant_id", "gate_id", "submitted_at"],
        schema="domain_hr",
    )

    op.create_table(
        "hrm_operations_gate_probes",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=80), nullable=False),
        sa.Column("gate_id", sa.String(length=80), nullable=False),
        sa.Column("provider", sa.String(length=120), nullable=False),
        sa.Column("probe_type", sa.String(length=80), nullable=False),
        sa.Column("result", sa.String(length=40), nullable=False),
        sa.Column("performed_by", sa.String(length=160), nullable=False),
        sa.Column("performed_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.ForeignKeyConstraint(
            ["tenant_id", "gate_id"],
            ["domain_hr.hrm_operations_gates.tenant_id", "domain_hr.hrm_operations_gates.gate_id"],
            ondelete="CASCADE",
            name="fk_hrm_gate_probes_gate",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("result IN ('passed','failed','manual','not_configured')", name="ck_hrm_gate_probes_result"),
        schema="domain_hr",
    )
    op.create_index(
        "idx_hrm_gate_probes_tenant_gate",
        "hrm_operations_gate_probes",
        ["tenant_id", "gate_id", "performed_at"],
        schema="domain_hr",
    )

    op.create_table(
        "hrm_operations_gate_audit",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=80), nullable=False),
        sa.Column("gate_id", sa.String(length=80), nullable=False),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("actor", sa.String(length=160), nullable=False),
        sa.Column("from_status", sa.String(length=40), nullable=True),
        sa.Column("to_status", sa.String(length=40), nullable=False),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("details", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        schema="domain_hr",
    )
    op.create_index(
        "idx_hrm_gate_audit_tenant_gate",
        "hrm_operations_gate_audit",
        ["tenant_id", "gate_id", "created_at"],
        schema="domain_hr",
    )


def downgrade() -> None:
    op.drop_index("idx_hrm_gate_audit_tenant_gate", table_name="hrm_operations_gate_audit", schema="domain_hr")
    op.drop_table("hrm_operations_gate_audit", schema="domain_hr")
    op.drop_index("idx_hrm_gate_probes_tenant_gate", table_name="hrm_operations_gate_probes", schema="domain_hr")
    op.drop_table("hrm_operations_gate_probes", schema="domain_hr")
    op.drop_index("idx_hrm_gate_evidence_tenant_gate", table_name="hrm_operations_gate_evidence", schema="domain_hr")
    op.drop_table("hrm_operations_gate_evidence", schema="domain_hr")
    op.drop_index("idx_hrm_operations_gates_tenant_status", table_name="hrm_operations_gates", schema="domain_hr")
    op.drop_table("hrm_operations_gates", schema="domain_hr")
