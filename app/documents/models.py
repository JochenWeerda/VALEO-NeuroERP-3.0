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
    date: str  ***REMOVED*** YYYY-MM-DD
    customerId: str
    status: str = "OFFEN"  ***REMOVED*** Status-Management: OFFEN → IN_BEARBEITUNG → ANGEBOTEN → ABGELEHNT
    contactPerson: Optional[str] = None
    inquiryType: str = "STANDARD"  ***REMOVED*** STANDARD, PROJEKT, SUPPORT
    priority: str = "NORMAL"  ***REMOVED*** HOCH, NORMAL, NIEDRIG
    description: Optional[str] = ""
    requirements: Optional[str] = ""
    deadline: Optional[str] = None
    notes: Optional[str] = ""
    lines: List[DocLine] = Field(default_factory=list)


class SalesOffer(BaseModel):
    """Verkaufsangebot"""
    number: str
    date: str  ***REMOVED*** YYYY-MM-DD
    customerId: str
    status: str = "ENTWURF"  ***REMOVED*** Status-Management: ENTWURF → VERSENDET → ANGENOMMEN → ABGELEHNT
    contactPerson: Optional[str] = None
    validUntil: Optional[str] = None  ***REMOVED*** Gültig bis
    deliveryDate: Optional[str] = None
    deliveryAddress: Optional[str] = ""
    paymentTerms: str = "net30"
    notes: Optional[str] = ""
    lines: List[DocLine] = Field(default_factory=list)
    ***REMOVED*** Gesamtbeträge
    subtotalNet: float = 0.0  ***REMOVED*** Netto-Summe
    totalTax: float = 0.0     ***REMOVED*** Steuer-Summe
    totalGross: float = 0.0   ***REMOVED*** Brutto-Summe


class SalesOrder(BaseModel):
    """Verkaufsauftrag"""
    number: str
    date: str  ***REMOVED*** YYYY-MM-DD
    customerId: str
    salesOfferId: Optional[str] = None  ***REMOVED*** Referenz zum SalesOffer
    status: str = "ENTWURF"  ***REMOVED*** Status-Management
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
    deliveryDate: Optional[str] = None  ***REMOVED*** Lieferdatum
    status: str = "ENTWURF"  ***REMOVED*** Status-Management: ENTWURF → VERSENDET → GELIEFERT
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
    status: str = "ENTWURF"  ***REMOVED*** Status-Management: ENTWURF → VERSENDET → BEZAHLT → ÜBERFÄLLIG
    notes: Optional[str] = ""
    lines: List[DocLine] = Field(default_factory=list)
    ***REMOVED*** Gesamtbeträge
    subtotalNet: float = 0.0  ***REMOVED*** Netto-Summe
    totalTax: float = 0.0     ***REMOVED*** Steuer-Summe
    totalGross: float = 0.0   ***REMOVED*** Brutto-Summe


class PaymentReceived(BaseModel):
    """Zahlungseingang"""
    number: str
    date: str  ***REMOVED*** YYYY-MM-DD
    salesInvoiceId: str  ***REMOVED*** Referenz zur SalesInvoice
    amount: float  ***REMOVED*** Zahlungsbetrag
    paymentMethod: str  ***REMOVED*** Zahlungsart (Überweisung, Lastschrift, Bar, etc.)
    bankReference: Optional[str] = None  ***REMOVED*** Bankverbindung oder Zahlungsreferenz
    status: str = "EINGEGANGEN"  ***REMOVED*** Status-Management: EINGEGANGEN → VERBUCHT → ABGEGLICHEN
    notes: Optional[str] = ""


class PurchaseRequest(BaseModel):
    """Einkaufsanfrage"""
    number: str
    date: str  ***REMOVED*** YYYY-MM-DD
    supplierId: Optional[str] = None
    status: str = "OFFEN"  ***REMOVED*** Status-Management: OFFEN → IN_BEARBEITUNG → BESTELLT → ABGELEHNT
    contactPerson: Optional[str] = None
    requestType: str = "STANDARD"  ***REMOVED*** STANDARD, DRINGEND, PLANUNG
    priority: str = "NORMAL"  ***REMOVED*** HOCH, NORMAL, NIEDRIG
    description: Optional[str] = ""
    requirements: Optional[str] = ""
    deadline: Optional[str] = None
    notes: Optional[str] = ""
    lines: List[DocLine] = Field(default_factory=list)


class PurchaseOffer(BaseModel):
    """Einkaufsangebot"""
    number: str
    date: str  ***REMOVED*** YYYY-MM-DD
    supplierId: str
    purchaseRequestId: Optional[str] = None  ***REMOVED*** Referenz zur PurchaseRequest
    status: str = "ENTWURF"  ***REMOVED*** Status-Management: ENTWURF → EINGEGANGEN → ANGENOMMEN → ABGELEHNT
    contactPerson: Optional[str] = None
    validUntil: Optional[str] = None  ***REMOVED*** Gültig bis
    deliveryDate: Optional[str] = None
    deliveryAddress: Optional[str] = ""
    paymentTerms: str = "net30"
    notes: Optional[str] = ""
    lines: List[DocLine] = Field(default_factory=list)
    ***REMOVED*** Gesamtbeträge
    subtotalNet: float = 0.0  ***REMOVED*** Netto-Summe
    totalTax: float = 0.0     ***REMOVED*** Steuer-Summe
    totalGross: float = 0.0   ***REMOVED*** Brutto-Summe


class PurchaseOrder(BaseModel):
    """Kaufauftrag"""
    number: str
    date: str  ***REMOVED*** YYYY-MM-DD
    supplierId: str
    purchaseOfferId: Optional[str] = None  ***REMOVED*** Referenz zum PurchaseOffer
    status: str = "ENTWURF"  ***REMOVED*** Status-Management: ENTWURF → FREIGEGEBEN → TEILGELIEFERT → VOLLGELIEFERT → STORNIERT
    contactPerson: Optional[str] = None
    deliveryDate: Optional[str] = None
    deliveryAddress: Optional[str] = ""
    paymentTerms: str = "net30"
    notes: Optional[str] = ""
    lines: List[DocLine] = Field(default_factory=list)
    ***REMOVED*** Gesamtbeträge
    subtotalNet: float = 0.0  ***REMOVED*** Netto-Summe
    totalTax: float = 0.0     ***REMOVED*** Steuer-Summe
    totalGross: float = 0.0   ***REMOVED*** Brutto-Summe


class FollowRequest(BaseModel):
    """Request für Folgebeleg-Erstellung"""
    fromType: str
    toType: str
    payload: dict

