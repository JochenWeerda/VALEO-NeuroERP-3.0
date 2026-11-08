"""Belegvertrag (BELEG-010): Form, Varianten und Abbildung der bisherigen Feldnamen.

Ohne Datenbank. Der Vertrag wird gegen das geprueft, was es schon gibt: die Belegarten und Uebergaenge von
DocFlow und die fuenf Beleg-ScreenDefinitions.
"""

from __future__ import annotations

import subprocess
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest

from app.core import belegvertrag as bv
from app.core.screen_definitions import _SCREEN_DEFINITIONS
from app.services.docflow_service import DOC_PREFIX, POS_TYPES, TRANSITIONS, steuerrichtung

WURZEL = Path(__file__).resolve().parent.parent


def _rechnung(**anders) -> bv.Beleg:
    daten = {
        "beleg_id": "b1", "belegart": "sales_invoice", "beleg_nr": "SIV-2026-000001", "status": "posted",
        "belegdatum": date(2026, 10, 13),
        "partner": {"rolle": "kunde", "nummer": "K1", "name": "Hof Beispiel"},
        "positionen": [
            {"pos_nr": 1, "artikel_nr": "A1", "menge": "10", "einheit": "t", "einzelpreis": "100.00",
             "steuerschluessel": "3", "steuersatz": "19", "netto": "1000.00", "steuer": "190.00", "brutto": "1190.00"},
            {"pos_nr": 2, "artikel_nr": "A2", "menge": "5", "einheit": "t", "einzelpreis": "40.00",
             "steuerschluessel": "2", "steuersatz": "7", "netto": "200.00", "steuer": "14.00", "brutto": "214.00"},
        ],
        "summen": {"netto": "1200.00", "steuer": "204.00", "brutto": "1404.00"},
        "buchung": {"stand": "gebucht", "journal_id": "j1"},
    }
    daten.update(anders)
    return bv.Beleg.model_validate(daten)


# ── Varianten gegen DocFlow ───────────────────────────────────────────────────

def test_jede_docflow_belegart_ausser_kasse_hat_eine_variante():
    assert set(bv.BELEGARTEN) == set(DOC_PREFIX) - POS_TYPES


@pytest.mark.parametrize("belegart", sorted(bv.BELEGARTEN))
def test_folgebelege_und_steuerrichtung_stimmen_mit_docflow(belegart):
    variante = bv.BELEGARTEN[belegart]
    assert set(variante.folgebelege) == set(TRANSITIONS.get(belegart, {}))
    assert variante.richtung == steuerrichtung(belegart)
    assert variante.partnerrolle == ("lieferant" if variante.richtung == "einkauf" else "kunde")


def test_nur_lieferschein_und_wareneingang_sind_ohne_preise():
    assert {a for a, v in bv.BELEGARTEN.items() if not v.mit_preisen} == {"sales_delivery", "goods_receipt"}


# ── Pruefung eines Belegs ─────────────────────────────────────────────────────

def test_vollstaendige_rechnung_ist_vertragsgerecht():
    assert bv.pruefe(_rechnung()) == []


def test_unbekanntes_feld_wird_abgelehnt():
    with pytest.raises(ValueError):
        _rechnung(mwst_prozent=19)


def test_summe_muss_zu_den_positionen_passen():
    fehler = bv.pruefe(_rechnung(summen={"netto": "1200.00", "steuer": "228.00", "brutto": "1428.00"}))
    assert any("Summe steuer" in f for f in fehler)


def test_ohne_preisrecht_keine_preisfelder_und_keine_summen():
    beleg = _rechnung()
    # Nur das Kennzeichen umzulegen genuegt nicht: Die Felder duerfen nicht ausgeliefert werden.
    nur_markiert = beleg.model_copy(update={"preise_sichtbar": False})
    assert any("Summen" in f for f in bv.pruefe(nur_markiert))
    assert any("einzelpreis" in f for f in bv.pruefe(nur_markiert))

    bereinigt = bv.ohne_preise(beleg)
    assert bv.pruefe(bereinigt) == []
    assert bereinigt.summen is None
    roh = bereinigt.model_dump(mode="json")
    assert all(pos[feld] is None for pos in roh["positionen"] for feld in bv.PREISFELDER)
    # Mengen bleiben.
    assert [p.menge for p in bereinigt.positionen] == [Decimal("10"), Decimal("5")]


def test_lieferschein_traegt_keine_preise():
    lieferschein = _rechnung(belegart="sales_delivery", status="open", buchung={})
    fehler = bv.pruefe(lieferschein)
    assert any("Variante Lieferschein" in f for f in fehler)
    assert bv.pruefe(bv.ohne_preise(lieferschein)) == []


def test_buchungsstand_braucht_journal_bzw_grund_und_passt_zur_belegart():
    assert "Gebucht ohne Journalbezug." in bv.pruefe(_rechnung(buchung={"stand": "gebucht"}))
    assert "Pruefvermerk ohne Grund." in bv.pruefe(_rechnung(status="open", buchung={"stand": "pruefen"}))
    auftrag = _rechnung(belegart="sales_order", buchung={"stand": "gebucht", "journal_id": "j1"})
    assert "Auftrag wird nicht gebucht." in bv.pruefe(auftrag)


def test_partnerrolle_kette_und_aktionen_folgen_der_variante():
    falsch = _rechnung(
        partner={"rolle": "lieferant", "name": "X"},
        kette=[
            {"richtung": "vorgaenger", "belegart": "sales_delivery", "beleg_id": "d", "beleg_nr": "SDL-1"},
            {"richtung": "vorgaenger", "belegart": "purchase_order", "beleg_id": "p", "beleg_nr": "POR-1"},
            {"richtung": "nachfolger", "belegart": "sales_order", "beleg_id": "o", "beleg_nr": "SOR-1"},
        ],
        aktionen=[
            {"key": "gutschrift", "bezeichnung": "Gutschrift erstellen", "folgebelegart": "sales_credit_memo"},
            {"key": "liefern", "bezeichnung": "Liefern", "folgebelegart": "sales_delivery"},
            {"key": "stornieren", "bezeichnung": "Stornieren", "erlaubt": False},
        ],
    )
    fehler = bv.pruefe(falsch)
    assert len(fehler) == 5, fehler
    assert any("Partnerrolle 'kunde'" in f for f in fehler)
    assert any("'purchase_order' ist kein Vorgaenger" in f for f in fehler)
    assert any("'sales_order' ist kein Folgebeleg" in f for f in fehler)
    assert any("Aktion 'liefern'" in f for f in fehler)
    assert any("Aktion 'stornieren' ist gesperrt" in f for f in fehler)


def test_unbekannte_belegart_status_baustein_und_doppelte_position():
    assert bv.pruefe(_rechnung(belegart="frachtbrief")) == ["Belegart 'frachtbrief' hat keine Variante."]
    fehler = bv.pruefe(_rechnung(status="verbucht", bausteine={"wiegung": {}}))
    assert any("kein Belegstand" in f for f in fehler) and any("Baustein 'wiegung'" in f for f in fehler)
    doppelt = _rechnung()
    doppelt.positionen[1].pos_nr = 1
    assert "Positionsnummern sind nicht eindeutig." in bv.pruefe(doppelt)


# ── Abbildung gegen die ScreenDefinitions ─────────────────────────────────────

def _name(eintrag: dict) -> str:
    return eintrag.get("name") or eintrag["key"]


def _felder(kennung: str) -> dict[str, set[str]]:
    """Feldnamen des Reiters ``kopf`` und Spalten der Tabelle ``positionen`` einer ScreenDefinition."""
    kopf: set[str] = set()
    positionen: set[str] = set()
    for tab in _SCREEN_DEFINITIONS[kennung]().get("tabs", []):
        bereiche = [tab] + list(tab.get("sections") or [])
        if tab.get("key") == "kopf":
            kopf |= {_name(f) for b in bereiche for f in b.get("fields") or []}
        for tabelle in (t for b in bereiche for t in b.get("tables") or []):
            if _name(tabelle) == "positionen":
                positionen |= {_name(c) for c in tabelle.get("columns") or []}
    return {"kopf": kopf, "positionen": positionen}


@pytest.mark.parametrize("kennung", sorted(bv.ABBILDUNG))
def test_abbildung_deckt_die_screen_definition_genau(kennung):
    """Ein neues Feld ohne Platz im Vertrag macht den Test rot — ebenso ein Eintrag fuer ein entferntes Feld."""
    vorhanden = _felder(kennung)
    assert vorhanden["kopf"] and vorhanden["positionen"], "ScreenDefinition hat keinen Kopf oder keine Positionen"
    for bereich in ("kopf", "positionen"):
        assert set(bv.ABBILDUNG[kennung][bereich]) == vorhanden[bereich], bereich


def test_jedes_ziel_der_abbildung_gibt_es_im_vertrag():
    ungueltig = [
        (kennung, alt, ziel)
        for kennung, teile in bv.ABBILDUNG.items()
        for felder in teile.values()
        for alt, ziel in felder.items()
        if not bv.ziel_ist_gueltig(ziel)
    ]
    assert ungueltig == []
    assert not bv.ziel_ist_gueltig("positionen[].mwst_prozent")
    assert not bv.ziel_ist_gueltig("baustein:wiegung")
    assert not bv.ziel_ist_gueltig("partner.ort")


def test_positionen_einer_spalte_landen_bei_positionen_oder_im_baustein():
    for kennung, teile in bv.ABBILDUNG.items():
        for alt, ziel in teile["positionen"].items():
            assert ziel.startswith(("positionen[].", "kette[].", "baustein:")), (kennung, alt, ziel)


# ── Erzeugte Dateien ──────────────────────────────────────────────────────────

def test_schema_und_uebersicht_sind_aktuell():
    lauf = subprocess.run([sys.executable, "scripts/generate_belegvertrag.py", "--check"],
                          cwd=WURZEL, capture_output=True, text=True, timeout=120)
    assert lauf.returncode == 0, lauf.stderr
