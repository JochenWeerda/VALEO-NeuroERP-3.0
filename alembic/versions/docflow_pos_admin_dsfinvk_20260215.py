"""docflow pos admin and dsfinvk export tables

Revision ID: docflow_pos_admin_dsfinvk_20260215
Revises: docflow_pos_tse_compliance_20260215
Create Date: 2026-02-15
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "docflow_pos_admin_dsfinvk_20260215"
down_revision = "docflow_pos_tse_compliance_20260215"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "pos_terminals",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column("terminal_code", sa.String(length=60), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("location_name", sa.String(length=120), nullable=True),
        sa.Column("branch_code", sa.String(length=60), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("TRUE")),
        sa.Column("registered_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("unregistered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "terminal_code", name="uq_pos_terminal_code"),
        schema="domain_docflow",
    )
    op.create_index(
        "ix_pos_terminals_tenant_active",
        "pos_terminals",
        ["tenant_id", "is_active"],
        unique=False,
        schema="domain_docflow",
    )

    op.create_table(
        "pos_tse_devices",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column("terminal_id", sa.String(length=36), nullable=False),
        sa.Column("serial_number", sa.String(length=120), nullable=False),
        sa.Column("provider", sa.String(length=120), nullable=True),
        sa.Column("api_endpoint", sa.String(length=255), nullable=True),
        sa.Column("certificate_fingerprint", sa.String(length=255), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("activation_date", sa.Date(), nullable=True),
        sa.Column("deactivation_date", sa.Date(), nullable=True),
        sa.Column("last_heartbeat_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("settings", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["terminal_id"], ["domain_docflow.pos_terminals.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("tenant_id", "serial_number", name="uq_pos_tse_serial"),
        sa.CheckConstraint("status IN ('active','inactive','retired')", name="chk_pos_tse_status"),
        schema="domain_docflow",
    )
    op.create_index(
        "ix_pos_tse_devices_tenant_status",
        "pos_tse_devices",
        ["tenant_id", "status"],
        unique=False,
        schema="domain_docflow",
    )

    op.create_table(
        "pos_regulatory_notices",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column("terminal_id", sa.String(length=36), nullable=True),
        sa.Column("tse_device_id", sa.String(length=36), nullable=True),
        sa.Column("notice_type", sa.String(length=30), nullable=False),
        sa.Column("notice_status", sa.String(length=20), nullable=False, server_default="draft"),
        sa.Column("effective_date", sa.Date(), nullable=False),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("reference_number", sa.String(length=120), nullable=True),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["terminal_id"], ["domain_docflow.pos_terminals.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["tse_device_id"], ["domain_docflow.pos_tse_devices.id"], ondelete="SET NULL"),
        sa.CheckConstraint("notice_type IN ('install','change','decommission')", name="chk_pos_notice_type"),
        sa.CheckConstraint("notice_status IN ('draft','submitted','accepted','rejected')", name="chk_pos_notice_status"),
        schema="domain_docflow",
    )
    op.create_index(
        "ix_pos_notices_tenant_effective",
        "pos_regulatory_notices",
        ["tenant_id", "effective_date"],
        unique=False,
        schema="domain_docflow",
    )

    op.create_table(
        "dsfinvk_exports",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column("period_from", sa.Date(), nullable=False),
        sa.Column("period_to", sa.Date(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="running"),
        sa.Column("file_path", sa.String(length=500), nullable=True),
        sa.Column("checksum_sha256", sa.String(length=64), nullable=True),
        sa.Column("row_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("generated_by", sa.String(length=100), nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("status IN ('running','completed','failed')", name="chk_dsfinvk_export_status"),
        sa.CheckConstraint("period_to >= period_from", name="chk_dsfinvk_period"),
        schema="domain_docflow",
    )
    op.create_index(
        "ix_dsfinvk_exports_tenant_period",
        "dsfinvk_exports",
        ["tenant_id", "period_from", "period_to"],
        unique=False,
        schema="domain_docflow",
    )


def downgrade() -> None:
    op.drop_index("ix_dsfinvk_exports_tenant_period", table_name="dsfinvk_exports", schema="domain_docflow")
    op.drop_table("dsfinvk_exports", schema="domain_docflow")

    op.drop_index("ix_pos_notices_tenant_effective", table_name="pos_regulatory_notices", schema="domain_docflow")
    op.drop_table("pos_regulatory_notices", schema="domain_docflow")

    op.drop_index("ix_pos_tse_devices_tenant_status", table_name="pos_tse_devices", schema="domain_docflow")
    op.drop_table("pos_tse_devices", schema="domain_docflow")

    op.drop_index("ix_pos_terminals_tenant_active", table_name="pos_terminals", schema="domain_docflow")
    op.drop_table("pos_terminals", schema="domain_docflow")
