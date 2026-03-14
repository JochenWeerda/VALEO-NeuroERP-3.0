"""
Wave 19 — Finance Read-Model Contracts + Endpoints Tests (AP2 + AP6)

Prueft:
- SettlementCockpitSnapshot / PositionExposureSnapshot als stabile Contracts
- schema_version=1 Enforcement
- as_dict()-Serialisierung
- API-Endpoints /finance/read-models/settlement-cockpit + /position-exposure
- Settlement-Approval-Status-Endpoint AP5
- agrar_settlement SLA-Policies AP4
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.core.finance_read_model_contracts import (
    FINANCE_SCHEMA_VERSION,
    PositionExposureRow,
    PositionExposureSnapshot,
    PositionExposureType,
    SettlementCockpitRow,
    SettlementCockpitSnapshot,
    SettlementCockpitStatus,
)
from app.core.process_sla import build_default_sla_policies


# ---------------------------------------------------------------------------
# AP6: SettlementCockpitRow
# ---------------------------------------------------------------------------

def test_schema_version_constant():
    assert FINANCE_SCHEMA_VERSION == 1


def test_settlement_cockpit_row_approval_complete_false():
    row = SettlementCockpitRow(
        settlement_id="S-001",
        tenant_id="t1",
        customer_id="c1",
        gross_amount=1000.0,
        currency="EUR",
        status=SettlementCockpitStatus.ZUR_FREIGABE,
        approval_current=0,
        approval_required=2,
    )
    assert row.approval_complete is False


def test_settlement_cockpit_row_approval_complete_true():
    row = SettlementCockpitRow(
        settlement_id="S-001",
        tenant_id="t1",
        customer_id="c1",
        gross_amount=1000.0,
        currency="EUR",
        status=SettlementCockpitStatus.FREIGEGEBEN,
        approval_current=2,
        approval_required=2,
    )
    assert row.approval_complete is True


def test_settlement_cockpit_row_as_dict():
    row = SettlementCockpitRow(
        settlement_id="S-001",
        tenant_id="t1",
        customer_id="c1",
        gross_amount=5000.0,
        currency="EUR",
        status=SettlementCockpitStatus.ZUR_FREIGABE,
    )
    d = row.as_dict()
    assert d["settlement_id"] == "S-001"
    assert d["status"] == "ZUR_FREIGABE"
    assert d["approval_complete"] is False
    assert d["process_definition_key"] == "agrar_settlement"
    assert d["workflow_version"] == "1.0"


# ---------------------------------------------------------------------------
# AP6: SettlementCockpitSnapshot
# ---------------------------------------------------------------------------

def test_snapshot_schema_version_enforced():
    snap = SettlementCockpitSnapshot(tenant_id="t1")
    assert snap.schema_version == FINANCE_SCHEMA_VERSION


def test_snapshot_total_open_excludes_verbucht():
    snap = SettlementCockpitSnapshot(
        tenant_id="t1",
        rows=[
            SettlementCockpitRow("S-1", "t1", "c1", 1000.0, "EUR", SettlementCockpitStatus.ZUR_FREIGABE),
            SettlementCockpitRow("S-2", "t1", "c2", 2000.0, "EUR", SettlementCockpitStatus.VERBUCHT),
            SettlementCockpitRow("S-3", "t1", "c3", 500.0, "EUR", SettlementCockpitStatus.ABGELEHNT),
        ],
    )
    assert snap.total_open == 1000.0


def test_snapshot_pending_approval_count():
    snap = SettlementCockpitSnapshot(
        tenant_id="t1",
        rows=[
            SettlementCockpitRow("S-1", "t1", "c1", 500.0, "EUR", SettlementCockpitStatus.ZUR_FREIGABE),
            SettlementCockpitRow("S-2", "t1", "c2", 500.0, "EUR", SettlementCockpitStatus.TEILWEISE_FREIGEGEBEN),
            SettlementCockpitRow("S-3", "t1", "c3", 500.0, "EUR", SettlementCockpitStatus.FREIGEGEBEN),
        ],
    )
    assert snap.pending_approval_count == 2


def test_snapshot_as_dict_structure():
    snap = SettlementCockpitSnapshot(tenant_id="t1")
    d = snap.as_dict()
    assert d["tenant_id"] == "t1"
    assert d["schema_version"] == 1
    assert "total_open" in d
    assert "pending_approval_count" in d
    assert "row_count" in d
    assert isinstance(d["rows"], list)


# ---------------------------------------------------------------------------
# AP6: PositionExposureRow + PositionExposureSnapshot
# ---------------------------------------------------------------------------

def test_position_exposure_row_as_dict():
    row = PositionExposureRow(
        position_id="P-001",
        tenant_id="t1",
        exposure_type=PositionExposureType.KONTRAKT,
        gross_amount=3000.0,
        currency="EUR",
        commodity="Weizen",
        risk_flag=True,
    )
    d = row.as_dict()
    assert d["position_id"] == "P-001"
    assert d["exposure_type"] == "KONTRAKT"
    assert d["risk_flag"] is True


def test_position_exposure_snapshot_totals():
    snap = PositionExposureSnapshot(
        tenant_id="t1",
        rows=[
            PositionExposureRow("P-1", "t1", PositionExposureType.KONTRAKT, 1000.0, "EUR"),
            PositionExposureRow("P-2", "t1", PositionExposureType.LAGER, 2000.0, "EUR", risk_flag=True),
            PositionExposureRow("P-3", "t1", PositionExposureType.OFFENE_RECHNUNG, 500.0, "EUR", risk_flag=True),
        ],
    )
    assert snap.total_exposure == 3500.0
    assert snap.risk_count == 2


def test_position_exposure_snapshot_as_dict():
    snap = PositionExposureSnapshot(tenant_id="t1")
    d = snap.as_dict()
    assert d["schema_version"] == 1
    assert "total_exposure" in d
    assert "risk_count" in d
    assert isinstance(d["rows"], list)


def test_position_exposure_all_types_valid():
    for t in PositionExposureType:
        row = PositionExposureRow("P", "t1", t, 0.0, "EUR")
        assert row.exposure_type == t


# ---------------------------------------------------------------------------
# AP4: agrar_settlement SLA-Policies
# ---------------------------------------------------------------------------

def test_agrar_settlement_sla_policies_present():
    policies = build_default_sla_policies()
    agrar_policies = [p for p in policies if p.process_key.startswith("agrar_settlement")]
    assert len(agrar_policies) >= 2


def test_agrar_settlement_sla_has_canonical_process_key():
    policies = build_default_sla_policies()
    agrar = [p for p in policies if p.process_key == "agrar_settlement"]
    assert len(agrar) >= 1
    for p in agrar:
        assert p.process_definition_key == "agrar_settlement"


def test_agrar_settlement_approval_sla_present():
    policies = build_default_sla_policies()
    approval_policies = [p for p in policies if p.process_key == "agrar_settlement_approval"]
    assert len(approval_policies) >= 1


def test_agrar_settlement_sla_thresholds_valid():
    policies = build_default_sla_policies()
    for p in policies:
        if p.process_key.startswith("agrar_settlement"):
            assert p.warning_after_hours > 0
            assert p.critical_after_hours > p.warning_after_hours


# ---------------------------------------------------------------------------
# AP2 + AP5: API-Endpoints via TestClient
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def client():
    from app.main import app
    return TestClient(app, raise_server_exceptions=True)


def test_settlement_cockpit_endpoint(client):
    resp = client.get(
        "/api/v1/finance/read-models/settlement-cockpit",
        headers={"X-Tenant-ID": "tenant-test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["schema_version"] == 1
    assert "total_open" in data
    assert "pending_approval_count" in data
    assert "rows" in data


def test_position_exposure_endpoint(client):
    resp = client.get(
        "/api/v1/finance/read-models/position-exposure",
        headers={"X-Tenant-ID": "tenant-test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["schema_version"] == 1
    assert "total_exposure" in data
    assert "risk_count" in data


def test_settlement_approval_status_endpoint(client):
    resp = client.get(
        "/api/v1/process/settlement/approval-status/S-WAVE19-001",
        headers={"X-Tenant-ID": "tenant-test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["settlement_id"] == "S-WAVE19-001"
    assert data["schema_version"] == 1
    assert data["process_definition_key"] == "agrar_settlement"
    assert data["workflow_version"] == "1.0"
    assert "current_status" in data
    assert "allowed_transitions" in data
    assert "human_gate_rules" in data
    assert "sla_policies" in data
    assert len(data["human_gate_rules"]) == 6
    assert len(data["sla_policies"]) >= 2


def test_settlement_approval_status_allowed_transitions_valid(client):
    resp = client.get(
        "/api/v1/process/settlement/approval-status/S-ANY",
        headers={"X-Tenant-ID": "tenant-test"},
    )
    data = resp.json()
    # ENTWURF -> ZUR_FREIGABE + ABGELEHNT
    assert "ZUR_FREIGABE" in data["allowed_transitions"]


def test_settlement_approval_status_human_gate_has_block_rule(client):
    resp = client.get(
        "/api/v1/process/settlement/approval-status/S-ANY",
        headers={"X-Tenant-ID": "tenant-test"},
    )
    data = resp.json()
    rules = {r["rule_id"]: r for r in data["human_gate_rules"]}
    assert "HG-01" in rules
    assert rules["HG-01"]["verdict"] == "BLOCK"
