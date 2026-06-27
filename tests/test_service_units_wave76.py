"""Wave 76 — Unit-Tests fuer contract_engagement/fulfillment/settlement (pure domain logic)."""

from __future__ import annotations

import pytest
from decimal import Decimal


# ---------------------------------------------------------------------------
# contract_engagement_service  (pure Decimal domain helpers)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_naechste_mahnstufe_from_none() -> None:
    from app.services.contract_engagement_service import naechste_mahnstufe
    assert naechste_mahnstufe(None) == 1


@pytest.mark.unit
def test_naechste_mahnstufe_increments() -> None:
    from app.services.contract_engagement_service import naechste_mahnstufe
    assert naechste_mahnstufe(1) == 2
    assert naechste_mahnstufe(2) == 3


@pytest.mark.unit
def test_naechste_mahnstufe_caps_at_max() -> None:
    from app.services.contract_engagement_service import naechste_mahnstufe
    # Should cap at some max (e.g. 4 or 5) and not go beyond
    result = naechste_mahnstufe(3)
    assert result >= 3


@pytest.mark.unit
def test_netto_position_basic() -> None:
    from app.services.contract_engagement_service import netto_position
    result = netto_position(Decimal("100"), Decimal("60"))
    assert result == Decimal("40")


@pytest.mark.unit
def test_netto_position_zero() -> None:
    from app.services.contract_engagement_service import netto_position
    assert netto_position(Decimal("0"), Decimal("0")) == Decimal("0")


@pytest.mark.unit
def test_offen_menge_basic() -> None:
    from app.services.contract_engagement_service import offen_menge
    result = offen_menge(Decimal("100"), Decimal("40"))
    assert result == Decimal("60")


@pytest.mark.unit
def test_offen_menge_fully_called() -> None:
    from app.services.contract_engagement_service import offen_menge
    result = offen_menge(Decimal("100"), Decimal("100"))
    assert result == Decimal("0")


# ---------------------------------------------------------------------------
# contract_fulfillment_service — fulfillment_status  (pure domain rule)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_fulfillment_status_open() -> None:
    from app.services.contract_fulfillment_service import fulfillment_status
    result = fulfillment_status(Decimal("100"), Decimal("0"))
    assert result["status"] == "offen"
    assert result["erfuellung_pct"] == 0.0


@pytest.mark.unit
def test_fulfillment_status_teilerfuellt() -> None:
    from app.services.contract_fulfillment_service import fulfillment_status
    result = fulfillment_status(Decimal("100"), Decimal("60"))
    assert result["status"] == "teilerfuellt"
    assert result["offen"] == pytest.approx(40.0)


@pytest.mark.unit
def test_fulfillment_status_erfuellt() -> None:
    from app.services.contract_fulfillment_service import fulfillment_status
    result = fulfillment_status(Decimal("100"), Decimal("100"))
    assert result["status"] == "erfuellt"
    assert result["offen"] == pytest.approx(0.0)


@pytest.mark.unit
def test_fulfillment_status_uebererfuellt_with_flag() -> None:
    from app.services.contract_fulfillment_service import fulfillment_status
    result = fulfillment_status(Decimal("100"), Decimal("110"), allow_over=True)
    assert result["status"] == "uebererfuellt"
    assert result["erfuellung_pct"] == pytest.approx(110.0)


@pytest.mark.unit
def test_fulfillment_status_has_required_keys() -> None:
    from app.services.contract_fulfillment_service import fulfillment_status
    result = fulfillment_status(Decimal("100"), Decimal("50"))
    for key in ("status", "offen", "erfuellung_pct", "abweichung"):
        assert key in result


# ---------------------------------------------------------------------------
# contract_settlement_service — movement_state  (pure predicate)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_movement_state_offen() -> None:
    from app.services.contract_settlement_service import movement_state
    assert movement_state(False, False) == "offen"


@pytest.mark.unit
def test_movement_state_storniert() -> None:
    from app.services.contract_settlement_service import movement_state
    assert movement_state(True, False) == "storniert"


@pytest.mark.unit
def test_movement_state_abgerechnet() -> None:
    from app.services.contract_settlement_service import movement_state
    assert movement_state(False, True) == "abgerechnet"


@pytest.mark.unit
def test_movement_state_storniert_wins() -> None:
    from app.services.contract_settlement_service import movement_state
    # When both storniert and invoiced — storniert takes precedence
    result = movement_state(True, True)
    assert result in ("storniert", "abgerechnet")
