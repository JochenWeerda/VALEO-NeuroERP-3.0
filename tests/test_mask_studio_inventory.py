"""MASK-STUDIO-INVENTAR — Ratsche gegen neue handgebaute Masken und Maskenaktionen ohne MCP/CLI.

Nutzerentscheid 2026-10-19: nur Studio-generierte Masken; jede Maskenfunktion auch per CLI und MCP.
Das Inventar selbst steht in ``scripts/mask_studio_inventory.py``; diese Vertraege halten es ehrlich.
"""
from __future__ import annotations

import copy
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def modul():
    spec = importlib.util.spec_from_file_location("mask_studio_inventory", ROOT / "scripts/mask_studio_inventory.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def inventar(modul):
    return modul.inventory()


def _seite(inv, route):
    return next(r for r in inv["seiten"] if r["route"] == route)


def test_ratsche_ist_gruen(modul, inventar, capsys):
    assert modul.check(inventar) == 0, capsys.readouterr().out


def test_neue_handgebaute_route_macht_die_ratsche_rot(modul, inventar, capsys):
    inv = copy.deepcopy(inventar)
    inv["seiten"].append({"route": "neu/handgebaut", "stufe": "handgebaut", "screen_ids": [], "bereich": "neu"})
    assert modul.check(inv) == 1
    assert "+ neu/handgebaut" in capsys.readouterr().out


def test_neue_altmuster_route_macht_die_ratsche_rot(modul, inventar):
    inv = copy.deepcopy(inventar)
    inv["seiten"].append({"route": "neu/altmuster", "stufe": "builder_altmuster", "screen_ids": [], "bereich": "neu"})
    assert modul.check(inv) == 1


def test_neue_serverwirksame_aktion_ohne_mcp_und_cli_macht_die_ratsche_rot(modul, inventar, capsys):
    inv = copy.deepcopy(inventar)
    inv["aktionen"].append({"id": "mask:neu/maske:buchen", "maske": "neu/maske", "aktion": "buchen",
                            "art": "serverwirksam", "rest": "/api/v1/neu/actions/buchen",
                            "mcp": "unklassifiziert", "cli": False})
    assert modul.check(inv) == 1
    out = capsys.readouterr().out
    assert "aktionen_ohne_mcp_klassifikation" in out and "aktionen_ohne_cli" in out


def test_geschlossene_luecke_ist_hinweis_kein_fehler(modul, inventar, capsys):
    inv = copy.deepcopy(inventar)
    route = next(r for r in inv["seiten"] if r["stufe"] == "handgebaut")
    route["stufe"] = "studio_versioniert"
    assert modul.check(inv) == 0
    assert "geschlossen" in capsys.readouterr().out


def test_belegfamilie_ist_studio_versioniert(inventar):
    seite = _seite(inventar, "belege/:belegart/:id")
    assert seite["stufe"] == "studio_versioniert"
    assert inventar["familien"]["beleg"], "Belegfamilie ohne Varianten"


def test_native_screen_definition_wird_erkannt(inventar):
    assert _seite(inventar, "verkauf/rechnungen")["stufe"] in {"screen_definition", "studio_versioniert"}
    assert _seite(inventar, "logistik/frachtbriefe")["stufe"] == "screen_definition"  # CaptureScreenHost


def test_reine_weiterleitung_zaehlt_nicht_als_maske(inventar):
    assert _seite(inventar, "verkauf/kunde-neu")["stufe"] == "weiterleitung"


def test_belegvarianten_liefern_ihre_aktionen(inventar):
    beleg = {a["maske"] for a in inventar["aktionen"] if a["maske"].startswith("beleg/")}
    assert len(beleg) == len(inventar["familien"]["beleg"])


def test_cli_wird_nicht_geschoent(modul, inventar):
    """Ohne CLI-Register hat keine Aktion einen CLI-Zugang — die Luecke steht vollstaendig in der Ratsche."""
    if (ROOT / "config/cli_mask_commands.json").is_file():
        pytest.skip("CLI-Register vorhanden")
    wirksam = {a["id"] for a in inventar["aktionen"] if a["art"] == "serverwirksam"}
    assert set(modul.gaps(inventar)["aktionen_ohne_cli"]) == wirksam
