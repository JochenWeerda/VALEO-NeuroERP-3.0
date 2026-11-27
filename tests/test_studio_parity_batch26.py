"""Paritaet Batch 26: Schlagkartei + Milchvieh-Karte (agrar_workbench)."""
from __future__ import annotations

from pathlib import Path

import pytest

from app.core.screen_definitions_agrar_workbench import (
    build_agrar_kunden_schlagkartei,
    build_agrar_milchvieh_karte,
)
from app.services.studio_runtime_surface_contracts import SPECIALIZED_SCREENS, validate_runtime_surface

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "packages/frontend-web/src/pages"
REGISTRY = ROOT / "packages/frontend-web/src/components/mask-builder/specialized/registry.ts"
WORKBENCH = ROOT / "packages/frontend-web/src/components/mask-builder/specialized/agrar/agrar-workbench.tsx"


@pytest.mark.unit
def test_schlagkartei_page_and_actions():
    src = (PAGES / "agrar/kunden-schlagkartei.tsx").read_text(encoding="utf-8")
    assert "UniversalNativeCockpitPage" in src
    assert 'screenId="agrar/kunden-schlagkartei"' in src
    sd = build_agrar_kunden_schlagkartei()
    assert sd["mode"] == "cockpit"
    assert sd["specialized"] == {"type": "agrar_workbench", "id": "agrar/kunden-schlagkartei"}
    assert not validate_runtime_surface(sd)
    actions = {a["key"]: a for a in sd["actions"]}
    assert actions["lohn_spritz"]["commandEndpoint"] == "/api/v1/portal/lohndienste"
    assert actions["mahl_misch"]["commandEndpoint"] == "/api/v1/portal/lohndienste"
    assert actions["ankaufsangebot"]["commandEndpoint"] == (
        "/api/v1/portal/empfehlungen/generieren/schlagkartei"
    )
    assert actions["lohn_spritz"]["method"] == "POST"
    field_keys = {f["key"] for f in actions["lohn_spritz"]["inputFields"]}
    assert {"typ", "flaeche_ha", "kultur"}.issubset(field_keys)


@pytest.mark.unit
def test_milchvieh_karte_page_and_map_source():
    src = (PAGES / "agrar/milchvieh-karte.tsx").read_text(encoding="utf-8")
    assert "UniversalNativeCockpitPage" in src
    assert 'screenId="agrar/milchvieh-karte"' in src
    sd = build_agrar_milchvieh_karte()
    assert sd["specialized"]["type"] == "agrar_workbench"
    assert not validate_runtime_surface(sd)
    sources = {d["key"]: d["endpoint"] for d in sd.get("dataSources") or []}
    assert sources["entity"] == "/api/v1/agrar/milchvieh-crosssell/map"


@pytest.mark.unit
def test_agrar_workbench_registered():
    assert "agrar/kunden-schlagkartei" in SPECIALIZED_SCREENS["agrar_workbench"]
    assert "agrar/milchvieh-karte" in SPECIALIZED_SCREENS["agrar_workbench"]
    registry = REGISTRY.read_text(encoding="utf-8")
    assert "agrar_workbench: AgrarWorkbench" in registry
    workbench = WORKBENCH.read_text(encoding="utf-8")
    assert "'agrar/kunden-schlagkartei'" in workbench
    assert "'agrar/milchvieh-karte'" in workbench
    assert "plan.specialized" in workbench
