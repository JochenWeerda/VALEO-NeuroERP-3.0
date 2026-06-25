"""Tests fuer P2.1 — ProcessMapService."""

import pytest
from app.services.process_map_service import (
    GateStatus,
    ProcessDomain,
    ProcessMapService,
    StepType,
)


@pytest.fixture()
def svc() -> ProcessMapService:
    return ProcessMapService()


def test_list_domains_returns_all(svc: ProcessMapService) -> None:
    domains = svc.list_domains()
    domain_ids = {d["domain"] for d in domains}
    assert "o2c" in domain_ids
    assert "wms" in domain_ids
    assert "p2p" in domain_ids
    assert "fibu" in domain_ids
    assert "pos" in domain_ids


def test_get_o2c_map(svc: ProcessMapService) -> None:
    pm = svc.get_process_map(ProcessDomain.O2C)
    assert pm.domain == ProcessDomain.O2C
    assert len(pm.steps) >= 5
    step_ids = [s.step_id for s in pm.steps]
    assert "o2c-1" in step_ids
    assert "o2c-6" in step_ids  # Rechnung


def test_get_wms_map_has_qs_gate(svc: ProcessMapService) -> None:
    pm = svc.get_process_map(ProcessDomain.WMS)
    gate_steps = [s for s in pm.steps if s.step_type == StepType.GATE]
    assert len(gate_steps) >= 1
    assert any("QS" in s.name or "freigabe" in s.name.lower() for s in gate_steps)


def test_wms_map_has_traceability(svc: ProcessMapService) -> None:
    pm = svc.get_process_map(ProcessDomain.WMS)
    audit_steps = [s for s in pm.steps if s.step_type == StepType.AUDIT]
    assert len(audit_steps) >= 1


def test_human_approval_on_qs_step(svc: ProcessMapService) -> None:
    pm = svc.get_process_map(ProcessDomain.WMS)
    approval_steps = [s for s in pm.steps if s.human_approval]
    assert len(approval_steps) >= 1


def test_o2c_has_audit_steps(svc: ProcessMapService) -> None:
    pm = svc.get_process_map(ProcessDomain.O2C)
    audit_steps = [s for s in pm.steps if s.audit_relevant]
    assert len(audit_steps) >= 3


def test_external_gates_list(svc: ProcessMapService) -> None:
    gates = svc.list_external_gates()
    assert len(gates) >= 2
    assert all("domain" in g and "gate" in g for g in gates)


def test_open_gates_are_subset_of_all(svc: ProcessMapService) -> None:
    all_gates = svc.list_external_gates()
    open_gates = svc.get_open_gates()
    assert len(open_gates) <= len(all_gates)
    assert all(g["status"] == GateStatus.OFFEN.value for g in open_gates)


def test_summary_structure(svc: ProcessMapService) -> None:
    s = svc.summary()
    assert s["domains"] >= 5
    assert s["total_steps"] >= 30
    assert s["total_externe_gates"] >= 5
    assert s["human_approval_steps"] >= 2
    assert s["audit_relevante_steps"] >= 5


def test_unknown_domain_raises(svc: ProcessMapService) -> None:
    with pytest.raises(KeyError):
        svc.get_process_map(ProcessDomain.COMPLIANCE)  # nicht definiert in _PROCESS_MAPS MVP


def test_to_dict_structure(svc: ProcessMapService) -> None:
    pm = svc.get_process_map(ProcessDomain.FIBU)
    d = pm.to_dict()
    assert d["domain"] == "fibu"
    assert isinstance(d["steps"], list)
    assert len(d["steps"]) > 0
    step = d["steps"][0]
    assert "step_id" in step
    assert "step_type" in step
    assert "audit_relevant" in step
