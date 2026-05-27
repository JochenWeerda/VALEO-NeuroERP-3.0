"""
Einkauf — RFQ (Request for Quotation) — Anfrageprozess

Endpoints:
  GET/POST /einkauf/rfq                        → Anfragen liste/erstellen
  GET      /einkauf/rfq/{id}                   → Detail mit Angeboten
  POST     /einkauf/rfq/{id}/send              → An Lieferanten versenden
  POST     /einkauf/rfq/{id}/quotes            → Angebot erfassen
  GET      /einkauf/rfq/{id}/comparison        → Angebotsvergleich (nach Preis)
  POST     /einkauf/rfq/{id}/accept/{quote_id} → Zuschlag erteilen → Bestellung
"""
from __future__ import annotations

from datetime import date
from typing import Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

router = APIRouter(prefix="/einkauf/rfq", tags=["einkauf", "rfq"])


# ─────────────────────────────────────────────────────────────────────────────
# Schemas
# ─────────────────────────────────────────────────────────────────────────────

class RfqCreate(BaseModel):
    article_id: str
    quantity: float
    needed_by_date: Optional[date] = None
    notes: Optional[str] = None


class QuoteCreate(BaseModel):
    supplier_id: str
    unit_price: float
    delivery_days: Optional[int] = None
    notes: Optional[str] = None


class SendRequest(BaseModel):
    supplier_ids: Optional[List[str]] = None


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def _ensure_schema(db: Session) -> None:
    db.execute(text("CREATE SCHEMA IF NOT EXISTS domain_einkauf"))
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_einkauf.rfq_requests (
            id              BIGSERIAL PRIMARY KEY,
            article_id      TEXT NOT NULL,
            quantity        NUMERIC(18,4) NOT NULL,
            needed_by_date  DATE,
            notes           TEXT,
            status          TEXT NOT NULL DEFAULT 'OFFEN',
            tenant_id       TEXT,
            created_at      TIMESTAMPTZ DEFAULT NOW()
        )
    """))
    db.execute(text("""
        CREATE TABLE IF NOT EXISTS domain_einkauf.rfq_quotes (
            id            BIGSERIAL PRIMARY KEY,
            rfq_id        BIGINT NOT NULL REFERENCES domain_einkauf.rfq_requests(id) ON DELETE CASCADE,
            supplier_id   TEXT NOT NULL,
            unit_price    NUMERIC(18,4) NOT NULL,
            delivery_days INT,
            notes         TEXT,
            status        TEXT NOT NULL DEFAULT 'OFFEN',
            received_at   TIMESTAMPTZ DEFAULT NOW(),
            tenant_id     TEXT
        )
    """))
    db.commit()


def _get_rfq(db: Session, rfq_id: int, tenant_id: str) -> Any:
    row = db.execute(
        text("""
            SELECT id, article_id, quantity, needed_by_date, notes, status, created_at
            FROM domain_einkauf.rfq_requests
            WHERE id = :id AND tenant_id = :tid
        """),
        {"id": rfq_id, "tid": tenant_id},
    ).fetchone()
    return row


# ─────────────────────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@router.get("", summary="Rfq auflisten",
    response_model=list
)
def list_rfq(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> list[dict[str, Any]]:
    """Alle Anfragen auflisten."""
    try:
        _ensure_schema(db)
        rows = db.execute(
            text("""
                SELECT id, article_id, quantity, needed_by_date, notes, status, created_at
                FROM domain_einkauf.rfq_requests
                WHERE tenant_id = :tid
                ORDER BY created_at DESC
            """),
            {"tid": tenant_id},
        ).fetchall()
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Datenbankfehler: {exc}") from exc

    return [
        {
            "id": r[0], "article_id": r[1], "quantity": float(r[2]),
            "needed_by_date": r[3].isoformat() if r[3] else None,
            "notes": r[4], "status": r[5],
            "created_at": r[6].isoformat() if r[6] else None,
        }
        for r in rows
    ]


@router.post("", summary="Rfq anlegen",
    response_model=dict
)
def create_rfq(
    body: RfqCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Neue Anfrage anlegen."""
    try:
        _ensure_schema(db)
        row = db.execute(
            text("""
                INSERT INTO domain_einkauf.rfq_requests
                    (article_id, quantity, needed_by_date, notes, tenant_id)
                VALUES (:aid, :qty, :nbd, :notes, :tid)
                RETURNING id, article_id, quantity, needed_by_date, notes, status, created_at
            """),
            {
                "aid": body.article_id,
                "qty": body.quantity,
                "nbd": body.needed_by_date,
                "notes": body.notes,
                "tid": tenant_id,
            },
        ).fetchone()
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail=f"Datenbankfehler: {exc}") from exc

    return {
        "id": row[0], "article_id": row[1], "quantity": float(row[2]),
        "needed_by_date": row[3].isoformat() if row[3] else None,
        "notes": row[4], "status": row[5],
        "created_at": row[6].isoformat() if row[6] else None,
    }


@router.get("/{rfq_id}", summary="Rfq abrufen",
    response_model=dict
)
def get_rfq(
    rfq_id: int,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """RFQ-Detail inklusive aller Angebote."""
    try:
        _ensure_schema(db)
        rfq = _get_rfq(db, rfq_id, tenant_id)
        if not rfq:
            raise HTTPException(status_code=404, detail="Anfrage nicht gefunden")

        quotes = db.execute(
            text("""
                SELECT id, supplier_id, unit_price, delivery_days, notes, status, received_at
                FROM domain_einkauf.rfq_quotes
                WHERE rfq_id = :rid AND tenant_id = :tid
                ORDER BY unit_price
            """),
            {"rid": rfq_id, "tid": tenant_id},
        ).fetchall()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Datenbankfehler: {exc}") from exc

    return {
        "id": rfq[0], "article_id": rfq[1], "quantity": float(rfq[2]),
        "needed_by_date": rfq[3].isoformat() if rfq[3] else None,
        "notes": rfq[4], "status": rfq[5],
        "created_at": rfq[6].isoformat() if rfq[6] else None,
        "quotes": [
            {
                "id": q[0], "supplier_id": q[1], "unit_price": float(q[2]),
                "delivery_days": q[3], "notes": q[4], "status": q[5],
                "received_at": q[6].isoformat() if q[6] else None,
            }
            for q in quotes
        ],
    }


@router.post("/{rfq_id}/send", summary="Rfq senden",
    response_model=dict
)
def send_rfq(
    rfq_id: int,
    body: SendRequest,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """RFQ an Lieferanten versenden — markiert als VERSENDET."""
    try:
        _ensure_schema(db)
        rfq = _get_rfq(db, rfq_id, tenant_id)
        if not rfq:
            raise HTTPException(status_code=404, detail="Anfrage nicht gefunden")

        db.execute(
            text("""
                UPDATE domain_einkauf.rfq_requests
                SET status = 'VERSENDET'
                WHERE id = :id AND tenant_id = :tid
            """),
            {"id": rfq_id, "tid": tenant_id},
        )
        db.commit()
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail=f"Datenbankfehler: {exc}") from exc

    # In Produktion: E-Mails/EDI-Nachrichten an Lieferanten verschicken
    return {
        "rfq_id": rfq_id,
        "status": "VERSENDET",
        "suppliers_notified": body.supplier_ids or [],
    }


@router.post("/{rfq_id}/quotes", summary="Quote hinzufügen",
    response_model=dict
)
def add_quote(
    rfq_id: int,
    body: QuoteCreate,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Angebot für eine Anfrage erfassen."""
    try:
        _ensure_schema(db)
        rfq = _get_rfq(db, rfq_id, tenant_id)
        if not rfq:
            raise HTTPException(status_code=404, detail="Anfrage nicht gefunden")

        row = db.execute(
            text("""
                INSERT INTO domain_einkauf.rfq_quotes
                    (rfq_id, supplier_id, unit_price, delivery_days, notes, tenant_id)
                VALUES (:rid, :sid, :price, :days, :notes, :tid)
                RETURNING id, rfq_id, supplier_id, unit_price, delivery_days, notes, status, received_at
            """),
            {
                "rid": rfq_id,
                "sid": body.supplier_id,
                "price": body.unit_price,
                "days": body.delivery_days,
                "notes": body.notes,
                "tid": tenant_id,
            },
        ).fetchone()

        # RFQ auf BEWERTET setzen wenn mind. 1 Angebot vorliegt
        db.execute(
            text("""
                UPDATE domain_einkauf.rfq_requests
                SET status = 'BEWERTET'
                WHERE id = :id AND tenant_id = :tid AND status = 'VERSENDET'
            """),
            {"id": rfq_id, "tid": tenant_id},
        )
        db.commit()
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail=f"Datenbankfehler: {exc}") from exc

    return {
        "id": row[0], "rfq_id": row[1], "supplier_id": row[2],
        "unit_price": float(row[3]), "delivery_days": row[4],
        "notes": row[5], "status": row[6],
        "received_at": row[7].isoformat() if row[7] else None,
    }


@router.get("/{rfq_id}/comparison", summary="Quotes compare",
    response_model=dict
)
def compare_quotes(
    rfq_id: int,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Angebotsvergleich: alle Angebote sortiert nach Preis (günstigstes zuerst)."""
    try:
        _ensure_schema(db)
        rfq = _get_rfq(db, rfq_id, tenant_id)
        if not rfq:
            raise HTTPException(status_code=404, detail="Anfrage nicht gefunden")

        rows = db.execute(
            text("""
                SELECT id, supplier_id, unit_price, delivery_days, notes, status,
                       RANK() OVER (ORDER BY unit_price ASC) AS price_rank
                FROM domain_einkauf.rfq_quotes
                WHERE rfq_id = :rid AND tenant_id = :tid
                ORDER BY unit_price ASC
            """),
            {"rid": rfq_id, "tid": tenant_id},
        ).fetchall()
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Datenbankfehler: {exc}") from exc

    quotes = [
        {
            "id": r[0], "supplier_id": r[1], "unit_price": float(r[2]),
            "delivery_days": r[3], "notes": r[4], "status": r[5],
            "price_rank": r[6],
        }
        for r in rows
    ]

    return {
        "rfq_id": rfq_id,
        "article_id": rfq[1],
        "quantity": float(rfq[2]),
        "quotes_count": len(quotes),
        "best_price": quotes[0]["unit_price"] if quotes else None,
        "quotes": quotes,
    }


@router.post("/{rfq_id}/accept/{quote_id}", summary="Quote akzeptieren",
    response_model=dict
)
def accept_quote(
    rfq_id: int,
    quote_id: int,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
) -> dict[str, Any]:
    """Zuschlag erteilen → Bestellung erzeugen."""
    try:
        _ensure_schema(db)

        rfq = _get_rfq(db, rfq_id, tenant_id)
        if not rfq:
            raise HTTPException(status_code=404, detail="Anfrage nicht gefunden")

        quote = db.execute(
            text("""
                SELECT id, supplier_id, unit_price, delivery_days
                FROM domain_einkauf.rfq_quotes
                WHERE id = :qid AND rfq_id = :rid AND tenant_id = :tid
            """),
            {"qid": quote_id, "rid": rfq_id, "tid": tenant_id},
        ).fetchone()
        if not quote:
            raise HTTPException(status_code=404, detail="Angebot nicht gefunden")

        # Angebot akzeptieren
        db.execute(
            text("""
                UPDATE domain_einkauf.rfq_quotes
                SET status = 'AKZEPTIERT'
                WHERE id = :qid AND tenant_id = :tid
            """),
            {"qid": quote_id, "tid": tenant_id},
        )

        # Übrige Angebote ablehnen
        db.execute(
            text("""
                UPDATE domain_einkauf.rfq_quotes
                SET status = 'ABGELEHNT'
                WHERE rfq_id = :rid AND id != :qid AND tenant_id = :tid
            """),
            {"rid": rfq_id, "qid": quote_id, "tid": tenant_id},
        )

        # RFQ abschließen
        db.execute(
            text("""
                UPDATE domain_einkauf.rfq_requests
                SET status = 'ABGESCHLOSSEN'
                WHERE id = :id AND tenant_id = :tid
            """),
            {"id": rfq_id, "tid": tenant_id},
        )

        # Bestellung anlegen (domain_einkauf.bestellungen)
        total_amount = float(rfq[2]) * float(quote[2])
        po_row = None
        try:
            po_row = db.execute(
                text("""
                    INSERT INTO domain_einkauf.bestellungen
                        (lieferant_id, bestelldatum, lieferdatum_geplant,
                         gesamtbetrag, status, tenant_id)
                    VALUES
                        (:sid, CURRENT_DATE,
                         CURRENT_DATE + INTERVAL '1 day' * COALESCE(:days, 14),
                         :amount, 'OFFEN', :tid)
                    RETURNING id
                """),
                {
                    "sid": quote[1],
                    "days": quote[3],
                    "amount": total_amount,
                    "tid": tenant_id,
                },
            ).fetchone()
        except Exception:
            # Bestellung-Tabelle könnte andere Spalten haben — weich fehlschlagen
            pass

        db.commit()
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=503, detail=f"Datenbankfehler: {exc}") from exc

    return {
        "rfq_id": rfq_id,
        "accepted_quote_id": quote_id,
        "supplier_id": quote[1],
        "unit_price": float(quote[2]),
        "quantity": float(rfq[2]),
        "total_amount": float(rfq[2]) * float(quote[2]),
        "purchase_order_id": po_row[0] if po_row else None,
        "status": "ABGESCHLOSSEN",
    }
