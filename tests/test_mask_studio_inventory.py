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


def test_cli_befund_kommt_allein_aus_dem_register(modul, inventar):
    """CLI-Zugang hat genau, was das aus valeo_cli.support erzeugte Register fuehrt — nichts wird geschoent."""
    import json
    register = set(json.loads((ROOT / "config/cli_mask_commands.json").read_text(encoding="utf-8"))["mask_action_ids"])
    assert {a["id"] for a in inventar["aktionen"] if a["cli"]} == register
    wirksam = {a["id"] for a in inventar["aktionen"] if a["art"] == "serverwirksam"}
    assert set(modul.gaps(inventar)["aktionen_ohne_cli"]) == wirksam - register


def test_katalogaktion_ohne_route_oder_mcp_macht_die_ratsche_rot(modul, inventar, capsys):
    """Studio-Masken tragen nur Katalogaktionen — eine unbedienbare Katalogaktion waere in jeder Studio-Maske kaputt."""
    inv = copy.deepcopy(inventar)
    inv["studio_katalog"]["aktionen"].append({"aktion": "neu_kaputt", "endpunkt": "/api/v1/gibt/es/nicht",
                                              "route": False, "cli": True, "mcp": [], "mcp_bedienbar": False})
    assert modul.check(inv) == 1
    out = capsys.readouterr().out
    assert "aktion:neu_kaputt:ohne_route" in out and "aktion:neu_kaputt:mcp_nicht_ausfuehrbar" in out


def test_katalog_wird_gegen_openapi_und_mcp_karte_geprueft(modul, inventar):
    rows = {a["aktion"]: a for a in inventar["studio_katalog"]["aktionen"]}
    assert rows["freigeben"]["route"] and rows["freigeben"]["cli"] and rows["freigeben"]["mcp_bedienbar"]
    assert "mapped_read" not in modul.MCP_BEDIENBAR, "nur Status lesen ist kein Bedienen"
    for row in rows.values():
        assert row["mcp_bedienbar"] == bool(set(row["mcp"]) & modul.MCP_BEDIENBAR)
