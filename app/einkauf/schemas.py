"""
VALEO-NeuroERP - Einkauf Schemas
Pydantic Schemas für API
"""

from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal


def _to_camel(name: str) -> str:
    """snake_case -> camelCase"""
    parts = name.split("_")
    return parts[0] + "".join(w.capitalize() for w in parts[1:])


class CamelModel(BaseModel):
    """Base model that accepts both camelCase and snake_case field names."""
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=_to_camel,
    )


***REMOVED*** ============================================================================
***REMOVED*** LIEFERANTEN
***REMOVED*** ============================================================================

class LieferantBase(BaseModel):
    lieferantennummer: str
    firmenname: str
    ansprechpartner: Optional[str] = None
    email: Optional[EmailStr] = None
    telefon: Optional[str] = None
    strasse: Optional[str] = None
    plz: Optional[str] = None
    ort: Optional[str] = None
    land: str = "Deutschland"
    zahlungsbedingungen: Optional[str] = None
    lieferzeit_tage: Optional[int] = None
    bewertung: Optional[int] = None
    aktiv: bool = True


class LieferantCreate(LieferantBase):
    pass


class LieferantUpdate(BaseModel):
    firmenname: Optional[str] = None
    ansprechpartner: Optional[str] = None
    email: Optional[EmailStr] = None
    telefon: Optional[str] = None
    strasse: Optional[str] = None
    plz: Optional[str] = None
    ort: Optional[str] = None
    land: Optional[str] = None
    zahlungsbedingungen: Optional[str] = None
    lieferzeit_tage: Optional[int] = None
    bewertung: Optional[int] = None
    aktiv: Optional[bool] = None


class Lieferant(LieferantBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


***REMOVED*** ============================================================================
***REMOVED*** BESTELLUNGEN
***REMOVED*** ============================================================================

class BestellungBase(BaseModel):
    bestellnummer: str
    lieferant_id: int
    bestelldatum: date
    gewuenschtes_lieferdatum: Optional[date] = None
    status: str = "entwurf"
    netto_summe: Optional[Decimal] = None
    mwst_betrag: Optional[Decimal] = None
    brutto_summe: Optional[Decimal] = None
    erstellt_von: Optional[str] = None


class BestellungCreate(BestellungBase):
    pass


class BestellungUpdate(BaseModel):
    lieferant_id: Optional[int] = None
    bestelldatum: Optional[date] = None
    gewuenschtes_lieferdatum: Optional[date] = None
    status: Optional[str] = None
    netto_summe: Optional[Decimal] = None
    mwst_betrag: Optional[Decimal] = None
    brutto_summe: Optional[Decimal] = None


class Bestellung(BestellungBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


***REMOVED*** ============================================================================
***REMOVED*** WARENEINGANG (Goods Receipt) - PROC-GR-01
***REMOVED*** ============================================================================

class GoodsReceiptItemCreate(CamelModel):
    purchase_order_item_id: Optional[str] = None
    article_id: str = ""
    article_name: Optional[str] = None
    ordered_quantity: Decimal = Decimal("0")
    received_quantity: Decimal = Decimal("0")
    accepted_quantity: Decimal = Decimal("0")
    rejected_quantity: Decimal = Decimal("0")
    condition: str = "PERFECT"  ***REMOVED*** PERFECT, GOOD, DAMAGED, DEFECTIVE


class GoodsReceiptItemResponse(GoodsReceiptItemCreate):
    id: str
    wareneingang_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True, alias_generator=_to_camel)


class GoodsReceiptCreate(CamelModel):
    purchase_order_id: Optional[str] = None  ***REMOVED*** Can be passed via URL path
    delivery_note_number: Optional[str] = None
    received_date: date
    received_by: str
    received_location: str
    items: List[GoodsReceiptItemCreate] = []
    quality_inspection_status: str = "PENDING"  ***REMOVED*** PENDING, PASSED, FAILED, CONDITIONAL
    inspection_notes: Optional[str] = None
    damage_report: Optional[str] = None


class GoodsReceiptResponse(CamelModel):
    id: str
    purchase_order_id: str
    delivery_note_number: Optional[str] = None
    received_date: date
    received_by: str
    received_location: str
    quality_inspection_status: str
    inspection_notes: Optional[str] = None
    damage_report: Optional[str] = None
    items: List[GoodsReceiptItemResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True, populate_by_name=True, alias_generator=_to_camel)


***REMOVED*** ============================================================================
***REMOVED*** BEDARFSMELDUNG / ANFRAGE (Requisition) - PROC-REQ-01
***REMOVED*** ============================================================================

class AnfragePositionCreate(BaseModel):
    article_id: Optional[str] = None
    artikel: Optional[str] = None  ***REMOVED*** Freitext Artikelname
    quantity: Decimal
    unit: str = "Stueck"
    due_date: Optional[date] = None
    notes: Optional[str] = None


class AnfragePositionResponse(AnfragePositionCreate):
    id: str
    anfrage_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class AnfrageBase(BaseModel):
    anfrageNummer: Optional[str] = None
    typ: str = "BANF"  ***REMOVED*** BANF (Bedarfsanforderung), ANF (Anfrage)
    anforderer: str
    abteilung: Optional[str] = None
    datum: Optional[date] = None
    prioritaet: str = "normal"  ***REMOVED*** niedrig, normal, hoch, dringend
    status: str = "ENTWURF"  ***REMOVED*** ENTWURF, FREIGEGEBEN, ANGEBOTSPHASE, BESTELLT, ABGELEHNT
    begruendung: Optional[str] = None
    kostenstelle: Optional[str] = None
    projekt_id: Optional[str] = None
    artikel: Optional[str] = None  ***REMOVED*** Legacy single-article field
    menge: Optional[Decimal] = None
    einheit: Optional[str] = None
    budget: Optional[Decimal] = None
    notizen: Optional[str] = None


class AnfrageCreate(AnfrageBase):
    positionen: Optional[List[AnfragePositionCreate]] = None


class AnfrageUpdate(BaseModel):
    anforderer: Optional[str] = None
    abteilung: Optional[str] = None
    datum: Optional[date] = None
    prioritaet: Optional[str] = None
    status: Optional[str] = None
    begruendung: Optional[str] = None
    kostenstelle: Optional[str] = None
    projekt_id: Optional[str] = None
    artikel: Optional[str] = None
    menge: Optional[Decimal] = None
    einheit: Optional[str] = None
    budget: Optional[Decimal] = None
    notizen: Optional[str] = None
    positionen: Optional[List[AnfragePositionCreate]] = None


class AnfrageResponse(AnfrageBase):
    id: str
    positionen: List[AnfragePositionResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


***REMOVED*** ============================================================================
***REMOVED*** RECHNUNGSEINGANG (Invoice Receipt) - PROC-IV-02
***REMOVED*** ============================================================================

class RechnungseingangPositionCreate(BaseModel):
    artikelId: Optional[str] = None
    artikelName: Optional[str] = None
    menge: Decimal
    einzelpreis: Decimal
    gesamtpreis: Optional[Decimal] = None
    mwstSatz: Decimal = Decimal("19.0")


class RechnungseingangPositionResponse(RechnungseingangPositionCreate):
    id: str
    rechnungseingang_id: str

    class Config:
        from_attributes = True


class RechnungseingangBase(BaseModel):
    rechnungsNummer: str
    lieferantId: Optional[str] = None
    lieferantName: Optional[str] = None
    bestellungId: Optional[str] = None
    wareneingangId: Optional[str] = None
    rechnungsDatum: date
    faelligkeitsDatum: Optional[date] = None
    nettoBetrag: Decimal
    mwstBetrag: Optional[Decimal] = None
    bruttoBetrag: Optional[Decimal] = None
    waehrung: str = "EUR"
    status: str = "OFFEN"  ***REMOVED*** OFFEN, GEPRUEFT, FREIGEGEBEN, BEZAHLT, STORNIERT
    zahlungsreferenz: Optional[str] = None
    notizen: Optional[str] = None
    abgleichErgebnis: Optional[dict] = None
    abweichungsBegruendung: Optional[str] = None


class RechnungseingangCreate(RechnungseingangBase):
    positionen: Optional[List[RechnungseingangPositionCreate]] = None


class RechnungseingangUpdate(BaseModel):
    lieferantId: Optional[str] = None
    lieferantName: Optional[str] = None
    bestellungId: Optional[str] = None
    wareneingangId: Optional[str] = None
    rechnungsDatum: Optional[date] = None
    faelligkeitsDatum: Optional[date] = None
    nettoBetrag: Optional[Decimal] = None
    mwstBetrag: Optional[Decimal] = None
    bruttoBetrag: Optional[Decimal] = None
    status: Optional[str] = None
    zahlungsreferenz: Optional[str] = None
    notizen: Optional[str] = None
    abgleichErgebnis: Optional[dict] = None
    abweichungsBegruendung: Optional[str] = None
    positionen: Optional[List[RechnungseingangPositionCreate]] = None


class RechnungseingangResponse(RechnungseingangBase):
    id: str
    positionen: List[RechnungseingangPositionResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


***REMOVED*** ============================================================================
***REMOVED*** 2/3-WEGE-ABGLEICH (PO-GR-IV Matching) - PROC-IV-02
***REMOVED*** ============================================================================

class MatchItemResult(CamelModel):
    purchase_order_item_id: str
    receipt_item_id: Optional[str] = None
    invoice_item_id: Optional[str] = None
    product_name: str
    po_quantity: Decimal
    po_price: Decimal
    gr_quantity: Optional[Decimal] = None
    gr_accepted: Optional[Decimal] = None
    iv_quantity: Optional[Decimal] = None
    iv_price: Optional[Decimal] = None
    quantity_match: bool
    price_match: bool
    quality_match: bool
    exceptions: List[str] = []
    variance_amount: Decimal = Decimal("0")


class MatchRequest(CamelModel):
    invoice_id: str
    purchase_order_id: str
    goods_receipt_id: Optional[str] = None
    tolerance_quantity: Decimal = Decimal("2.0")  ***REMOVED*** Prozent
    tolerance_price: Decimal = Decimal("1.0")  ***REMOVED*** Prozent


class MatchResponse(CamelModel):
    match_id: str
    purchase_order_id: str
    receipt_id: Optional[str] = None
    invoice_id: str
    match_type: str  ***REMOVED*** two_way, three_way
    overall_status: str  ***REMOVED*** matched, partial_match, exceptions, no_match
    quantity_match: str  ***REMOVED*** matched, over_invoice, under_invoice, no_receipt
    price_match: str  ***REMOVED*** matched, price_variance, no_match
    quality_match: str  ***REMOVED*** matched, quality_issues, no_receipt
    item_matches: List[MatchItemResult]
    total_variance: Decimal
    variance_percentage: Decimal
    exceptions_count: int
    auto_approval_eligible: bool

