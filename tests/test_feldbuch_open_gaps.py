"""
Offene Lastenheft-Gaps (TDD): Stammdaten, Aussaat, Beregnung, AUM, QS,
Lagerverbrauch, Schlaginfo-Druck, Offline-Queue.
"""
from __future__ import annotations

import os
import sys
from datetime import date, datetime, timezone

import pytest

_ROOT = os.path.join(os.path.dirname(__file__), "..")
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


# ── ASK-MST-001 Stammdaten-Resolver ─────────────────────────────────────────

def test_resolve_duenger_applies_nutrients():
    from app.agrar.feldbuch.stammdaten import resolve_mittel

    catalog = {
        "duenger": [
            {"id": "d1", "name": "KAS", "n_gehalt": 27.0, "p_gehalt": 0.0, "k_gehalt": 0.0,
             "typ": "Mineraldünger", "vk_preis": 0.35},
        ],
        "psm": [],
        "saatgut": [],
        "kulturen": [],
    }
    r = resolve_mittel(catalog, mittel_typ="duenger", mittel_id="d1", menge=350.0, flaeche=10.0)
    assert r["mittel"] == "KAS"
    assert r["n_gehalt"] == 27.0
    assert r["duenger_form"] == "M"
    assert r["n_kg"] == pytest.approx(945.0)
    assert r["kosten_eur"] == pytest.approx(0.35 * 350 * 10, abs=0.01)


def test_resolve_psm_sets_wartezeit_and_wirkungsbereich():
    from app.agrar.feldbuch.stammdaten import resolve_mittel

    catalog = {
        "duenger": [],
        "psm": [
            {"id": "p1", "name": "Atlantis", "mittel_typ": "Herbizid", "wartezeit": 42,
             "vk_preis": 40.0},
        ],
        "saatgut": [],
        "kulturen": [],
    }
    r = resolve_mittel(catalog, mittel_typ="psm", mittel_id="p1", menge=1.5, flaeche=8.0)
    assert r["wirkungsbereich"] == "Herbizid"
    assert r["wartezeit_tage"] == 42
    assert r["mittel"] == "Atlantis"


def test_resolve_unknown_raises():
    from app.agrar.feldbuch.stammdaten import resolve_mittel

    with pytest.raises(ValueError, match="nicht gefunden"):
        resolve_mittel({"duenger": [], "psm": [], "saatgut": [], "kulturen": []},
                       mittel_typ="duenger", mittel_id="x", menge=1, flaeche=1)


def test_list_kulturen_unique_sorted():
    from app.agrar.feldbuch.stammdaten import list_kulturen

    k = list_kulturen([
        {"kultur": "Winterweizen"},
        {"kultur": "Raps"},
        {"kultur": "Winterweizen"},
        {"kultur": None},
    ], extra=["Gerste", "Raps"])
    assert k == ["Gerste", "Raps", "Winterweizen"]


# ── ASK-SEED-001 Aussaat ────────────────────────────────────────────────────

def test_aussaat_register_requires_sorte_and_menge():
    from app.agrar.feldbuch.aussaat import validate_aussaat

    with pytest.raises(ValueError, match="sorte"):
        validate_aussaat({"menge": 180})
    ok = validate_aussaat({"sorte": "RGT Reform", "menge": 180, "einheit": "kg/ha", "flaeche": 10})
    assert ok["sorte"] == "RGT Reform"
    assert ok["typ"] == "aussaat"


# ── ASK-IRR-001 Beregnung ───────────────────────────────────────────────────

def test_beregnung_requires_wassermenge():
    from app.agrar.feldbuch.beregnung import validate_beregnung

    with pytest.raises(ValueError, match="wassermenge"):
        validate_beregnung({})
    ok = validate_beregnung({"wassermenge_mm": 25, "art": "Beregnung", "flaeche": 5})
    assert ok["typ"] == "beregnung"
    assert ok["menge"] == 25


# ── ASK-ENV-001 AUM ─────────────────────────────────────────────────────────

def test_aum_requires_code_and_flaeche():
    from app.agrar.feldbuch.aum import validate_aum

    with pytest.raises(ValueError, match="aum_code"):
        validate_aum({"flaeche": 2})
    ok = validate_aum({"aum_code": "ÖRö1", "bezeichnung": "Vielfalt", "flaeche": 2.5})
    assert ok["typ"] == "aum"
    assert ok["aum_code"] == "ÖRö1"


# ── ASK-QS-001 QS-Checkliste ────────────────────────────────────────────────

def test_qs_checkliste_scores_pflichtfelder():
    from app.agrar.feldbuch.qs_checkliste import evaluate_qs_checkliste

    r = evaluate_qs_checkliste({
        "schlagdokumentation_vollstaendig": True,
        "wartezeiten_eingehalten": True,
        "sachkunde_nachgewiesen": False,
        "geraetepruefung_gueltig": True,
        "risikobewertung_boden": True,
    })
    assert r["bestanden"] is False
    assert "sachkunde_nachgewiesen" in r["offene"]
    assert r["erfuellt"] == 4
    assert r["gesamt"] == 5


# ── ASK-COST-001 Lagerverbrauch ─────────────────────────────────────────────

def test_lagerverbrauch_bucht_positiv_und_idempotent():
    from app.agrar.feldbuch.lagerverbrauch import plane_lagerverbrauch

    buchung = plane_lagerverbrauch(
        massnahme_id="m1",
        artikel_id="a1",
        charge="CH-1",
        menge=350.0,
        einheit="kg",
        kostentraeger_schlag_id="s1",
        client_ref="offline-1",
    )
    assert buchung["richtung"] == "verbrauch"
    assert buchung["menge"] == 350.0
    assert buchung["client_ref"] == "offline-1"
    with pytest.raises(ValueError, match="menge"):
        plane_lagerverbrauch(
            massnahme_id="m1", artikel_id="a1", charge=None, menge=0, einheit="kg",
            kostentraeger_schlag_id="s1",
        )


# ── ASK-FLD-002 Druck/Export Schlaginfo ─────────────────────────────────────

def test_schlaginfo_druck_contains_sections_and_dfl():
    from app.agrar.feldbuch.schlaginfo_export import render_schlaginfo_text

    text = render_schlaginfo_text({
        "schlag": {"name": "Südfeld", "flaecheHa": 10, "kultur": "WW", "flik": "X"},
        "wirtschaftsjahr": 2026,
        "aussaat": [{"mittel": "Sorte A"}],
        "duengung": [{"mittel": "KAS"}],
        "pflanzenschutz": [],
        "ernte": [{"ertrag_dt_ha": 80}],
        "kosten": {
            "direktkostenEur": 500,
            "erloesEur": 2000,
            "direktkostenfreieLeistungEur": 1500,
            "direktkostenfreieLeistungEurHa": 150,
        },
    })
    assert "Südfeld" in text
    assert "Direktkostenfreie Leistung" in text
    assert "1500" in text or "1.500" in text
    assert "Aussaat" in text


# ── ASK-MOB-001 Offline-Queue ───────────────────────────────────────────────

def test_offline_queue_dedupes_by_client_ref():
    from app.agrar.feldbuch.offline_queue import merge_offline_ops

    ops = [
        {"client_ref": "c1", "op": "create_massnahme", "payload": {"typ": "duengung"}},
        {"client_ref": "c1", "op": "create_massnahme", "payload": {"typ": "duengung"}},
        {"client_ref": "c2", "op": "create_schlag", "payload": {"name": "A"}},
    ]
    merged = merge_offline_ops(ops)
    assert len(merged) == 2
    assert {o["client_ref"] for o in merged} == {"c1", "c2"}


def test_offline_queue_rejects_missing_client_ref():
    from app.agrar.feldbuch.offline_queue import merge_offline_ops

    with pytest.raises(ValueError, match="client_ref"):
        merge_offline_ops([{"op": "create_massnahme", "payload": {}}])


# ── ASK-BUS-001 Betriebssnapshot ────────────────────────────────────────────

def test_betrieb_snapshot_from_crm_fields():
    from app.agrar.feldbuch.betrieb import build_betrieb_snapshot

    s = build_betrieb_snapshot({
        "id": "c1",
        "name": "Hof Ost",
        "ort": "Emden",
        "plz": "26721",
        "bundesland": "NI",
    })
    assert s["betriebName"] == "Hof Ost"
    assert s["anschrift"]["ort"] == "Emden"
    assert s["bundesland"] == "NI"
