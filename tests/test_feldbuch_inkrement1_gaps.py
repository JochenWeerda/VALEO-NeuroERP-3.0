"""
ASK Inkrement-1 Gaps (TDD): Arbeitskontext, Schlaginfo, Jahreswechsel, Sammelbuchung.

Lastenheft: Kap. 5 (Arbeitskontext), 19 (Schlaginfo), 31 (Sammelbuchung), 36 (Jahreswechsel).
"""
from __future__ import annotations

import os
import sys
from datetime import date, datetime, timezone

import pytest

_ROOT = os.path.join(os.path.dirname(__file__), "..")
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)


# ── Arbeitskontext (ASK-BUS / Kap. 5) ───────────────────────────────────────

def test_arbeitskontext_requires_wirtschaftsjahr():
    from app.agrar.feldbuch.arbeitskontext import build_arbeitskontext

    with pytest.raises(ValueError, match="wirtschaftsjahr"):
        build_arbeitskontext(customer_id="c1", betrieb_name="Hof A", wirtschaftsjahr=None)


def test_arbeitskontext_defaults_erntejahr_and_sync():
    from app.agrar.feldbuch.arbeitskontext import build_arbeitskontext

    ctx = build_arbeitskontext(
        customer_id="c1",
        betrieb_name="Hof Ostfriesland",
        wirtschaftsjahr=2026,
        rolle="betriebsleiter",
    )
    assert ctx["customerId"] == "c1"
    assert ctx["betriebName"] == "Hof Ostfriesland"
    assert ctx["wirtschaftsjahr"] == 2026
    assert ctx["erntejahr"] == 2026
    assert ctx["rolle"] == "betriebsleiter"
    assert ctx["syncStatus"] == "online"
    assert ctx["datenstand"] is not None


# ── Schlaginfo (ASK-FLD / Kap. 19) ──────────────────────────────────────────

def test_schlaginfo_aggregates_sections_and_dfl():
    from app.agrar.feldbuch.schlaginfo import build_schlaginfo

    schlag = {
        "id": "s1",
        "name": "Südfeld",
        "flaeche": 10.0,
        "kultur": "Winterweizen",
        "vorkultur": "Raps",
        "flik": "DENILI0001",
        "n_sollwert_kg_ha": 180.0,
        "nmin_fruehjahr_kg_ha": 40.0,
        "versorgungsstufe": "C",
    }
    massnahmen = [
        {
            "typ": "aussaat",
            "datum": date(2025, 10, 5),
            "mittel": "RGT Reform",
            "menge": 180.0,
            "einheit": "kg/ha",
            "flaeche": 10.0,
            "kosten_eur": 450.0,
        },
        {
            "typ": "duengung",
            "datum": date(2026, 3, 10),
            "mittel": "KAS",
            "n_kg": 135.0,
            "kosten_eur": 300.0,
            "flaeche": 10.0,
        },
        {
            "typ": "psm",
            "datum": date(2026, 4, 1),
            "mittel": "Atlantis",
            "wirkungsbereich": "Herbizid",
            "kosten_eur": 120.0,
            "flaeche": 10.0,
        },
        {
            "typ": "ernte",
            "datum": date(2026, 8, 1),
            "ertrag_dt_ha": 85.0,
            "erloes_eur": 2500.0,
            "nebenleistung_eur": 200.0,
            "flaeche": 10.0,
        },
    ]
    info = build_schlaginfo(schlag, massnahmen, wirtschaftsjahr=2026)
    assert info["schlag"]["name"] == "Südfeld"
    assert info["wirtschaftsjahr"] == 2026
    assert len(info["aussaat"]) == 1
    assert len(info["duengung"]) == 1
    assert len(info["pflanzenschutz"]) == 1
    assert len(info["ernte"]) == 1
    assert info["kosten"]["direktkostenEur"] == pytest.approx(870.0)
    assert info["kosten"]["erloesEur"] == pytest.approx(2700.0)
    assert info["kosten"]["direktkostenfreieLeistungEur"] == pytest.approx(1830.0)
    assert info["kosten"]["direktkostenfreieLeistungEurHa"] == pytest.approx(183.0)


def test_schlaginfo_empty_massnahmen():
    from app.agrar.feldbuch.schlaginfo import build_schlaginfo

    info = build_schlaginfo(
        {"id": "s1", "name": "Leer", "flaeche": 5.0, "kultur": None},
        [],
        wirtschaftsjahr=2026,
    )
    assert info["aussaat"] == []
    assert info["kosten"]["direktkostenfreieLeistungEur"] == 0.0


# ── Jahreswechsel (ASK-PLAN / Kap. 36) ──────────────────────────────────────

def test_jahreswechsel_copies_master_without_massnahmen():
    from app.agrar.feldbuch.jahreswechsel import plan_jahreswechsel

    geplant = plan_jahreswechsel(
        schlaege=[
            {
                "id": "old-1",
                "name": "Südfeld",
                "flaeche": 10.0,
                "kultur": "Winterweizen",
                "vorkultur": "Raps",
                "flik": "DENILI0001",
                "gemeinde": "Musterdorf",
                "bodenart": "lehmig",
                "ackerzahl": 45.0,
                "wirtschaftsjahr": 2025,
                "n_sollwert_kg_ha": 180.0,
            }
        ],
        von_jahr=2025,
        nach_jahr=2026,
    )
    assert len(geplant) == 1
    neu = geplant[0]
    assert neu["name"] == "Südfeld"
    assert neu["flaeche"] == 10.0
    assert neu["vorkultur"] == "Winterweizen"  # Vorjahreskultur
    assert neu["kultur"] is None  # neu zu planen
    assert neu["wirtschaftsjahr"] == 2026
    assert neu["flik"] == "DENILI0001"
    assert "id" not in neu  # neue ID erst beim Persistieren
    assert neu["quelle_schlag_id"] == "old-1"


def test_jahreswechsel_skips_wrong_year_and_rejects_same_year():
    from app.agrar.feldbuch.jahreswechsel import plan_jahreswechsel

    with pytest.raises(ValueError, match="nach_jahr"):
        plan_jahreswechsel(schlaege=[], von_jahr=2026, nach_jahr=2026)

    geplant = plan_jahreswechsel(
        schlaege=[
            {"id": "a", "name": "A", "flaeche": 1.0, "kultur": "WW", "wirtschaftsjahr": 2024},
            {"id": "b", "name": "B", "flaeche": 2.0, "kultur": "WG", "wirtschaftsjahr": 2025},
        ],
        von_jahr=2025,
        nach_jahr=2026,
    )
    assert len(geplant) == 1
    assert geplant[0]["name"] == "B"


# ── Sammelbuchung Düngung (ASK-FERT / Kap. 31) ──────────────────────────────

def test_sammelbuchung_distributes_by_area():
    from app.agrar.feldbuch.sammelbuchung import plane_sammel_duengung

    result = plane_sammel_duengung(
        schlaege=[
            {"id": "s1", "name": "A", "flaeche": 10.0},
            {"id": "s2", "name": "B", "flaeche": 5.0},
        ],
        datum=datetime(2026, 3, 15, tzinfo=timezone.utc),
        mittel="KAS",
        menge_kg_ha=350.0,
        einheit="kg/ha",
        n_gehalt=27.0,
        duenger_form="M",
        preis_je_einheit=0.35,
        anwender="Max Mustermann",
    )
    assert result["anzahl"] == 2
    assert result["gesamtFlaecheHa"] == pytest.approx(15.0)
    m1, m2 = result["massnahmen"]
    assert m1["schlag_id"] == "s1"
    assert m1["typ"] == "duengung"
    assert m1["menge"] == 350.0
    assert m1["flaeche"] == 10.0
    assert m1["n_kg"] == pytest.approx(945.0)
    assert m1["kosten_eur"] == pytest.approx(0.35 * 350 * 10, abs=0.01)
    assert m2["schlag_id"] == "s2"
    assert m2["n_kg"] == pytest.approx(472.5)
    assert m2["flaeche"] == 5.0


def test_sammelbuchung_rejects_empty_and_nonpositive():
    from app.agrar.feldbuch.sammelbuchung import plane_sammel_duengung

    with pytest.raises(ValueError, match="schlaege"):
        plane_sammel_duengung(
            schlaege=[],
            datum=datetime(2026, 3, 15, tzinfo=timezone.utc),
            mittel="KAS",
            menge_kg_ha=100.0,
        )
    with pytest.raises(ValueError, match="menge"):
        plane_sammel_duengung(
            schlaege=[{"id": "s1", "flaeche": 1.0}],
            datum=datetime(2026, 3, 15, tzinfo=timezone.utc),
            mittel="KAS",
            menge_kg_ha=0,
        )
