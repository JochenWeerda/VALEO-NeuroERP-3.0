"""add agrar settlements and deductions

Revision ID: agrar_settlements_initial_20260213
Revises: agrar_silo_lots_initial_20260213
Create Date: 2026-02-13 19:45:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "agrar_settlements_initial_20260213"
down_revision = "agrar_silo_lots_initial_20260213"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "agrar_settlements",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("settlement_number", sa.String(length=50), nullable=False),
        sa.Column("contract_id", sa.String(), nullable=True),
        sa.Column("ticket_id", sa.String(), nullable=True),
        sa.Column("supplier_id", sa.String(length=64), nullable=False),
        sa.Column("article_id", sa.String(length=64), nullable=True),
        sa.Column("gross_quantity_kg", sa.DECIMAL(12, 3), nullable=False),
        sa.Column("billing_quantity_kg", sa.DECIMAL(12, 3), nullable=False),
        sa.Column("unit_price_eur_per_ton", sa.DECIMAL(12, 4), nullable=False),
        sa.Column("gross_amount_eur", sa.DECIMAL(14, 2), nullable=False),
        sa.Column("total_deductions_eur", sa.DECIMAL(14, 2), nullable=False, server_default="0"),
        sa.Column("net_amount_eur", sa.DECIMAL(14, 2), nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="EUR"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="draft"),
        sa.Column("posted_journal_ref", sa.String(length=80), nullable=True),
        sa.Column("posted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["contract_id"], ["domain_inventory.agrar_contracts.id"]),
        sa.ForeignKeyConstraint(["ticket_id"], ["domain_inventory.weighing_tickets.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="domain_inventory",
    )
    op.create_index(
        "uq_agrar_settlements_tenant_number",
        "agrar_settlements",
        ["tenant_id", "settlement_number"],
        unique=True,
        schema="domain_inventory",
    )
    op.create_index(
        "ix_agrar_settlements_supplier",
        "agrar_settlements",
        ["supplier_id"],
        unique=False,
        schema="domain_inventory",
    )

    op.create_table(
        "agrar_settlement_deductions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("settlement_id", sa.String(), nullable=False),
        sa.Column("deduction_type", sa.String(length=30), nullable=False),
        sa.Column("mode", sa.String(length=20), nullable=False),
        sa.Column("rate_per_ton_eur", sa.DECIMAL(12, 4), nullable=True),
        sa.Column("fixed_amount_eur", sa.DECIMAL(14, 2), nullable=True),
        sa.Column("basis_quantity_tons", sa.DECIMAL(12, 3), nullable=True),
        sa.Column("amount_eur", sa.DECIMAL(14, 2), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["settlement_id"], ["domain_inventory.agrar_settlements.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="domain_inventory",
    )
    op.create_index(
        "ix_agrar_settlement_deductions_settlement",
        "agrar_settlement_deductions",
        ["settlement_id"],
        unique=False,
        schema="domain_inventory",
    )


def downgrade() -> None:
    op.drop_index("ix_agrar_settlement_deductions_settlement", table_name="agrar_settlement_deductions", schema="domain_inventory")
    op.drop_table("agrar_settlement_deductions", schema="domain_inventory")
    op.drop_index("ix_agrar_settlements_supplier", table_name="agrar_settlements", schema="domain_inventory")
    op.drop_index("uq_agrar_settlements_tenant_number", table_name="agrar_settlements", schema="domain_inventory")
    op.drop_table("agrar_settlements", schema="domain_inventory")
