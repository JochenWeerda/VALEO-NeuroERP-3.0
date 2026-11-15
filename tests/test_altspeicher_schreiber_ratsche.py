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
    "domain_einkauf.bestellungen", "domain_einkauf.bestellpositionen",
)
SCHREIBEN = re.compile(
    r"(INSERT\s+INTO|UPDATE|DELETE\s+FROM)\s+(" + "|".join(re.escape(t) for t in ALTSPEICHER) + r")\b", re.I)

# Stand 15.11.2026 - nur streichen, nie ergaenzen.
SCHREIBER = {
    # Auftragsbestaetigung des Lieferanten schreibt den Status der Altbestellung fort (Schnitt S3).
    "app/services/einkauf_compat_service.py": {"domain_einkauf.bestellungen"},
}


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
