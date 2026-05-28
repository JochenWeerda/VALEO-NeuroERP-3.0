"""POS payment split and promotions preview endpoints."""

from __future__ import annotations

from datetime import date
from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.api.v1.schemas.base import BaseSchema
from app.api.v1.schemas.base import CompatFlexOut
from app.api.v1.schemas.pos_payments_promotions_schemas import PosPaymentsPromotionsOut


router = APIRouter(prefix="/pos", tags=["pos", "payments", "promotions"])

PaymentMethod = Literal["BAR", "KARTE", "SEPA", "GUTSCHEIN", "KUNDENKONTO"]
PromotionType = Literal["PERCENT", "FIXED"]


class PosCartLine(BaseModel):
    article_id: str = Field(..., min_length=1)
    quantity: float = Field(..., gt=0)
    unit_price: float = Field(..., ge=0)
    article_group: str | None = None


class PosPaymentLine(BaseModel):
    method: PaymentMethod
    amount: float = Field(..., gt=0)
    reference: str | None = None


class PromotionRule(BaseModel):
    promotion_id: str
    label: str
    promotion_type: PromotionType
    value: float = Field(..., gt=0)
    article_id: str | None = None
    article_group: str | None = None
    valid_from: date | None = None
    valid_to: date | None = None


class PosCheckoutPreviewIn(BaseModel):
    lines: list[PosCartLine] = Field(..., min_length=1)
    payments: list[PosPaymentLine] = Field(default_factory=list)
    promotions: list[PromotionRule] = Field(default_factory=list)


def _line_gross(line: PosCartLine) -> float:
    return round(line.quantity * line.unit_price, 2)


def _promotion_applies(line: PosCartLine, rule: PromotionRule, today: date | None = None) -> bool:
    current = today or date.today()
    if rule.valid_from and current < rule.valid_from:
        return False
    if rule.valid_to and current > rule.valid_to:
        return False
    if rule.article_id and rule.article_id != line.article_id:
        return False
    if rule.article_group and rule.article_group != line.article_group:
        return False
    return bool(rule.article_id or rule.article_group)


def _promotion_discount(line: PosCartLine, rule: PromotionRule) -> float:
    base = _line_gross(line)
    if rule.promotion_type == "PERCENT":
        return round(base * min(rule.value, 100.0) / 100.0, 2)
    return round(min(rule.value, base), 2)


@router.get("/payment-methods", summary="Payment methods auflisten",
    response_model=PosPaymentsPromotionsOut
)
async def list_payment_methods() -> dict:
    return {
        "methods": [
            {"id": "BAR", "label": "Bar", "splitAllowed": True},
            {"id": "KARTE", "label": "Karte", "splitAllowed": True},
            {"id": "SEPA", "label": "SEPA", "splitAllowed": True},
            {"id": "GUTSCHEIN", "label": "Gutschein", "splitAllowed": True},
            {"id": "KUNDENKONTO", "label": "Kundenkonto", "splitAllowed": True},
        ]
    }


@router.post("/promotions/simulate", summary="Promotions simulate",
    response_model=PosPaymentsPromotionsOut
)
async def simulate_promotions(payload: PosCheckoutPreviewIn) -> dict:
    discounts = []
    total_discount = 0.0
    for line in payload.lines:
        for rule in payload.promotions:
            if _promotion_applies(line, rule):
                amount = _promotion_discount(line, rule)
                if amount > 0:
                    discounts.append({
                        "article_id": line.article_id,
                        "promotion_id": rule.promotion_id,
                        "label": rule.label,
                        "discount": amount,
                    })
                    total_discount += amount
    return {"discounts": discounts, "total_discount": round(total_discount, 2)}


@router.post("/checkout/preview", summary="Checkout vorschauen",
    response_model=PosPaymentsPromotionsOut
)
async def preview_checkout(payload: PosCheckoutPreviewIn) -> dict:
    subtotal = round(sum(_line_gross(line) for line in payload.lines), 2)
    promotion_result = await simulate_promotions(payload)
    total_discount = float(promotion_result["total_discount"])
    total_due = round(max(0.0, subtotal - total_discount), 2)
    paid = round(sum(payment.amount for payment in payload.payments), 2)
    difference = round(paid - total_due, 2)

    if payload.payments and difference < 0:
        raise HTTPException(
            status_code=422,
            detail=f"Zahlbetrag fehlt: {abs(difference):.2f} EUR",
        )

    return {
        "subtotal": subtotal,
        "discount": total_discount,
        "total_due": total_due,
        "paid": paid,
        "change_due": difference if difference > 0 else 0.0,
        "payment_split": [payment.model_dump() for payment in payload.payments],
        "promotions": promotion_result["discounts"],
        "ready_to_post": not payload.payments or difference >= 0,
    }
