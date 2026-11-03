"""Fachliche Wertetypen: Backend-Regeln gegen die gemeinsamen Beispiele; Frontend-Kopie ohne Drift.

Das Frontend prueft dieselben Beispiele in feldklassen.test.tsx - zusammen halten beide Tests die Masken und
den Server deckungsgleich (eine Quelle: config/wertetypen.json).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from app.core import wertetypen
from app.core.screen_governance import FIELD_TYPES, TEXT_FORMATS

pytestmark = pytest.mark.unit
ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("format_name", sorted(wertetypen.beispiele()))
def test_beispiele_gelten_im_backend(format_name):
    faelle = wertetypen.beispiele()[format_name]
    assert all(wertetypen.wert_gueltig(format_name, w) for w in faelle["gueltig"]), faelle["gueltig"]
    assert not any(wertetypen.wert_gueltig(format_name, w) for w in faelle["ungueltig"]), faelle["ungueltig"]


def test_jedes_format_hat_beispiele_und_ist_in_der_governance():
    assert set(wertetypen.beispiele()) == TEXT_FORMATS | {"period"}
    assert "period" in FIELD_TYPES


def test_gs1_pruefziffer_wie_der_etikettendruck():
    from app.api.v1.endpoints.gs1_barcode import _gs1_mod10_check_digit

    for koerper in ("401234567890", "00012345600012345", "400638133393"):
        assert wertetypen.gs1_pruefziffer(koerper) == _gs1_mod10_check_digit(koerper)


def test_ust_id_debitoren_und_kreditoren_aus_einer_quelle():
    from fastapi import HTTPException

    from app.api.v1.endpoints import creditors, debtors

    for modul in (debtors, creditors):
        modul._validate_vat_id_format("DE123456789")
        with pytest.raises(HTTPException):
            modul._validate_vat_id_format("DE12345678")


def test_frontend_kopie_ohne_drift():
    lauf = subprocess.run([sys.executable, "scripts/generate_wertetypen_frontend.py", "--check"],
                          cwd=ROOT, capture_output=True, text=True)
    assert lauf.returncode == 0, lauf.stdout + lauf.stderr


@pytest.mark.parametrize("format_name,pruefer", [("iban", "validate_iban"), ("gln", "validate_gln")])
def test_aeltere_pruefer_urteilen_wie_die_wertetypen(format_name, pruefer):
    """validation_contracts (Banken, Kontoauszugsimport, Annahme) bleibt deckungsgleich mit der Maske."""
    from app.core import validation_contracts

    funktion = getattr(validation_contracts, pruefer)
    faelle = wertetypen.beispiele()[format_name]
    assert all(funktion(w).is_valid for w in faelle["gueltig"]), faelle["gueltig"]
    assert not any(funktion(w).is_valid for w in faelle["ungueltig"]), faelle["ungueltig"]


@pytest.mark.parametrize("spalte,gueltig", [
    ({"key": "m", "label": "Menge", "renderKind": "quantity", "unit": "kg", "displayUnit": "dt"}, True),
    ({"key": "m", "label": "Menge", "renderKind": "quantity", "displayUnit": "Doppelzentner"}, True),
    ({"key": "m", "label": "Menge", "renderKind": "quantity", "displayUnit": "Sack"}, False),
    ({"key": "m", "label": "Menge", "renderKind": "number", "displayUnit": "dt"}, False),
])
def test_anzeigeeinheit_nur_fuer_umrechenbare_mengen(spalte, gueltig):
    """Landhandel zeigt Masse in dt (agrar_units); Zaehleinheiten wie Sack sind nie global umrechenbar."""
    from app.core.screen_governance import validate_screen_definition

    definition = {"schemaVersion": 1, "id": "probe/menge", "title": "Menge", "mode": "list", "domain": "lager",
                  "layout": {"floorplan": "worklist", "density": "compact", "tableProfile": "inventory"},
                  "tables": [{"key": "t", "label": "T", "columns": [spalte]}]}
    fehler = [f for f in validate_screen_definition(definition) if "displayUnit" in f]
    assert (not fehler) is gueltig, fehler


def test_frontend_kennt_dieselben_einheiten_wie_agrar_units():
    import json

    from app.core import agrar_units

    kopie = json.loads((ROOT / "packages/frontend-web/src/components/mask-builder/runtime/wertetypen.generated.json")
                       .read_text(encoding="utf-8"))["einheiten"]
    assert kopie["masseInKg"] == {e: float(f) for e, f in agrar_units.MASSE_IN_KG.items()}
    assert kopie["anzeigeMasse"] == "dt"
    assert set(kopie["zaehleinheiten"]) == set(agrar_units.ZAEHLEINHEITEN)


@pytest.mark.parametrize("spalte,gueltig", [
    ({"key": "p", "label": "Preis je dt", "renderKind": "currency", "pricePer": "t", "displayPricePer": "dt"}, True),
    ({"key": "p", "label": "Preis je l", "renderKind": "currency", "pricePer": "hl", "displayPricePer": "l"}, True),
    ({"key": "p", "label": "Preis", "renderKind": "currency", "pricePer": "t", "displayPricePer": "l"}, False),
    ({"key": "p", "label": "Preis", "renderKind": "currency", "pricePer": "sack", "displayPricePer": "kg"}, False),
    ({"key": "p", "label": "Preis", "renderKind": "number", "pricePer": "t", "displayPricePer": "dt"}, False),
])
def test_preis_je_einheit_nur_exakt_umrechenbar(spalte, gueltig):
    """Landhandel zeigt Preise je dt (100 kg); Sack und andere Zaehleinheiten haben keinen globalen Faktor."""
    from app.core.screen_governance import validate_screen_definition

    definition = {"schemaVersion": 1, "id": "probe/preis", "title": "Preis", "mode": "list", "domain": "futtermittel",
                  "layout": {"floorplan": "worklist", "density": "compact", "tableProfile": "inventory"},
                  "tables": [{"key": "t", "label": "T", "columns": [spalte]}]}
    fehler = [f for f in validate_screen_definition(definition) if "pricePer" in f]
    assert (not fehler) is gueltig, fehler
