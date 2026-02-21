"""controlling module initial tables

Revision ID: controlling_module_initial_20260215
Revises: ops_chargen_add_mhd_20260215
Create Date: 2026-02-15
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "controlling_module_initial_20260215"
down_revision = "ops_chargen_add_mhd_20260215"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(sa.text("CREATE SCHEMA IF NOT EXISTS domain_controlling"))

    op.create_table(
        "kpi_definitions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("kpi_code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("formula", sa.Text(), nullable=True),
        sa.Column("target_value", sa.Numeric(18, 4), nullable=True),
        sa.Column("unit", sa.String(length=30), nullable=True),
        sa.Column("ampel_logic", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("filters", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "kpi_code", name="uq_controlling_kpi_code"),
        schema="domain_controlling",
    )
    op.create_index(
        "ix_controlling_kpi_tenant_active",
        "kpi_definitions",
        ["tenant_id", "is_active"],
        unique=False,
        schema="domain_controlling",
    )

    op.create_table(
        "dashboard_configs",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("dashboard_code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("layout", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("default_filters", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("role_scope", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "dashboard_code", name="uq_controlling_dashboard_code"),
        schema="domain_controlling",
    )
    op.create_index(
        "ix_controlling_dashboards_tenant_active",
        "dashboard_configs",
        ["tenant_id", "is_active"],
        unique=False,
        schema="domain_controlling",
    )

    op.create_table(
        "dashboard_widgets",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("dashboard_id", sa.String(), nullable=False),
        sa.Column("widget_type", sa.String(length=40), nullable=False),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("kpi_id", sa.String(), nullable=True),
        sa.Column("position_x", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("position_y", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("size_w", sa.Integer(), nullable=False, server_default="4"),
        sa.Column("size_h", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("settings", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["dashboard_id"], ["domain_controlling.dashboard_configs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["kpi_id"], ["domain_controlling.kpi_definitions.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        schema="domain_controlling",
    )
    op.create_index(
        "ix_controlling_widgets_dashboard",
        "dashboard_widgets",
        ["tenant_id", "dashboard_id"],
        unique=False,
        schema="domain_controlling",
    )

    op.create_table(
        "kpi_timeseries",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("kpi_id", sa.String(), nullable=False),
        sa.Column("period_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("period_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("value", sa.Numeric(18, 4), nullable=False),
        sa.Column("dimensions", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("source", sa.String(length=60), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["kpi_id"], ["domain_controlling.kpi_definitions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        schema="domain_controlling",
    )
    op.create_index(
        "ix_controlling_timeseries_kpi_period",
        "kpi_timeseries",
        ["tenant_id", "kpi_id", "period_start"],
        unique=False,
        schema="domain_controlling",
    )

    op.create_table(
        "controlling_actions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("kpi_id", sa.String(), nullable=True),
        sa.Column("dashboard_id", sa.String(), nullable=True),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("owner_user_id", sa.String(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="open"),
        sa.Column("due_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["kpi_id"], ["domain_controlling.kpi_definitions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["dashboard_id"], ["domain_controlling.dashboard_configs.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("status IN ('open','in_progress','done','cancelled')", name="chk_controlling_actions_status"),
        schema="domain_controlling",
    )
    op.create_index(
        "ix_controlling_actions_status_due",
        "controlling_actions",
        ["tenant_id", "status", "due_date"],
        unique=False,
        schema="domain_controlling",
    )


def downgrade() -> None:
    op.drop_index("ix_controlling_actions_status_due", table_name="controlling_actions", schema="domain_controlling")
    op.drop_table("controlling_actions", schema="domain_controlling")
    op.drop_index("ix_controlling_timeseries_kpi_period", table_name="kpi_timeseries", schema="domain_controlling")
    op.drop_table("kpi_timeseries", schema="domain_controlling")
    op.drop_index("ix_controlling_widgets_dashboard", table_name="dashboard_widgets", schema="domain_controlling")
    op.drop_table("dashboard_widgets", schema="domain_controlling")
    op.drop_index("ix_controlling_dashboards_tenant_active", table_name="dashboard_configs", schema="domain_controlling")
    op.drop_table("dashboard_configs", schema="domain_controlling")
    op.drop_index("ix_controlling_kpi_tenant_active", table_name="kpi_definitions", schema="domain_controlling")
    op.drop_table("kpi_definitions", schema="domain_controlling")
    op.execute(sa.text("DROP SCHEMA IF EXISTS domain_controlling CASCADE"))
