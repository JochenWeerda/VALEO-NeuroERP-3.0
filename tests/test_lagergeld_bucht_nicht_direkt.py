"""Lagergeld bucht nicht direkt ins Journal (M3, Journal-Schreiber-Ratsche).

Der Lagergeldlauf buchte bis 19.11.2026 Forderung an Erloes direkt ins Journal: ohne Umsatzsteuer, ohne offenen
Posten, und fehlende Konten legte er selbst an. Lagergeld ist eine Leistung an den Einlagerer und wird ueber die
Ausgangsrechnung gebucht. Der Lauf berechnet und protokolliert nur noch.
"""
from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException

from app.domains.inventory.api import storage_fees
from app.domains.inventory.api.storage_fees import StorageFeeRunRequest, run_storage_fee_engine

pytestmark = pytest.mark.unit


def test_die_direktbuchung_wird_abgewiesen_bevor_etwas_geschrieben_wird():
    db = MagicMock()
    with pytest.raises(HTTPException) as fehler:
        asyncio.run(run_storage_fee_engine(
            StorageFeeRunRequest(period="2026-10", post_to_ledger=True), db=db, _="admin", effective_tenant="t"))
    assert fehler.value.status_code == 422 and "Ausgangsrechnung" in fehler.value.detail
    assert db.method_calls == []


def test_der_lauf_bucht_standardmaessig_nicht():
    assert StorageFeeRunRequest(period="2026-10").post_to_ledger is False


def test_der_direktbuchungsweg_ist_entfernt():
    assert not hasattr(storage_fees, "_post_storage_fee_journal")
