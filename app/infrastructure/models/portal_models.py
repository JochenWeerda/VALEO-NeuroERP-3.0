"""
Kundenportal Datenbank-Modelle

Modelle für:
- Kundenkontrakte (Rahmenverträge)
- Vorkäufe (bereits bezahlte Ware)
- Kundenbestellungen
- Bestellpositionen
"""

from datetime import datetime
from decimal import Decimal
import uuid

from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Integer,
    Numeric, String, Text, Enum as SQLEnum
)
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class ContractStatus(str, enum.Enum):
    """Kontrakt-Status"""
    NONE = "NONE"
    ACTIVE = "ACTIVE"
    LOW = "LOW"  # < 20% Restmenge
    EXHAUSTED = "EXHAUSTED"


class OrderStatus(str, enum.Enum):
    """Bestellstatus"""
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    CONFIRMED = "CONFIRMED"
    IN_PROGRESS = "IN_PROGRESS"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class CustomerContract(Base):
    """
    Kundenkontrakt / Rahmenvertrag
    
    Ermöglicht dem Kunden, Artikel zu einem vereinbarten Preis
    bis zu einer festgelegten Gesamtmenge abzurufen.
    """
    __tablename__ = "customer_contracts"
    __table_args__ = {"schema": "domain_portal"}
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Mandant & Kunde
    tenant_id = Column(String(36), nullable=False, index=True)
    customer_id = Column(String(36), nullable=False, index=True)
    
    # Artikel
    article_id = Column(String(36), nullable=False, index=True)
    article_number = Column(String(50), nullable=False)
    article_name = Column(String(200), nullable=False)
    
    # Vertragsdaten
    contract_number = Column(String(50), nullable=False, unique=True)
    contract_price = Column(Numeric(12, 2), nullable=False)  # Vereinbarter Preis
    list_price = Column(Numeric(12, 2), nullable=False)  # Aktueller Listenpreis zum Vergleich
    unit = Column(String(20), nullable=False)  # dt, kg, l, m³...
    
    # Mengen
    total_quantity = Column(Numeric(12, 2), nullable=False)  # Gesamtmenge im Vertrag
    remaining_quantity = Column(Numeric(12, 2), nullable=False)  # Verfügbare Restmenge
    
    # Status
    status = Column(SQLEnum(ContractStatus), default=ContractStatus.ACTIVE, nullable=False)
    
    # Laufzeit
    valid_from = Column(DateTime(timezone=True), nullable=False)
    valid_until = Column(DateTime(timezone=True), nullable=False)
    
    # Metadaten
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(36), nullable=True)
    
    def calculate_status(self) -> ContractStatus:
        """Berechnet den aktuellen Status basierend auf Restmenge"""
        if self.remaining_quantity <= 0:
            return ContractStatus.EXHAUSTED
        percent_remaining = (self.remaining_quantity / self.total_quantity) * 100
        if percent_remaining < 20:
            return ContractStatus.LOW
        return ContractStatus.ACTIVE


class CustomerPrePurchase(Base):
    """
    Kundenvorkauf / Bereits bezahlte Ware
    
    Ermöglicht dem Kunden, bereits bezahlte Ware (z.B. Dünger)
    zum Vorkaufpreis abzurufen. Der Kunde hat das Guthaben bereits bezahlt.
    """
    __tablename__ = "customer_pre_purchases"
    __table_args__ = {"schema": "domain_portal"}
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Mandant & Kunde
    tenant_id = Column(String(36), nullable=False, index=True)
    customer_id = Column(String(36), nullable=False, index=True)
    
    # Artikel
    article_id = Column(String(36), nullable=False, index=True)
    article_number = Column(String(50), nullable=False)
    article_name = Column(String(200), nullable=False)
    
    # Vorkaufdaten
    pre_purchase_number = Column(String(50), nullable=False, unique=True)
    pre_purchase_price = Column(Numeric(12, 2), nullable=False)  # Bezahlter Preis
    current_list_price = Column(Numeric(12, 2), nullable=False)  # Aktueller Marktpreis
    unit = Column(String(20), nullable=False)
    
    # Mengen
    total_quantity = Column(Numeric(12, 2), nullable=False)  # Gesamtmenge gekauft
    remaining_quantity = Column(Numeric(12, 2), nullable=False)  # Verbleibende Guthabenmenge
    
    # Zahlungsdaten
    payment_date = Column(DateTime(timezone=True), nullable=False)  # Wann wurde bezahlt
    payment_reference = Column(String(100), nullable=True)  # Zahlungsreferenz
    
    # Gültigkeitszeitraum
    valid_until = Column(DateTime(timezone=True), nullable=True)  # Optional: Ablaufdatum
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Metadaten
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def is_low(self) -> bool:
        """Prüft ob Guthaben fast aufgebraucht (< 20%)"""
        if self.total_quantity <= 0:
            return True
        return (self.remaining_quantity / self.total_quantity) * 100 < 20


class CustomerOrder(Base):
    """
    Kundenbestellung aus dem Portal
    """
    __tablename__ = "customer_orders"
    __table_args__ = {"schema": "domain_portal"}
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Mandant & Kunde
    tenant_id = Column(String(36), nullable=False, index=True)
    customer_id = Column(String(36), nullable=False, index=True)
    customer_number = Column(String(50), nullable=False)
    customer_name = Column(String(200), nullable=False)
    
    # Bestelldaten
    order_number = Column(String(50), nullable=False, unique=True)
    order_date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Status
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.SUBMITTED, nullable=False)
    
    # Beträge
    total_net = Column(Numeric(12, 2), default=0)
    total_gross = Column(Numeric(12, 2), default=0)
    
    # Lieferadresse
    delivery_address = Column(Text, nullable=True)
    delivery_date_requested = Column(DateTime(timezone=True), nullable=True)
    
    # Notizen
    customer_notes = Column(Text, nullable=True)
    internal_notes = Column(Text, nullable=True)
    
    # Metadaten
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Beziehungen
    items = relationship("CustomerOrderItem", back_populates="order", cascade="all, delete-orphan")


class CustomerOrderItem(Base):
    """
    Bestellposition einer Kundenbestellung
    """
    __tablename__ = "customer_order_items"
    __table_args__ = {"schema": "domain_portal"}
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Bestellung
    order_id = Column(String(36), ForeignKey("domain_portal.customer_orders.id"), nullable=False)
    
    # Artikel
    article_id = Column(String(36), nullable=False)
    article_number = Column(String(50), nullable=False)
    article_name = Column(String(200), nullable=False)
    
    # Mengen & Preise
    quantity = Column(Numeric(12, 2), nullable=False)
    unit = Column(String(20), nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    total_price = Column(Numeric(12, 2), nullable=False)
    
    # Preisquelle
    price_source = Column(String(20), nullable=False)  # 'LIST', 'CONTRACT', 'PRE_PURCHASE', 'PROMO'
    contract_id = Column(String(36), nullable=True)  # Referenz auf Kontrakt falls verwendet
    pre_purchase_id = Column(String(36), nullable=True)  # Referenz auf Vorkauf falls verwendet
    
    # Bei Vorkauf: wie viel kam aus Guthaben, wie viel zum Listenpreis?
    quantity_from_credit = Column(Numeric(12, 2), default=0)  # Aus Guthaben
    quantity_at_list_price = Column(Numeric(12, 2), default=0)  # Zum Listenpreis
    
    # Beziehung
    order = relationship("CustomerOrder", back_populates="items")


class CustomerOrderHistory(Base):
    """
    Historie der letzten Bestellungen pro Artikel/Kunde
    Für "Erneut bestellen" Funktion
    """
    __tablename__ = "customer_order_history"
    __table_args__ = {"schema": "domain_portal"}
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    tenant_id = Column(String(36), nullable=False, index=True)
    customer_id = Column(String(36), nullable=False, index=True)
    article_id = Column(String(36), nullable=False, index=True)
    
    # Letzte Bestellung
    last_order_date = Column(DateTime(timezone=True), nullable=False)
    last_order_quantity = Column(Numeric(12, 2), nullable=False)
    last_order_id = Column(String(36), nullable=False)
    
    # Statistik
    total_orders = Column(Integer, default=1)
    total_quantity = Column(Numeric(12, 2), nullable=False)
    average_quantity = Column(Numeric(12, 2), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

