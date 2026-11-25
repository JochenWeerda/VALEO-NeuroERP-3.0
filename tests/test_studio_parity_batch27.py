"""Paritaet Batch 27: Ernte-Erfassung, Abrechnung, Materialfluss."""
from __future__ import annotations

from pathlib import Path

import pytest

from app.core.screen_definitions_agrar_workbench import (
    build_agrar_ernte_annahme_erfassung,
    build_annahme_abrechnung,
)
from app.core.screen_definitions_lager_workbench import build_lager_materialfluss
from app.services.studio_runtime_surface_contracts import SPECIALIZED_SCREENS, validate_runtime_surface

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "packages/frontend-web/src/pages"
REGISTRY = ROOT / "packages/frontend-web/src/components/mask-builder/specialized/registry.ts"


@pytest.mark.unit
def test_ernte_annahme_erfassung_parity():
    src = (PAGES / "agrar/ernte-annahme-erfassung.tsx").read_text(encoding="utf-8")
    assert "UniversalNativeCockpitPage" in src
    assert 'screenId="agrar/ernte-annahme-erfassung"' in src
    assert (PAGES / "agrar/ernte-annahme-erfassung-legacy.tsx").exists()
    sd = build_agrar_ernte_annahme_erfassung()
    assert sd["specialized"] == {"type": "agrar_workbench", "id": "agrar/ernte-annahme-erfassung"}
    assert not validate_runtime_surface(sd)
    actions = {a["key"]: a for a in sd["actions"]}
    assert actions["anlegen"]["commandEndpoint"] == "/api/v1/agrar/harvest-acceptance"
    assert actions["speichern"]["commandEndpoint"] == "/api/v1/agrar/harvest-acceptance/{entity_id}"
    assert actions["speichern"]["method"] == "PUT"
    assert actions["berechnen"]["commandEndpoint"] == "/api/v1/agrar/harvest-acceptance/{entity_id}/calculate"
    assert actions["freigeben"]["commandEndpoint"] == "/api/v1/agrar/harvest-acceptance/{entity_id}/release"
    assert actions["loeschen"]["method"] == "DELETE"
    assert "customer_id" in {f["key"] for f in actions["anlegen"]["inputFields"]}


@pytest.mark.unit
def test_annahme_abrechnung_parity():
    src = (PAGES / "annahme/abrechnung.tsx").read_text(encoding="utf-8")
    assert "UniversalNativeCockpitPage" in src
    assert 'screenId="annahme/abrechnung"' in src
    assert (PAGES / "annahme/abrechnung-legacy.tsx").exists()
    sd = build_annahme_abrechnung()
    assert sd["specialized"]["id"] == "annahme/abrechnung"
    assert not validate_runtime_surface(sd)
    actions = {a["key"]: a for a in sd["actions"]}
    assert actions["anlegen"]["commandEndpoint"] == "/api/v1/agrar/settlements"
    assert actions["billing_preview"]["commandEndpoint"] == (
        "/api/v1/agrar/settlements/billing-weight/preview"
    )
    assert actions["drying_compute"]["commandEndpoint"] == "/api/v1/agrar/settlements/drying/compute"
    assert actions["post_fibu"]["commandEndpoint"] == "/api/v1/agrar/settlements/{entity_id}/post-fibu"
    assert actions["freigabe"]["commandEndpoint"] == "/api/v1/agrar/settlements/{entity_id}/freigabe"
    assert actions["stornieren"]["commandEndpoint"] == "/api/v1/agrar/settlements/{entity_id}/cancel"


@pytest.mark.unit
def test_materialfluss_lager_workbench():
    src = (PAGES / "lager/materialfluss.tsx").read_text(encoding="utf-8")
    assert "UniversalNativeCockpitPage" in src
    assert 'screenId="lager/materialfluss"' in src
    assert (PAGES / "lager/materialfluss-legacy.tsx").exists()
    sd = build_lager_materialfluss()
    assert sd["specialized"] == {"type": "lager_workbench", "id": "lager/materialfluss"}
    assert not validate_runtime_surface(sd)
    actions = {a["key"]: a for a in sd["actions"]}
    assert actions["node_anlegen"]["commandEndpoint"] == "/api/v1/lager/wms/agri/material-flow/nodes"
    assert actions["transfer"]["commandEndpoint"] == "/api/v1/lager/wms/agri/material-flow/transfer"
    assert actions["lot_link"]["commandEndpoint"] == "/api/v1/lager/wms/agri/material-flow/lot-link"
    assert "lager/materialfluss" in SPECIALIZED_SCREENS["lager_workbench"]
    assert "agrar/ernte-annahme-erfassung" in SPECIALIZED_SCREENS["agrar_workbench"]
    assert "annahme/abrechnung" in SPECIALIZED_SCREENS["agrar_workbench"]
    registry = REGISTRY.read_text(encoding="utf-8")
    assert "lager_workbench: LagerWorkbench" in registry
