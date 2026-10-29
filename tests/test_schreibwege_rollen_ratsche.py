"""Ratsche: Kein neuer Schreibweg ohne Rollen- oder Rechtepruefung (``scripts/check_write_routes_roles.py``).

Die Bearer-Pruefung sagt nur, *wer* anfragt, nicht, *was* er darf. Am 19.10.2026 standen 1603 Schreibwege ohne
erkennbare Pruefung in ``config/write_routes_without_roles.json``; die Liste darf nur schrumpfen.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.unit


def test_keine_neuen_schreibwege_ohne_rollenpruefung():
    import importlib.util
    from pathlib import Path

    pfad = Path(__file__).resolve().parents[1] / "scripts" / "check_write_routes_roles.py"
    spec = importlib.util.spec_from_file_location("check_write_routes_roles", pfad)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    assert modul.main(["--check"]) == 0


def test_die_kommando_wege_des_rollouts_pruefen_rollen():
    """Die im Rollout gebauten oder gesicherten Wege stehen nicht in der Bestandsliste."""
    import json
    from pathlib import Path

    bestand = set(json.loads((Path(__file__).resolve().parents[1] / "config" / "write_routes_without_roles.json")
                             .read_text(encoding="utf-8"))["wege"])
    for weg in (
        "POST /api/v1/billing-batches/{entity_id}/actions/{action_key}",
        "POST /api/v1/production-control/operations/{entity_id}/actions/{action_key}",
        "POST /api/v1/production-control/operations/{operation_id}/transition",
        "POST /api/v1/foreign-goods/{entity_id}/actions/{action_key}",
        "POST /api/v1/inventory/auxiliary/batches/{entity_id}/actions/{action_key}",
        "POST /api/v1/tank-adapter/intake/{entity_id}/actions/{action_key}",
        "POST /api/v1/mobile/sync-queue/{entity_id}/actions/retry_event",
        "POST /api/v1/document-returns/{entity_id}/actions/{action_key}",
        "POST /api/v1/sales/orders/{entity_id}/actions/stornieren",
        "POST /api/v1/document-control/exceptions/{entity_id}/actions/{action_key}",
    ):
        assert weg not in bestand, weg
