"""Paritaet Batch 29: Konditionssystem pricing_workbench."""
from __future__ import annotations

from pathlib import Path

import pytest

from app.core.screen_definitions_pricing_workbench import build_konditionen_konditionssystem
from app.services.studio_runtime_surface_contracts import SPECIALIZED_SCREENS, validate_runtime_surface

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "packages/frontend-web/src/pages"
SPECIALIZED = ROOT / "packages/frontend-web/src/components/mask-builder/specialized"
SCHEMA = ROOT / "packages/frontend-web/src/components/mask-builder/schema.ts"
REGISTRY = SPECIALIZED / "registry.ts"
AUTO_GROUP = ROOT / "packages/frontend-web/src/app/route-builders/auto-groups/generated/konditionen.ts"
API = ROOT / "packages/frontend-web/src/lib/api/konditionen.ts"


@pytest.mark.unit
def test_konditionssystem_pricing_workbench_parity():
    src = (PAGES / "konditionen/konditionssystem.tsx").read_text(encoding="utf-8")
    assert "UniversalNativeCockpitPage" in src
    assert 'screenId="konditionen/konditionssystem"' in src
    assert (PAGES / "konditionen/konditionssystem-legacy.tsx").exists()
    assert (SPECIALIZED / "pricing/konditionssystem-surface.tsx").exists()
    assert (SPECIALIZED / "pricing/pricing-workbench.tsx").exists()

    sd = build_konditionen_konditionssystem()
    assert sd["id"] == "konditionen/konditionssystem"
    assert sd["specialized"] == {
        "type": "pricing_workbench",
        "id": "konditionen/konditionssystem",
    }
    assert not validate_runtime_surface(sd)
    assert "konditionen/konditionssystem" in SPECIALIZED_SCREENS["pricing_workbench"]

    sources = {ds["key"]: ds["endpoint"] for ds in sd["dataSources"]}
    assert sources["preislisten"] == "/api/v1/price-lists/"
    assert sources["rabattgruppen"] == "/api/v1/preise/rabatte/gruppen"
    assert sources["individualpreise"] == "/api/v1/preise/individualpreise"

    actions = {a["key"]: a for a in sd["actions"]}
    assert actions["preisliste_anlegen"]["commandEndpoint"] == "/api/v1/price-lists/"
    assert actions["rabattgruppe_anlegen"]["commandEndpoint"] == "/api/v1/preise/rabatte/gruppen"
    assert actions["rabattsatz_anlegen"]["commandEndpoint"] == "/api/v1/preise/rabatte/saetze"
    assert actions["individualpreis_anlegen"]["commandEndpoint"] == "/api/v1/preise/individualpreise"
    assert actions["preis_berechnen"]["commandEndpoint"] == "/api/v1/pricing/calculate"
    assert actions["preis_berechnen"]["method"] == "GET"
    assert all(a.get("surfaceOnly") is True for a in sd["actions"])

    field_keys = {f["key"] for f in actions["rabattgruppe_anlegen"]["inputFields"]}
    assert {"gruppe_nr", "bezeichnung", "richtung"}.issubset(field_keys)
    ip_keys = {f["key"] for f in actions["individualpreis_anlegen"]["inputFields"]}
    assert {"artikel_nr", "preis_eur", "gueltig_von", "preis_typ"}.issubset(ip_keys)

    api = API.read_text(encoding="utf-8")
    assert "/api/v1/price-lists/" in api
    assert "/api/v1/preise/rabatte/gruppen" in api
    assert "/api/v1/pricing/calculate" in api

    schema = SCHEMA.read_text(encoding="utf-8")
    assert "pricing_workbench" in schema
    assert "'konditionen/konditionssystem'" in schema or '"konditionen/konditionssystem"' in schema

    registry = REGISTRY.read_text(encoding="utf-8")
    assert "pricing_workbench: PricingWorkbench" in registry

    auto = AUTO_GROUP.read_text(encoding="utf-8")
    assert "konditionssystem" in auto
    assert "@/pages/konditionen/konditionssystem" in auto
