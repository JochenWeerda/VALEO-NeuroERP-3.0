from __future__ import annotations

import asyncio
from datetime import date, timedelta

import pytest
from fastapi import HTTPException

from app.api.v1.endpoints import compliance_whistleblower_lksg as compliance_ext
from app.api.v1.endpoints import pos_payments_promotions as pos_ext


def test_lksg_risk_scoring_levels():
    payload = compliance_ext.LksgRiskAssessmentIn(
        supplier_id="SUP-1",
        country_code="DE",
        spend_eur=300_000,
        sector_risk=4,
        human_rights_flags=2,
        environmental_flags=1,
    )

    score = compliance_ext._risk_score(payload)

    assert score == 13
    assert compliance_ext._risk_level(score) == "HOCH"
    assert compliance_ext._risk_level(5) == "MITTEL"
    assert compliance_ext._risk_level(4) == "NIEDRIG"


def test_pos_promotions_apply_only_inside_validity_window():
    line = pos_ext.PosCartLine(article_id="A-1", quantity=2, unit_price=10, article_group="FUTTER")
    rule = pos_ext.PromotionRule(
        promotion_id="PROMO-1",
        label="Futter Aktion",
        promotion_type="PERCENT",
        value=10,
        article_group="FUTTER",
        valid_from=date.today() - timedelta(days=1),
        valid_to=date.today() + timedelta(days=1),
    )

    assert pos_ext._promotion_applies(line, rule)
    assert pos_ext._promotion_discount(line, rule) == 2.0


def test_pos_checkout_preview_supports_split_payment_and_change():
    payload = pos_ext.PosCheckoutPreviewIn(
        lines=[pos_ext.PosCartLine(article_id="A-1", quantity=2, unit_price=10, article_group="FUTTER")],
        promotions=[
            pos_ext.PromotionRule(
                promotion_id="P-1",
                label="Aktion",
                promotion_type="FIXED",
                value=3,
                article_group="FUTTER",
            )
        ],
        payments=[
            pos_ext.PosPaymentLine(method="BAR", amount=10),
            pos_ext.PosPaymentLine(method="KARTE", amount=10),
        ],
    )

    result = asyncio.run(pos_ext.preview_checkout(payload))

    assert result["subtotal"] == 20.0
    assert result["discount"] == 3.0
    assert result["total_due"] == 17.0
    assert result["change_due"] == 3.0
    assert result["ready_to_post"] is True


def test_pos_checkout_preview_rejects_underpayment():
    payload = pos_ext.PosCheckoutPreviewIn(
        lines=[pos_ext.PosCartLine(article_id="A-1", quantity=1, unit_price=20)],
        payments=[pos_ext.PosPaymentLine(method="BAR", amount=5)],
    )

    with pytest.raises(HTTPException) as exc:
        asyncio.run(pos_ext.preview_checkout(payload))

    assert exc.value.status_code == 422
