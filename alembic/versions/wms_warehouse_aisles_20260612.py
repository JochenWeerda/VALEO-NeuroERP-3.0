"""WMS: Lager-Gang (warehouse_aisles) + optionale Zuordnung auf warehouse_bins.

Revision ID: wms_warehouse_aisles_20260612
Revises: log_freight_tariff_storno_20260613

WM-STRUCT-001 / Depth-Plan §3 Schritt 1: Hierarchie Lager → Zone → Gang → Fach.
Bisher hingen Bins direkt an Zonen; Gänge sind jetzt optional zwischen Zone und Fach.
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "wms_warehouse_aisles_20260612"
down_revision: Union[str, Sequence[str], None] = "log_freight_tariff_storno_20260613"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "warehouse_aisles",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "zone_id",
            sa.String(36),
            sa.ForeignKey("domain_inventory.warehouse_zones.id"),
            nullable=False,
        ),
        sa.Column(
            "warehouse_id",
            sa.String(36),
            sa.ForeignKey("domain_inventory.warehouses.id"),
            nullable=False,
        ),
        sa.Column("aisle_code", sa.String(30), nullable=False),
        sa.Column("name", sa.String(100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("zone_id", "aisle_code", name="uq_wa_zone_aisle_code"),
        schema="domain_inventory",
    )
    op.create_index(
        "idx_wa_zone",
        "warehouse_aisles",
        ["zone_id"],
        schema="domain_inventory",
    )
    op.create_index(
        "idx_wa_warehouse",
        "warehouse_aisles",
        ["warehouse_id"],
        schema="domain_inventory",
    )
    op.create_index(
        "idx_wa_tenant",
        "warehouse_aisles",
        ["tenant_id"],
        schema="domain_inventory",
    )

    op.add_column(
        "warehouse_bins",
        sa.Column("aisle_id", sa.String(36), nullable=True),
        schema="domain_inventory",
    )
    op.create_foreign_key(
        "fk_wb_aisle",
        "warehouse_bins",
        "warehouse_aisles",
        ["aisle_id"],
        ["id"],
        source_schema="domain_inventory",
        referent_schema="domain_inventory",
    )
    op.create_index(
        "idx_wb_aisle",
        "warehouse_bins",
        ["aisle_id"],
        schema="domain_inventory",
    )


def downgrade() -> None:
    op.drop_constraint("fk_wb_aisle", "warehouse_bins", schema="domain_inventory", type_="foreignkey")
    op.drop_index("idx_wb_aisle", table_name="warehouse_bins", schema="domain_inventory")
    op.drop_column("warehouse_bins", "aisle_id", schema="domain_inventory")
    op.drop_table("warehouse_aisles", schema="domain_inventory")
