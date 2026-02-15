"""add consignment storage fee run and charge tables

Revision ID: consignment_storage_fee_engine_20260215
Revises: inventory_stock_movements_consignment_ownership_20260215
Create Date: 2026-02-15
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "consignment_storage_fee_engine_20260215"
down_revision = "inventory_stock_movements_consignment_ownership_20260215"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "consignment_storage_fee_runs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column("period_month", sa.Date(), nullable=False),
        sa.Column("run_type", sa.String(length=16), nullable=False, server_default=sa.text("'post'")),
        sa.Column("status", sa.String(length=20), nullable=False, server_default=sa.text("'running'")),
        sa.Column("idempotency_key", sa.String(length=120), nullable=True),
        sa.Column("posting_date", sa.Date(), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default=sa.text("'EUR'")),
        sa.Column("total_items", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("total_amount", sa.Numeric(14, 2), nullable=False, server_default=sa.text("0")),
        sa.Column("journal_entry_id", sa.String(length=64), nullable=True),
        sa.Column("created_by", sa.String(length=100), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("run_type IN ('preview', 'post')", name="chk_consignment_storage_fee_runs_run_type"),
        sa.CheckConstraint("status IN ('running', 'posted', 'failed', 'preview')", name="chk_consignment_storage_fee_runs_status"),
        sa.UniqueConstraint("tenant_id", "period_month", "run_type", name="uq_consignment_storage_fee_runs_tenant_period_type"),
        schema="domain_inventory",
    )
    op.create_index(
        "ix_consignment_storage_fee_runs_tenant_period",
        "consignment_storage_fee_runs",
        ["tenant_id", "period_month"],
        unique=False,
        schema="domain_inventory",
    )

    op.create_table(
        "consignment_storage_fee_charges",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("run_id", sa.String(length=36), nullable=False),
        sa.Column("tenant_id", sa.String(length=64), nullable=False),
        sa.Column("owner_partner_id", sa.String(length=64), nullable=False),
        sa.Column("article_id", sa.String(length=64), nullable=False),
        sa.Column("warehouse_id", sa.String(length=64), nullable=False),
        sa.Column("charge", sa.String(length=64), nullable=True),
        sa.Column("basis_quantity", sa.Numeric(14, 3), nullable=False),
        sa.Column("monthly_rate", sa.Numeric(12, 4), nullable=False),
        sa.Column("amount", sa.Numeric(14, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default=sa.text("'EUR'")),
        sa.Column("calculation_details", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["run_id"],
            ["domain_inventory.consignment_storage_fee_runs.id"],
            ondelete="CASCADE",
        ),
        sa.CheckConstraint("basis_quantity >= 0", name="chk_consignment_storage_fee_charges_basis_qty_non_negative"),
        sa.CheckConstraint("monthly_rate >= 0", name="chk_consignment_storage_fee_charges_rate_non_negative"),
        sa.CheckConstraint("amount >= 0", name="chk_consignment_storage_fee_charges_amount_non_negative"),
        schema="domain_inventory",
    )
    op.create_index(
        "ix_consignment_storage_fee_charges_run_id",
        "consignment_storage_fee_charges",
        ["run_id"],
        unique=False,
        schema="domain_inventory",
    )
    op.create_index(
        "ix_consignment_storage_fee_charges_owner_partner_id",
        "consignment_storage_fee_charges",
        ["owner_partner_id"],
        unique=False,
        schema="domain_inventory",
    )
    op.create_index(
        "ix_consignment_storage_fee_charges_tenant_owner_article",
        "consignment_storage_fee_charges",
        ["tenant_id", "owner_partner_id", "article_id"],
        unique=False,
        schema="domain_inventory",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_consignment_storage_fee_charges_tenant_owner_article",
        table_name="consignment_storage_fee_charges",
        schema="domain_inventory",
    )
    op.drop_index(
        "ix_consignment_storage_fee_charges_owner_partner_id",
        table_name="consignment_storage_fee_charges",
        schema="domain_inventory",
    )
    op.drop_index(
        "ix_consignment_storage_fee_charges_run_id",
        table_name="consignment_storage_fee_charges",
        schema="domain_inventory",
    )
    op.drop_table("consignment_storage_fee_charges", schema="domain_inventory")

    op.drop_index(
        "ix_consignment_storage_fee_runs_tenant_period",
        table_name="consignment_storage_fee_runs",
        schema="domain_inventory",
    )
    op.drop_table("consignment_storage_fee_runs", schema="domain_inventory")
