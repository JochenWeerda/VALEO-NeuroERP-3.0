"""Contracts for ScreenDefinition → mask action catalog (ACTION-DEN)."""

from __future__ import annotations

import json
from pathlib import Path

from app.core.screen_action_catalog import (
    action_has_execution_path,
    build_screen_action_catalog,
    catalog_stats,
    mask_action_id,
    screen_action_to_catalog_entry,
)

REPO = Path(__file__).resolve().parents[1]
CATALOG_JSON = REPO / "services" / "ki-usability" / "app" / "data" / "screen_mask_actions.json"


def test_action_has_execution_path_requires_real_route() -> None:
    assert action_has_execution_path({"commandEndpoint": "/api/v1/x"})
    assert action_has_execution_path({"navigationRoute": "/lager"})
    assert action_has_execution_path({"command": "local.save"})
    assert action_has_execution_path(
        {"inputFlow": {"kind": "humanForm", "submitEndpoint": "/api/v1/y"}}
    )
    assert not action_has_execution_path({"key": "stub", "stubReason": "todo"})
    assert not action_has_execution_path({})


def test_screen_action_to_catalog_entry_namespaces_id() -> None:
    entry = screen_action_to_catalog_entry(
        "finance/ap-invoice",
        "finance",
        {
            "key": "freigeben",
            "label": "Freigeben",
            "commandEndpoint": "/api/v1/finance/ap/invoices/{entity_id}/actions/freigeben",
            "method": "POST",
        },
    )
    assert entry is not None
    assert entry["id"] == mask_action_id("finance/ap-invoice", "freigeben")
    assert entry["mask"] == "finance/ap-invoice"
    assert entry["domain"] == "finance"
    assert "Freigeben" in entry["intent_phrases"]
    assert entry["required_data"] == ["entity_id"]


def test_build_catalog_unique_ids_and_min_size() -> None:
    catalog = build_screen_action_catalog()
    ids = [row["id"] for row in catalog]
    assert len(ids) == len(set(ids))
    stats = catalog_stats(catalog)
    assert stats["actions"] >= 80
    assert stats["screens_with_actions"] >= 20
    assert all(row["id"].startswith("mask:") for row in catalog)


def test_committed_catalog_json_matches_builders() -> None:
    assert CATALOG_JSON.is_file(), "generate screen_mask_actions.json first"
    live = build_screen_action_catalog()
    payload = json.loads(CATALOG_JSON.read_text(encoding="utf-8"))
    assert payload["schemaVersion"] == 1
    assert payload["stats"]["actions"] == len(live)
    assert [a["id"] for a in payload["actions"]] == [a["id"] for a in live]

