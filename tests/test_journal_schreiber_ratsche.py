"""Ratsche: das Journal wird nur ueber den kanonischen Buchungsdienst geschrieben (M3, Integritaet).

``FinanceTransactionService`` prueft Periodensperre, Konten, Betraege, Belegbezug und stempelt Sequenz und Hash-Kette.
Wer roh per SQL in ``domain_erp.journal_entries``/``journal_entry_lines`` schreibt, umgeht das alles. Die Liste der
verbliebenen Rohschreiber darf nur schrumpfen - Ziel ist die leere Liste.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

WURZEL = Path(__file__).resolve().parents[1]
SCHREIBEN = re.compile(
    r"(INSERT\s+INTO|UPDATE|DELETE\s+FROM)\s+\"?(?:\w+\"?\.\"?)?(journal_entries|journal_entry_lines)\b", re.I)

# Stand 19.11.2026: Abgrenzung bucht ueber den Dienst; Lagergeld, Periodenabschluss und der manuelle OP-Ausgleich
# schreiben kein Journal mehr.
# Nur streichen, nie ergaenzen.
SCHREIBER: dict[str, set[str]] = {
    "app/api/v1/endpoints/compat.py": {"journal_entries", "journal_entry_lines"},
    "app/api/v1/endpoints/inventory_operations.py": {"journal_entries", "journal_entry_lines"},
    "app/core/connectors/workflow.py": {"journal_entries", "journal_entry_lines"},
}


def _schreiber() -> dict[str, set[str]]:
    gefunden: dict[str, set[str]] = {}
    for ordner in ("app", "modules"):
        for pfad in (WURZEL / ordner).rglob("*.py"):
            text = pfad.read_text(encoding="utf-8", errors="ignore")
            for treffer in SCHREIBEN.finditer(text):
                gefunden.setdefault(pfad.relative_to(WURZEL).as_posix(), set()).add(treffer.group(2).lower())
    return gefunden


def test_keine_neuen_rohschreiber_ins_journal():
    ist = _schreiber()
    neu = {datei: tabellen - SCHREIBER.get(datei, set()) for datei, tabellen in ist.items()}
    neu = {datei: tabellen for datei, tabellen in neu.items() if tabellen}
    assert neu == {}, f"Neue Rohschreiber ins Journal - FinanceTransactionService benutzen: {neu}"


def test_entfallene_rohschreiber_werden_gestrichen():
    ist = _schreiber()
    veraltet = {datei: tabellen - ist.get(datei, set()) for datei, tabellen in SCHREIBER.items()}
    veraltet = {datei: tabellen for datei, tabellen in veraltet.items() if tabellen}
    assert veraltet == {}, f"Rohschreiber entfallen - aus SCHREIBER streichen: {veraltet}"


def test_das_muster_trifft_was_es_soll():
    """Ein Muster, das nie trifft, laesst jede Ratsche gruen (Backspace statt Wortgrenze, 2026-10)."""
    assert SCHREIBEN.search("INSERT INTO domain_erp.journal_entries (id) VALUES")
    assert SCHREIBEN.search("insert into\n    domain_erp.journal_entry_lines\n (id)")
    assert SCHREIBEN.search('UPDATE "domain_erp"."journal_entries" SET status')
    assert SCHREIBEN.search("DELETE FROM journal_entry_lines WHERE")
    assert not SCHREIBEN.search("SELECT * FROM domain_erp.journal_entries")
    assert not SCHREIBEN.search("INSERT INTO domain_erp.journal_entry_anchors (id)")
