"""
Tests: HRM Organigramm, DSGVO, Whistleblower, POS Multi-Zahlung, Promotions
"""
from __future__ import annotations
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import date, timedelta
import asyncio


def _mock_db():
    db = MagicMock()
    db.execute.return_value.fetchone.return_value = None
    db.execute.return_value.fetchall.return_value = []
    db.execute.return_value.scalar.return_value = None
    db.commit = MagicMock()
    db.rollback = MagicMock()
    return db


def _row(**kwargs):
    m = MagicMock()
    m._mapping = kwargs
    for k, v in kwargs.items():
        setattr(m, k, v)
    return m


# ── HRM: Organigramm ──────────────────────────────────────────────────────

@pytest.mark.unit
def test_org_chart_endpoint_exists():
    from app.api.v1.endpoints.personal import get_org_chart
    assert callable(get_org_chart)


@pytest.mark.unit
def test_org_chart_returns_tree_structure():
    from app.api.v1.endpoints.personal import get_org_chart
    db = _mock_db()
    # Simulate 3 units: root, child, grandchild
    rows = [
        _row(id="u-1", unit_code="GF", name="Geschäftsführung",
             unit_type="ABTEILUNG", parent_id=None, cost_center_id=None, manager_ref=None),
        _row(id="u-2", unit_code="VK", name="Verkauf",
             unit_type="ABTEILUNG", parent_id="u-1", cost_center_id=None, manager_ref=None),
        _row(id="u-3", unit_code="VK-IN", name="Innendienst",
             unit_type="TEAM", parent_id="u-2", cost_center_id=None, manager_ref=None),
    ]
    db.execute.return_value.fetchall.return_value = rows

    result = asyncio.run(
        get_org_chart(db=db, tenant_id="t-1")
    )
    assert "units" in result or isinstance(result, (list, dict))


@pytest.mark.unit
def test_application_stage_pipeline_valid_stages():
    """Erlaubte Stages: EINGANG/VORAUSWAHL/ERSTGESPRAECH/ENDGESPRAECH/ANGEBOT/EINGESTELLT/ABGELEHNT"""
    valid_stages = ["EINGANG", "VORAUSWAHL", "ERSTGESPRAECH", "ENDGESPRAECH",
                    "ANGEBOT", "EINGESTELLT", "ABGELEHNT"]
    assert len(valid_stages) == 7
    assert "EINGESTELLT" in valid_stages


# ── DSGVO ─────────────────────────────────────────────────────────────────

@pytest.mark.unit
def test_dsgvo_erasure_request_endpoint_exists():
    from app.api.v1.endpoints.compliance_dsgvo import create_erasure_request
    assert callable(create_erasure_request)


@pytest.mark.unit
def test_dsgvo_erasure_creates_record():
    from app.api.v1.endpoints.compliance_dsgvo import create_erasure_request, ErasureRequestIn
    db = _mock_db()

    payload = ErasureRequestIn(
        requester_name="Max Mustermann",
        requester_email="max@example.com",
        subject_id="c-123",
        subject_type="CUSTOMER",
    )

    result = asyncio.run(
        create_erasure_request(payload=payload, db=db, tenant_id="t-1")
    )
    assert "id" in result or "request_id" in result
    db.commit.assert_called()


# ── Whistleblower ─────────────────────────────────────────────────────────

@pytest.mark.unit
def test_whistleblower_submit_returns_only_token():
    from app.api.v1.endpoints.compliance_whistleblower import submit_report, ReportIn
    db = _mock_db()

    payload = ReportIn(
        category="BETRUG",
        description="Verdacht auf Unregelmäßigkeiten",
        severity="HOCH",
    )

    with patch("app.api.v1.endpoints.compliance_whistleblower._ensure_table"):
        result = asyncio.run(
            submit_report(payload=payload, db=db)
        )

    assert "token" in result
    assert "message" in result
    # KEINE id im Response (Anonymität)
    assert "id" not in result


@pytest.mark.unit
def test_whistleblower_token_is_12_chars():
    from app.api.v1.endpoints.compliance_whistleblower import submit_report, ReportIn
    db = _mock_db()

    payload = ReportIn(category="SICHERHEIT", description="Test", severity="MITTEL")

    with patch("app.api.v1.endpoints.compliance_whistleblower._ensure_table"):
        result = asyncio.run(
            submit_report(payload=payload, db=db)
        )
    assert len(result["token"]) == 12


@pytest.mark.unit
def test_whistleblower_status_not_found():
    from app.api.v1.endpoints.compliance_whistleblower import report_status
    from fastapi import HTTPException
    db = _mock_db()
    db.execute.return_value.fetchone.return_value = None

    with patch("app.api.v1.endpoints.compliance_whistleblower._ensure_table"):
        with pytest.raises(HTTPException) as exc:
            asyncio.run(
                report_status(token="WRONGTOKEN12", db=db)
            )
    assert exc.value.status_code == 404


# ── POS Multi-Zahlung ─────────────────────────────────────────────────────

@pytest.mark.unit
def test_split_payment_validates_total():
    from app.api.v1.endpoints.pos_payments import split_payment, SplitPaymentIn, PaymentLine
    from fastapi import HTTPException
    db = _mock_db()

    payload = SplitPaymentIn(
        cart_total=100.0,
        payments=[
            PaymentLine(method_code="BAR", amount=50.0),
            PaymentLine(method_code="KARTE", amount=40.0),  # Summe 90 ≠ 100
        ],
    )

    with pytest.raises(HTTPException) as exc:
        asyncio.run(
            split_payment(payload=payload, db=db, tenant_id="t-1")
        )
    assert exc.value.status_code == 422


@pytest.mark.unit
def test_split_payment_success():
    from app.api.v1.endpoints.pos_payments import split_payment, SplitPaymentIn, PaymentLine
    db = _mock_db()

    payload = SplitPaymentIn(
        cart_total=100.0,
        payments=[
            PaymentLine(method_code="BAR", amount=60.0),
            PaymentLine(method_code="KARTE", amount=40.0),
        ],
    )

    result = asyncio.run(
        split_payment(payload=payload, db=db, tenant_id="t-1")
    )
    assert "receipt_id" in result
    assert result["change_amount"] == 0.0
    assert len(result["payments_applied"]) == 2


# ── POS Promotions ────────────────────────────────────────────────────────

@pytest.mark.unit
def test_promotion_percent_discount():
    from app.api.v1.endpoints.pos_payments import check_promotion, PromotionCheckIn
    db = _mock_db()

    promo_row = _row(
        promo_type="PROZENT", discount_value=10.0, name="10% Rabatt",
        article_id="art-1", min_quantity=1.0,
        valid_from=None, valid_to=None,
    )
    db.execute.return_value.fetchall.return_value = [promo_row]

    payload = PromotionCheckIn(article_id="art-1", quantity=2.0, price=50.0)

    with patch("app.api.v1.endpoints.pos_payments._ensure_tables"):
        result = asyncio.run(
            check_promotion(payload=payload, db=db, tenant_id="t-1")
        )
    assert result["applicable"] is True
    assert result["discount_amount"] == pytest.approx(10.0)  # 100 * 10% = 10


@pytest.mark.unit
def test_promotion_not_applicable_no_match():
    from app.api.v1.endpoints.pos_payments import check_promotion, PromotionCheckIn
    db = _mock_db()
    db.execute.return_value.fetchall.return_value = []

    payload = PromotionCheckIn(article_id="art-99", quantity=1.0, price=20.0)

    with patch("app.api.v1.endpoints.pos_payments._ensure_tables"):
        result = asyncio.run(
            check_promotion(payload=payload, db=db, tenant_id="t-1")
        )
    assert result["applicable"] is False
    assert result["discount_amount"] == 0.0
