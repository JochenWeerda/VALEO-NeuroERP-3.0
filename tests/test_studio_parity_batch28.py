"""Paritaet Batch 28: Externe Gates + Admin Agent-Ops/Superglue."""
from __future__ import annotations

from pathlib import Path

import pytest

from app.core.screen_definitions_listen import (
    build_admin_control_center_agent_ops_workbench,
    build_admin_control_center_superglue_workbench,
    build_admin_externe_gates_cockpit,
)
from app.services.studio_runtime_surface_contracts import SPECIALIZED_SCREENS, validate_runtime_surface

ROOT = Path(__file__).resolve().parents[1]
PAGES = ROOT / "packages/frontend-web/src/pages"
ADMIN_WB = ROOT / "packages/frontend-web/src/components/mask-builder/specialized/admin/admin-workbench.tsx"
EXTERNAL = ROOT / "app/api/v1/endpoints/external_gates.py"


@pytest.mark.unit
def test_externe_gates_cockpit_parity():
    src = (PAGES / "admin/externe-gates.tsx").read_text(encoding="utf-8")
    assert "UniversalNativeCockpitPage" in src
    assert 'screenId="admin/externe-gates"' in src
    assert (PAGES / "admin/externe-gates-legacy.tsx").exists()
    api = EXTERNAL.read_text(encoding="utf-8")
    assert '"/overview"' in api
    assert '"/items"' in api
    assert "get_gates_overview" in api
    assert "list_gate_items" in api
    sd = build_admin_externe_gates_cockpit()
    assert sd["id"] == "admin/externe-gates"
    sources = {ds["key"]: ds["endpoint"] for ds in sd["dataSources"]}
    assert sources["entity"] == "/api/v1/external-gates/overview"
    assert sources["gates"] == "/api/v1/external-gates/items"
    cols = {c["key"] for c in sd["tables"][0]["columns"]}
    assert {"label", "status", "kategorie", "hinweis"}.issubset(cols)


@pytest.mark.unit
def test_agent_ops_admin_workbench_parity():
    src = (PAGES / "admin/control-center/agent-ops.tsx").read_text(encoding="utf-8")
    assert "IntakeWeighingPage" in src
    assert 'screenId="admin/control-center/agent-ops"' in src
    assert (PAGES / "admin/control-center/agent-ops-legacy.tsx").exists()
    sd = build_admin_control_center_agent_ops_workbench()
    assert sd["specialized"] == {
        "type": "admin_workbench",
        "id": "admin/control-center/agent-ops",
    }
    assert not validate_runtime_surface(sd)
    assert sd["dataSources"][0]["endpoint"] == "/api/v1/agents/neuroassist/ops/persistence"
    assert "admin/control-center/agent-ops" in SPECIALIZED_SCREENS["admin_workbench"]
    wb = ADMIN_WB.read_text(encoding="utf-8")
    assert "admin/control-center/agent-ops" in wb
    assert "AgentOpsSurface" in wb


@pytest.mark.unit
def test_superglue_admin_workbench_parity():
    src = (PAGES / "admin/control-center/superglue.tsx").read_text(encoding="utf-8")
    assert "IntakeWeighingPage" in src
    assert 'screenId="admin/control-center/superglue"' in src
    assert (PAGES / "admin/control-center/superglue-legacy.tsx").exists()
    sd = build_admin_control_center_superglue_workbench()
    assert sd["specialized"]["id"] == "admin/control-center/superglue"
    assert not validate_runtime_surface(sd)
    actions = {a["key"]: a for a in sd["actions"]}
    base = "/api/v1/agent/integrations/providers/superglue/tenants/{tenant_id}"
    assert actions["connector_override"]["commandEndpoint"] == f"{base}/connectors/{{connector_key}}/config"
    assert actions["policy_override"]["commandEndpoint"] == f"{base}/policy"
    assert actions["wizard_apply"]["commandEndpoint"] == f"{base}/wizard/apply"
    assert actions["connector_override"]["surfaceOnly"] is True
    assert "admin/control-center/superglue" in SPECIALIZED_SCREENS["admin_workbench"]
    wb = ADMIN_WB.read_text(encoding="utf-8")
    assert "SuperglueSurface" in wb
