"""Agrar: Siloanlagen, Silozellen, Materialfluss-Knoten/Kanten (domain_inventory).

Revision ID: agri_silo_material_flow_20260612
Revises: wms_warehouse_aisles_20260612

WM-AGRI-SILO-001 — additive Erweiterung zum generischen WMS (Lager/Zone/Gang/Fach).
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "agri_silo_material_flow_20260612"
down_revision: Union[str, Sequence[str], None] = "wms_warehouse_aisles_20260612"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "silo_systems",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "warehouse_id",
            sa.String(36),
            sa.ForeignKey("domain_inventory.warehouses.id"),
            nullable=False,
        ),
        sa.Column("system_code", sa.String(40), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("warehouse_id", "system_code", name="uq_silo_sys_wh_code"),
        schema="domain_inventory",
    )
    op.create_index("idx_silo_sys_wh", "silo_systems", ["warehouse_id"], schema="domain_inventory")
    op.create_index("idx_silo_sys_tenant", "silo_systems", ["tenant_id"], schema="domain_inventory")

    op.create_table(
        "silo_cells",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "silo_system_id",
            sa.String(36),
            sa.ForeignKey("domain_inventory.silo_systems.id"),
            nullable=False,
        ),
        sa.Column(
            "warehouse_id",
            sa.String(36),
            sa.ForeignKey("domain_inventory.warehouses.id"),
            nullable=False,
        ),
        sa.Column(
            "zone_id",
            sa.String(36),
            sa.ForeignKey("domain_inventory.warehouse_zones.id"),
            nullable=True,
        ),
        sa.Column(
            "aisle_id",
            sa.String(36),
            sa.ForeignKey("domain_inventory.warehouse_aisles.id"),
            nullable=True,
        ),
        sa.Column(
            "bin_id",
            sa.String(36),
            sa.ForeignKey("domain_inventory.warehouse_bins.id"),
            nullable=True,
        ),
        sa.Column("cell_code", sa.String(40), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("capacity_kg", sa.DECIMAL(14, 4), nullable=False, server_default="0"),
        sa.Column("current_material_id", sa.String(64), nullable=True),
        sa.Column("current_lot_id", sa.String(64), nullable=True),
        sa.Column(
            "qs_status",
            sa.String(32),
            nullable=False,
            server_default="frei",
        ),
        sa.Column("contamination_risk_class", sa.String(32), nullable=True),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("silo_system_id", "cell_code", name="uq_silo_cell_sys_code"),
        sa.CheckConstraint(
            "qs_status IN ('frei','gesperrt','in_pruefung','reinigung','reserviert')",
            name="ck_silo_cells_qs_status",
        ),
        schema="domain_inventory",
    )
    op.create_index("idx_silo_cells_sys", "silo_cells", ["silo_system_id"], schema="domain_inventory")
    op.create_index("idx_silo_cells_wh", "silo_cells", ["warehouse_id"], schema="domain_inventory")
    op.create_index("idx_silo_cells_tenant", "silo_cells", ["tenant_id"], schema="domain_inventory")

    op.create_table(
        "material_flow_nodes",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "warehouse_id",
            sa.String(36),
            sa.ForeignKey("domain_inventory.warehouses.id"),
            nullable=False,
        ),
        sa.Column("node_type", sa.String(40), nullable=False),
        sa.Column("ref_type", sa.String(40), nullable=True),
        sa.Column("ref_id", sa.String(64), nullable=True),
        sa.Column("code", sa.String(64), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("status", sa.String(32), nullable=False, server_default="active"),
        sa.Column("geo_lat", sa.DECIMAL(10, 7), nullable=True),
        sa.Column("geo_lng", sa.DECIMAL(10, 7), nullable=True),
        sa.Column("layout_x", sa.DECIMAL(12, 3), nullable=True),
        sa.Column("layout_y", sa.DECIMAL(12, 3), nullable=True),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("warehouse_id", "code", name="uq_mfn_wh_code"),
        sa.CheckConstraint(
            "node_type IN ('intake','scale','elevator','conveyor','valve','diverter','silo_cell','mixer','loader','mobile_unit')",
            name="ck_mfn_node_type",
        ),
        sa.CheckConstraint(
            "status IN ('active','blocked','maintenance','cleaning')",
            name="ck_mfn_status",
        ),
        schema="domain_inventory",
    )
    op.create_index("idx_mfn_wh", "material_flow_nodes", ["warehouse_id"], schema="domain_inventory")
    op.create_index("idx_mfn_tenant", "material_flow_nodes", ["tenant_id"], schema="domain_inventory")

    op.create_table(
        "material_flow_edges",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "warehouse_id",
            sa.String(36),
            sa.ForeignKey("domain_inventory.warehouses.id"),
            nullable=False,
        ),
        sa.Column(
            "from_node_id",
            sa.String(36),
            sa.ForeignKey("domain_inventory.material_flow_nodes.id"),
            nullable=False,
        ),
        sa.Column(
            "to_node_id",
            sa.String(36),
            sa.ForeignKey("domain_inventory.material_flow_nodes.id"),
            nullable=False,
        ),
        sa.Column("conveyor_type", sa.String(64), nullable=False, server_default="generic"),
        sa.Column("status", sa.String(32), nullable=False, server_default="open"),
        sa.Column(
            "contamination_guard_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.true(),
        ),
        sa.Column("flush_required", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("max_capacity_kg_h", sa.DECIMAL(14, 4), nullable=True),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "status IN ('open','blocked','maintenance','cleaning')",
            name="ck_mfe_status",
        ),
        schema="domain_inventory",
    )
    op.create_index("idx_mfe_wh", "material_flow_edges", ["warehouse_id"], schema="domain_inventory")
    op.create_index("idx_mfe_from", "material_flow_edges", ["from_node_id"], schema="domain_inventory")
    op.create_index("idx_mfe_to", "material_flow_edges", ["to_node_id"], schema="domain_inventory")
    op.create_index("idx_mfe_tenant", "material_flow_edges", ["tenant_id"], schema="domain_inventory")


def downgrade() -> None:
    op.drop_table("material_flow_edges", schema="domain_inventory")
    op.drop_table("material_flow_nodes", schema="domain_inventory")
    op.drop_table("silo_cells", schema="domain_inventory")
    op.drop_table("silo_systems", schema="domain_inventory")
