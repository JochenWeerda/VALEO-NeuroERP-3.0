"""Paritaet Batch 30: Nav-Routen connectoren + Fahrzeug-Vertiefung."""
from __future__ import annotations

from pathlib import Path

import pytest

from app.core.screen_definitions_fleet_workbench import build_fuhrpark_fahrzeug_vertiefung
from app.core.screen_definitions_listen import build_admin_suite_connectoren_cockpit
from app.services.studio_runtime_surface_contracts import SPECIALIZED_SCREENS, validate_runtime_surface

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "packages/frontend-web/src/pages"
SPECIALIZED = ROOT / "packages/frontend-web/src/components/mask-builder/specialized"
SCHEMA = ROOT / "packages/frontend-web/src/components/mask-builder/schema.ts"
REGISTRY = SPECIALIZED / "registry.ts"
ADMIN_SUITE_AUTO = ROOT / "packages/frontend-web/src/app/route-builders/auto-groups/generated/admin-suite.ts"
FUHRPARK_AUTO = ROOT / "packages/frontend-web/src/app/route-builders/auto-groups/generated/fuhrpark.ts"
API = ROOT / "packages/frontend-web/src/lib/api/fuhrpark.ts"


@pytest.mark.unit
def test_admin_suite_connectoren_route_and_cockpit():
    src = (PAGES / "admin-suite/connectoren.tsx").read_text(encoding="utf-8")
    assert "UniversalNativeCockpitPage" in src
    assert 'screenId="admin-suite/connectoren"' in src
    auto = ADMIN_SUITE_AUTO.read_text(encoding="utf-8")
    assert "connectoren" in auto
    assert "@/pages/admin-suite/connectoren" in auto
    sd = build_admin_suite_connectoren_cockpit()
    assert sd["id"] == "admin-suite/connectoren"
    sources = {ds["key"]: ds["endpoint"] for ds in sd["dataSources"]}
    assert sources["entity"] == "/api/v1/admin-suite/capture-connectors/overview"
    actions = {a["key"]: a for a in sd["actions"]}
    assert "stt_speichern" in actions
    assert "imap_speichern" in actions


@pytest.mark.unit
def test_fahrzeug_vertiefung_fleet_workbench_parity():
    src = (PAGES / "fuhrpark/fahrzeug-vertiefung.tsx").read_text(encoding="utf-8")
    assert "UniversalNativeCockpitPage" in src
    assert 'screenId="fuhrpark/fahrzeug-vertiefung"' in src
    legacy = (PAGES / "fuhrpark/fahrzeug-vertiefung-legacy.tsx").read_text(encoding="utf-8")
    assert "min-h-touch" in legacy
    assert "Abschließen" in legacy or "Abschlie" in legacy
    assert "Bezahlt" in legacy
    assert (SPECIALIZED / "fleet/fahrzeug-vertiefung-surface.tsx").exists()
    assert (SPECIALIZED / "fleet/fleet-workbench.tsx").exists()

    auto = FUHRPARK_AUTO.read_text(encoding="utf-8")
    assert "fahrzeug-vertiefung" in auto
    assert "@/pages/fuhrpark/fahrzeug-vertiefung" in auto

    sd = build_fuhrpark_fahrzeug_vertiefung()
    assert sd["id"] == "fuhrpark/fahrzeug-vertiefung"
    assert sd["specialized"] == {
        "type": "fleet_workbench",
        "id": "fuhrpark/fahrzeug-vertiefung",
    }
    assert not validate_runtime_surface(sd)
    assert "fuhrpark/fahrzeug-vertiefung" in SPECIALIZED_SCREENS["fleet_workbench"]

    actions = {a["key"]: a for a in sd["actions"]}
    base = "/api/v1/fuhrpark/fahrzeuge/{fahrzeug_id}"
    assert actions["status_wechseln"]["commandEndpoint"] == f"{base}/status"
    assert actions["schaden_anlegen"]["commandEndpoint"] == f"{base}/schaeden"
    assert actions["bussgeld_bezahlt"]["commandEndpoint"] == f"{base}/bussgeld/{{bg_id}}"
    assert actions["leasing_rueckgabe"]["commandEndpoint"] == f"{base}/leasing-rueckgabe"
    assert all(a.get("surfaceOnly") is True for a in sd["actions"])

    api = API.read_text(encoding="utf-8")
    assert "/status" in api
    assert "/schaeden" in api
    assert "/bussgeld" in api
    assert "/leasing-rueckgabe" in api

    schema = SCHEMA.read_text(encoding="utf-8")
    assert "fleet_workbench" in schema
    registry = REGISTRY.read_text(encoding="utf-8")
    assert "fleet_workbench: FleetWorkbench" in registry
