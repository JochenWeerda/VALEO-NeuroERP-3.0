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


class SalesOrder(BaseModel):
    """Verkaufsauftrag"""
    number: str
    date: str  # YYYY-MM-DD
    customerId: str
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
    notes: Optional[str] = ""
    lines: List[DocLine] = Field(default_factory=list)


class FollowRequest(BaseModel):
    """Request für Folgebeleg-Erstellung"""
    fromType: str
    toType: str
    payload: dict

