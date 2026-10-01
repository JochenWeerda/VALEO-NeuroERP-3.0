from __future__ import annotations
from datetime import date
from typing import Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.tenant import get_tenant_id

from app.api.v1.schemas.base import BaseSchema
from pydantic import ConfigDict as _ConfigDict


class PosPaymentOut(BaseSchema):
    model_config = _ConfigDict(extra="allow")


router = APIRouter()


#: Wortlaut, wenn die Migration nicht gelaufen ist. Frueher legte dieses Modul
#: die Tabellen zur Laufzeit selbst an (`_ensure_tables`) — das Schema hing
#: damit davon ab, ob jemand die Kasse geoeffnet hatte. Jetzt kommen sie aus
#: `pos_zahlarten_aktionen_20260930`.
_FEHLT = (
    "Kassentabellen fehlen — Migration pos_zahlarten_aktionen_20260930 "
    "ausfuehren."
)

#: Startkonfiguration, wenn ein Haus noch keine Zahlart eingerichtet hat.
#: Bewusst **nur** fuer den leeren Fall, nicht fuer den Fehlerfall: Eine
#: Datenbankstoerung sah zuvor aus wie eine Konfiguration, und ein Kassierer
#: haette eine Zahlart waehlen koennen, die das Haus gar nicht annimmt.
_START_ZAHLARTEN = [
    {"method_code": "BAR", "name": "Bargeld"},
    {"method_code": "KARTE", "name": "EC-/Kreditkarte"},
    {"method_code": "SEPA", "name": "SEPA-Überweisung"},
]


# ── Schemas ────────────────────────────────────────────────────────────────

class PaymentLine(BaseModel):
    method_code: str
    amount: float


class SplitPaymentIn(BaseModel):
    cart_total: float
    payments: list[PaymentLine]
    cart_ref: Optional[str] = None


class PromotionIn(BaseModel):
    name: str
    promo_type: str  # PROZENT/BETRAG/BOGO/MENGENSTAFFEL
    article_id: Optional[str] = None
    article_group: Optional[str] = None
    discount_value: float
    min_quantity: float = 1.0
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None


class PromotionCheckIn(BaseModel):
    article_id: str
    quantity: float
    price: float


# ── Payment Methods ────────────────────────────────────────────────────────

@router.get("/payment-methods", summary="Payment methods auflisten",
    response_model=list[PosPaymentOut]
)
async def list_payment_methods(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    try:
        rows = db.execute(
            text("SELECT * FROM domain_pos.payment_methods WHERE tenant_id = :tid AND is_active = TRUE"),
            {"tid": tenant_id},
        ).fetchall()
    except Exception as fehler:
        # Kein Rueckfall auf erfundene Zahlarten: Eine Stoerung ist keine
        # Konfiguration. Wer hier BAR/KARTE/SEPA sieht, glaubt, das Haus nehme
        # sie an.
        raise HTTPException(status_code=503, detail=_FEHLT) from fehler
    # Nur wenn das Haus wirklich nichts gepflegt hat — nicht bei einer
    # Stoerung, die oben als 503 herausgeht.
    return [dict(r._mapping) for r in rows] or list(_START_ZAHLARTEN)


@router.post("/checkout/split-payment", status_code=201, summary="Payment aufteilen",
    response_model=PosPaymentOut
)
async def split_payment(
    payload: SplitPaymentIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    total_paid = round(sum(p.amount for p in payload.payments), 2)
    cart_total = round(payload.cart_total, 2)
    tolerance = 0.01
    if abs(total_paid - cart_total) > tolerance:
        raise HTTPException(422, f"Zahlungssumme {total_paid} stimmt nicht mit Warenkorbsumme {cart_total} überein")
    receipt_id = str(uuid4())
    return {
        "receipt_id": receipt_id,
        "payments_applied": [{"method_code": p.method_code, "amount": p.amount} for p in payload.payments],
        "change_amount": max(0.0, round(total_paid - cart_total, 2)),
        "cart_ref": payload.cart_ref,
    }


# ── Promotions ─────────────────────────────────────────────────────────────

@router.get("/promotions", summary="Promotions auflisten",
    response_model=list[PosPaymentOut]
)
async def list_promotions(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    try:
        rows = db.execute(
            text("""
                SELECT * FROM domain_pos.promotions
                WHERE tenant_id = :tid AND is_active = TRUE
                AND (valid_to IS NULL OR valid_to >= CURRENT_DATE)
                ORDER BY name
            """),
            {"tid": tenant_id},
        ).fetchall()
    except Exception as e:
        raise HTTPException(503, f"Datenbank nicht erreichbar: {e}")
    return [dict(r._mapping) for r in rows]


@router.post("/promotions", status_code=201, summary="Promotion anlegen",
    response_model=PosPaymentOut
)
async def create_promotion(
    payload: PromotionIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    promo_id = str(uuid4())
    try:
        db.execute(text("""
            INSERT INTO domain_pos.promotions
              (id, name, promo_type, article_id, article_group, discount_value,
               min_quantity, valid_from, valid_to, tenant_id)
            VALUES (:id, :name, :ptype, :art_id, :art_grp, :disc, :min_qty, :vf, :vt, :tid)
        """), {
            "id": promo_id, "name": payload.name, "ptype": payload.promo_type,
            "art_id": payload.article_id, "art_grp": payload.article_group,
            "disc": payload.discount_value, "min_qty": payload.min_quantity,
            "vf": payload.valid_from, "vt": payload.valid_to, "tid": tenant_id,
        })
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(503, str(e))
    return {"id": promo_id, **payload.model_dump()}


@router.post("/promotions/check", summary="Promotion prüfen",
    response_model=PosPaymentOut
)
async def check_promotion(
    payload: PromotionCheckIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    today = date.today().isoformat()
    try:
        rows = db.execute(text("""
            SELECT * FROM domain_pos.promotions
            WHERE tenant_id = :tid AND is_active = TRUE
              AND (article_id = :art_id OR article_id IS NULL)
              AND (valid_from IS NULL OR valid_from <= :today)
              AND (valid_to IS NULL OR valid_to >= :today)
              AND min_quantity <= :qty
            ORDER BY discount_value DESC
            LIMIT 1
        """), {"tid": tenant_id, "art_id": payload.article_id,
               "today": today, "qty": payload.quantity}).fetchall()
    except Exception:
        return {"applicable": False, "discount_amount": 0.0, "promotion_name": None}

    if not rows:
        return {"applicable": False, "discount_amount": 0.0, "promotion_name": None}

    promo = dict(rows[0]._mapping)
    discount = 0.0
    if promo["promo_type"] == "PROZENT":
        discount = round(payload.price * payload.quantity * promo["discount_value"] / 100, 2)
    elif promo["promo_type"] == "BETRAG":
        discount = round(min(promo["discount_value"], payload.price * payload.quantity), 2)

    return {
        "applicable": True,
        "discount_amount": discount,
        "promotion_name": promo["name"],
        "promo_type": promo["promo_type"],
    }


# ── X/Z-Report ──────────────────────────────────────────────

#: Der Kassenumsatz liegt in ``domain_docflow.pos_fiscal_transactions`` —
#: dort schreibt ihn der Fiskalisierungsdienst mit Signatur, Geschaeftstag und
#: Zahlarten-Aufteilung. Bis zum 01.10.2026 lasen X- und Z-Bericht
#: ``domain_pos.pos_transactions``: ein Schema, in dem diese Tabelle nicht
#: liegt. Jede Abfrage scheiterte, und das ``except`` meldete 0,00 Euro.
_UMSATZ_JE_ZAHLART = """
    SELECT z.schluessel            AS payment_method,
           SUM((z.wert)::numeric)  AS total,
           COUNT(*)                AS anzahl
    FROM domain_docflow.pos_fiscal_transactions t
    CROSS JOIN LATERAL jsonb_each_text(COALESCE(t.payment_breakdown, '{}'::jsonb))
        AS z(schluessel, wert)
    WHERE t.tenant_id = :tid AND t.business_date = :tag
    GROUP BY z.schluessel
    ORDER BY z.schluessel
"""

#: Kennzahlen des Tages, unabhaengig von der Zahlart: Bruttoumsatz, Anzahl der
#: Vorgaenge und — fachlich das Wichtigste — wie viele davon **nicht**
#: abgeschlossen sind. Ein Z-Bon ueber unfertige Vorgaenge ist kein Abschluss.
_TAGESKENNZAHLEN = """
    SELECT COALESCE(SUM(gross_total), 0) AS brutto,
           COUNT(*)                      AS vorgaenge,
           COUNT(*) FILTER (WHERE state <> 'FINISHED') AS unfertig
    FROM domain_docflow.pos_fiscal_transactions
    WHERE tenant_id = :tid AND business_date = :tag
"""

#: Ob der Tag abgeschlossen ist, weiss der Tagesabschluss
#: (``pos_tagesabschluss_service``, Zustandsmaschine mit TSE und DSFinV-K) —
#: nicht der Bericht, der ihn anzeigt. Vorher stand im Z-Bon ``closed: True``
#: als Zuweisung.
_ABSCHLUSS_STAND = """
    SELECT status
    FROM domain_pos.pos_tagesabschluesse
    WHERE tenant_id = :tid AND datum = :tag
    ORDER BY updated_at DESC NULLS LAST, created_at DESC
    LIMIT 1
"""


def _tagesbericht(db: Session, tenant_id: str, tag: str) -> dict:
    """Liest einen Kassentag. Eine Stoerung wird gemeldet, nicht zu Null."""
    try:
        kennzahlen = db.execute(text(_TAGESKENNZAHLEN), {"tid": tenant_id, "tag": tag}).mappings().one()
        zahlarten = db.execute(text(_UMSATZ_JE_ZAHLART), {"tid": tenant_id, "tag": tag}).mappings().all()
    except Exception as fehler:
        # Kein Nullbericht: Bei einer Kasse ist "0,00 Euro" eine Aussage ueber
        # den Tag, keine ueber die Datenbank. Wer sie glaubt, verbucht einen
        # umsatzlosen Tag und verliert den Kassenbestand aus dem Blick.
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail="Kassenumsatz ist derzeit nicht lesbar — Bericht nicht aussagefaehig.",
        ) from fehler

    return {
        "brutto": float(kennzahlen["brutto"] or 0),
        "vorgaenge": int(kennzahlen["vorgaenge"] or 0),
        "unfertig": int(kennzahlen["unfertig"] or 0),
        "zahlarten": [
            {
                "method": z["payment_method"],
                "total": float(z["total"] or 0),
                "count": int(z["anzahl"] or 0),
            }
            for z in zahlarten
        ],
    }


@router.get("/x-report", summary="Report x",
    response_model=PosPaymentOut
)
async def x_report(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Zwischenbericht des laufenden Tages. Schliesst nichts ab."""
    heute = date.today().isoformat()
    bericht = _tagesbericht(db, tenant_id, heute)
    return {
        "report_type": "X",
        "date": heute,
        "total_eur": bericht["brutto"],
        "transaction_count": bericht["vorgaenge"],
        "unfinished_count": bericht["unfertig"],
        "by_payment_method": bericht["zahlarten"],
    }


@router.get("/z-report/{report_date}", summary="Report z",
    response_model=PosPaymentOut
)
async def z_report(
    report_date: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Tagesbericht. ``closed`` kommt aus dem Tagesabschluss, nicht von hier."""
    bericht = _tagesbericht(db, tenant_id, report_date)
    try:
        stand = db.execute(text(_ABSCHLUSS_STAND), {"tid": tenant_id, "tag": report_date}).scalar()
    except Exception as fehler:
        db.rollback()
        raise HTTPException(
            status_code=503,
            detail="Stand des Tagesabschlusses ist derzeit nicht lesbar.",
        ) from fehler

    return {
        "report_type": "Z",
        "date": report_date,
        "total_eur": bericht["brutto"],
        "transaction_count": bericht["vorgaenge"],
        "unfinished_count": bericht["unfertig"],
        "by_payment_method": bericht["zahlarten"],
        "closing_status": stand,
        "closed": stand == "ABGESCHLOSSEN",
    }


@router.post("/checkout/preview", summary="Preview checkout",
    response_model=PosPaymentOut
)
async def checkout_preview(
    payload: SplitPaymentIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    """Vorschau-Kalkulation ohne Verbuchung — prüft Zahlungssumme und gibt Wechselgeld zurück."""
    total_paid = round(sum(p.amount for p in payload.payments), 2)
    cart_total = round(payload.cart_total, 2)
    difference = round(total_paid - cart_total, 2)
    return {
        "cart_total": cart_total,
        "total_paid": total_paid,
        "difference": difference,
        "change_amount": max(0.0, difference),
        "valid": abs(difference) <= 0.01,
        "payments": [{"method_code": p.method_code, "amount": p.amount} for p in payload.payments],
    }
