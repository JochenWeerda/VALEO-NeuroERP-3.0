"""
Drift-Gate: Studio WorkspaceComposition YAML ↔ kanonische screenIds/Kinds.

Kein Server-Write, keine Secrets. Spiegelt den Vitest-Vertrag
packages/frontend-web/src/__tests__/studio/workspace-composition.test.ts.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_PATH = REPO_ROOT / "config" / "studio_workspace_composition.fixture.yaml"

EXPECTED_VIEW_SCREEN_IDS = {
    "workspace/disposition-cockpit",
    "workspace/document-inbox",
}
EXPECTED_KINDS = {"inbox", "disposition_board"}


@pytest.mark.unit
def test_studio_workspace_composition_fixture_screen_ids_and_kinds() -> None:
    raw = FIXTURE_PATH.read_text(encoding="utf-8")
    data = yaml.safe_load(raw)
    assert isinstance(data, dict)
    assert data.get("schemaVersion") == 1
    assert data.get("id") == "workspace.disposition-und-inbox"

    views = data.get("views") or []
    slots = data.get("specializedComponents") or []
    assert isinstance(views, list) and views
    assert isinstance(slots, list) and slots

    view_screen_ids = {view["screenId"] for view in views if isinstance(view, dict)}
    assert view_screen_ids == EXPECTED_VIEW_SCREEN_IDS

    kinds = {slot["kind"] for slot in slots if isinstance(slot, dict)}
    assert kinds == EXPECTED_KINDS

    for slot in slots:
        assert isinstance(slot, dict)
        screen_id = slot.get("screenId")
        assert screen_id in view_screen_ids
        assert slot.get("hostViewId") in {view["id"] for view in views}

    personalization = data.get("personalization") or {}
    assert str(personalization.get("pinStorageKey", "")).startswith("valeo.")
