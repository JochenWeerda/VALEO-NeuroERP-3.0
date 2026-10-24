"""Studio release catalog for native ScreenDefinitions."""
from __future__ import annotations

import json

import pytest

from app.core.studio_release import definition_hash
from app.core.studio_screen_versions import (
    REGISTRY_PATH,
    build_catalog_entry,
    check_registry,
    current_matches,
    released_screen_ids,
)
from app.services.made_by_studio_gates import load_registered_definitions


def _native_definitions():
    return {sid: definition for sid, definition in load_registered_definitions().items()
            if not sid.startswith("beleg/") and definition}


def test_catalog_matches_all_native_builders():
    if not REGISTRY_PATH.is_file():
        pytest.skip("catalog not generated yet")
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    definitions = _native_definitions()
    assert current_matches(registry, definitions)


def test_released_ids_are_subset_of_catalog():
    if not REGISTRY_PATH.is_file():
        pytest.skip("catalog not generated yet")
    registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    released = released_screen_ids()
    assert released <= set(registry.get("screens", {}))
    for screen_id in released:
        entry = registry["screens"][screen_id]
        assert entry["gates_passed"] == ["A", "B", "C", "E"]
        assert entry["studio_draft_clean"] is True


def test_build_catalog_entry_hash_is_stable():
    definition = {"schemaVersion": 1, "id": "test/catalog", "title": "T", "mode": "list", "domain": "test"}
    entry = build_catalog_entry(definition, version="1.0.0", gates_passed=["A"], studio_draft_clean=False)
    assert entry["definition_hash"] == definition_hash(definition)
    check_registry({"schemaVersion": 1, "releaseVersion": "1.0.0", "screens": {"test/catalog": entry}},
                   definitions={"test/catalog": definition})
