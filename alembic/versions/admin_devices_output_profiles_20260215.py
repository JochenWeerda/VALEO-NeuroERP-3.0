"""admin devices and output profile settings

Revision ID: admin_devices_output_profiles_20260215
Revises: admin_api_keys_20260215
Create Date: 2026-02-15
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "admin_devices_output_profiles_20260215"
down_revision = "admin_api_keys_20260215"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "admin_devices",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("device_type", sa.String(length=20), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("vendor", sa.String(length=120), nullable=True),
        sa.Column("model", sa.String(length=120), nullable=True),
        sa.Column("station_code", sa.String(length=80), nullable=True),
        sa.Column("connection_uri", sa.String(length=255), nullable=True),
        sa.Column("capabilities", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("device_type IN ('printer','scanner')", name="chk_admin_devices_type"),
        schema="domain_shared",
    )
    op.create_index(
        "ix_admin_devices_tenant_type_active",
        "admin_devices",
        ["tenant_id", "device_type", "is_active"],
        unique=False,
        schema="domain_shared",
    )

    op.create_table(
        "admin_device_mappings",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("device_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("document_type", sa.String(length=60), nullable=False),
        sa.Column("process_code", sa.String(length=60), nullable=False),
        sa.Column("output_format", sa.String(length=20), nullable=False, server_default="pdf"),
        sa.Column("copies", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("is_default", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("settings", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["device_id"], ["domain_shared.admin_devices.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("copies >= 1 AND copies <= 20", name="chk_admin_device_mappings_copies"),
        sa.CheckConstraint("output_format IN ('pdf','zpl','epl','raw')", name="chk_admin_device_mappings_format"),
        sa.UniqueConstraint(
            "tenant_id",
            "device_id",
            "document_type",
            "process_code",
            "output_format",
            name="uq_admin_device_mappings_device_doc_process_format",
        ),
        schema="domain_shared",
    )
    op.create_index(
        "ix_admin_device_mappings_tenant_doc_process",
        "admin_device_mappings",
        ["tenant_id", "document_type", "process_code"],
        unique=False,
        schema="domain_shared",
    )

    op.create_table(
        "admin_output_templates",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("template_code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("document_type", sa.String(length=60), nullable=False),
        sa.Column("output_format", sa.String(length=20), nullable=False, server_default="pdf"),
        sa.Column("language", sa.String(length=10), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("current_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "template_code", name="uq_admin_output_templates_tenant_code"),
        sa.CheckConstraint("output_format IN ('pdf','zpl','epl','html','txt')", name="chk_admin_output_templates_format"),
        schema="domain_shared",
    )
    op.create_index(
        "ix_admin_output_templates_tenant_doc",
        "admin_output_templates",
        ["tenant_id", "document_type", "is_active"],
        unique=False,
        schema="domain_shared",
    )

    op.create_table(
        "admin_output_template_versions",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("template_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("version_no", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("change_note", sa.String(length=255), nullable=True),
        sa.Column("created_by", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["template_id"], ["domain_shared.admin_output_templates.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("template_id", "version_no", name="uq_admin_output_template_versions_template_version"),
        schema="domain_shared",
    )
    op.create_index(
        "ix_admin_output_template_versions_tenant_template",
        "admin_output_template_versions",
        ["tenant_id", "template_id", "version_no"],
        unique=False,
        schema="domain_shared",
    )

    op.create_table(
        "admin_output_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("profile_code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("document_type", sa.String(length=60), nullable=False),
        sa.Column("process_code", sa.String(length=60), nullable=False),
        sa.Column("template_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("device_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("output_channel", sa.String(length=20), nullable=False, server_default="print"),
        sa.Column("archive_mode", sa.String(length=20), nullable=False, server_default="dms"),
        sa.Column("archive_retention_days", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("settings", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["template_id"], ["domain_shared.admin_output_templates.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["device_id"], ["domain_shared.admin_devices.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "profile_code", name="uq_admin_output_profiles_tenant_code"),
        sa.CheckConstraint("output_channel IN ('print','email','dms','pdf')", name="chk_admin_output_profiles_channel"),
        sa.CheckConstraint("archive_mode IN ('none','dms','worm')", name="chk_admin_output_profiles_archive_mode"),
        sa.CheckConstraint(
            "archive_retention_days IS NULL OR archive_retention_days >= 0",
            name="chk_admin_output_profiles_retention_non_negative",
        ),
        schema="domain_shared",
    )
    op.create_index(
        "ix_admin_output_profiles_tenant_doc_process",
        "admin_output_profiles",
        ["tenant_id", "document_type", "process_code", "is_active"],
        unique=False,
        schema="domain_shared",
    )


def downgrade() -> None:
    op.drop_index("ix_admin_output_profiles_tenant_doc_process", table_name="admin_output_profiles", schema="domain_shared")
    op.drop_table("admin_output_profiles", schema="domain_shared")
    op.drop_index(
        "ix_admin_output_template_versions_tenant_template",
        table_name="admin_output_template_versions",
        schema="domain_shared",
    )
    op.drop_table("admin_output_template_versions", schema="domain_shared")
    op.drop_index("ix_admin_output_templates_tenant_doc", table_name="admin_output_templates", schema="domain_shared")
    op.drop_table("admin_output_templates", schema="domain_shared")
    op.drop_index("ix_admin_device_mappings_tenant_doc_process", table_name="admin_device_mappings", schema="domain_shared")
    op.drop_table("admin_device_mappings", schema="domain_shared")
    op.drop_index("ix_admin_devices_tenant_type_active", table_name="admin_devices", schema="domain_shared")
    op.drop_table("admin_devices", schema="domain_shared")
