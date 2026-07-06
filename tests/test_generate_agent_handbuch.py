"""Tests fuer scripts/generate_agent_handbuch.py und agent_handbuch_sources.py."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.agent_handbuch_sources import (
    MASK_TO_PROCESSES,
    derive_agent_contract,
    load_flow_spine_catalog,
    load_screen_definitions,
    mask_rollout_route,
    risk_summary,
)
from scripts.generate_agent_handbuch import (
    GENERATED_FILES,
    OUT,
    generate,
    normalize_for_check,
)

REPO = Path(__file__).resolve().parents[1]


@pytest.mark.unit
def test_load_flow_spine_catalog_has_nine_processes() -> None:
    catalog = load_flow_spine_catalog()
    assert len(catalog) == 9
    keys = {item["key"] for item in catalog}
    assert "order-to-cash" in keys
    assert "procure-to-pay" in keys


@pytest.mark.unit
def test_load_screen_definitions_count() -> None:
    masks = load_screen_definitions()
    assert len(masks) >= 26
    assert "sales/sales-order" in masks


@pytest.mark.unit
def test_derive_agent_contract_includes_actions() -> None:
    masks = load_screen_definitions()
    order = masks["sales/sales-order"]
    contract = derive_agent_contract(order)
    assert contract["screenId"]
    assert isinstance(contract["readableFields"], list)
    assert isinstance(contract["availableActions"], list)


@pytest.mark.unit
def test_mask_rollout_route_format() -> None:
    assert mask_rollout_route("sales/sales-order") == "/mask-rollout/sales__sales-order/:entityId"


@pytest.mark.unit
def test_risk_summary_escalates_with_danger_level() -> None:
    assert risk_summary([{"dangerLevel": "safe"}]) == "low"
    assert risk_summary([{"dangerLevel": "moderate"}]) == "medium"
    assert risk_summary([{"dangerLevel": "high"}]) == "high"


@pytest.mark.unit
def test_mask_to_processes_links_known_masks() -> None:
    assert "order-to-cash" in MASK_TO_PROCESSES["sales/sales-order"]
    assert "procure-to-pay" in MASK_TO_PROCESSES["einkauf/purchase-order"]


@pytest.mark.unit
def test_generate_produces_five_artifacts() -> None:
    outputs = generate()
    assert len(outputs) == 5
    assert all(path in outputs for path in GENERATED_FILES)
    index = outputs[OUT / "index.md"]
    assert "Agent-Handbuch" in index
    assert "generate_agent_handbuch.py" in index
    manifest = json.loads(outputs[OUT / "agent-process-manifest.json"])
    assert manifest["schemaVersion"] == 1
    assert len(manifest["processes"]) == 9
    assert len(manifest["masks"]) >= 26


@pytest.mark.unit
def test_normalize_for_check_ignores_volatile_dates() -> None:
    md_a = "---\nlast_reviewed: 2026-01-01\n---\nbody\n"
    md_b = "---\nlast_reviewed: 2026-07-01\n---\nbody\n"
    assert normalize_for_check(md_a) == normalize_for_check(md_b)

    json_a = json.dumps({"generatedAt": "2026-01-01", "x": 1}, indent=2) + "\n"
    json_b = json.dumps({"generatedAt": "2026-07-01", "x": 1}, indent=2) + "\n"
    assert normalize_for_check(json_a, ".json") == normalize_for_check(json_b, ".json")


@pytest.mark.unit
def test_generated_files_exist_and_match_check() -> None:
    for path in GENERATED_FILES:
        assert path.is_file(), f"fehlend: {path.relative_to(REPO)}"
    outputs = generate()
    for path, expected in outputs.items():
        actual = path.read_text(encoding="utf-8")
        exp = expected if expected.endswith("\n") else expected + "\n"
        assert normalize_for_check(actual, path.suffix) == normalize_for_check(exp, path.suffix)
