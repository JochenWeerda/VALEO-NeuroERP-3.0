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

router = APIRouter()


def _ensure_tables(db: Session) -> None:
    try:
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS domain_pos.payment_methods (
                id TEXT PRIMARY KEY,
                method_code TEXT NOT NULL,
                name TEXT NOT NULL,
                is_active BOOLEAN DEFAULT TRUE,
                tenant_id TEXT NOT NULL
            )
        """))
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS domain_pos.promotions (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                promo_type TEXT NOT NULL,
                article_id TEXT,
                article_group TEXT,
                discount_value NUMERIC,
                min_quantity NUMERIC DEFAULT 1,
                valid_from DATE,
                valid_to DATE,
                is_active BOOLEAN DEFAULT TRUE,
                tenant_id TEXT NOT NULL
            )
        """))
        db.commit()
    except Exception:
        db.rollback()


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
    response_model=dict
)
async def list_payment_methods(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    _ensure_tables(db)
    try:
        rows = db.execute(
            text("SELECT * FROM domain_pos.payment_methods WHERE tenant_id = :tid AND is_active = TRUE"),
            {"tid": tenant_id},
        ).fetchall()
    except Exception:
        # Return defaults if table not yet populated
        return [
            {"method_code": "BAR", "name": "Bargeld"},
            {"method_code": "KARTE", "name": "EC-/Kreditkarte"},
            {"method_code": "SEPA", "name": "SEPA-Überweisung"},
        ]
    return [dict(r._mapping) for r in rows] or [
        {"method_code": "BAR", "name": "Bargeld"},
        {"method_code": "KARTE", "name": "EC-/Kreditkarte"},
    ]


@router.post("/checkout/split-payment", status_code=201, summary="Payment aufteilen",
    response_model=dict
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
    response_model=dict
)
async def list_promotions(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    _ensure_tables(db)
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
    response_model=dict
)
async def create_promotion(
    payload: PromotionIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    _ensure_tables(db)
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
    response_model=dict
)
async def check_promotion(
    payload: PromotionCheckIn,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    _ensure_tables(db)
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


# ── X/Z-Report ─────────────────────────────────────────────────────────────

@router.get("/x-report", summary="Report x",
    response_model=dict
)
async def x_report(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    try:
        rows = db.execute(text("""
            SELECT payment_method, SUM(amount) as total
            FROM domain_pos.pos_transactions
            WHERE tenant_id = :tid AND DATE(created_at) = CURRENT_DATE
            GROUP BY payment_method
        """), {"tid": tenant_id}).fetchall()
        total = sum(r.total or 0 for r in rows)
        return {
            "report_type": "X",
            "date": date.today().isoformat(),
            "total_eur": float(total),
            "by_payment_method": [{"method": r.payment_method, "total": float(r.total or 0)} for r in rows],
        }
    except Exception:
        return {"report_type": "X", "date": date.today().isoformat(), "total_eur": 0.0, "by_payment_method": []}


@router.get("/z-report/{report_date}", summary="Report z",
    response_model=dict
)
async def z_report(
    report_date: str,
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_tenant_id),
):
    try:
        rows = db.execute(text("""
            SELECT payment_method, SUM(amount) as total, COUNT(*) as count
            FROM domain_pos.pos_transactions
            WHERE tenant_id = :tid AND DATE(created_at) = :dt
            GROUP BY payment_method
        """), {"tid": tenant_id, "dt": report_date}).fetchall()
        total = sum(r.total or 0 for r in rows)
        return {
            "report_type": "Z",
            "date": report_date,
            "total_eur": float(total),
            "transaction_count": sum(r.count or 0 for r in rows),
            "by_payment_method": [{"method": r.payment_method, "total": float(r.total or 0)} for r in rows],
            "closed": True,
        }
    except Exception:
        return {"report_type": "Z", "date": report_date, "total_eur": 0.0, "closed": True}


@router.post("/checkout/preview", summary="Preview checkout",
    response_model=dict
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
