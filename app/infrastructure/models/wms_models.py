"""SQLAlchemy models for WMS (Warehouse Management System).

Covers warehouse zones, bins, bin-level stock, and WMS-extended pick lists.
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


class WarehouseBin(Base):
    """An individual storage location (bin/slot) within a warehouse zone."""

    __tablename__ = "warehouse_bins"
    __table_args__ = (
        UniqueConstraint("warehouse_id", "bin_code", name="uq_wb_warehouse_bin_code"),
        Index("idx_wb_zone", "zone_id"),
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
