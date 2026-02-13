"""link weighing tickets to agrar contracts

Revision ID: agrar_wiegeschein_contract_link_20260213
Revises: agrar_contracts_initial_20260213
Create Date: 2026-02-13 18:50:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "agrar_wiegeschein_contract_link_20260213"
down_revision = "agrar_contracts_initial_20260213"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "weighing_tickets",
        sa.Column("contract_id", sa.String(), nullable=True),
        schema="domain_inventory",
    )
    op.add_column(
        "weighing_tickets",
        sa.Column("allocated_quantity_kg", sa.DECIMAL(12, 3), nullable=True),
        schema="domain_inventory",
    )
    op.add_column(
        "weighing_tickets",
        sa.Column("allocation_status", sa.String(length=20), nullable=False, server_default="unallocated"),
        schema="domain_inventory",
    )
    op.create_foreign_key(
        "fk_weighing_tickets_contract_id",
        "weighing_tickets",
        "agrar_contracts",
        ["contract_id"],
        ["id"],
        source_schema="domain_inventory",
        referent_schema="domain_inventory",
    )
    op.create_index(
        "ix_weighing_tickets_contract",
        "weighing_tickets",
        ["contract_id"],
        unique=False,
        schema="domain_inventory",
    )


def downgrade() -> None:
    op.drop_index("ix_weighing_tickets_contract", table_name="weighing_tickets", schema="domain_inventory")
    op.drop_constraint(
        "fk_weighing_tickets_contract_id",
        "weighing_tickets",
        schema="domain_inventory",
        type_="foreignkey",
    )
    op.drop_column("weighing_tickets", "allocation_status", schema="domain_inventory")
    op.drop_column("weighing_tickets", "allocated_quantity_kg", schema="domain_inventory")
    op.drop_column("weighing_tickets", "contract_id", schema="domain_inventory")

