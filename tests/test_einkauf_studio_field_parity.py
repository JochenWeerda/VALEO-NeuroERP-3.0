"""Paritaet Legacy-ObjectPage → Studio ScreenDefinition (Angebot / Anlieferavis).

Studio-made Masken duerfen gegenueber dem Vorgaenger keine Felder oder Aktionen
verlieren; Human, CI und MCP nutzen dieselben commandEndpoints (MCP-WRITE-015).
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from app.core.screen_definitions import (
    build_einkauf_angebot_screen_definition,
    build_einkauf_anlieferavis_screen_definition,
)

ROOT = Path(__file__).resolve().parents[1]
FE_PAGES = ROOT / "packages" / "frontend-web" / "src" / "pages" / "einkauf"


def _field_names_from_legacy(source: str) -> set[str]:
    """Nur ``fields: [...]``-Bloecke der MaskConfig (nicht tabs/actions)."""
    names: set[str] = set()
    for block in re.finditer(r"fields:\s*\[(.*?)\](?=\s*(?:\}|,?\s*\{?\s*key:|\s*actions:))", source, re.S):
        body = block.group(1)
        names |= {m.group(1) for m in re.finditer(r"name:\s*'([^']+)'", body)}
        names |= {m.group(1) for m in re.finditer(r"\{\s*key:\s*'([^']+)'\s*,\s*label:", body)}
    return names


def _action_keys_from_legacy(source: str) -> set[str]:
    block = re.search(r"actions:\s*\[(.*?)\]\s*,\s*api:", source, re.S)
    if not block:
        return set()
    return {m.group(1) for m in re.finditer(r"key:\s*'([^']+)'", block.group(1))}


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
    legacy = (FE_PAGES / "angebot-stamm-legacy.tsx").read_text(encoding="utf-8")
    sd = build_einkauf_angebot_screen_definition()
    legacy_fields = _flatten_legacy_nested(_field_names_from_legacy(legacy))
    # angebotNummer ist readOnly auf Detail; Create vergibt sie serverseitig.
    required = legacy_fields - {"angebotNummer"}
    missing = required - _collect_sd_field_keys(sd)
    assert not missing, f"Studio Angebot fehlt Legacy-Felder: {sorted(missing)}"

    legacy_actions = {"pruefen", "genehmigen", "ablehnen", "inBestellung"}
    missing_actions = legacy_actions - _collect_sd_action_keys(sd)
    assert not missing_actions, f"Studio Angebot fehlt Legacy-Aktionen: {sorted(missing_actions)}"

    endpoints = {a["key"]: a.get("commandEndpoint", "") for a in sd["actions"]}
    assert endpoints["pruefen"].endswith("/review")
    assert endpoints["genehmigen"].endswith("/approve")
    assert endpoints["ablehnen"].endswith("/reject")
    assert endpoints["inBestellung"].endswith("/convert-to-order")
    assert sd["creation"]["endpoint"] == "/api/v1/einkauf/angebote"
    assert any(a.get("method") == "PUT" for a in sd["actions"])


@pytest.mark.unit
def test_anlieferavis_studio_covers_legacy_fields_and_actions():
    legacy = (FE_PAGES / "anlieferavis-legacy.tsx").read_text(encoding="utf-8")
    sd = build_einkauf_anlieferavis_screen_definition()
    legacy_fields = _flatten_legacy_nested(_field_names_from_legacy(legacy))
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
