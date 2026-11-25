"""Paritaet Legacy-Zinsabrechnung → Studio NativeListPage."""
from __future__ import annotations

import re
from pathlib import Path

import pytest

from app.core.screen_definitions_listen import build_agrar_zinsabrechnung_liste

ROOT = Path(__file__).resolve().parents[1]
LEGACY = ROOT / "packages/frontend-web/src/pages/agrar/zinsabrechnung-legacy.tsx"
PAGE = ROOT / "packages/frontend-web/src/pages/agrar/zinsabrechnung.tsx"


@pytest.mark.unit
def test_zinsabrechnung_page_is_native_list():
    src = PAGE.read_text(encoding="utf-8")
    assert "NativeListPage" in src
    assert "agrar/zinsabrechnung" in src
    assert "-legacy" not in src


@pytest.mark.unit
def test_zinsabrechnung_studio_covers_legacy_form_and_actions():
    legacy = LEGACY.read_text(encoding="utf-8")
    form_fields = set(re.findall(r"register\('([^']+)'", legacy))
    assert form_fields, "Legacy-Formfelder nicht gefunden"

    sd = build_agrar_zinsabrechnung_liste()
    anlegen = next(a for a in sd["actions"] if a["key"] == "anlegen")
    create_keys = {f["key"] for f in anlegen["inputFields"]}
    missing = form_fields - create_keys
    assert not missing, f"Studio Anlegen fehlt Legacy-Felder: {sorted(missing)}"
    assert anlegen["commandEndpoint"] == "/api/v1/zinsabrechnung"

    row_keys = {a["key"] for a in sd["tables"][0]["rowActions"]} if sd.get("tables") else set()
    # stamm_list stores row_actions on the table inside the builder output
    if not row_keys:
        # inspect builder structure
        for tab in sd.get("tabs") or []:
            for table in tab.get("tables") or []:
                row_keys |= {a["key"] for a in table.get("rowActions") or []}
    if not row_keys:
        # some parents put rowActions at top level under actions only for header
        # Fall back: rebuild expects row_actions in definition via stamm parent
        from app.core.stamm_list_parent import build_stamm_list_screen
        # parse from sd recursively
        def walk(obj):
            found = set()
            if isinstance(obj, dict):
                if "rowActions" in obj:
                    found |= {a["key"] for a in obj["rowActions"]}
                for v in obj.values():
                    found |= walk(v)
            elif isinstance(obj, list):
                for v in obj:
                    found |= walk(v)
            return found
        row_keys = walk(sd)

    assert {"buchen", "stornieren"}.issubset(row_keys)
    assert "drucken" in row_keys  # additive backend action
