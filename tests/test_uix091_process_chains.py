"""UIX-091: Prozessketten-Konfiguration valide (screenIds existieren).

Reine Unit-Tests: `pytest tests/test_uix091_process_chains.py --noconftest -p no:cacheprovider --no-cov -q -o addopts=""`.
"""
from __future__ import annotations

import pytest

from scripts.check_process_chains import validate

pytestmark = pytest.mark.unit

KNOWN = {
    "agrar/kontrakte", "einkauf/anlieferavis", "qualitaet/reklamation",
    "lager/article-stock", "agrar/harvest-settlement", "sales/sales-order",
    "sales/delivery-note", "finance/ar-open-item", "finance/payment-run",
    "einkauf/anfrage", "einkauf/angebot", "einkauf/purchase-order",
    "finance/ap-invoice", "crm/lead", "crm/opportunity", "crm/customer-360",
}


def test_repo_config_ist_valide_gegen_bekannte_screen_ids():
    # Die ausgelieferte config nur gegen die (bekannten) nativen screenIds pruefen —
    # unabhaengig von der DB/Registry-Ladung.
    assert validate(known_screen_ids=KNOWN) == []


def test_unbekannte_screen_id_wird_gemeldet():
    config = {"chains": {"x": {"label": "X", "steps": [{"key": "a", "label": "A", "screenId": "gibts/nicht"}]}}}
    errors = validate(config=config, known_screen_ids=KNOWN)
    assert any("nicht in Registry" in e for e in errors)


def test_fehlende_steps_werden_gemeldet():
    errors = validate(config={"chains": {"x": {"label": "X"}}}, known_screen_ids=KNOWN)
    assert any("steps fehlen" in e for e in errors)


def test_doppelter_step_key_wird_gemeldet():
    config = {"chains": {"x": {"label": "X", "steps": [
        {"key": "a", "label": "A", "screenId": "crm/lead"},
        {"key": "a", "label": "A2", "screenId": "crm/opportunity"},
    ]}}}
    errors = validate(config=config, known_screen_ids=KNOWN)
    assert any("doppelter key" in e for e in errors)


def test_leere_chains_werden_gemeldet():
    assert validate(config={"chains": {}}, known_screen_ids=KNOWN) == ["chains fehlt oder leer"]
