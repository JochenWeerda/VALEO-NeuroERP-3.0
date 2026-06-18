"""SQLAlchemy models for WMS (Warehouse Management System).

Covers warehouse zones, aisles, bins, bin-level stock, WMS-extended pick lists,
and agrar-specific silo / material-flow tables (WM-AGRI-SILO-001).
All tables live in the ``domain_inventory`` schema.
"""

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    DECIMAL,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)

from app.core.database import Base
from app.core.uuid7 import uuid7


class WarehouseZone(Base):
    """A named zone within a warehouse (e.g. kuehl, tiefkuehl, silo)."""

    __tablename__ = "warehouse_zones"
    __table_args__ = (
        UniqueConstraint("warehouse_id", "zone_code", name="uq_wz_warehouse_zone_code"),
        Index("idx_wz_warehouse", "warehouse_id"),
        Index("idx_wz_tenant", "tenant_id"),
        {"schema": "domain_inventory", "extend_existing": True},
    )

    id = Column(String(36), primary_key=True, default=uuid7)
    warehouse_id = Column(
        String(36),
        ForeignKey("domain_inventory.warehouses.id"),
        nullable=False,
    )
    zone_code = Column(String(20), nullable=False)
    name = Column(String(100), nullable=False)
    # standard / kuehl / tiefkuehl / gefahrgut / silo / quarantaene
    zone_type = Column(String(20), nullable=False, server_default="standard")
    description = Column(Text, nullable=True)
    tenant_id = Column(String(64), nullable=False)
    is_active = Column(Boolean, server_default="true")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class WarehouseAisle(Base):
    """Gang/Reihe innerhalb einer Zone (optional zwischen Zone und Lagerplatz)."""

    __tablename__ = "warehouse_aisles"
    __table_args__ = (
        UniqueConstraint("zone_id", "aisle_code", name="uq_wa_zone_aisle_code"),
        Index("idx_wa_zone", "zone_id"),
        Index("idx_wa_warehouse", "warehouse_id"),
        Index("idx_wa_tenant", "tenant_id"),
        {"schema": "domain_inventory", "extend_existing": True},
    )

    id = Column(String(36), primary_key=True, default=uuid7)
    zone_id = Column(
        String(36),
        ForeignKey("domain_inventory.warehouse_zones.id"),
        nullable=False,
    )
    warehouse_id = Column(
        String(36),
        ForeignKey("domain_inventory.warehouses.id"),
        nullable=False,
    )
    aisle_code = Column(String(30), nullable=False)
    name = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    tenant_id = Column(String(64), nullable=False)
    is_active = Column(Boolean, server_default="true")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class WarehouseBin(Base):
    """An individual storage location (bin/slot) within a warehouse zone."""

    __tablename__ = "warehouse_bins"
    __table_args__ = (
        UniqueConstraint("warehouse_id", "bin_code", name="uq_wb_warehouse_bin_code"),
        Index("idx_wb_zone", "zone_id"),
        Index("idx_wb_aisle", "aisle_id"),
        Index("idx_wb_warehouse", "warehouse_id"),
        Index("idx_wb_tenant", "tenant_id"),
        {"schema": "domain_inventory", "extend_existing": True},
    )

    id = Column(String(36), primary_key=True, default=uuid7)
    zone_id = Column(
        String(36),
        ForeignKey("domain_inventory.warehouse_zones.id"),
        nullable=False,
    )
    # Denormalised for query performance — avoids join through zone on every lookup.
    warehouse_id = Column(
        String(36),
        ForeignKey("domain_inventory.warehouses.id"),
        nullable=False,
    )
    aisle_id = Column(
        String(36),
        ForeignKey("domain_inventory.warehouse_aisles.id"),
        nullable=True,
    )
    bin_code = Column(String(30), nullable=False)
    # standard / silo / regal / boden / extern
    bin_type = Column(String(20), server_default="standard")
    capacity_kg = Column(DECIMAL(12, 3), nullable=True)
    is_active = Column(Boolean, server_default="true")
    is_blocked = Column(Boolean, server_default="false")
    block_reason = Column(String(200), nullable=True)
    tenant_id = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class BinStock(Base):
    """Current stock level per bin / article / batch combination.

    Note: No DB-level UNIQUE constraint on (bin_id, article_id, batch_number)
    because batch_number is nullable and databases handle NULL inequality
    differently.  A partial unique index can be added later if needed.
    """

    __tablename__ = "bin_stock"
    __table_args__ = (
        Index("idx_bs_bin", "bin_id"),
        Index("idx_bs_article_tenant", "tenant_id", "article_id"),
        Index("idx_bs_best_before", "best_before_date"),
        {"schema": "domain_inventory", "extend_existing": True},
    )

    id = Column(String(36), primary_key=True, default=uuid7)
    bin_id = Column(
        String(36),
        ForeignKey("domain_inventory.warehouse_bins.id"),
        nullable=False,
    )
    article_id = Column(String(64), nullable=False)
    batch_number = Column(String(64), nullable=True)
    best_before_date = Column(Date, nullable=True)
    quantity_kg = Column(DECIMAL(14, 4), nullable=False, server_default="0")
    # FIFO valuation cost
    unit_cost = Column(DECIMAL(12, 4), nullable=True)
    last_movement_at = Column(DateTime(timezone=True), nullable=True)
    tenant_id = Column(String(64), nullable=False)


class WmsPickList(Base):
    """WMS-extended pick list header.

    Extends ``domain_inventory.pick_lists`` (created by the L3C migration) with
    WMS-specific columns.  ``extend_existing=True`` allows both model classes to
    map to the same table.
    """

    __tablename__ = "pick_lists"
    __table_args__ = (
        Index("idx_pl_tenant_status", "tenant_id", "status"),
        Index("idx_pl_source", "source_doc_ref"),
        {"schema": "domain_inventory", "extend_existing": True},
    )

    id = Column(String(36), primary_key=True, default=uuid7)
    tenant_id = Column(String(64), nullable=False)
    warehouse_id = Column(String(36), nullable=True)
    # e.g. Lieferschein-ID
    source_doc_ref = Column(String(128), nullable=True)
    # DELIVERY_NOTE / PRODUCTION_ORDER / MANUAL
    source_doc_type = Column(String(32), nullable=True)
    # OPEN / IN_PROGRESS / COMPLETED / CANCELLED
    status = Column(String(20), server_default="OPEN")
    # FEFO / FIFO / MANUAL
    strategy = Column(String(20), server_default="FEFO")
    created_by = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)


class WmsPickListLine(Base):
    """WMS-extended pick list line.

    Extends ``domain_inventory.pick_list_lines`` with WMS bin / FEFO columns.
    ``extend_existing=True`` allows coexistence with the L3C PickListLine class.
    """

    __tablename__ = "pick_list_lines"
    __table_args__ = (
        Index("idx_pll_pick_list", "pick_list_id"),
        Index("idx_pll_bin", "bin_id"),
        {"schema": "domain_inventory", "extend_existing": True},
    )

    id = Column(String(36), primary_key=True, default=uuid7)
    pick_list_id = Column(
        String(36),
        ForeignKey("domain_inventory.pick_lists.id"),
        nullable=False,
    )
    article_id = Column(String(64), nullable=False)
    # Suggested bin from pick strategy
    bin_id = Column(
        String(36),
        ForeignKey("domain_inventory.warehouse_bins.id"),
        nullable=True,
    )
    batch_number = Column(String(64), nullable=True)
    best_before_date = Column(Date, nullable=True)
    quantity_required = Column(DECIMAL(14, 4), nullable=False)
    quantity_picked = Column(DECIMAL(14, 4), server_default="0")
    unit = Column(String(20), server_default="kg")
    # OPEN / PARTIAL / DONE / SKIPPED
    status = Column(String(20), server_default="OPEN")
    # Sequence by bin location code for efficient warehouse walk
    sort_order = Column(Integer, server_default="0")
    tenant_id = Column(String(64), nullable=True)


# ── Agrar: Siloanlagen & Materialfluss (WM-AGRI-SILO-001) ───────────────────


class SiloSystem(Base):
    """Siloanlage / Silogruppe innerhalb eines Lagers."""

    __tablename__ = "silo_systems"
    __table_args__ = (
        UniqueConstraint("warehouse_id", "system_code", name="uq_silo_sys_wh_code"),
        Index("idx_silo_sys_wh", "warehouse_id"),
        Index("idx_silo_sys_tenant", "tenant_id"),
        {"schema": "domain_inventory", "extend_existing": True},
    )

    id = Column(String(36), primary_key=True, default=uuid7)
    warehouse_id = Column(
        String(36),
        ForeignKey("domain_inventory.warehouses.id"),
        nullable=False,
    )
    system_code = Column(String(40), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    tenant_id = Column(String(64), nullable=False)
    is_active = Column(Boolean, server_default="true")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class SiloCell(Base):
    """Silozelle / Kammer; optional an Zone, Gang, Fach angebunden."""

    __tablename__ = "silo_cells"
    __table_args__ = (
        UniqueConstraint("silo_system_id", "cell_code", name="uq_silo_cell_sys_code"),
        Index("idx_silo_cells_sys", "silo_system_id"),
        Index("idx_silo_cells_wh", "warehouse_id"),
        Index("idx_silo_cells_tenant", "tenant_id"),
        {"schema": "domain_inventory", "extend_existing": True},
    )

    id = Column(String(36), primary_key=True, default=uuid7)
    silo_system_id = Column(
        String(36),
        ForeignKey("domain_inventory.silo_systems.id"),
        nullable=False,
    )
    warehouse_id = Column(
        String(36),
        ForeignKey("domain_inventory.warehouses.id"),
        nullable=False,
    )
    zone_id = Column(String(36), ForeignKey("domain_inventory.warehouse_zones.id"), nullable=True)
    aisle_id = Column(String(36), ForeignKey("domain_inventory.warehouse_aisles.id"), nullable=True)
    bin_id = Column(String(36), ForeignKey("domain_inventory.warehouse_bins.id"), nullable=True)
    cell_code = Column(String(40), nullable=False)
    name = Column(String(200), nullable=False)
    capacity_kg = Column(DECIMAL(14, 4), nullable=False, server_default="0")
    current_material_id = Column(String(64), nullable=True)
    current_lot_id = Column(String(64), nullable=True)
    current_stock_kg = Column(DECIMAL(16, 3), nullable=False, server_default="0")
    qs_status = Column(String(32), nullable=False, server_default="frei")
    contamination_risk_class = Column(String(32), nullable=True)
    layout_x = Column(DECIMAL(12, 3), nullable=True)
    layout_y = Column(DECIMAL(12, 3), nullable=True)
    tenant_id = Column(String(64), nullable=False)
    is_active = Column(Boolean, server_default="true")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class MaterialFlowNode(Base):
    """Knoten im Materialfluss (Waage, Elevator, Silozelle, Mischer, …)."""

    __tablename__ = "material_flow_nodes"
    __table_args__ = (
        UniqueConstraint("warehouse_id", "code", name="uq_mfn_wh_code"),
        Index("idx_mfn_wh", "warehouse_id"),
        Index("idx_mfn_tenant", "tenant_id"),
        {"schema": "domain_inventory", "extend_existing": True},
    )

    id = Column(String(36), primary_key=True, default=uuid7)
    warehouse_id = Column(
        String(36),
        ForeignKey("domain_inventory.warehouses.id"),
        nullable=False,
    )
    node_type = Column(String(40), nullable=False)
    ref_type = Column(String(40), nullable=True)
    ref_id = Column(String(64), nullable=True)
    code = Column(String(64), nullable=False)
    name = Column(String(200), nullable=False)
    status = Column(String(32), nullable=False, server_default="active")
    geo_lat = Column(DECIMAL(10, 7), nullable=True)
    geo_lng = Column(DECIMAL(10, 7), nullable=True)
    layout_x = Column(DECIMAL(12, 3), nullable=True)
    layout_y = Column(DECIMAL(12, 3), nullable=True)
    tenant_id = Column(String(64), nullable=False)
    is_active = Column(Boolean, server_default="true")
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class MaterialFlowEdge(Base):
    """Gerichtete Kante zwischen Materialfluss-Knoten."""

    __tablename__ = "material_flow_edges"
    __table_args__ = (
        Index("idx_mfe_wh", "warehouse_id"),
        Index("idx_mfe_from", "from_node_id"),
        Index("idx_mfe_to", "to_node_id"),
        Index("idx_mfe_tenant", "tenant_id"),
        {"schema": "domain_inventory", "extend_existing": True},
    )

    id = Column(String(36), primary_key=True, default=uuid7)
    warehouse_id = Column(
        String(36),
        ForeignKey("domain_inventory.warehouses.id"),
        nullable=False,
    )
    from_node_id = Column(
        String(36),
        ForeignKey("domain_inventory.material_flow_nodes.id"),
        nullable=False,
    )
    to_node_id = Column(
        String(36),
        ForeignKey("domain_inventory.material_flow_nodes.id"),
        nullable=False,
    )
    conveyor_type = Column(String(64), nullable=False, server_default="generic")
    status = Column(String(32), nullable=False, server_default="open")
    contamination_guard_enabled = Column(Boolean, nullable=False, server_default="true")
    flush_required = Column(Boolean, nullable=False, server_default="false")
    max_capacity_kg_h = Column(DECIMAL(14, 4), nullable=True)
    tenant_id = Column(String(64), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
