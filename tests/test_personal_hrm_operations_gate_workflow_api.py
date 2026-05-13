from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints.personal import router
from app.core.database import get_db


_HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": "tenant-hrm"}
_APP = FastAPI()
_APP.include_router(router, prefix="/api/v1")


class _Result:
    def __init__(self, rows: list[dict[str, Any]] | None = None):
        self._rows = rows or []

    def mappings(self) -> "_Result":
        return self

    def all(self) -> list[dict[str, Any]]:
        return self._rows

    def first(self) -> dict[str, Any] | None:
        return self._rows[0] if self._rows else None


class _HrmGateSession:
    def __init__(self):
        self.gates: dict[str, dict[str, Any]] = {}
        self.evidence: list[dict[str, Any]] = []
        self.probes: list[dict[str, Any]] = []
        self.audit: list[dict[str, Any]] = []
        self.commits = 0
        self.rollbacks = 0

    def execute(self, statement: Any, params: dict[str, Any] | None = None) -> _Result:
        sql = str(statement)
        params = params or {}
        gate_id = params.get("gate_id")
        if "INSERT INTO domain_hr.hrm_operations_gates" in sql:
            self.gates.setdefault(
                gate_id,
                {
                    "gate_id": gate_id,
                    "status": params["status"],
                    "owner_role": params["owner_role"],
                    "go_live_blocking": params["go_live_blocking"],
                    "last_probe_status": None,
                    "last_probe_at": None,
                    "approved_by": None,
                    "approved_at": None,
                    "rejection_reason": None,
                },
            )
            return _Result([])
        if "FROM domain_hr.hrm_operations_gates g" in sql:
            rows = []
            for gate in self.gates.values():
                gate_evidence = [item for item in self.evidence if item["gate_id"] == gate["gate_id"]]
                latest = gate_evidence[-1]["artifact_ref"] if gate_evidence else None
                rows.append({**gate, "evidence_count": len(gate_evidence), "latest_evidence_ref": latest})
            return _Result(rows)
        if "INSERT INTO domain_hr.hrm_operations_gate_evidence" in sql:
            row = {
                "id": params["id"],
                "gate_id": gate_id,
                "evidence_type": params["evidence_type"],
                "title": params["title"],
                "artifact_ref": params["artifact_ref"],
                "submitted_by": params["submitted_by"],
                "submitted_at": datetime(2026, 5, 13, 9, 0, 0),
                "metadata": params["metadata"],
            }
            self.evidence.append(row)
            return _Result([row])
        if "UPDATE domain_hr.hrm_operations_gates" in sql:
            gate = self.gates[gate_id]
            if "last_probe_status" in sql:
                gate["status"] = params["status"]
                gate["last_probe_status"] = params["probe_status"]
                gate["last_probe_at"] = datetime(2026, 5, 13, 10, 0, 0)
            elif "approved_by" in sql:
                gate["status"] = params["status"]
                gate["approved_by"] = params["actor"] if params["status"] == "approved" else None
                gate["approved_at"] = datetime(2026, 5, 13, 11, 0, 0) if params["status"] == "approved" else None
                gate["rejection_reason"] = params["reason"] if params["status"] == "rejected" else None
            else:
                gate["status"] = "evidence_submitted"
                gate["rejection_reason"] = None
            return _Result([{"gate_id": gate_id, "status": gate["status"]}])
        if "INSERT INTO domain_hr.hrm_operations_gate_audit" in sql:
            self.audit.append(dict(params))
            return _Result([])
        if "INSERT INTO domain_hr.hrm_operations_gate_probes" in sql:
            row = {
                "id": params["id"],
                "gate_id": gate_id,
                "provider": params["provider"],
                "probe_type": params["probe_type"],
                "result": params["result"],
                "performed_by": params["performed_by"],
                "performed_at": datetime(2026, 5, 13, 10, 0, 0),
                "details": params["details"],
            }
            self.probes.append(row)
            return _Result([row])
        return _Result([])

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1


def _override_db(session: _HrmGateSession):
    def _inner():
        yield session

    return _inner


def _client_with(session: _HrmGateSession) -> TestClient:
    _APP.dependency_overrides[get_db] = _override_db(session)
    return TestClient(_APP, raise_server_exceptions=False)


def test_hrm_operations_gates_runtime_starts_blocked_from_persistent_seed():
    session = _HrmGateSession()
    client = _client_with(session)
    try:
        response = client.get("/api/v1/personal/hrm-operations-gates", headers=_HEADERS)
    finally:
        _APP.dependency_overrides.pop(get_db, None)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "external_gates_runtime"
    assert data["goLiveAllowed"] is False
    assert len(session.gates) == 7
    eau = next(gate for gate in data["gates"] if gate["id"] == "eau-communication")
    assert eau["priority"] == "P0"
    assert eau["riskLevel"] == "hoch"
    assert eau["dueDate"] == "2026-05-20"
    assert "HR Admin" in eau["allowedRoles"]
    assert "Geschaeftsleitung" in eau["readOnlyRoles"]
    assert all(gate["status"] == "external_evidence_required" for gate in session.gates.values())


def test_hrm_operations_gate_evidence_probe_and_approval_are_persistent_and_audited():
    session = _HrmGateSession()
    client = _client_with(session)
    try:
        evidence = client.post(
            "/api/v1/personal/hrm-operations-gates/datev-payroll/evidence",
            headers=_HEADERS,
            json={
                "evidenceType": "test_export",
                "title": "DATEV Testexport Mai",
                "artifactRef": "dms://hrm/datev/testexport-2026-05",
                "submittedBy": "payroll-admin",
                "metadata": {"period": "2026-05"},
            },
        )
        probe = client.post(
            "/api/v1/personal/hrm-operations-gates/datev-payroll/probe",
            headers=_HEADERS,
            json={
                "provider": "DATEV",
                "probeType": "format_validation",
                "result": "passed",
                "performedBy": "payroll-admin",
                "details": {"records": 42},
            },
        )
        decision = client.post(
            "/api/v1/personal/hrm-operations-gates/datev-payroll/decision",
            headers=_HEADERS,
            json={"decision": "approve", "decidedBy": "payroll-lead", "reason": "Steuerberaterfreigabe liegt vor"},
        )
        gates = client.get("/api/v1/personal/hrm-operations-gates", headers=_HEADERS)
    finally:
        _APP.dependency_overrides.pop(get_db, None)

    assert evidence.status_code == 201
    assert evidence.json()["artifactRef"] == "dms://hrm/datev/testexport-2026-05"
    assert probe.status_code == 201
    assert probe.json()["result"] == "passed"
    assert decision.status_code == 200
    approved_gate = decision.json()["gate"]
    assert approved_gate["status"] == "approved"
    assert approved_gate["approvedBy"] == "payroll-lead"
    datev_gate = next(gate for gate in gates.json()["gates"] if gate["id"] == "datev-payroll")
    assert datev_gate["evidenceCount"] == 1
    assert datev_gate["latestEvidenceRef"] == "dms://hrm/datev/testexport-2026-05"
    assert datev_gate["lastProbeStatus"] == "passed"
    assert len(session.audit) == 3
    assert session.commits == 3


def test_hrm_operations_gate_approval_requires_evidence_and_go_live_policy_lists_blockers():
    session = _HrmGateSession()
    client = _client_with(session)
    try:
        rejected = client.post(
            "/api/v1/personal/hrm-operations-gates/eau-communication/decision",
            headers=_HEADERS,
            json={"decision": "approve", "decidedBy": "hr-lead"},
        )
        policy = client.get("/api/v1/personal/hrm-operations-gates/go-live-policy", headers=_HEADERS)
    finally:
        _APP.dependency_overrides.pop(get_db, None)

    assert rejected.status_code == 409
    assert rejected.json()["detail"] == "Gate approval requires at least one evidence artifact"
    assert policy.status_code == 200
    data = policy.json()
    assert data["goLiveAllowed"] is False
    assert data["blockerCount"] == 7
    assert {gate["id"] for gate in data["blockers"]} >= {"eau-communication", "datev-payroll"}
