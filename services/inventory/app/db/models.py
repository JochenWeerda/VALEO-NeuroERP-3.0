"""SQLAlchemy Modelle für Inventory Service."""

from __future__ import annotations

from datetime import datetime
from enum import Enum as PyEnum
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Column, DateTime, Enum as SQLEnum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy import JSON
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class InventoryTransactionType(str, PyEnum):  # type: ignore[misc]
    RECEIPT = "receipt"
    TRANSFER = "transfer"
    ADJUSTMENT = "adjustment"


class Warehouse(Base):
    __tablename__ = "inventory_warehouses"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    address: Mapped[str | None] = mapped_column(Text)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, default="default")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    locations: Mapped[list["Location"]] = relationship(back_populates="warehouse", cascade="all, delete-orphan")


class Location(Base):
    __tablename__ = "inventory_locations"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    warehouse_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("inventory_warehouses.id"), nullable=False, index=True)
    code: Mapped[str] = mapped_column(String(32), nullable=False)
    location_type: Mapped[str] = mapped_column(String(32), nullable=False, default="STANDARD")
    capacity_units: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    warehouse: Mapped[Warehouse] = relationship(back_populates="locations")
    stock_items: Mapped[list[StockItem]] = relationship(back_populates="location", cascade="all, delete-orphan")


class Lot(Base):
    __tablename__ = "inventory_lots"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    sku: Mapped[str] = mapped_column(String(64), nullable=False)
    lot_number: Mapped[str] = mapped_column(String(64), nullable=False)
    production_date: Mapped[datetime | None] = mapped_column(DateTime)
    expiry_date: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    stock_items: Mapped[list[StockItem]] = relationship(back_populates="lot")


class StockItem(Base):
    __tablename__ = "inventory_stock_items"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    warehouse_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("inventory_warehouses.id"), nullable=False, index=True)
    location_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("inventory_locations.id"), nullable=False, index=True)
    lot_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("inventory_lots.id"), nullable=False, index=True)
    quantity: Mapped[float] = mapped_column(Numeric(16, 3), nullable=False, default=0)
    reserved_quantity: Mapped[float] = mapped_column(Numeric(16, 3), nullable=False, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    location: Mapped[Location] = relationship(back_populates="stock_items")
    lot: Mapped[Lot] = relationship(back_populates="stock_items")
    transactions: Mapped[list[InventoryTransaction]] = relationship(back_populates="stock_item", cascade="all, delete-orphan")


class InventoryTransaction(Base):
    __tablename__ = "inventory_transactions"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    stock_item_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("inventory_stock_items.id"), nullable=False, index=True)
    transaction_type: Mapped[InventoryTransactionType] = mapped_column(
        SQLEnum(InventoryTransactionType, name="inventory_transaction_type"),
        nullable=False,
    )
    quantity: Mapped[float] = mapped_column(Numeric(16, 3), nullable=False)
    reference: Mapped[str | None] = mapped_column(String(128))
    from_location_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("inventory_locations.id"))
    to_location_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("inventory_locations.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    stock_item: Mapped[StockItem] = relationship(back_populates="transactions")


class GoodsReceiptStatus(str, PyEnum):  # type: ignore[misc]
    DRAFT = "draft"
    POSTED = "posted"
    CANCELLED = "cancelled"


class GoodsReceipt(Base):
    """Wareneingang (Goods Receipt) against a Purchase Order."""
    __tablename__ = "inventory_goods_receipts"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, default="default", index=True)
    gr_number: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    po_number: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    po_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True))
    supplier_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True))
    supplier_name: Mapped[str] = mapped_column(String(256), default="")
    delivery_note_number: Mapped[str | None] = mapped_column(String(64))
    receipt_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    status: Mapped[GoodsReceiptStatus] = mapped_column(
        SQLEnum(GoodsReceiptStatus, name="goods_receipt_status"),
        nullable=False,
        default=GoodsReceiptStatus.DRAFT,
    )
    notes: Mapped[str] = mapped_column(Text, default="")
    created_by: Mapped[str] = mapped_column(String(128), nullable=False, default="system")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    lines: Mapped[list["GoodsReceiptLine"]] = relationship(back_populates="goods_receipt", cascade="all, delete-orphan")


class GoodsReceiptLine(Base):
    """Single line item of a Goods Receipt."""
    __tablename__ = "inventory_goods_receipt_lines"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    goods_receipt_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("inventory_goods_receipts.id"), nullable=False, index=True
    )
    po_line_number: Mapped[int] = mapped_column(Integer, nullable=False)
    sku: Mapped[str] = mapped_column(String(64), nullable=False)
    description: Mapped[str] = mapped_column(String(256), default="")
    ordered_quantity: Mapped[float] = mapped_column(Numeric(16, 3), nullable=False)
    received_quantity: Mapped[float] = mapped_column(Numeric(16, 3), nullable=False)
    unit: Mapped[str] = mapped_column(String(16), default="ST")
    lot_number: Mapped[str | None] = mapped_column(String(64))
    warehouse_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("inventory_warehouses.id"), nullable=False)
    location_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("inventory_locations.id"), nullable=False)
    quality_status: Mapped[str] = mapped_column(String(32), default="pending")
    notes: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    goods_receipt: Mapped[GoodsReceipt] = relationship(back_populates="lines")


class EpcisEventType(str, PyEnum):  # type: ignore[misc]
    OBJECT = "ObjectEvent"
    AGGREGATION = "AggregationEvent"
    TRANSFORMATION = "TransformationEvent"
    TRANSACTION = "TransactionEvent"


class EpcisEvent(Base):
    """Minimale EPCIS-Event-Persistenz für Lieferkettentracking."""

    __tablename__ = "inventory_epcis_events"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    tenant_id: Mapped[str] = mapped_column(String(64), nullable=False, default="default", index=True)
    # Idempotenz-/Deduplikationsschlüssel (optional, aber falls gesetzt: eindeutig)
    event_key: Mapped[str | None] = mapped_column(String(128), unique=True, index=True)
    event_type: Mapped[EpcisEventType] = mapped_column(SQLEnum(EpcisEventType, name="epcis_event_type"), nullable=False)
    event_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    biz_step: Mapped[str | None] = mapped_column(String(128))
    read_point: Mapped[str | None] = mapped_column(String(128))
    lot_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("inventory_lots.id"))
    sku: Mapped[str | None] = mapped_column(String(64))
    quantity: Mapped[float | None] = mapped_column(Numeric(16, 3))
    extensions: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    lot: Mapped[Lot | None] = relationship()

