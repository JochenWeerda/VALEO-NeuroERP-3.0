"""Reine Logik-Tests der Dubletten-Erkennung (DOM-CRM-004) — ohne DB.

Deckt Namens-Normalisierung (Rechtsform/Reihenfolge), Telefon-Tail und Union-Find ab.
"""

from __future__ import annotations

import pytest

from app.services.crm_duplicate_service import _UnionFind, _norm_email, _norm_name, _norm_phone

pytestmark = pytest.mark.unit


def test_norm_name_ignores_legal_and_order():
    # Umgestellte GbR-Namen + Rechtsform/Füllwörter → gleicher Normalwert.
    a = _norm_name("Hillrich & Sandine Kleemann GbR")
    b = _norm_name("Kleemann GbR, Hillrich & Sandine")
    assert a == b and a != ""


def test_norm_name_und_vs_ampersand():
    assert _norm_name("Enno & Etta Ohling GbR") == _norm_name("Ohling GbR, Enno und Etta")


def test_norm_name_empty():
    assert _norm_name(None) == ""
    assert _norm_name("GmbH & Co. KG") == ""  # nur Rechtsformwörter → leer


def test_norm_phone_tail():
    assert _norm_phone("0551 / 12345 67") == _norm_phone("+49 551 1234567")
    assert _norm_phone("123") == ""  # zu kurz


def test_norm_email():
    assert _norm_email("  Info@Beispiel.DE ") == "info@beispiel.de"


def test_unionfind_clusters():
    uf = _UnionFind()
    uf.union("a", "b")
    uf.union("b", "c")
    uf.union("x", "y")
    assert uf.find("a") == uf.find("c")
    assert uf.find("a") != uf.find("x")
    assert uf.find("x") == uf.find("y")
