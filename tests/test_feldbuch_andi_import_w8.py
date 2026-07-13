"""
AS-W8-Regression: ANDI-Schlagdaten-XML-Parser (robust gegen Namespaces).
"""
from __future__ import annotations

import os
import sys

import pytest

_ROOT = os.path.join(os.path.dirname(__file__), "..")
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from app.agrar.feldbuch.andi_import import parse_andi_schlaege  # noqa: E402

_XML = """<schlaege jahr="2026">
  <schlag nr="1" name="Am Bach" flaeche="12,5" flik="DENILI0123" kultur="Winterweizen" gemeinde="Musterdorf"/>
  <schlag nr="2" name="Hinterm Hof" flaeche="8.0" flik="DENILI0456" kultur="Wintergerste"/>
</schlaege>"""


def test_parse_basic():
    r = parse_andi_schlaege(_XML)
    assert r["jahr"] == 2026
    assert r["anzahl"] == 2
    s0 = r["schlaege"][0]
    assert s0["name"] == "Am Bach"
    assert s0["flaeche"] == pytest.approx(12.5)
    assert s0["flik"] == "DENILI0123"
    assert s0["kultur"] == "Winterweizen"


def test_namespaced_xml():
    xml = '<ns:schlaege xmlns:ns="urn:andi" jahr="2025"><ns:schlag name="Feld A" flaeche="5"/></ns:schlaege>'
    r = parse_andi_schlaege(xml)
    assert r["anzahl"] == 1
    assert r["schlaege"][0]["name"] == "Feld A"


def test_invalid_xml_raises():
    with pytest.raises(ValueError, match="Ungueltiges"):
        parse_andi_schlaege("<schlaege><schlag ")


def test_missing_flaeche_raises():
    with pytest.raises(ValueError, match="flaeche"):
        parse_andi_schlaege('<schlaege><schlag name="X"/></schlaege>')


def test_empty_raises():
    with pytest.raises(ValueError):
        parse_andi_schlaege("")
