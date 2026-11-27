"""Paritaet Legacy-ObjectPage → Studio ScreenDefinition (Angebot / Anlieferavis).

Studio-made Masken duerfen gegenueber dem Vorgaenger keine Felder oder Aktionen
verlieren; Human, CI und MCP nutzen dieselben commandEndpoints (MCP-WRITE-015).
"""
from __future__ import annotations

import pytest

from app.core.screen_definitions import (
    build_einkauf_angebot_screen_definition,
    build_einkauf_anlieferavis_screen_definition,
)

# Eingefrorene Legacy-Feldvertraege (ObjectPage-Altlasten entfernt 2026-11-25).
# Studio darf gegenueber diesem Stand keine Felder verlieren.
ANGEBOT_LEGACY_FIELDS = {
    "anfrageId",
    "angebotNummer",
    "artikel",
    "einheit",
    "incoterms",
    "lieferantId",
    "menge",
    "mindestabnahme",
    "status",
    "zahlungsbedingungen",
}
ANLIEFERAVIS_LEGACY_FIELDS = {
    "avisNummer",
    "bemerkungen",
    "bestellungId",
    "chargenNummer",
    "fahrzeug.fahrer",
    "fahrzeug.kennzeichen",
    "fahrzeug.telefon",
    "menge",
    "positionId",
    "positionen",
    "status",
    "verpackung",
}


def _collect_sd_field_keys(definition: dict) -> set[str]:
    keys: set[str] = set()
    for tab in definition.get("tabs") or []:
        for field in tab.get("fields") or []:
            keys.add(field["key"])
            for row in field.get("rowFields") or []:
                keys.add(row["key"])
    creation = definition.get("creation") or {}
    for field in creation.get("fields") or []:
        keys.add(field["key"])
        for row in field.get("rowFields") or []:
            keys.add(row["key"])
    return keys


def _collect_sd_action_keys(definition: dict) -> set[str]:
    return {a["key"] for a in definition.get("actions") or []}


def _flatten_legacy_nested(names: set[str]) -> set[str]:
    """``fahrzeug.kennzeichen`` → ``kennzeichen`` (Studio flacht Fahrzeugfelder)."""
    return {name.split(".")[-1] if "." in name else name for name in names}


@pytest.mark.unit
def test_angebot_studio_covers_legacy_fields_and_actions():
    sd = build_einkauf_angebot_screen_definition()
    legacy_fields = _flatten_legacy_nested(ANGEBOT_LEGACY_FIELDS)
    # angebotNummer ist readOnly auf Detail; Create vergibt sie serverseitig.
    required = legacy_fields - {"angebotNummer"}
    missing = required - _collect_sd_field_keys(sd)
    assert not missing, f"Studio Angebot fehlt Legacy-Felder: {sorted(missing)}"

    # bestellen ist die kanonische Fachaktion (Maske/MCP/CLI); Legacy-UI-Label bleibt „In Bestellung“.
    fachaktionen = {"pruefen", "genehmigen", "ablehnen", "bestellen"}
    missing_actions = fachaktionen - _collect_sd_action_keys(sd)
    assert not missing_actions, f"Studio Angebot fehlt Fachaktionen: {sorted(missing_actions)}"

    endpoints = {a["key"]: a.get("commandEndpoint", "") for a in sd["actions"]}
    assert endpoints["pruefen"].endswith("/review")
    assert endpoints["genehmigen"].endswith("/approve")
    assert endpoints["ablehnen"].endswith("/reject")
    assert endpoints["bestellen"].endswith("/actions/bestellen")
    assert sd["creation"]["endpoint"] == "/api/v1/einkauf/angebote"
    assert any(a.get("method") == "PUT" for a in sd["actions"])


@pytest.mark.unit
def test_anlieferavis_studio_covers_legacy_fields_and_actions():
    sd = build_einkauf_anlieferavis_screen_definition()
    legacy_fields = _flatten_legacy_nested(ANLIEFERAVIS_LEGACY_FIELDS)
    missing = legacy_fields - _collect_sd_field_keys(sd)
    assert not missing, f"Studio Anlieferavis fehlt Legacy-Felder: {sorted(missing)}"

    legacy_actions = {"senden", "bestaetigen", "stornieren"}
    missing_actions = legacy_actions - _collect_sd_action_keys(sd)
    assert not missing_actions, f"Studio Anlieferavis fehlt Legacy-Aktionen: {sorted(missing_actions)}"

    endpoints = {a["key"]: a.get("commandEndpoint", "") for a in sd["actions"]}
    assert endpoints["senden"].endswith("/send")
    assert endpoints["bestaetigen"].endswith("/confirm")
    assert endpoints["stornieren"].endswith("/cancel")
    assert "wareneingang" in endpoints  # additive, kein Verlust
    assert sd["creation"]["endpoint"] == "/api/v1/einkauf/anlieferavis"
    assert any(a.get("method") == "PUT" for a in sd["actions"])
