"""Wave 71 — Unit-Tests fuer contract_fixing_service (pure domain math)."""

from __future__ import annotations

import pytest
from decimal import Decimal


# ---------------------------------------------------------------------------
# contract_fixing_service  (pure Decimal math — keine DB, kein HTTP)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_effektiv_preis_basic() -> None:
    from app.services.contract_fixing_service import effektiv_preis
    result = effektiv_preis(Decimal("200.00"), Decimal("5.00"))
    assert result == Decimal("205.00")


@pytest.mark.unit
def test_effektiv_preis_zero_premium() -> None:
    from app.services.contract_fixing_service import effektiv_preis
    result = effektiv_preis(Decimal("200.00"), Decimal("0"))
    assert result == Decimal("200.00")


@pytest.mark.unit
def test_effektiv_preis_negative_premium() -> None:
    from app.services.contract_fixing_service import effektiv_preis
    result = effektiv_preis(Decimal("200.00"), Decimal("-10.00"))
    assert result == Decimal("190.00")


@pytest.mark.unit
def test_restmenge_basic() -> None:
    from app.services.contract_fixing_service import restmenge
    result = restmenge(Decimal("100"), Decimal("60"))
    assert result == Decimal("40")


@pytest.mark.unit
def test_restmenge_fully_fixed() -> None:
    from app.services.contract_fixing_service import restmenge
    result = restmenge(Decimal("100"), Decimal("100"))
    assert result == Decimal("0")


@pytest.mark.unit
def test_restmenge_nothing_fixed() -> None:
    from app.services.contract_fixing_service import restmenge
    result = restmenge(Decimal("100"), Decimal("0"))
    assert result == Decimal("100")


@pytest.mark.unit
def test_marktwert_offen_basic() -> None:
    from app.services.contract_fixing_service import marktwert_offen
    result = marktwert_offen(Decimal("40"), Decimal("220.00"))
    assert result == Decimal("8800.00")


@pytest.mark.unit
def test_marktwert_offen_zero_quantity() -> None:
    from app.services.contract_fixing_service import marktwert_offen
    result = marktwert_offen(Decimal("0"), Decimal("220.00"))
    assert result == Decimal("0")


@pytest.mark.unit
def test_mtm_fixiert_einkauf_profit() -> None:
    from app.services.contract_fixing_service import mtm_fixiert
    # Einkauf=True: fixed cheaper than market → positive P&L
    result = mtm_fixiert(Decimal("210"), Decimal("220"), Decimal("60"), einkauf=True)
    assert result > 0


@pytest.mark.unit
def test_mtm_fixiert_einkauf_loss() -> None:
    from app.services.contract_fixing_service import mtm_fixiert
    # Einkauf=True: fixed more expensive than market → negative P&L
    result = mtm_fixiert(Decimal("220"), Decimal("210"), Decimal("60"), einkauf=True)
    assert result < 0


@pytest.mark.unit
def test_mtm_fixiert_verkauf_inverted() -> None:
    from app.services.contract_fixing_service import mtm_fixiert
    # Verkauf=False: inverted sign vs einkauf
    result_buy = mtm_fixiert(Decimal("210"), Decimal("220"), Decimal("60"), einkauf=True)
    result_sell = mtm_fixiert(Decimal("210"), Decimal("220"), Decimal("60"), einkauf=False)
    assert result_buy == -result_sell


@pytest.mark.unit
def test_mtm_fixiert_zero_quantity() -> None:
    from app.services.contract_fixing_service import mtm_fixiert
    result = mtm_fixiert(Decimal("210"), Decimal("220"), Decimal("0"), einkauf=True)
    assert result == Decimal("0")


@pytest.mark.unit
def test_effektiv_preis_returns_decimal() -> None:
    from app.services.contract_fixing_service import effektiv_preis
    result = effektiv_preis(Decimal("150.5"), Decimal("3.2"))
    assert isinstance(result, Decimal)


@pytest.mark.unit
def test_restmenge_returns_decimal() -> None:
    from app.services.contract_fixing_service import restmenge
    result = restmenge(Decimal("500"), Decimal("200"))
    assert isinstance(result, Decimal)
    assert result == Decimal("300")
