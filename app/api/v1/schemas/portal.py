"""
Kundenportal API Schemas

Pydantic-Modelle für:
- Produktkacheln mit Kontrakt/Vorkauf-Informationen
- Bestellungen
- Warenkorb
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from enum import Enum

from pydantic import BaseModel, Field


class ContractStatus(str, Enum):
    """Kontrakt-Status"""
    NONE = "NONE"
    ACTIVE = "ACTIVE"
    LOW = "LOW"
    EXHAUSTED = "EXHAUSTED"


class OrderStatus(str, Enum):
    """Bestellstatus"""
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    CONFIRMED = "CONFIRMED"
    IN_PROGRESS = "IN_PROGRESS"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class PriceSource(str, Enum):
    """Preisquelle"""
    LIST = "LIST"
    CONTRACT = "CONTRACT"
    PRE_PURCHASE = "PRE_PURCHASE"
    PROMO = "PROMO"


# ============================================
# Produkt-Schemas für Shop-Kacheln
# ============================================

class LastOrderInfo(BaseModel):
    """Information zur letzten Bestellung eines Artikels"""
    datum: datetime
    menge: Decimal
    unit: str


class ContractInfo(BaseModel):
    """Kontrakt-Informationen für Produktkachel"""
    status: ContractStatus
    contract_id: str
    contract_number: str
    contract_price: Decimal
    total_qty: Decimal
    remaining_qty: Decimal
    valid_until: datetime


class PrePurchaseInfo(BaseModel):
    """Vorkauf-Informationen für Produktkachel"""
    pre_purchase_id: str
    pre_purchase_number: str
    pre_purchase_price: Decimal
    total_qty: Decimal
    remaining_qty: Decimal
    payment_date: datetime
    valid_until: Optional[datetime] = None


class PortalProduct(BaseModel):
    """
    Vollständiges Produkt für Portal-Shop-Kachel
    Enthält alle Informationen für die Darstellung inkl. Kontrakt/Vorkauf
    """
    id: str
    artikel_nummer: str = Field(..., alias="artikelnummer")
    name: str
    kategorie: str
    beschreibung: Optional[str] = None
    einheit: str
    
    # Preise
    listenpreis: Decimal = Field(..., alias="preis")
    aktionspreis: Optional[Decimal] = Field(None, alias="rabattPreis")
    
    # Verfügbarkeit
    verfuegbar: bool
    bestand: Decimal
    
    # Zertifikate
    zertifikate: List[str] = []
    
    # Letzte Bestellung (für "Erneut bestellen")
    letzte_bestellung: Optional[LastOrderInfo] = Field(None, alias="letzteBestellung")
    
    # Kontrakt-Informationen
    contract_status: ContractStatus = Field(ContractStatus.NONE, alias="contractStatus")
    contract_price: Optional[Decimal] = Field(None, alias="contractPrice")
    contract_total_qty: Optional[Decimal] = Field(None, alias="contractTotalQty")
    contract_remaining_qty: Optional[Decimal] = Field(None, alias="contractRemainingQty")
    
    # Vorkauf-Informationen
    is_pre_purchase: bool = Field(False, alias="isPrePurchase")
    pre_purchase_price: Optional[Decimal] = Field(None, alias="prePurchasePrice")
    pre_purchase_total_qty: Optional[Decimal] = Field(None, alias="prePurchaseTotalQty")
    pre_purchase_remaining_qty: Optional[Decimal] = Field(None, alias="prePurchaseRemainingQty")
    
    class Config:
        populate_by_name = True
        from_attributes = True


class PortalProductList(BaseModel):
    """Liste von Portal-Produkten mit Metadaten"""
    items: List[PortalProduct]
    total: int
    page: int = 1
    size: int = 50
    has_contracts: int = 0  # Anzahl Produkte mit aktivem Kontrakt
    has_pre_purchases: int = 0  # Anzahl Produkte mit Vorkauf-Guthaben


# ============================================
# Warenkorb-Schemas
# ============================================

class CartItem(BaseModel):
    """Warenkorb-Position"""
    article_id: str
    artikel_nummer: str
    name: str
    menge: Decimal
    einheit: str
    
    # Preisinformationen
    unit_price: Decimal
    total_price: Decimal
    price_source: PriceSource
    
    # Bei Vorkauf: Aufschlüsselung
    quantity_from_credit: Decimal = Decimal("0")
    quantity_at_list_price: Decimal = Decimal("0")
    credit_amount: Decimal = Decimal("0")  # Wert aus Guthaben
    list_amount: Decimal = Decimal("0")  # Wert zum Listenpreis


class CartSummary(BaseModel):
    """Warenkorb-Zusammenfassung"""
    items: List[CartItem]
    item_count: int
    total_net: Decimal
    credit_used: Decimal = Decimal("0")  # Aus Vorkauf-Guthaben
    to_pay: Decimal = Decimal("0")  # Tatsächlich zu zahlen


# ============================================
# Bestellung-Schemas
# ============================================

class OrderItemCreate(BaseModel):
    """Bestellposition erstellen"""
    article_id: str
    quantity: Decimal
    
    # Optional: Explizite Preisquelle (sonst automatisch beste Option)
    preferred_price_source: Optional[PriceSource] = None


class OrderCreate(BaseModel):
    """Bestellung erstellen"""
    items: List[OrderItemCreate]
    delivery_address: Optional[str] = None
    delivery_date_requested: Optional[datetime] = None
    customer_notes: Optional[str] = None


class OrderItemResponse(BaseModel):
    """Bestellposition in Antwort"""
    id: str
    article_id: str
    artikel_nummer: str
    name: str
    quantity: Decimal
    einheit: str
    unit_price: Decimal
    total_price: Decimal
    price_source: PriceSource
    quantity_from_credit: Decimal
    quantity_at_list_price: Decimal


class OrderResponse(BaseModel):
    """Bestellung Antwort"""
    id: str
    order_number: str
    order_date: datetime
    status: OrderStatus
    
    customer_id: str
    customer_name: str
    
    items: List[OrderItemResponse]
    
    total_net: Decimal
    total_gross: Decimal
    
    delivery_address: Optional[str] = None
    delivery_date_requested: Optional[datetime] = None
    customer_notes: Optional[str] = None
    
    created_at: datetime


class OrderListItem(BaseModel):
    """Bestellung in Liste (kompakt)"""
    id: str
    order_number: str
    order_date: datetime
    status: OrderStatus
    item_count: int
    total_net: Decimal
    main_article: str  # Erstes/Haupt-Artikel der Bestellung


class OrderList(BaseModel):
    """Liste von Bestellungen"""
    items: List[OrderListItem]
    total: int
    page: int = 1
    size: int = 20


# ============================================
# Anfrage-Schemas
# ============================================

class InquiryCreate(BaseModel):
    """Anfrage erstellen"""
    kategorie: str
    anfrage_text: str
    artikel_id: Optional[str] = None


class InquiryResponse(BaseModel):
    """Anfrage Antwort"""
    id: str
    anfrage_nummer: str
    status: str
    created_at: datetime

