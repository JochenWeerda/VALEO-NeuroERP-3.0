"""add agrar contracts and allocations

Revision ID: agrar_contracts_initial_20260213
Revises: agrar_wiegeschein_fields_20260213
Create Date: 2026-02-13 18:35:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "agrar_contracts_initial_20260213"
down_revision = "agrar_wiegeschein_fields_20260213"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "agrar_contracts",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("contract_number", sa.String(length=50), nullable=False),
        sa.Column("contract_type", sa.String(length=10), nullable=False),
        sa.Column("harvest_year", sa.Integer(), nullable=False),
        sa.Column("partner_id", sa.String(length=64), nullable=False),
        sa.Column("article_id", sa.String(length=64), nullable=False),
        sa.Column("pricing_model", sa.String(length=10), nullable=False),
        sa.Column("pool_group_id", sa.String(length=64), nullable=True),
        sa.Column("fixed_price", sa.DECIMAL(12, 2), nullable=True),
        sa.Column("currency", sa.String(length=3), nullable=False, server_default="EUR"),
        sa.Column("total_quantity_kg", sa.DECIMAL(12, 3), nullable=False),
        sa.Column("remaining_quantity_kg", sa.DECIMAL(12, 3), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="open"),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("valid_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="domain_inventory",
    )
    op.create_index(
        "uq_agrar_contracts_contract_number_tenant",
        "agrar_contracts",
        ["tenant_id", "contract_number"],
        unique=True,
        schema="domain_inventory",
    )
    op.create_index(
        "ix_agrar_contracts_tenant_status",
        "agrar_contracts",
        ["tenant_id", "status"],
        unique=False,
        schema="domain_inventory",
    )
    op.create_index(
        "ix_agrar_contracts_tenant_article",
        "agrar_contracts",
        ["tenant_id", "article_id"],
        unique=False,
        schema="domain_inventory",
    )

    op.create_table(
        "agrar_contract_allocations",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("contract_id", sa.String(), nullable=False),
        sa.Column("ticket_id", sa.String(), nullable=True),
        sa.Column("allocation_quantity_kg", sa.DECIMAL(12, 3), nullable=False),
        sa.Column("allocated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["contract_id"], ["domain_inventory.agrar_contracts.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"]),
        sa.ForeignKeyConstraint(["ticket_id"], ["domain_inventory.weighing_tickets.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="domain_inventory",
    )
    op.create_index(
        "ix_agrar_contract_allocations_contract",
        "agrar_contract_allocations",
        ["contract_id"],
        unique=False,
        schema="domain_inventory",
    )


def downgrade() -> None:
    op.drop_index(
        "ix_agrar_contract_allocations_contract",
        table_name="agrar_contract_allocations",
        schema="domain_inventory",
    )
    op.drop_table("agrar_contract_allocations", schema="domain_inventory")
    op.drop_index("ix_agrar_contracts_tenant_article", table_name="agrar_contracts", schema="domain_inventory")
    op.drop_index("ix_agrar_contracts_tenant_status", table_name="agrar_contracts", schema="domain_inventory")
    op.drop_index("uq_agrar_contracts_contract_number_tenant", table_name="agrar_contracts", schema="domain_inventory")
    op.drop_table("agrar_contracts", schema="domain_inventory")

