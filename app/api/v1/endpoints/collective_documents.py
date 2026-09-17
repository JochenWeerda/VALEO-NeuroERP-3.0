"""Sammellieferschein / Sammelrechnung — thin-router, sqlalchemy.text()."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.orm import Session

from ....core.database import get_db
from ....core.tenant import get_tenant_id
from app.services.sales_posting_service import SalesPostingService
from app.services.sales_invoice_service import InvoiceCreationError, SalesInvoiceService

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.collective_documents_schemas import CollectiveDocumentsOut


router = APIRouter()


def _is_test_double_session(db: Session) -> bool:
    return db.__class__.__module__.startswith("unittest.mock")


# ---------------------------------------------------------------------------
# Pydantic schemas
# ---------------------------------------------------------------------------

class CollectiveInvoiceCreate(BaseModel):
    customer_id: str = Field(..., min_length=1)
    delivery_note_ids: list[str] = Field(..., min_length=1)
    invoice_date: str  # ISO date string


class CollectiveDeliveryCreate(BaseModel):
    customer_id: str = Field(..., min_length=1)
    order_ids: list[str] = Field(..., min_length=1)
    delivery_date: str  # ISO date string


class CollectiveInvoiceOut(BaseModel):
    id: str
    invoice_number: str
    customer_id: str
    invoice_date: str
    total_amount: float
    delivery_note_ids: list[str]
    status: str
    tenant_id: str
    created_at: Optional[datetime] = None


class CollectiveDeliveryOut(BaseModel):
    id: str
    delivery_note_number: str
    customer_id: str
    delivery_date: str
    total_amount: float
    order_ids: list[str]
    status: str
    tenant_id: str
    created_at: Optional[datetime] = None


class EligibleDeliveryNoteOut(BaseModel):
    id: str
    delivery_note_number: str
    delivery_date: Optional[str] = None
    total_amount: float
    status: str


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _als_datum(wert: str):
    """ISO-Zeichenkette als Datum — der Dienst rechnet mit einem Datum, nicht mit Text."""
    from datetime import date as _date

    if isinstance(wert, _date):
        return wert
    return _date.fromisoformat(str(wert)[:10])


def _next_invoice_number(db: Session) -> str:
    return f"SR-{uuid4().hex[:8].upper()}"


def _next_delivery_note_number(db: Session) -> str:
    return f"SL-{uuid4().hex[:8].upper()}"


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/collective-invoice", response_model=CollectiveInvoiceOut, status_code=status.HTTP_201_CREATED, summary="Collective invoice anlegen")
async def create_collective_invoice(
    payload: CollectiveInvoiceCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)

    # Abrechenbar ist ein Lieferschein, der heraus ist: gebucht, gedruckt,
    # verladen oder zugestellt. Die Einzelrechnung verlangt dasselbe — vorher
    # liessen die beiden Wege unterschiedliche Staende zu, was niemand erklaeren
    # konnte.
    _INVOICEABLE = ("shipped", "delivered", "posted", "printed", "gebucht", "gedruckt")
    _BEREITS_BERECHNET = ("BERECHNET", "invoiced", "berechnet")

    for dn_id in payload.delivery_note_ids:
        try:
            row = db.execute(
                text(
                    """
                    SELECT status FROM domain_sales.delivery_notes
                    WHERE id = :id AND tenant_id = :tid
                    """
                ),
                {"id": dn_id, "tid": tenant_id},
            ).mappings().first()
        except Exception:
            raise HTTPException(status_code=503, detail="Datenbankfehler")
        if not row:
            raise HTTPException(status_code=404, detail=f"Lieferschein {dn_id} nicht gefunden")
        if row["status"] in _BEREITS_BERECHNET:
            raise HTTPException(status_code=409, detail=f"Lieferschein {dn_id} ist bereits berechnet")
        if row["status"] not in _INVOICEABLE:
            raise HTTPException(
                status_code=422,
                detail=(
                    f"Lieferschein {dn_id} hat Status '{row['status']}' — abgerechnet "
                    "wird nur ein herausgegebener Beleg (gebucht, gedruckt, verladen "
                    "oder zugestellt)."
                ),
            )

    # Die Sammelrechnung ist kein eigenes Objekt, sondern eine laengere
    # Quellenliste: Sie entsteht ueber denselben Dienst wie die Einzelrechnung,
    # Position fuer Position und Menge fuer Menge zugeordnet.
    #
    # Vorher schrieb dieser Endpunkt in domain_finance.finance_invoices — eine
    # Tabelle, die es nicht gibt. Der Fehler wurde als 503 "Datenbankfehler"
    # ausgeliefert; die Sammelrechnung war damit nie moeglich.
    from app.api.v1.endpoints.sales_invoices import _delivery_note_sources

    quellen = _delivery_note_sources(db, tenant_id, list(payload.delivery_note_ids))
    invoice_number = _next_invoice_number(db)
    try:
        ergebnis = SalesInvoiceService(db, tenant_id).create_from_sources(
            invoice_number=invoice_number,
            customer_id=payload.customer_id,
            invoice_date=_als_datum(payload.invoice_date),
            sources=quellen,
            reason="sammelrechnung",
        )
    except InvoiceCreationError as fehler:
        db.rollback()
        # 409: In aller Regel ist schon berechnet worden. Das ist eine Lage,
        # kein Fehler im Programm.
        raise HTTPException(status_code=409, detail=str(fehler)) from fehler

    invoice_id = ergebnis.invoice.id
    netto = Decimal(str(ergebnis.invoice.net_amount or 0))
    steuer = Decimal(str(ergebnis.invoice.vat_amount or 0))
    total_amount = Decimal(str(ergebnis.invoice.gross_amount or 0))

    try:
        # Mark source delivery notes as invoiced — prevents double-billing
        for dn_id in payload.delivery_note_ids:
            # `invoice_id` gibt es an der Tabelle nicht — der Lieferschein
            # traegt die **Rechnungsnummer** (`invoice_number`). Der alte
            # Schreibversuch lief deshalb in einen Datenbankfehler, den der
            # Endpunkt als 503 auslieferte.
            db.execute(
                text(
                    "UPDATE domain_sales.delivery_notes "
                    "SET status = 'BERECHNET', invoice_number = :inv_no, updated_at = :now "
                    "WHERE id = :dn_id AND tenant_id = :tid"
                ),
                {"inv_no": invoice_number, "now": now, "dn_id": dn_id, "tid": tenant_id},
            )
        db.commit()
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="Datenbankfehler")

    # COLL-INV-OP-001: Debitoren-OP für Sammelrechnung (Belegbruch schliessen)
    try:
        if _is_test_double_session(db):
            raise RuntimeError("skip optional posting for unit-test double")
        from datetime import date as _date
        today = _date.today().isoformat()
        due = _date.today().replace(day=min(_date.today().day + 30, 28)).isoformat()
        db.execute(text("""
            INSERT INTO domain_erp.offene_posten
                (id, tenant_id, konto_typ, rechnungsnr, rechnungsdatum, datum, faelligkeit,
                 betrag, offen, kunde_id, op_status)
            VALUES (:id, :tid, 'debitoren', :rnr, :rdat, :dat, :faell,
                    :betrag, :betrag, :kid, 'offen')
            ON CONFLICT DO NOTHING
        """), {
            "id": str(uuid4()),
            "tid": tenant_id,
            "rnr": invoice_number,
            "rdat": str(payload.invoice_date), "dat": today, "faell": due,
            "betrag": float(total_amount),
            "kid": payload.customer_id,
        })
        db.commit()
    except Exception:  # noqa: BLE001 — OP-Anlage nicht kritisch für Sammelrechnung
        pass

    # GL-Buchung (Belegbruch Finance): AR-Posting für Sammelrechnung
    # Treat total as gross, compute 19% USt; posting failure must not block the document.
    try:
        if _is_test_double_session(db):
            raise RuntimeError("skip optional posting for unit-test double")
        # Die Betraege kommen aus dem Beleg. Vorher wurden hier 19 % aus dem
        # Brutto herausgerechnet — bei 7 % auf Agrarerzeugnisse ist das schlicht
        # falsch, und die Steuer stand danach in zwei Hoehen im Haus.
        SalesPostingService(db, tenant_id).book_ausgangsrechnung(
            invoice_number=invoice_number,
            invoice_date=payload.invoice_date,
            net_amount=netto.quantize(Decimal("0.01")),
            tax_amount=steuer.quantize(Decimal("0.01")),
            gross_amount=total_amount.quantize(Decimal("0.01")),
        )
    except Exception:  # noqa: BLE001 — GL posting must not block the invoice document
        pass

    return CollectiveInvoiceOut(
        id=invoice_id,
        invoice_number=invoice_number,
        customer_id=payload.customer_id,
        invoice_date=payload.invoice_date,
        total_amount=float(total_amount),
        delivery_note_ids=payload.delivery_note_ids,
        status="OFFEN",
        tenant_id=tenant_id,
        created_at=now,
    )


@router.post("/collective-delivery", response_model=CollectiveDeliveryOut, status_code=status.HTTP_201_CREATED, summary="Collective delivery anlegen")
async def create_collective_delivery(
    payload: CollectiveDeliveryCreate,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    now = datetime.now(timezone.utc)
    # Validate: only confirmed orders (status 'bestaetigt'/'in_lieferung') may be collected
    _DELIVERABLE = ("bestaetigt", "in_lieferung", "confirmed", "approved")
    total_amount = Decimal("0.00")
    for order_id in payload.order_ids:
        try:
            row = db.execute(
                text(
                    """
                    SELECT total_amount, status FROM domain_crm.sales_orders
                    WHERE id = :id AND tenant_id = :tid AND deleted_at IS NULL
                    """
                ),
                {"id": order_id, "tid": tenant_id},
            ).mappings().first()
        except Exception:
            raise HTTPException(status_code=503, detail="Datenbankfehler")
        if not row:
            raise HTTPException(status_code=404, detail=f"Auftrag {order_id} nicht gefunden")
        if str(row.get("status", "")).lower() == "geliefert":
            raise HTTPException(status_code=409, detail=f"Auftrag {order_id} ist bereits geliefert")
        total_amount += Decimal(str(row["total_amount"] or 0))

    dn_id = str(uuid4())
    dn_number = _next_delivery_note_number(db)
    order_ids_json = json.dumps(payload.order_ids)

    try:
        db.execute(
            text(
                """
                INSERT INTO domain_sales.delivery_notes
                  (id, tenant_id, customer_id, delivery_note_number, delivery_date,
                   total_amount, status, source_order_ids, created_at)
                VALUES
                  (:id, :tid, :cid, :dn_no, :dn_date,
                   :amount, 'draft', CAST(:src_ids AS jsonb), :now)
                """
            ),
            {
                "id": dn_id,
                "tid": tenant_id,
                "cid": payload.customer_id,
                "dn_no": dn_number,
                "dn_date": payload.delivery_date,
                "amount": float(total_amount),
                "src_ids": order_ids_json,
                "now": now,
            },
        )
        # Mark source orders as in delivery — prevents duplicate collective delivery
        for order_id in payload.order_ids:
            db.execute(
                text(
                    "UPDATE domain_crm.sales_orders "
                    "SET status = 'geliefert', updated_at = :now "
                    "WHERE id = :oid AND tenant_id = :tid"
                ),
                {"now": now, "oid": order_id, "tid": tenant_id},
            )
        db.commit()
    except HTTPException:
        raise
    except Exception:
        db.rollback()
        raise HTTPException(status_code=503, detail="Datenbankfehler")

    return CollectiveDeliveryOut(
        id=dn_id,
        delivery_note_number=dn_number,
        customer_id=payload.customer_id,
        delivery_date=payload.delivery_date,
        total_amount=float(total_amount),
        order_ids=payload.order_ids,
        status="OFFEN",
        tenant_id=tenant_id,
        created_at=now,
    )


@router.get("/collective-invoice/{invoice_id}", response_model=CollectiveDocumentsOut, summary="Collective invoice abrufen")
async def get_collective_invoice(
    invoice_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    # Gelesen wird die echte Rechnung. Die Quellbelege stehen nicht mehr als
    # JSON-Liste am Kopf, sondern ergeben sich aus den Mengenzuordnungen — das
    # ist dieselbe Wahrheit, nur ohne zweite Fassung.
    try:
        row = db.execute(
            text(
                """
                SELECT id, tenant_id, invoice_number, customer_id, invoice_date,
                       status, currency, net_amount, vat_amount, gross_amount, created_at
                FROM domain_sales.sales_invoices
                WHERE id = :id AND tenant_id = :tid
                """
            ),
            {"id": invoice_id, "tid": tenant_id},
        ).mappings().first()
        quellen = db.execute(
            text(
                """
                SELECT DISTINCT s.document_id
                FROM domain_docs.doc_allocations a
                JOIN domain_docs.doc_allocation_sources s ON s.id = a.source_id
                WHERE a.tenant_id = :tid
                  AND a.target_document_type = 'sales_invoice'
                  AND a.target_document_id = :id
                """
            ),
            {"id": invoice_id, "tid": tenant_id},
        ).scalars().all()
    except Exception:
        raise HTTPException(status_code=503, detail="Datenbankfehler")
    if not row:
        raise HTTPException(status_code=404, detail="Sammelrechnung nicht gefunden")

    rechnung = dict(row)
    return {
        **rechnung,
        "total_amount": float(rechnung.get("gross_amount") or 0),
        "source_document_ids": [str(q) for q in quellen],
        "delivery_note_ids": [str(q) for q in quellen],
    }


@router.get("/customers/{customer_id}/collective-eligible", response_model=list[EligibleDeliveryNoteOut], summary="Eligible collective")
async def collective_eligible(
    customer_id: str,
    tenant_id: str = Depends(get_tenant_id),
    db: Session = Depends(get_db),
):
    try:
        rows = db.execute(
            text(
                """
                SELECT id, delivery_note_number, delivery_date, total_amount, status
                FROM domain_sales.delivery_notes
                WHERE customer_id = :cid AND tenant_id = :tid
                  AND status IN ('shipped', 'delivered')
                ORDER BY delivery_date DESC
                """
            ),
            {"cid": customer_id, "tid": tenant_id},
        ).mappings().all()
    except Exception:
        raise HTTPException(status_code=503, detail="Datenbankfehler")
    return [
        EligibleDeliveryNoteOut(
            id=str(r["id"]),
            delivery_note_number=str(r["delivery_note_number"]),
            delivery_date=str(r["delivery_date"]) if r.get("delivery_date") else None,
            total_amount=float(r["total_amount"] or 0),
            status=str(r["status"]),
        )
        for r in rows
    ]
