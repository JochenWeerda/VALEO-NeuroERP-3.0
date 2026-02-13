"""add agrar silo lots and quality snapshots

Revision ID: agrar_silo_lots_initial_20260213
Revises: agrar_wiegeschein_contract_link_20260213
Create Date: 2026-02-13 19:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "agrar_silo_lots_initial_20260213"
down_revision = "agrar_wiegeschein_contract_link_20260213"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "silos",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("silo_number", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=True),
        sa.Column("article_id", sa.String(length=64), nullable=True),
        sa.Column("capacity_tons", sa.DECIMAL(12, 3), nullable=False),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="domain_inventory",
    )
    op.create_index("uq_silos_tenant_number", "silos", ["tenant_id", "silo_number"], unique=True, schema="domain_inventory")

    op.create_table(
        "silo_lots",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("silo_id", sa.String(), nullable=False),
        sa.Column("virtual_lot_number", sa.String(length=64), nullable=False),
        sa.Column("source_ticket_id", sa.String(), nullable=True),
        sa.Column("source_partner_id", sa.String(length=64), nullable=True),
        sa.Column("article_id", sa.String(length=64), nullable=True),
        sa.Column("quantity_tons", sa.DECIMAL(12, 3), nullable=False),
        sa.Column("moisture_pct", sa.DECIMAL(5, 2), nullable=True),
        sa.Column("protein_pct", sa.DECIMAL(5, 2), nullable=True),
        sa.Column("impurities_pct", sa.DECIMAL(5, 2), nullable=True),
        sa.Column("hl_weight", sa.DECIMAL(6, 2), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["silo_id"], ["domain_inventory.silos.id"]),
        sa.ForeignKeyConstraint(["source_ticket_id"], ["domain_inventory.weighing_tickets.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="domain_inventory",
    )
    op.create_index("ix_silo_lots_silo", "silo_lots", ["silo_id"], unique=False, schema="domain_inventory")

    op.create_table(
        "silo_lot_movements",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("silo_lot_id", sa.String(), nullable=False),
        sa.Column("movement_type", sa.String(length=20), nullable=False),
        sa.Column("quantity_tons", sa.DECIMAL(12, 3), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["silo_lot_id"], ["domain_inventory.silo_lots.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="domain_inventory",
    )

    op.create_table(
        "silo_quality_snapshots",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("silo_id", sa.String(), nullable=False),
        sa.Column("total_quantity_tons", sa.DECIMAL(12, 3), nullable=False),
        sa.Column("moisture_avg_pct", sa.DECIMAL(5, 2), nullable=True),
        sa.Column("protein_avg_pct", sa.DECIMAL(5, 2), nullable=True),
        sa.Column("impurities_avg_pct", sa.DECIMAL(5, 2), nullable=True),
        sa.Column("hl_weight_avg", sa.DECIMAL(6, 2), nullable=True),
        sa.Column("lot_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["silo_id"], ["domain_inventory.silos.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="domain_inventory",
    )
    op.create_index("ix_silo_quality_snapshots_silo", "silo_quality_snapshots", ["silo_id"], unique=False, schema="domain_inventory")


def downgrade() -> None:
    op.drop_index("ix_silo_quality_snapshots_silo", table_name="silo_quality_snapshots", schema="domain_inventory")
    op.drop_table("silo_quality_snapshots", schema="domain_inventory")
    op.drop_table("silo_lot_movements", schema="domain_inventory")
    op.drop_index("ix_silo_lots_silo", table_name="silo_lots", schema="domain_inventory")
    op.drop_table("silo_lots", schema="domain_inventory")
    op.drop_index("uq_silos_tenant_number", table_name="silos", schema="domain_inventory")
    op.drop_table("silos", schema="domain_inventory")
