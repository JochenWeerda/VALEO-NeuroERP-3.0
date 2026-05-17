"""WMS warehouse zones, bins, bin_stock, pick_lists and pick_list_lines

Revision ID: warehouse_wms_structure_20260517
Revises: merge_driver_time_hrm_gates_20260517
Create Date: 2026-05-17
"""
from alembic import op
import sqlalchemy as sa

revision = "warehouse_wms_structure_20260517"
down_revision = "merge_driver_time_hrm_gates_20260517"
branch_labels = None
depends_on = None


def upgrade():
    # --- warehouse_zones ---
    op.create_table(
        "warehouse_zones",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "warehouse_id",
            sa.String(36),
            sa.ForeignKey("domain_inventory.warehouses.id"),
            nullable=False,
        ),
        sa.Column("zone_code", sa.String(20), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("zone_type", sa.String(20), nullable=False, server_default="standard"),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column("is_active", sa.Boolean, server_default=sa.true()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("warehouse_id", "zone_code", name="uq_wz_warehouse_zone_code"),
        schema="domain_inventory",
    )
    op.create_index(
        "idx_wz_warehouse",
        "warehouse_zones",
        ["warehouse_id"],
        schema="domain_inventory",
    )
    op.create_index(
        "idx_wz_tenant",
        "warehouse_zones",
        ["tenant_id"],
        schema="domain_inventory",
    )

    # --- warehouse_bins ---
    op.create_table(
        "warehouse_bins",
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
        sa.Column("bin_code", sa.String(30), nullable=False),
        sa.Column("bin_type", sa.String(20), server_default="standard"),
        sa.Column("capacity_kg", sa.DECIMAL(12, 3), nullable=True),
        sa.Column("is_active", sa.Boolean, server_default=sa.true()),
        sa.Column("is_blocked", sa.Boolean, server_default=sa.false()),
        sa.Column("block_reason", sa.String(200), nullable=True),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("warehouse_id", "bin_code", name="uq_wb_warehouse_bin_code"),
        schema="domain_inventory",
    )
    op.create_index(
        "idx_wb_zone",
        "warehouse_bins",
        ["zone_id"],
        schema="domain_inventory",
    )
    op.create_index(
        "idx_wb_warehouse",
        "warehouse_bins",
        ["warehouse_id"],
        schema="domain_inventory",
    )
    op.create_index(
        "idx_wb_tenant",
        "warehouse_bins",
        ["tenant_id"],
        schema="domain_inventory",
    )

    # --- bin_stock ---
    op.create_table(
        "bin_stock",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column(
            "bin_id",
            sa.String(36),
            sa.ForeignKey("domain_inventory.warehouse_bins.id"),
            nullable=False,
        ),
        sa.Column("article_id", sa.String(64), nullable=False),
        sa.Column("batch_number", sa.String(64), nullable=True),
        sa.Column("best_before_date", sa.Date, nullable=True),
        sa.Column("quantity_kg", sa.DECIMAL(14, 4), nullable=False, server_default="0"),
        sa.Column("unit_cost", sa.DECIMAL(12, 4), nullable=True),
        sa.Column("last_movement_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("tenant_id", sa.String(64), nullable=False),
        schema="domain_inventory",
    )
    # No DB-level UNIQUE on (bin_id, article_id, batch_number) because batch_number is nullable
    op.create_index(
        "idx_bs_bin",
        "bin_stock",
        ["bin_id"],
        schema="domain_inventory",
    )
    op.create_index(
        "idx_bs_article_tenant",
        "bin_stock",
        ["tenant_id", "article_id"],
        schema="domain_inventory",
    )
    op.create_index(
        "idx_bs_best_before",
        "bin_stock",
        ["best_before_date"],
        schema="domain_inventory",
    )

    # --- pick_lists: add WMS columns if table already exists, else create ---
    # The table was created by l3c migration; we extend it with WMS columns.
    op.add_column(
        "pick_lists",
        sa.Column("warehouse_id", sa.String(36), nullable=True),
        schema="domain_inventory",
    )
    op.add_column(
        "pick_lists",
        sa.Column("source_doc_ref", sa.String(128), nullable=True),
        schema="domain_inventory",
    )
    op.add_column(
        "pick_lists",
        sa.Column("source_doc_type", sa.String(32), nullable=True),
        schema="domain_inventory",
    )
    op.add_column(
        "pick_lists",
        sa.Column("strategy", sa.String(20), server_default="FEFO", nullable=True),
        schema="domain_inventory",
    )
    op.add_column(
        "pick_lists",
        sa.Column("created_by", sa.String(128), nullable=True),
        schema="domain_inventory",
    )
    op.add_column(
        "pick_lists",
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        schema="domain_inventory",
    )
    op.create_index(
        "idx_pl_tenant_status",
        "pick_lists",
        ["tenant_id", "status"],
        schema="domain_inventory",
    )
    op.create_index(
        "idx_pl_source",
        "pick_lists",
        ["source_doc_ref"],
        schema="domain_inventory",
    )

    # --- pick_list_lines: add WMS columns ---
    op.add_column(
        "pick_list_lines",
        sa.Column(
            "bin_id",
            sa.String(36),
            sa.ForeignKey("domain_inventory.warehouse_bins.id"),
            nullable=True,
        ),
        schema="domain_inventory",
    )
    op.add_column(
        "pick_list_lines",
        sa.Column("best_before_date", sa.Date, nullable=True),
        schema="domain_inventory",
    )
    op.add_column(
        "pick_list_lines",
        sa.Column(
            "quantity_required",
            sa.DECIMAL(14, 4),
            nullable=True,
        ),
        schema="domain_inventory",
    )
    op.add_column(
        "pick_list_lines",
        sa.Column(
            "quantity_picked",
            sa.DECIMAL(14, 4),
            server_default="0",
            nullable=True,
        ),
        schema="domain_inventory",
    )
    op.add_column(
        "pick_list_lines",
        sa.Column("unit", sa.String(20), server_default="kg", nullable=True),
        schema="domain_inventory",
    )
    op.add_column(
        "pick_list_lines",
        sa.Column("sort_order", sa.Integer, server_default="0", nullable=True),
        schema="domain_inventory",
    )
    op.create_index(
        "idx_pll_pick_list",
        "pick_list_lines",
        ["pick_list_id"],
        schema="domain_inventory",
    )
    op.create_index(
        "idx_pll_bin",
        "pick_list_lines",
        ["bin_id"],
        schema="domain_inventory",
    )

    # --- inventory_stock_movements: add bin_id column ---
    op.add_column(
        "inventory_stock_movements",
        sa.Column(
            "bin_id",
            sa.String(36),
            sa.ForeignKey("domain_inventory.warehouse_bins.id"),
            nullable=True,
        ),
        schema="domain_inventory",
    )


def downgrade():
    op.drop_column("inventory_stock_movements", "bin_id", schema="domain_inventory")

    op.drop_index("idx_pll_bin", table_name="pick_list_lines", schema="domain_inventory")
    op.drop_index("idx_pll_pick_list", table_name="pick_list_lines", schema="domain_inventory")
    op.drop_column("pick_list_lines", "sort_order", schema="domain_inventory")
    op.drop_column("pick_list_lines", "unit", schema="domain_inventory")
    op.drop_column("pick_list_lines", "quantity_picked", schema="domain_inventory")
    op.drop_column("pick_list_lines", "quantity_required", schema="domain_inventory")
    op.drop_column("pick_list_lines", "best_before_date", schema="domain_inventory")
    op.drop_column("pick_list_lines", "bin_id", schema="domain_inventory")

    op.drop_index("idx_pl_source", table_name="pick_lists", schema="domain_inventory")
    op.drop_index("idx_pl_tenant_status", table_name="pick_lists", schema="domain_inventory")
    op.drop_column("pick_lists", "completed_at", schema="domain_inventory")
    op.drop_column("pick_lists", "created_by", schema="domain_inventory")
    op.drop_column("pick_lists", "strategy", schema="domain_inventory")
    op.drop_column("pick_lists", "source_doc_type", schema="domain_inventory")
    op.drop_column("pick_lists", "source_doc_ref", schema="domain_inventory")
    op.drop_column("pick_lists", "warehouse_id", schema="domain_inventory")

    op.drop_index("idx_bs_best_before", table_name="bin_stock", schema="domain_inventory")
    op.drop_index("idx_bs_article_tenant", table_name="bin_stock", schema="domain_inventory")
    op.drop_index("idx_bs_bin", table_name="bin_stock", schema="domain_inventory")
    op.drop_table("bin_stock", schema="domain_inventory")

    op.drop_index("idx_wb_tenant", table_name="warehouse_bins", schema="domain_inventory")
    op.drop_index("idx_wb_warehouse", table_name="warehouse_bins", schema="domain_inventory")
    op.drop_index("idx_wb_zone", table_name="warehouse_bins", schema="domain_inventory")
    op.drop_table("warehouse_bins", schema="domain_inventory")

    op.drop_index("idx_wz_tenant", table_name="warehouse_zones", schema="domain_inventory")
    op.drop_index("idx_wz_warehouse", table_name="warehouse_zones", schema="domain_inventory")
    op.drop_table("warehouse_zones", schema="domain_inventory")
