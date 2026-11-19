"""Ratsche: niemand schreibt mehr in die alten Belegspeicher (BELEG-052).

DocFlow ist der Belegspeicher. Die alten Tabellen bleiben bis zum Abbau ihrer Leser stehen; geschrieben wird in sie
nicht mehr. Die Liste der verbliebenen Schreiber darf nur schrumpfen - Ziel ist die leere Liste, danach fallen die
Tabellen per Migration.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

WURZEL = Path(__file__).resolve().parents[1]
ALTSPEICHER = (
    "domain_sales.delivery_notes", "domain_sales.delivery_note_positions", "domain_sales.sales_delivery_notes",
    "domain_sales.sales_invoices", "domain_sales.sales_invoice_lines",
    "domain_sales.sales_credit_notes", "domain_sales.sales_credit_note_lines",
    "domain_einkauf.bestellungen", "domain_einkauf.bestellung_positionen",
)
SCHREIBEN = re.compile(
    r"(INSERT\s+INTO|UPDATE|DELETE\s+FROM)\s+(" + "|".join(re.escape(t) for t in ALTSPEICHER) + r")\b", re.I)

# Stand 16.11.2026 (Schnitt S3: der letzte Schreiber, der tote Wareneingang im Compat-Dienst, ist entfernt).
# Nur streichen, nie ergaenzen.
SCHREIBER: dict[str, set[str]] = {}


def _schreiber() -> dict[str, set[str]]:
    gefunden: dict[str, set[str]] = {}
    for ordner in ("app", "modules"):
        for pfad in (WURZEL / ordner).rglob("*.py"):
            text = pfad.read_text(encoding="utf-8", errors="ignore")
            for treffer in SCHREIBEN.finditer(text):
                gefunden.setdefault(pfad.relative_to(WURZEL).as_posix(), set()).add(treffer.group(2).lower())
    return gefunden


def test_keine_neuen_schreiber_in_die_altspeicher():
    ist = _schreiber()
    neu = {datei: tabellen - SCHREIBER.get(datei, set()) for datei, tabellen in ist.items()}
    neu = {datei: tabellen for datei, tabellen in neu.items() if tabellen}
    assert neu == {}, f"Neue Schreiber in einen Alt-Belegspeicher - DocFlow-Kommando benutzen: {neu}"


def test_entfallene_schreiber_werden_gestrichen():
    ist = _schreiber()
    veraltet = {datei: tabellen - ist.get(datei, set()) for datei, tabellen in SCHREIBER.items()}
    veraltet = {datei: tabellen for datei, tabellen in veraltet.items() if tabellen}
    assert veraltet == {}, f"Schreiber entfallen - aus SCHREIBER streichen: {veraltet}"


def test_der_lieferschein_altspeicher_hat_keinen_schreiber_mehr():
    tabellen = {t for ts in _schreiber().values() for t in ts}
    assert not tabellen & {"domain_sales.delivery_notes", "domain_sales.delivery_note_positions",
                           "domain_sales.sales_delivery_notes"}


LESEN_LIEFERSCHEIN = re.compile(r"(FROM|JOIN)\s+domain_sales\.(delivery_notes|delivery_note_positions|sales_delivery_notes)\b",
                                re.I)


def test_der_lieferschein_altspeicher_hat_keinen_leser_mehr():
    """Seit Schnitt S2 (15.11.2026) lesen alle den DocFlow-Lieferschein; der Altspeicher ist leer und faellt weg."""
    leser = []
    for ordner in ("app", "modules"):
        for pfad in (WURZEL / ordner).rglob("*.py"):
            if LESEN_LIEFERSCHEIN.search(pfad.read_text(encoding="utf-8", errors="ignore")):
                leser.append(pfad.relative_to(WURZEL).as_posix())
    assert leser == [], f"Leser des Lieferschein-Altspeichers - DocFlow lesen: {leser}"


LESEN_BESTELLUNG = re.compile(r"(FROM|JOIN)\s+domain_einkauf\.(bestellungen|bestellung_positionen)\b", re.I)
ALTMODELL = re.compile(r"\bEinkaufBestellung(Position)?\b")
# Seit 17.11.2026 versendet auch Fax/EDI die DocFlow-Bestellung; das ORM-Modell nutzt niemand mehr.
ALTMODELL_NUTZER: set[str] = set()


def _dateien_mit(muster: re.Pattern[str]) -> list[str]:
    treffer = []
    for ordner in ("app", "modules"):
        for pfad in (WURZEL / ordner).rglob("*.py"):
            if muster.search(pfad.read_text(encoding="utf-8", errors="ignore")):
                treffer.append(pfad.relative_to(WURZEL).as_posix())
    return sorted(treffer)


def test_der_bestell_altspeicher_hat_keinen_leser_mehr():
    """Seit Schnitt S3 (16.11.2026) lesen alle die DocFlow-Bestellung; der Altspeicher faellt mit S5 weg."""
    leser = _dateien_mit(LESEN_BESTELLUNG)
    assert leser == [], f"Leser des Bestell-Altspeichers - DocFlow lesen: {leser}"


def test_das_orm_modell_der_altbestellung_nutzt_niemand_neu():
    nutzer = set(_dateien_mit(ALTMODELL)) - {"app/infrastructure/models/einkauf_models.py",
                                             "app/infrastructure/models/__init__.py"}
    assert nutzer <= ALTMODELL_NUTZER, f"Neue Nutzer des Altmodells - DocFlow benutzen: {nutzer - ALTMODELL_NUTZER}"
    assert nutzer == ALTMODELL_NUTZER, f"Nutzer entfallen - aus ALTMODELL_NUTZER streichen: {ALTMODELL_NUTZER - nutzer}"


def test_die_muster_treffen_was_sie_sollen():
    """Ein Muster, das nie trifft, laesst jede Ratsche gruen (Backspace statt Wortgrenze, 2026-10)."""
    assert LESEN_BESTELLUNG.search("SELECT 1 FROM domain_einkauf.bestellungen b")
    assert LESEN_BESTELLUNG.search("join domain_einkauf.bestellung_positionen p ON")
    assert not LESEN_BESTELLUNG.search("FROM domain_einkauf.bestellung_kommunikation k")
    assert ALTMODELL.search("x: EinkaufBestellung = y") and not ALTMODELL.search("EinkaufBestellvorschlag")
    assert SCHREIBEN.search("UPDATE domain_einkauf.bestellungen SET")
    assert LESEN_LIEFERSCHEIN.search("FROM domain_sales.delivery_notes d")
