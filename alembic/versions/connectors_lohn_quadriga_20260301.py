"""Connectors: Lohn-Import-Läufe und Quadriga/Connector-Konfiguration (domain_erp)

Revision ID: connectors_lohn_quadriga_20260301
Revises: gobd_aufbewahrungsfristen_20260301
Create Date: 2026-03-01

- domain_erp.lohn_import_runs: Lohn-Import-Läufe (LEXWARE/Connector)
- domain_erp.connector_configs: Konfiguration pro Connector/Mandant (z. B. Quadriga)
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "connectors_lohn_quadriga_20260301"
down_revision = "gobd_aufbewahrungsfristen_20260301"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "lohn_import_runs",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("period", sa.String(7), nullable=False),
        sa.Column("source", sa.String(50), nullable=False, server_default="LEXWARE"),
        sa.Column("status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("journal_entry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_debit", sa.Numeric(18, 2), nullable=True),
        sa.Column("total_credit", sa.Numeric(18, 2), nullable=True),
        sa.Column("message", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("created_by", sa.String(100), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        schema="domain_erp",
    )
    op.create_index(
        "ix_lohn_import_runs_tenant_period",
        "lohn_import_runs",
        ["tenant_id", "period"],
        unique=False,
        schema="domain_erp",
    )

    op.create_table(
        "connector_configs",
        sa.Column("id", sa.String(36), nullable=False),
        sa.Column("tenant_id", sa.String(36), nullable=False),
        sa.Column("connector_code", sa.String(50), nullable=False),
        sa.Column("name", sa.String(120), nullable=True),
        sa.Column("config_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "connector_code", name="uq_connector_config_tenant_code"),
        schema="domain_erp",
    )
    op.create_index(
        "ix_connector_configs_tenant_code",
        "connector_configs",
        ["tenant_id", "connector_code"],
        unique=True,
        schema="domain_erp",
    )


def downgrade() -> None:
    op.drop_index("ix_connector_configs_tenant_code", table_name="connector_configs", schema="domain_erp")
    op.drop_table("connector_configs", schema="domain_erp")
    op.drop_index("ix_lohn_import_runs_tenant_period", table_name="lohn_import_runs", schema="domain_erp")
    op.drop_table("lohn_import_runs", schema="domain_erp")
