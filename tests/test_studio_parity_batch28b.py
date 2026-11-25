"""Paritaet Batch 28b: restliche duenne Admin-Ops-Routen."""
from __future__ import annotations

from pathlib import Path

import pytest

from app.core.screen_definitions_admin_ops_thin import ADMIN_OPS_THIN_BUILDERS
from app.services.studio_runtime_surface_contracts import SPECIALIZED_SCREENS, validate_runtime_surface

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "packages/frontend-web/src/pages"
ADMIN_WB = ROOT / "packages/frontend-web/src/components/mask-builder/specialized/admin/admin-workbench.tsx"

EXPECTED = {
    "admin/GapPipelineConsole": "admin/GapPipelineConsole.tsx",
    "admin/agenten-integration": "admin/agenten-integration.tsx",
    "admin/postfaecher-anmeldung-rueckruf": "admin/postfaecher-anmeldung-rueckruf.tsx",
    "admin/screen-studio": "admin/screen-studio.tsx",
    "admin/setup": "admin/setup/index.tsx",
    "admin/setup/dms-integration": "admin/setup/dms-integration.tsx",
    "admin/voice-channel": "admin/voice-channel.tsx",
    "admin/vordruck-editor": "admin/vordruck-editor.tsx",
    "studio/workspace-composition-preview": "studio/workspace-composition-preview.tsx",
}


@pytest.mark.unit
@pytest.mark.parametrize("screen_id,rel", sorted(EXPECTED.items()))
def test_thin_admin_page_wired(screen_id: str, rel: str):
    src = (PAGES / rel).read_text(encoding="utf-8")
    assert "IntakeWeighingPage" in src
    assert f'screenId="{screen_id}"' in src
    assert screen_id in SPECIALIZED_SCREENS["admin_workbench"]
    sd = ADMIN_OPS_THIN_BUILDERS[screen_id]()
    assert sd["specialized"] == {"type": "admin_workbench", "id": screen_id}
    assert not validate_runtime_surface(sd)


@pytest.mark.unit
def test_vordruck_and_dms_commands():
    v = ADMIN_OPS_THIN_BUILDERS["admin/vordruck-editor"]()
    actions = {a["key"]: a for a in v["actions"]}
    assert actions["anlegen"]["commandEndpoint"] == "/api/v1/admin/vordrucke"
    assert actions["speichern"]["method"] == "PUT"
    assert actions["seed_standard"]["commandEndpoint"] == "/api/v1/admin/vordrucke/seed-standard"
    dms = ADMIN_OPS_THIN_BUILDERS["admin/setup/dms-integration"]()
    dms_actions = {a["key"]: a for a in dms["actions"]}
    assert dms_actions["bootstrap"]["commandEndpoint"] == "/api/v1/admin/dms/bootstrap"
    assert dms_actions["test"]["commandEndpoint"] == "/api/v1/admin/dms/test"
    gap = ADMIN_OPS_THIN_BUILDERS["admin/GapPipelineConsole"]()
    gap_actions = {a["key"]: a for a in gap["actions"]}
    assert gap_actions["run_pipeline"]["commandEndpoint"] == "/api/v1/gap/pipeline/run-year"
    wb = ADMIN_WB.read_text(encoding="utf-8")
    assert "admin/vordruck-editor" in wb
    assert "admin/GapPipelineConsole" in wb
