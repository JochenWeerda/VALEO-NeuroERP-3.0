"""admin self-service report permissions

Revision ID: admin_report_permissions_20260215
Revises: hr_personal_time_tracking_20260215
Create Date: 2026-02-15
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "admin_report_permissions_20260215"
down_revision = "hr_personal_time_tracking_20260215"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "admin_report_permissions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("role_id", sa.String(length=64), nullable=False),
        sa.Column("report_key", sa.String(length=120), nullable=False),
        sa.Column("can_view", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("can_export", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("allowed_scopes", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("filters", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "role_id", "report_key", name="uq_admin_report_permissions_role_report"),
        schema="domain_shared",
    )
    op.create_index(
        "ix_admin_report_permissions_tenant_role",
        "admin_report_permissions",
        ["tenant_id", "role_id", "active"],
        unique=False,
        schema="domain_shared",
    )
    op.create_index(
        "ix_admin_report_permissions_tenant_report",
        "admin_report_permissions",
        ["tenant_id", "report_key", "active"],
        unique=False,
        schema="domain_shared",
    )


def downgrade() -> None:
    op.drop_index("ix_admin_report_permissions_tenant_report", table_name="admin_report_permissions", schema="domain_shared")
    op.drop_index("ix_admin_report_permissions_tenant_role", table_name="admin_report_permissions", schema="domain_shared")
    op.drop_table("admin_report_permissions", schema="domain_shared")
