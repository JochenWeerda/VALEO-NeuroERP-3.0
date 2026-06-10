"""Reine Logik-Tests des Dokument-Nachweisraums (DOM-DOC-004) — ohne DB.

Deckt die GoBD-Lücken-Bewertung ab (Artefakt/Hash/Buchung/Export).
"""

from __future__ import annotations

import pytest

from app.services.docflow_evidence_service import evaluate_gaps

pytestmark = pytest.mark.unit


def test_kein_artefakt_ist_warnung():
    gaps = evaluate_gaps({"doc_type": "note", "status": "draft"}, [], [])
    assert any("Kein Artefakt" in g["text"] for g in gaps)


def test_artefakt_ohne_hash():
    gaps = evaluate_gaps(
        {"doc_type": "note", "status": "open"},
        [{"content_hash_sha256": None, "storage_key": "x"}],
        [],
    )
    assert any("nicht revisionssicher" in g["text"] for g in gaps)


def test_vollstaendig_kein_gap():
    gaps = evaluate_gaps(
        {"doc_type": "note", "status": "open", "exported_at": "2026-01-01"},
        [{"content_hash_sha256": "abc", "storage_key": "k"}],
        [{"posting_type": "ar"}],
    )
    assert gaps == []


def test_rechnung_ohne_buchung_und_export():
    gaps = evaluate_gaps(
        {"doc_type": "sales_invoice", "status": "open"},
        [{"content_hash_sha256": "abc", "storage_key": "k"}],
        [],
    )
    texte = " ".join(g["text"] for g in gaps)
    assert "nicht gebucht" in texte
    assert "GoBD-Export" in texte


def test_stornierte_rechnung_keine_buchungs_luecke():
    gaps = evaluate_gaps(
        {"doc_type": "sales_invoice", "status": "reversed", "exported_at": "2026-01-01"},
        [{"content_hash_sha256": "abc", "storage_key": "k"}],
        [],
    )
    assert not any("nicht gebucht" in g["text"] for g in gaps)
