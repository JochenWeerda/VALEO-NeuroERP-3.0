"""Executable Unit-Tests: HarvestAcceptance Schema-Validatoren (Sonar New-Code)."""
from __future__ import annotations

from datetime import date

import pytest
from pydantic import ValidationError

from app.api.v1.endpoints.harvest_acceptance import HarvestAcceptanceCreate


def test_harvest_create_requires_contract_for_fixed_pricing():
    with pytest.raises(ValidationError) as exc:
        HarvestAcceptanceCreate(
            delivery_date=date(2026, 11, 1),
            customer_id="C-1",
            pricing_mode="fixed_contract",
            contract_id=None,
        )
    assert "contract_id" in str(exc.value)


def test_harvest_create_derives_nuts2_from_postal():
    payload = HarvestAcceptanceCreate(
        delivery_date=date(2026, 11, 1),
        customer_id="C-1",
        origin_postal_code="20095",
        origin_country_code="DE",
        pricing_mode="spot_daily",
    )
    assert payload.origin_nuts2_code == "DE60"


def test_harvest_create_rejects_invalid_nuts2():
    with pytest.raises(ValidationError):
        HarvestAcceptanceCreate(
            delivery_date=date(2026, 11, 1),
            customer_id="C-1",
            origin_nuts2_code="INVALID",
            pricing_mode="spot_daily",
        )


def test_harvest_create_accepts_exchange_fix_later():
    payload = HarvestAcceptanceCreate(
        delivery_date=date(2026, 11, 1),
        customer_id="C-1",
        pricing_mode="exchange_fix_later",
        remarks="Börse später",
    )
    assert payload.pricing_mode == "exchange_fix_later"
    assert payload.acceptance_mode == "PURCHASE_AT_DELIVERY_PTBF"
