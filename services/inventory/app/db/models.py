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
