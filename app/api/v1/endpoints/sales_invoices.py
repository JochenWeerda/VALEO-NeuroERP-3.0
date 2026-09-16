"""Die Ausgangsrechnung mit ihren Positionen.

Bisher war die Rechnung im Belegfluss kein Gegenstand: Aus einem Lieferschein
wurde ein Journalsatz ueber den ganzen Beleg. Damit konnte eine
Positionszuordnung auf nichts zeigen, und niemand konnte nachlesen, woher eine
berechnete Menge kommt.

Diese Endpunkte liefern die Rechnung **mit** ihren Positionen und — je Position
— ihre **Herkunft**: aus welcher Lieferscheinposition welche Teilmenge stammt.
Das ist dieselbe Zuordnung, die der Lieferschein nach vorn zeigt, nur von der
anderen Seite gelesen.

Die Sammelrechnung ist hier kein Sonderfall, sondern der Regelfall: Mehrere
Lieferscheine in eine Rechnung sind nur eine laengere Quellenliste.
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, text
from sqlalchemy.orm import Session

from app.api.v1.schemas.base import BaseSchema
from app.core.database import get_db
from app.core.tenant_context import get_current_tenant_id
from app.core.uuid7 import uuid7
from app.domains.documents.allocation_models import (
    DocumentAllocation,
    DocumentAllocationSource,
)
from app.domains.documents.sales_invoice_models import SalesInvoice, SalesInvoiceLine
from app.services.document_allocation_service import LineToRegister
from app.services.sales_invoice_service import (
    InvoiceCreationError,
    SalesInvoiceService,
    SourceLine,
)

router = APIRouter()


class SalesInvoiceOut(BaseSchema):
    model_config = ConfigDict(extra="allow")


class CreateFromDeliveryNotes(BaseModel):
    model_config = ConfigDict(extra="forbid")

    customer_id: str = Field(min_length=1, max_length=120)
    delivery_note_ids: list[str] = Field(min_length=1)
    invoice_date: date
    invoice_number: Optional[str] = Field(default=None, max_length=60)
    due_date: Optional[date] = None
    note: Optional[str] = None
    user_id: Optional[str] = None


def _zahl(wert: Any) -> str:
    """Mengen und Betraege als Zeichenkette — die Anzeige rundet, der Wert nicht."""
    zahl = Decimal(str(wert)).normalize()
    if zahl == zahl.to_integral_value():
        zahl = zahl.quantize(Decimal(1))
    return format(zahl, "f")


def _delivery_note_sources(db: Session, tenant_id: str, ls_ids: list[str]) -> list[SourceLine]:
    """Die Positionen der genannten Lieferscheine, in der Reihenfolge der Belege.

    Fremde Lieferscheine bleiben draussen: Gefiltert wird ueber ``tenant_id``,
    nicht nur ueber die Kennung aus dem Aufruf.
    """
    quellen: list[SourceLine] = []
    for ls_id in ls_ids:
        kopf = db.execute(
            text(
                "SELECT id FROM domain_sales.delivery_notes "
                "WHERE id = :id AND tenant_id = :tid"
            ),
            {"id": ls_id, "tid": tenant_id},
        ).first()
        if kopf is None:
            raise HTTPException(
                status_code=404, detail=f"Lieferschein {ls_id} nicht gefunden"
            )
        zeilen = (
            db.execute(
                text(
                    "SELECT * FROM domain_sales.delivery_note_positions "
                    "WHERE delivery_note_id = :id ORDER BY pos_nr"
                ),
                {"id": ls_id},
            )
            .mappings()
            .all()
        )
        for zeile in zeilen:
            eintrag = dict(zeile)
            gelesen = LineToRegister.from_mapping(eintrag)
            if not gelesen.line_id or not gelesen.unit:
                continue
            quellen.append(
                SourceLine(
                    document_type="delivery_note",
                    document_id=ls_id,
                    line_id=gelesen.line_id,
                    article_id=gelesen.article_id,
                    article_number=eintrag.get("artikel_nr"),
                    description=eintrag.get("bezeichnung"),
                    quantity=Decimal(str(gelesen.quantity or 0)),
                    unit=str(gelesen.unit),
                    unit_price=Decimal(str(eintrag.get("netto_preis") or 0)),
                    vat_rate=(
                        Decimal(str(eintrag["mwst_prozent"]))
                        if eintrag.get("mwst_prozent") is not None
                        else None
                    ),
                )
            )
    return quellen


@router.post(
    "/invoices/from-delivery-notes",
    response_model=SalesInvoiceOut,
    status_code=201,
    summary="Rechnung aus Lieferscheinen anlegen",
)
def create_from_delivery_notes(
    body: CreateFromDeliveryNotes,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Eine Rechnung mit eigenen Positionen, Menge fuer Menge zugeordnet.

    Berechnet wird die **offene** Menge je Lieferscheinposition. Bereits
    berechnete Positionen kommen nicht noch einmal mit; sie stehen mit Grund in
    ``skipped``, damit nicht unbemerkt weniger berechnet wird als erwartet.
    """
    tenant_id = get_current_tenant_id()
    quellen = _delivery_note_sources(db, tenant_id, body.delivery_note_ids)
    nummer = body.invoice_number or f"RE-{uuid7()[:8].upper()}"

    try:
        ergebnis = SalesInvoiceService(db, tenant_id).create_from_sources(
            invoice_number=nummer,
            customer_id=body.customer_id,
            invoice_date=body.invoice_date,
            due_date=body.due_date,
            sources=quellen,
            reason="sammelrechnung" if len(body.delivery_note_ids) > 1 else "rechnung_aus_lieferschein",
            user_id=body.user_id,
            note=body.note,
        )
    except InvoiceCreationError as fehler:
        db.rollback()
        # 409: Der haeufigste Grund ist, dass bereits berechnet wurde. Das ist
        # eine Lage, kein Fehler im Programm.
        raise HTTPException(status_code=409, detail=str(fehler)) from fehler

    db.commit()
    return {
        "id": ergebnis.invoice.id,
        "invoice_number": ergebnis.invoice.invoice_number,
        "status": ergebnis.invoice.status,
        "net_amount": _zahl(ergebnis.invoice.net_amount),
        "lines": [
            {
                "line_no": zeile.line_no,
                "article_id": zeile.article_id,
                "quantity": _zahl(zeile.quantity),
                "unit": zeile.unit,
                "net_amount": _zahl(zeile.net_amount),
            }
            for zeile in ergebnis.lines
        ],
        "skipped": [
            {
                "document_id": eintrag.source.document_id,
                "line_id": eintrag.source.line_id,
                "reason": eintrag.reason,
            }
            for eintrag in ergebnis.skipped
        ],
    }


@router.get(
    "/invoices",
    response_model=SalesInvoiceOut,
    summary="Rechnungen suchen",
)
def list_invoices(
    db: Session = Depends(get_db),
    customer_id: Optional[str] = Query(default=None, max_length=120),
    status: Optional[str] = Query(default=None, max_length=20),
    invoice_number: Optional[str] = Query(default=None, max_length=60),
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> dict[str, Any]:
    """Die Liste, ueber die eine Rechnung erreichbar wird.

    Die Positionen kommen hier **nicht** mit: Eine Trefferliste ueber fuenfzig
    Rechnungen wuerde sonst mehrere hundert Zeilen laden, von denen keine
    angezeigt wird. Sichtbar ist die Positionszahl — sie beantwortet die Frage,
    ob ein Beleg leer aussieht, ohne ihn zu oeffnen.

    ``total`` ist die Trefferzahl **ohne** Seitenbegrenzung. Ohne sie waere
    "50 von 50" nicht von "50 von 900" zu unterscheiden.
    """
    tenant_id = get_current_tenant_id()

    abfrage = db.query(SalesInvoice).filter(SalesInvoice.tenant_id == tenant_id)
    if customer_id:
        abfrage = abfrage.filter(SalesInvoice.customer_id == customer_id)
    if status:
        abfrage = abfrage.filter(SalesInvoice.status == status)
    if invoice_number:
        # Teiltreffer, weil in der Praxis die letzten Stellen gesucht werden.
        abfrage = abfrage.filter(SalesInvoice.invoice_number.ilike(f"%{invoice_number}%"))
    if date_from:
        abfrage = abfrage.filter(SalesInvoice.invoice_date >= date_from)
    if date_to:
        abfrage = abfrage.filter(SalesInvoice.invoice_date <= date_to)

    gesamt = abfrage.count()
    treffer = (
        abfrage.order_by(SalesInvoice.invoice_date.desc(), SalesInvoice.invoice_number.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    # Eine Abfrage fuer alle Positionszahlen, nicht eine je Rechnung.
    zahlen: dict[str, int] = {}
    if treffer:
        for rechnung_id, anzahl in (
            db.query(SalesInvoiceLine.invoice_id, func.count(SalesInvoiceLine.id))
            .filter(
                SalesInvoiceLine.tenant_id == tenant_id,
                SalesInvoiceLine.invoice_id.in_([r.id for r in treffer]),
            )
            .group_by(SalesInvoiceLine.invoice_id)
            .all()
        ):
            zahlen[rechnung_id] = int(anzahl)

    return {
        "items": [
            {
                "id": rechnung.id,
                "invoice_number": rechnung.invoice_number,
                "customer_id": rechnung.customer_id,
                "invoice_date": rechnung.invoice_date.isoformat(),
                "due_date": rechnung.due_date.isoformat() if rechnung.due_date else None,
                "status": rechnung.status,
                "currency": rechnung.currency,
                "net_amount": _zahl(rechnung.net_amount),
                "vat_amount": _zahl(rechnung.vat_amount),
                "gross_amount": _zahl(rechnung.gross_amount),
                "line_count": zahlen.get(rechnung.id, 0),
            }
            for rechnung in treffer
        ],
        "total": gesamt,
        "limit": limit,
        "offset": offset,
    }


@router.get(
    "/invoices/{invoice_id}",
    response_model=SalesInvoiceOut,
    summary="Rechnung mit Positionen und Herkunft",
)
def get_invoice(
    invoice_id: str,
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Kopf, Positionen und je Position die Herkunft der Menge.

    Die Herkunft kommt in **einer** Abfrage mit, nicht in einer je Position:
    Eine Rechnung ueber zwanzig Lieferscheinpositionen soll nicht zwanzig
    Aufrufe ausloesen.
    """
    tenant_id = get_current_tenant_id()
    gefunden = SalesInvoiceService(db, tenant_id).get_with_lines(invoice_id)
    if gefunden is None:
        raise HTTPException(status_code=404, detail="Rechnung nicht gefunden")
    rechnung, positionen = gefunden

    herkunft: dict[str, list[dict[str, Any]]] = {}
    for zuordnung, quelle in (
        db.query(DocumentAllocation, DocumentAllocationSource)
        .join(
            DocumentAllocationSource,
            DocumentAllocation.source_id == DocumentAllocationSource.id,
        )
        .filter(
            DocumentAllocation.tenant_id == tenant_id,
            DocumentAllocation.target_document_type == "sales_invoice",
            DocumentAllocation.target_document_id == invoice_id,
        )
        .order_by(DocumentAllocation.created_at.asc())
        .all()
    ):
        herkunft.setdefault(zuordnung.target_line_id, []).append(
            {
                "source_document_type": quelle.document_type,
                "source_document_id": quelle.document_id,
                "source_line_id": quelle.line_id,
                "quantity": _zahl(zuordnung.quantity),
                "unit": zuordnung.unit,
                "reason": zuordnung.reason,
            }
        )

    return {
        "id": rechnung.id,
        "invoice_number": rechnung.invoice_number,
        "customer_id": rechnung.customer_id,
        "invoice_date": rechnung.invoice_date.isoformat(),
        "due_date": rechnung.due_date.isoformat() if rechnung.due_date else None,
        "status": rechnung.status,
        "currency": rechnung.currency,
        "net_amount": _zahl(rechnung.net_amount),
        "vat_amount": _zahl(rechnung.vat_amount),
        "gross_amount": _zahl(rechnung.gross_amount),
        "lines": [
            {
                "line_no": zeile.line_no,
                "article_id": zeile.article_id,
                "article_number": zeile.article_number,
                "description": zeile.description,
                "quantity": _zahl(zeile.quantity),
                "unit": zeile.unit,
                "unit_price": _zahl(zeile.unit_price),
                "net_amount": _zahl(zeile.net_amount),
                "vat_rate": _zahl(zeile.vat_rate) if zeile.vat_rate is not None else None,
                # Leer heisst hier: keine Zuordnung vorhanden. Das ist eine
                # Auskunft — eine Rechnungsposition ohne Herkunft gehoert
                # geprueft.
                "origins": herkunft.get(zeile.line_no, []),
            }
            for zeile in positionen
        ],
        "total": len(positionen),
    }
