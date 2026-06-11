"""Reine Logik-Tests des Kontrakt-Settlement (DOM-CON-004.4)."""

from __future__ import annotations

import pytest

from app.services.contract_settlement_service import movement_state

pytestmark = pytest.mark.unit


def test_movement_state_offen():
    assert movement_state(is_storniert=False, is_invoiced=False) == "offen"


def test_movement_state_abgerechnet():
    assert movement_state(is_storniert=False, is_invoiced=True) == "abgerechnet"


def test_movement_state_storniert_hat_vorrang():
    # Storniert übersteuert abgerechnet (defensiv, sollte fachlich nicht koexistieren).
    assert movement_state(is_storniert=True, is_invoiced=False) == "storniert"
    assert movement_state(is_storniert=True, is_invoiced=True) == "storniert"
