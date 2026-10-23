"""
Verladung Domain Models - Tours, Stops, Delivery Notes, Events
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey, JSON, UniqueConstraint, CheckConstraint, Index, ForeignKeyConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.core.uuid7 import default_prefixed_id

from app.core.database import Base


class TourStatus(str, enum.Enum):
    """Tour Status Enum"""
    PLANNED = "planned"
    LOADING = "loading"
    DISPATCHED = "dispatched"
    IN_TRANSIT = "in_transit"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class TourType(str, enum.Enum):
    """Tour Type Enum"""
    STueCKGUT = "stueckgut"
    SOLO = "solo"
    EXPRESS = "express"
    GROSSGUT = "grossgut"


class StopStatus(str, enum.Enum):
    """Stop Status Enum"""
    OPEN = "open"
    LOADING = "loading"
    UNLOADING = "unloading"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class DeliveryNoteStatus(str, enum.Enum):
    """Delivery Note Status Enum"""
    READY = "ready"
    LOADED = "loaded"
    DELIVERED = "delivered"
    RETURNED = "returned"


class EventType(str, enum.Enum):
    """Tour Event Types"""
    TOUR_CREATED = "TOUR_CREATED"
    TOUR_UPDATED = "TOUR_UPDATED"
    LOADING_STARTED = "LOADING_STARTED"
    LOADING_FINISHED = "LOADING_FINISHED"
    DISPATCHED = "DISPATCHED"
    STOP_ARRIVED = "STOP_ARRIVED"
    STOP_DEPARTED = "STOP_DEPARTED"
    DELIVERY_COMPLETED = "DELIVERY_COMPLETED"
    EXCEPTION = "EXCEPTION"


class VehicleType(str, enum.Enum):
    """Vehicle Type Enum"""
    TRANSPORTER = "transporter"
    LKW_7_5T = "7_5t"
    LKW_12T = "12t"
    LKW_40T = "40t"
    SPRINTER = "sprinter"


class Tour(Base):
    """
    Tour Model for Tour Management
    """
    __tablename__ = "log_touren"
    __table_args__ = (
        UniqueConstraint("tenant_id", "tour_no", name="uq_log_touren_tenant_tour_no"),
        CheckConstraint("trim(tenant_id) <> ''", name="ck_log_touren_tenant_nonblank"),
        Index("ix_log_touren_tenant_date", "tenant_id", "date"),
        Index("ix_log_touren_tenant_status", "tenant_id", "status"),
        {"schema": "domain_log", "extend_existing": True},
    )

    id = Column(String, primary_key=True, default=default_prefixed_id("TOUR"))
    
    tenant_id = Column(String(120), nullable=False)

    # Tour identification
    tour_no = Column(String(50), nullable=False)
    date = Column(DateTime(timezone=True), nullable=False)
    week = Column(String(10))  # 2026-W07
    
    # Tour details
    type = Column(String(20), default=TourType.STueCKGUT.value)
    status = Column(String(20), default=TourStatus.PLANNED.value)
    notes = Column(Text)
    
    # Driver & Vehicle
    driver_id = Column(String, ForeignKey("domain_ops.ops_fahrer.id", ondelete="SET NULL"))
    vehicle_id = Column(String, ForeignKey("domain_ops.ops_fahrzeuge.id", ondelete="SET NULL"))
    
    # Times
    planned_departure_at = Column(DateTime(timezone=True))
    actual_departure_at = Column(DateTime(timezone=True))
    planned_arrival_at = Column(DateTime(timezone=True))
    actual_arrival_at = Column(DateTime(timezone=True))
    
    # Totals (cached for fast access)
    totals_json = Column(JSON)  # {"stops": 2, "delivery_notes": 5, "pieces": 150, "weight_kg": 1200}
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(String(100))
    updated_by = Column(String(100))
    
    # Relationships
    driver = relationship("Fahrer", foreign_keys=[driver_id])
    vehicle = relationship("Fahrzeug", foreign_keys=[vehicle_id])
    stops = relationship("TourStop", back_populates="tour", cascade="all, delete-orphan", order_by="TourStop.sequence")
    events = relationship("TourEvent", back_populates="tour", cascade="all, delete-orphan")


class TourStop(Base):
    """
    Tour Stop / Abladestelle
    """
    __tablename__ = "log_tour_stops"
    __table_args__ = (UniqueConstraint("tour_id", "id", name="uq_log_tour_stops_tour_id_id"), {"schema": "domain_log", "extend_existing": True})

    id = Column(String, primary_key=True, default=default_prefixed_id("STOP"))
    
    # References
    tour_id = Column(String, ForeignKey("domain_log.log_touren.id", ondelete="CASCADE"))
    
    # Sequencing
    sequence = Column(Integer, nullable=False)
    
    # Status
    status = Column(String(20), default=StopStatus.OPEN.value)
    
    # Customer
    customer_id = Column(String(100))  # Reference to customer
    customer_name = Column(String(200))
    
    # Dropoff address
    address_id = Column(String(100))
    address_label = Column(String(200))
    street = Column(String(300))
    zip_code = Column(String(20))
    city = Column(String(200))
    country = Column(String(10), default="DE")
    
    # Time window
    time_window_from = Column(DateTime(timezone=True))
    time_window_to = Column(DateTime(timezone=True))
    
    # Notes
    notes = Column(Text)
    
    # Totals (cached)
    totals_json = Column(JSON)
    
    # Audit
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    tour = relationship("Tour", back_populates="stops")
    delivery_notes = relationship("TourDeliveryNote", back_populates="stop", cascade="all, delete-orphan", foreign_keys="[TourDeliveryNote.tour_id, TourDeliveryNote.stop_id]", primaryjoin="and_(TourStop.id == TourDeliveryNote.stop_id, TourStop.tour_id == TourDeliveryNote.tour_id)", overlaps="tour")


class TourDeliveryNote(Base):
    """
    Delivery Note / Lieferschein on Tour
    """
    __tablename__ = "log_tour_delivery_notes"
    __table_args__ = (
        CheckConstraint("stop_id IS NULL OR tour_id IS NOT NULL", name="ck_log_tour_dn_stop_requires_tour"),
        ForeignKeyConstraint(["tour_id", "stop_id"], ["domain_log.log_tour_stops.tour_id", "domain_log.log_tour_stops.id"], name="fk_log_tour_dn_same_tour_stop", ondelete="CASCADE"),
        {"schema": "domain_log", "extend_existing": True},
    )

    id = Column(String, primary_key=True, default=default_prefixed_id("DN"))
    
    # References
    tour_id = Column(String, ForeignKey("domain_log.log_touren.id", ondelete="CASCADE"))
    stop_id = Column(String, ForeignKey("domain_log.log_tour_stops.id", ondelete="CASCADE"))
    
    # Delivery note data
    dn_no = Column(String(50), nullable=False)
    status = Column(String(20), default=DeliveryNoteStatus.READY.value)
    
    # References
    order_id = Column(String(100))
    customer_ref = Column(String(100))  # Customer PO number
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    loaded_at = Column(DateTime(timezone=True))
    delivered_at = Column(DateTime(timezone=True))
    
    # Summary data (cached from original DN)
    items_lines = Column(Integer, default=0)
    items_pieces = Column(Integer, default=0)
    items_weight_kg = Column(Float, default=0)
    items_volume_m3 = Column(Float, default=0)
    
    # Audit
    created_at_record = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    tour = relationship("Tour", foreign_keys=[tour_id], overlaps="delivery_notes,stop")
    stop = relationship("TourStop", back_populates="delivery_notes", foreign_keys=[tour_id, stop_id], primaryjoin="and_(TourDeliveryNote.stop_id == TourStop.id, TourDeliveryNote.tour_id == TourStop.tour_id)", overlaps="tour")


class TourEvent(Base):
    """
    Tour Event / Audit Trail
    """
    __tablename__ = "log_tour_events"
    __table_args__ = {"schema": "domain_log", "extend_existing": True}

    id = Column(String, primary_key=True, default=default_prefixed_id("EVT"))
    
    # References
    tour_id = Column(String, ForeignKey("domain_log.log_touren.id", ondelete="CASCADE"))
    
    # Event data
    at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    type = Column(String(50), nullable=False)  # EventType enum values
    message = Column(Text)
    
    # Who
    user_id = Column(String(100))
    user_name = Column(String(200))
    
    # Additional data
    metadata_json = Column(JSON)
    
    # Relationships
    tour = relationship("Tour", back_populates="events")
