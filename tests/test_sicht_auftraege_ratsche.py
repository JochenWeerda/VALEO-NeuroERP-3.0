"""Ratsche fuer die Uebergangssicht domain_crm.sales_orders / sales_order_items (BELEG-052).

Seit ``docflow_auftraege_uebernahme_20261109`` sind beide Namen Sichten auf DocFlow. Sie sind ein Uebergang:
- kein neuer Leser (die Liste darf nur schrumpfen; neue Leser lesen DocFlow direkt),
- kein Schreiber (Schreiben auf die Sicht scheitert zur Laufzeit - hier schon im Code),
- Leser vergleichen nur das DocFlow-Statuswoerterbuch: Die Sicht liefert keinen alten Stand mehr, ein alter Wert
  in einer Bedingung waere stillschweigend wirkungslos (so zaehlte das Kreditlimit stornierte Auftraege mit).
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

WURZEL = Path(__file__).resolve().parents[1]
SICHT = re.compile(r"domain_crm\.sales_order(s|_items)\b")
SCHREIBEN = re.compile(r"(INSERT\s+INTO|UPDATE|DELETE\s+FROM)\s+domain_crm\.sales_order(s|_items)\b", re.I)
ALTER_STAND = re.compile(
    r"'(bestaetigt|geliefert|in_delivery|in_lieferung|ENTWURF|entwurf|abgeschlossen|storniert|invoiced|delivered)'")

# Stand 09.11.2026 - nur streichen, nie ergaenzen.
LESER = frozenset({
    "app/api/v1/endpoints/collective_documents.py",
    "app/api/v1/endpoints/compat.py",
    "app/api/v1/endpoints/credit_management.py",
    "app/api/v1/endpoints/crm_360.py",
    "app/api/v1/endpoints/crm_360_reads.py",
    "app/api/v1/endpoints/crm_kim.py",
    "app/api/v1/endpoints/pick_lists.py",
    "app/api/v1/endpoints/sales_delivery_notes.py",
    "app/api/v1/endpoints/sales_order_commands.py",
    "app/api/v1/endpoints/sales_reports.py",
    "app/services/beleg_anlage.py",
    "app/services/customer_reference.py",
    "app/services/ist_aggregation_service.py",
    "app/services/mcp_execution_service.py",
    "app/services/o2c_chain_service.py",
    "app/services/procurement_service.py",
    "app/services/sales_credit_service.py",
    "app/services/sales_match_service.py",
    "app/services/sales_storno_service.py",
    "app/services/webshop_integration_service.py",
    "modules/einkauf/services/bestellvorschlag_service.py",
})


def _quellen():
    for ordner in ("app", "modules"):
        for pfad in (WURZEL / ordner).rglob("*.py"):
            yield pfad.relative_to(WURZEL).as_posix(), pfad.read_text(encoding="utf-8", errors="ignore")


def test_keine_neuen_leser_der_sicht():
    ist = {name for name, text in _quellen() if SICHT.search(text)}
    assert ist <= LESER, f"Neue Leser der Uebergangssicht - DocFlow direkt lesen: {sorted(ist - LESER)}"
    assert LESER - ist == set(), f"Leser entfallen - aus LESER streichen: {sorted(LESER - ist)}"


def test_niemand_schreibt_auf_die_sicht():
    treffer = [f"{name}:{text[:m.start()].count(chr(10)) + 1}" for name, text in _quellen()
               for m in SCHREIBEN.finditer(text)]
    assert treffer == []


def test_leser_vergleichen_nur_docflow_staende():
    treffer = []
    for name, text in _quellen():
        for m in SICHT.finditer(text):
            fenster = text[m.start():m.end() + 700]
            # Nur die eine Abfrage: bis zum Ende des SQL-Literals.
            ende = min((i for i in (fenster.find('"""', 1), fenster.find("\n\n")) if i > 0), default=len(fenster))
            for alt in ALTER_STAND.findall(fenster[:ende]):
                treffer.append(f"{name}:{text[:m.start()].count(chr(10)) + 1} '{alt}'")
    assert treffer == [], treffer
