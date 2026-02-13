"""add agrar weighing ticket fields

Revision ID: agrar_wiegeschein_fields_20260213
Revises: merge_l3c_and_procurement_indexes_20260213
Create Date: 2026-02-13 18:20:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "agrar_wiegeschein_fields_20260213"
down_revision = "merge_l3c_and_procurement_indexes_20260213"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "weighing_measurements",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("ticket_id", sa.String(), nullable=False),
        sa.Column("metric_key", sa.String(length=50), nullable=False),
        sa.Column("metric_value", sa.DECIMAL(10, 3), nullable=False),
        sa.Column("unit", sa.String(length=20), nullable=True),
        sa.Column("measured_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("tenant_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["ticket_id"], ["domain_inventory.weighing_tickets.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["domain_shared.tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        schema="domain_inventory",
    )
    op.create_index(
        "ix_weighing_measurements_ticket",
        "weighing_measurements",
        ["ticket_id"],
        unique=False,
        schema="domain_inventory",
    )
    op.add_column(
        "weighing_tickets",
        sa.Column("first_weighing_at", sa.DateTime(timezone=True), nullable=True),
        schema="domain_inventory",
    )
    op.add_column(
        "weighing_tickets",
        sa.Column("second_weighing_at", sa.DateTime(timezone=True), nullable=True),
        schema="domain_inventory",
    )
    op.add_column(
        "weighing_tickets",
        sa.Column("moisture_pct", sa.DECIMAL(5, 2), nullable=True),
        schema="domain_inventory",
    )
    op.add_column(
        "weighing_tickets",
        sa.Column("protein_pct", sa.DECIMAL(5, 2), nullable=True),
        schema="domain_inventory",
    )
    op.add_column(
        "weighing_tickets",
        sa.Column("impurities_pct", sa.DECIMAL(5, 2), nullable=True),
        schema="domain_inventory",
    )
    op.add_column(
        "weighing_tickets",
        sa.Column("hl_weight", sa.DECIMAL(6, 2), nullable=True),
        schema="domain_inventory",
    )
    op.add_column(
        "weighing_tickets",
        sa.Column("billing_weight", sa.DECIMAL(12, 3), nullable=True),
        schema="domain_inventory",
    )
    op.add_column(
        "weighing_tickets",
        sa.Column("quality_data", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        schema="domain_inventory",
    )


def downgrade() -> None:
    op.drop_column("weighing_tickets", "quality_data", schema="domain_inventory")
    op.drop_column("weighing_tickets", "billing_weight", schema="domain_inventory")
    op.drop_column("weighing_tickets", "hl_weight", schema="domain_inventory")
    op.drop_column("weighing_tickets", "impurities_pct", schema="domain_inventory")
    op.drop_column("weighing_tickets", "protein_pct", schema="domain_inventory")
    op.drop_column("weighing_tickets", "moisture_pct", schema="domain_inventory")
    op.drop_column("weighing_tickets", "second_weighing_at", schema="domain_inventory")
    op.drop_column("weighing_tickets", "first_weighing_at", schema="domain_inventory")
    op.drop_index("ix_weighing_measurements_ticket", table_name="weighing_measurements", schema="domain_inventory")
    op.drop_table("weighing_measurements", schema="domain_inventory")
