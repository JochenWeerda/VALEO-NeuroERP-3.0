"""UIX-061: Rollen-Workspaces — 5 native cockpit-SDs mit Kacheln.

Sichert Readiness (generatorReady + advisoryScore>=0.8), die additive
tiles-Struktur, die aufgeloesten Kachel-Routen und das Saison-Ordering.
"""
from __future__ import annotations

import pytest

from app.core.screen_definitions import (
    _SCREEN_DEFINITIONS,
    get_screen_definition,
)
from app.api.v1.endpoints.mask_screen_definition import _check_readiness

WORKSPACES = [
    "workspace/einkauf",
    "workspace/verkauf",
    "workspace/lager",
    "workspace/fibu",
    "workspace/leitung",
]


def test_all_five_workspaces_registered():
    for sid in WORKSPACES:
        assert sid in _SCREEN_DEFINITIONS, f"{sid} fehlt in der Registry"


@pytest.mark.parametrize("screen_id", WORKSPACES)
def test_workspace_is_generator_ready(screen_id: str):
    sd = get_screen_definition(screen_id)
    assert sd is not None
    assert sd["mode"] == "cockpit"
    readiness = _check_readiness(sd)
    assert readiness["generatorReady"] is True, readiness
    assert readiness["advisoryScore"] >= 0.8


@pytest.mark.parametrize("screen_id", WORKSPACES)
def test_workspace_tiles_have_resolved_routes(screen_id: str):
    sd = get_screen_definition(screen_id)
    tiles = sd.get("tiles")
    assert tiles, f"{screen_id} hat keine Kacheln"
    for tile in tiles:
        assert tile.get("key")
        assert tile.get("label")
        assert tile.get("tone") in {"neutral", "warning", "danger"}
        # targetScreenId ist auf eine reale Listen-Route aufgeloest
        assert tile.get("targetRoute", "").startswith("/"), tile


@pytest.mark.parametrize("screen_id", WORKSPACES)
def test_workspace_has_summary_slots(screen_id: str):
    sd = get_screen_definition(screen_id)
    assert len(sd.get("summary") or []) >= 3


def test_cockpit_without_content_flags_advisory():
    """Das neue cockpit_content-Advisory schlaegt bei leerem Cockpit an."""
    empty = {
        "schemaVersion": 1, "id": "workspace/leer", "domain": "core",
        "mode": "cockpit", "title": "Leer",
        "adapter": {"type": "native", "temporary": False},
        "layout": {"floorplan": "cockpit", "density": "compact", "contextRail": "combined"},
        "agentContract": {"businessPurpose": "x", "testSelectors": {"screenRoot": "[data-testid='x']"}},
        "noWorkflowReason": "leer",
    }
    readiness = _check_readiness(empty)
    gate = next(g for g in readiness["gates"] if g["gate"] == "cockpit_content")
    assert gate["passed"] is False


def test_season_profile_reorders_tiles_within_window():
    """seasonProfile.tileOrderOverride sortiert nur um — Inhalt bleibt gleich."""
    from app.core.screen_definitions import _apply_season_profile

    definition = {
        "tiles": [
            {"key": "a", "label": "A"},
            {"key": "b", "label": "B"},
            {"key": "c", "label": "C"},
        ],
        "seasonProfile": {"activeFrom": "07-01", "activeTo": "09-15", "tileOrderOverride": ["c", "a", "b"]},
    }
    _apply_season_profile(definition, today="2026-08-01")
    assert [t["key"] for t in definition["tiles"]] == ["c", "a", "b"]

    # ausserhalb des Fensters bleibt die Reihenfolge unveraendert
    definition2 = {
        "tiles": [{"key": "a"}, {"key": "b"}, {"key": "c"}],
        "seasonProfile": {"activeFrom": "07-01", "activeTo": "09-15", "tileOrderOverride": ["c", "a", "b"]},
    }
    _apply_season_profile(definition2, today="2026-01-15")
    assert [t["key"] for t in definition2["tiles"]] == ["a", "b", "c"]
