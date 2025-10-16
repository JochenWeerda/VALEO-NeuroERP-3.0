"""
Document Models
Pydantic Models für Belege (Order, Delivery, Invoice)
"""

from __future__ import annotations
from typing import List, Optional
from pydantic import BaseModel, Field


class DocLine(BaseModel):
    """Beleg-Position (generisch)"""
    article: str
    qty: float
    price: Optional[float] = None
    vatRate: Optional[float] = None


class CustomerInquiry(BaseModel):
    """Kundenanfrage"""
    number: str
    date: str  # YYYY-MM-DD
    customerId: str
    status: str = "OFFEN"  # Status-Management: OFFEN → IN_BEARBEITUNG → ANGEBOTEN → ABGELEHNT
    contactPerson: Optional[str] = None
    inquiryType: str = "STANDARD"  # STANDARD, PROJEKT, SUPPORT
    priority: str = "NORMAL"  # HOCH, NORMAL, NIEDRIG
    description: Optional[str] = ""
    requirements: Optional[str] = ""
    deadline: Optional[str] = None
    notes: Optional[str] = ""
    lines: List[DocLine] = Field(default_factory=list)


class SalesOffer(BaseModel):
    """Verkaufsangebot"""
    number: str
    date: str  # YYYY-MM-DD
    customerId: str
    status: str = "ENTWURF"  # Status-Management: ENTWURF → VERSENDET → ANGENOMMEN → ABGELEHNT
    contactPerson: Optional[str] = None
    validUntil: Optional[str] = None  # Gültig bis
    deliveryDate: Optional[str] = None
    deliveryAddress: Optional[str] = ""
    paymentTerms: str = "net30"
    notes: Optional[str] = ""
    lines: List[DocLine] = Field(default_factory=list)
    # Gesamtbeträge
    subtotalNet: float = 0.0  # Netto-Summe
    totalTax: float = 0.0     # Steuer-Summe
    totalGross: float = 0.0   # Brutto-Summe


class SalesOrder(BaseModel):
    """Verkaufsauftrag"""
    number: str
    date: str  # YYYY-MM-DD
    customerId: str
    salesOfferId: Optional[str] = None  # Referenz zum SalesOffer
    status: str = "ENTWURF"  # Status-Management
    contactPerson: Optional[str] = None
    deliveryDate: Optional[str] = None
    deliveryAddress: Optional[str] = ""
    paymentTerms: str = "net30"
    notes: Optional[str] = ""
    lines: List[DocLine] = Field(default_factory=list)


class SalesDelivery(BaseModel):
    """Lieferschein"""
    number: str
    date: str
    customerId: str
    sourceOrder: Optional[str] = None
    deliveryAddress: str
    carrier: Optional[str] = None
    deliveryDate: Optional[str] = None  # Lieferdatum
    status: str = "ENTWURF"  # Status-Management: ENTWURF → VERSENDET → GELIEFERT
    notes: Optional[str] = ""
    lines: List[DocLine] = Field(default_factory=list)


class SalesInvoice(BaseModel):
    """Rechnung"""
    number: str
    date: str
    customerId: str
    sourceOrder: Optional[str] = None
    sourceDelivery: Optional[str] = None
    paymentTerms: str = "net30"
    dueDate: str
    status: str = "ENTWURF"  # Status-Management: ENTWURF → VERSENDET → BEZAHLT → ÜBERFÄLLIG
    notes: Optional[str] = ""
    lines: List[DocLine] = Field(default_factory=list)
    # Gesamtbeträge
    subtotalNet: float = 0.0  # Netto-Summe
    totalTax: float = 0.0     # Steuer-Summe
    totalGross: float = 0.0   # Brutto-Summe


class PaymentReceived(BaseModel):
    """Zahlungseingang"""
    number: str
    date: str  # YYYY-MM-DD
    salesInvoiceId: str  # Referenz zur SalesInvoice
    amount: float  # Zahlungsbetrag
    paymentMethod: str  # Zahlungsart (Überweisung, Lastschrift, Bar, etc.)
    bankReference: Optional[str] = None  # Bankverbindung oder Zahlungsreferenz
    status: str = "EINGEGANGEN"  # Status-Management: EINGEGANGEN → VERBUCHT → ABGEGLICHEN
    notes: Optional[str] = ""


class FollowRequest(BaseModel):
    """Request für Folgebeleg-Erstellung"""
    fromType: str
    toType: str
    payload: dict

