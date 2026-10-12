"""Was der Code an Fachrollen verlangt, steht im Katalog fuer den Anmeldedienst.

Eine Rolle, die es im Anmeldedienst nicht gibt, kann niemand bekommen: Der Weg ist dann fuer alle
ausser ``admin`` zu. Am 12.10.2026 verlangte der Code 34 Fachrollen, und die Realm-Datei kannte keine.
Der Katalog ``config/keycloak/fachrollen.json`` ist die Liste, aus der der Anmeldedienst eingerichtet
wird; dieser Vertrag haelt ihn am Code fest.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib

REPO = pathlib.Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location("check_fachrollen", REPO / "scripts" / "check_fachrollen.py")
fachrollen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fachrollen)


def _katalog() -> dict:
    return json.loads(fachrollen.KATALOG.read_text(encoding="utf-8"))


def test_jede_rolle_im_code_steht_im_katalog():
    """Eine neue Rolle im Code ohne Katalogeintrag — niemand wuesste, dass sie einzurichten ist."""
    im_katalog = {r["name"] for r in _katalog()["rollen"]}
    im_code = set(fachrollen.rollen_im_code())
    assert im_code - im_katalog == set(), "Im Code verlangt, aber nicht im Katalog: python scripts/check_fachrollen.py"
    assert im_katalog - im_code == set(), "Im Katalog, aber von keinem Weg mehr verlangt"


def test_katalog_ist_so_wie_das_skript_ihn_schreibt():
    bestehend = _katalog()
    assert fachrollen.render(fachrollen.katalog_aus_code(bestehend)) == fachrollen.render(bestehend)


def test_jede_rolle_ist_beschrieben_und_keine_ist_allgemein():
    for rolle in _katalog()["rollen"]:
        assert rolle["beschreibung"].strip(), rolle["name"]
        assert rolle["name"] not in {"admin", "manager", "user"}


def test_finanzrollen_der_rollenslices_sind_dabei():
    """Die Rollen, auf die die Finanz-Slices vom Oktober 2026 bauen."""
    namen = {r["name"] for r in _katalog()["rollen"]}
    assert {"FINANCE_LESEN", "FINANCE_BEARBEITEN", "FINANCE_ADMIN", "KONTENPLAN_PFLEGE", "KONTENRAHMEN_PFLEGE",
            "SALES_BEARBEITEN", "EINKAUF_BEARBEITEN", "CRM_LESEN"} <= namen
