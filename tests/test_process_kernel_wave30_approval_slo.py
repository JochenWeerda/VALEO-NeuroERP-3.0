"""
Wave 30 — Human-in-the-loop AI-Freigaben + SLO/SLI-Definitionen

Gap 015: Human-in-the-loop Freigaben fuer AI Aktionen — 100% AI-Aktionen mit Approval-Trail
Gap 050: Produktive Betriebsfuehrung mit SLO/SLI — Verfuegbarkeit >=99.9%

Testet:
  AP1: evaluate_approval_requirement() — NIEDRIG/MITTEL/HOCH/KRITISCH
  AP2: record_approval_decision() — Audit-Record, Immutabilitaet, Hash
  AP3: API-Endpoints /process/agent/approval-*
  AP4: SLODefinition, SLORegistry, get_process_kernel_slos()
  AP5: check_slo_compliance(), validate_slo_definition()
  AP6: API-Endpoints /process/slo/*
"""
from __future__ import annotations

import pytest
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def _get_regeln():
    from app.core.human_approval_gate import get_default_approval_rules
    return get_default_approval_rules()


# ---------------------------------------------------------------------------
# AP1: ApprovalRegel.matches() + evaluate_approval_requirement()
# ---------------------------------------------------------------------------

def test_approve_niedrig_kein_treffer():
    from app.core.human_approval_gate import evaluate_approval_requirement, ApprovalRisikostufe
    result = evaluate_approval_requirement("REPORT_GENERIEREN", {}, _get_regeln())
    assert result.risiko_stufe == ApprovalRisikostufe.NIEDRIG
    assert result.requires_human_approval is False


def test_approve_niedrig_lesende_aktion():
    from app.core.human_approval_gate import evaluate_approval_requirement, ApprovalRisikostufe
    result = evaluate_approval_requirement("DASHBOARD_LADEN", {"betrag_eur": 0}, _get_regeln())
    assert result.risiko_stufe == ApprovalRisikostufe.NIEDRIG
    assert result.requires_human_approval is False


def test_approve_mittel_settlement_kleiner_betrag():
    from app.core.human_approval_gate import evaluate_approval_requirement, ApprovalRisikostufe
    result = evaluate_approval_requirement(
        "SETTLEMENT_FREIGABE", {"betrag_eur": 10_000}, _get_regeln()
    )
    assert result.risiko_stufe == ApprovalRisikostufe.MITTEL
    assert result.requires_human_approval is False


def test_approve_hoch_settlement_grosser_betrag():
    from app.core.human_approval_gate import evaluate_approval_requirement, ApprovalRisikostufe
    result = evaluate_approval_requirement(
        "SETTLEMENT_FREIGABE", {"betrag_eur": 75_000}, _get_regeln()
    )
    assert result.risiko_stufe == ApprovalRisikostufe.HOCH
    assert result.requires_human_approval is True
    assert result.freigabe_rolle == "teamleiter"


def test_approve_kritisch_belegstorno():
    from app.core.human_approval_gate import evaluate_approval_requirement, ApprovalRisikostufe
    result = evaluate_approval_requirement("BELEG_STORNIEREN", {}, _get_regeln())
    assert result.risiko_stufe == ApprovalRisikostufe.KRITISCH
    assert result.requires_human_approval is True
    assert result.freigabe_rolle == "geschaeftsfuehrung"


def test_approve_kritisch_massenzahlung():
    from app.core.human_approval_gate import evaluate_approval_requirement, ApprovalRisikostufe
    result = evaluate_approval_requirement(
        "ZAHLUNG_AUSLOESEN", {"betrag_eur": 600_000}, _get_regeln()
    )
    assert result.risiko_stufe == ApprovalRisikostufe.KRITISCH
    assert result.requires_human_approval is True


def test_approve_hoch_externe_partei():
    from app.core.human_approval_gate import evaluate_approval_requirement, ApprovalRisikostufe
    result = evaluate_approval_requirement("ZAHLUNG_AUSLOESEN", {"betrag_eur": 1_000}, _get_regeln())
    # Externe-Partei-Regel greift (kein Betragslimit)
    assert result.risiko_stufe in (ApprovalRisikostufe.HOCH, ApprovalRisikostufe.MITTEL)


def test_approve_kritisch_massendaten():
    from app.core.human_approval_gate import evaluate_approval_requirement, ApprovalRisikostufe
    result = evaluate_approval_requirement(
        "STAMMDATEN_MASSENAENDERUNG", {"datensaetze_count": 5000}, _get_regeln()
    )
    assert result.risiko_stufe == ApprovalRisikostufe.KRITISCH
    assert result.requires_human_approval is True


def test_approve_hoch_regulatorisch_intrastat():
    from app.core.human_approval_gate import evaluate_approval_requirement, ApprovalRisikostufe
    result = evaluate_approval_requirement("INTRASTAT_EINREICHEN", {}, _get_regeln())
    assert result.risiko_stufe == ApprovalRisikostufe.HOCH
    assert result.requires_human_approval is True


def test_approve_as_dict_complete():
    from app.core.human_approval_gate import evaluate_approval_requirement
    result = evaluate_approval_requirement("BELEG_STORNIEREN", {}, _get_regeln())
    d = result.as_dict()
    assert d["risiko_stufe"] == "KRITISCH"
    assert d["requires_human_approval"] is True
    assert d["schema_version"] == 1
    assert "freigabe_rolle" in d
    assert "begruendung" in d


def test_approve_kein_treffer_ausgeloeste_regel_none():
    from app.core.human_approval_gate import evaluate_approval_requirement
    result = evaluate_approval_requirement("UNBEKANNTE_AKTION", {}, _get_regeln())
    assert result.ausgeloeste_regel_id is None


# ---------------------------------------------------------------------------
# AP2: record_approval_decision()
# ---------------------------------------------------------------------------

def test_approval_record_erstellt():
    from app.core.human_approval_gate import (
        record_approval_decision, ApprovalRisikostufe, ApprovalDecision
    )
    ts = datetime(2024, 9, 1, 10, 0, 0, tzinfo=timezone.utc)
    record = record_approval_decision(
        aktions_typ="SETTLEMENT_FREIGABE",
        instanz_id="inst-001",
        agent_id="agent-valeo-001",
        risiko_stufe=ApprovalRisikostufe.HOCH,
        decision=ApprovalDecision.GENEHMIGT,
        entschieden_von="user@valeo.de",
        begruendung="Freigabe nach Pruefung",
        kontext={"betrag_eur": 75000},
        timestamp=ts,
    )
    assert record.aktions_typ == "SETTLEMENT_FREIGABE"
    assert record.decision == "GENEHMIGT"
    assert record.risiko_stufe == "HOCH"
    assert record.entschieden_von == "user@valeo.de"
    assert record.record_id  # nicht leer
    assert record.kontext_hash  # nicht leer


def test_approval_record_frozen():
    """ApprovalRecord ist unveraenderlich (frozen=True)."""
    from app.core.human_approval_gate import (
        record_approval_decision, ApprovalRisikostufe, ApprovalDecision
    )
    record = record_approval_decision(
        aktions_typ="BELEG_STORNIEREN",
        instanz_id="inst-002",
        agent_id="agent-001",
        risiko_stufe=ApprovalRisikostufe.KRITISCH,
        decision=ApprovalDecision.ABGELEHNT,
        entschieden_von="gf@valeo.de",
        begruendung="Abgelehnt",
        kontext={},
    )
    with pytest.raises((AttributeError, TypeError)):
        record.decision = "GENEHMIGT"  # type: ignore


def test_approval_record_deterministischer_hash():
    """Gleicher Input → gleicher kontext_hash."""
    from app.core.human_approval_gate import (
        record_approval_decision, ApprovalRisikostufe, ApprovalDecision
    )
    ts = datetime(2024, 9, 1, tzinfo=timezone.utc)
    kontext = {"betrag_eur": 50000, "lieferant_id": "LF-001"}
    r1 = record_approval_decision(
        "SETTLEMENT_FREIGABE", "inst", "agent", ApprovalRisikostufe.HOCH,
        ApprovalDecision.GENEHMIGT, "user", "ok", kontext, timestamp=ts,
    )
    r2 = record_approval_decision(
        "SETTLEMENT_FREIGABE", "inst", "agent", ApprovalRisikostufe.HOCH,
        ApprovalDecision.GENEHMIGT, "user", "ok", kontext, timestamp=ts,
    )
    assert r1.kontext_hash == r2.kontext_hash
    assert r1.record_id == r2.record_id


def test_approval_record_as_dict():
    from app.core.human_approval_gate import (
        record_approval_decision, ApprovalRisikostufe, ApprovalDecision
    )
    record = record_approval_decision(
        "REPORT_GENERIEREN", "inst-003", "agent-001",
        ApprovalRisikostufe.NIEDRIG, ApprovalDecision.GENEHMIGT,
        "system", "Auto-approved", {},
    )
    d = record.as_dict()
    assert d["schema_version"] == 1
    assert "record_id" in d
    assert "kontext_hash" in d
    assert "entschieden_am" in d


# ---------------------------------------------------------------------------
# AP4: SLODefinition + SLORegistry
# ---------------------------------------------------------------------------

def test_slo_registry_count():
    from app.core.slo_definitions import get_process_kernel_slos
    registry = get_process_kernel_slos()
    assert len(registry.slos) >= 8


def test_slo_registry_by_dienst():
    from app.core.slo_definitions import get_process_kernel_slos
    registry = get_process_kernel_slos()
    api_slos = registry.by_dienst("api_gateway")
    assert len(api_slos) >= 3
    for s in api_slos:
        assert s.dienst == "api_gateway"


def test_slo_registry_by_slo_id():
    from app.core.slo_definitions import get_process_kernel_slos
    registry = get_process_kernel_slos()
    slo = registry.by_slo_id("SLO-API-VERF-01")
    assert slo is not None
    assert slo.zielwert == 99.9


def test_slo_registry_by_slo_id_not_found():
    from app.core.slo_definitions import get_process_kernel_slos
    registry = get_process_kernel_slos()
    assert registry.by_slo_id("SLO-UNBEKANNT") is None


def test_slo_toleranz_grenze_verfuegbarkeit():
    from app.core.slo_definitions import get_process_kernel_slos
    registry = get_process_kernel_slos()
    slo = registry.by_slo_id("SLO-API-VERF-01")
    assert slo.toleranz_grenze == pytest.approx(99.8)  # 99.9 - 0.1


def test_slo_toleranz_grenze_latenz():
    from app.core.slo_definitions import get_process_kernel_slos
    registry = get_process_kernel_slos()
    slo = registry.by_slo_id("SLO-API-LAT-01")
    assert slo.toleranz_grenze == pytest.approx(250.0)  # 200 + 50


def test_slo_as_dict_complete():
    from app.core.slo_definitions import get_process_kernel_slos
    registry = get_process_kernel_slos()
    slo = registry.by_slo_id("SLO-API-VERF-01")
    d = slo.as_dict()
    assert d["slo_id"] == "SLO-API-VERF-01"
    assert d["zielwert"] == 99.9
    assert d["schema_version"] == 1
    assert "sli" in d


def test_slo_registry_as_dict():
    from app.core.slo_definitions import get_process_kernel_slos
    registry = get_process_kernel_slos()
    d = registry.as_dict()
    assert "slo_count" in d
    assert "dienste" in d
    assert d["schema_version"] == 1


# ---------------------------------------------------------------------------
# AP5: check_slo_compliance()
# ---------------------------------------------------------------------------

def test_slo_compliance_erfuellt_verfuegbarkeit():
    from app.core.slo_definitions import get_process_kernel_slos, check_slo_compliance, SLOComplianceStatus
    slo = get_process_kernel_slos().by_slo_id("SLO-API-VERF-01")
    result = check_slo_compliance(slo, 99.95)
    assert result.status == SLOComplianceStatus.ERFUELLT
    assert not result.verletzt


def test_slo_compliance_toleranzbereich_verfuegbarkeit():
    from app.core.slo_definitions import get_process_kernel_slos, check_slo_compliance, SLOComplianceStatus
    slo = get_process_kernel_slos().by_slo_id("SLO-API-VERF-01")
    # 99.85 ist zwischen toleranz_grenze (99.8) und zielwert (99.9)
    result = check_slo_compliance(slo, 99.85)
    assert result.status == SLOComplianceStatus.TOLERANZBEREICH
    assert result.im_toleranzbereich is True


def test_slo_compliance_verletzt_verfuegbarkeit():
    from app.core.slo_definitions import get_process_kernel_slos, check_slo_compliance, SLOComplianceStatus
    slo = get_process_kernel_slos().by_slo_id("SLO-API-VERF-01")
    result = check_slo_compliance(slo, 99.5)
    assert result.status == SLOComplianceStatus.VERLETZT
    assert result.verletzt is True


def test_slo_compliance_erfuellt_latenz():
    from app.core.slo_definitions import get_process_kernel_slos, check_slo_compliance, SLOComplianceStatus
    slo = get_process_kernel_slos().by_slo_id("SLO-API-LAT-01")
    result = check_slo_compliance(slo, 150.0)  # unter Zielwert 200ms → OK
    assert result.status == SLOComplianceStatus.ERFUELLT


def test_slo_compliance_verletzt_latenz():
    from app.core.slo_definitions import get_process_kernel_slos, check_slo_compliance, SLOComplianceStatus
    slo = get_process_kernel_slos().by_slo_id("SLO-API-LAT-01")
    result = check_slo_compliance(slo, 300.0)  # ueber toleranz_grenze 250ms → VERLETZT
    assert result.status == SLOComplianceStatus.VERLETZT


def test_slo_compliance_unbekannt_none_wert():
    from app.core.slo_definitions import get_process_kernel_slos, check_slo_compliance, SLOComplianceStatus
    slo = get_process_kernel_slos().by_slo_id("SLO-API-VERF-01")
    result = check_slo_compliance(slo, None)
    assert result.status == SLOComplianceStatus.UNBEKANNT
    assert result.ist_wert is None


def test_slo_compliance_as_dict():
    from app.core.slo_definitions import get_process_kernel_slos, check_slo_compliance
    slo = get_process_kernel_slos().by_slo_id("SLO-WE-VERF-01")
    result = check_slo_compliance(slo, 100.0)
    d = result.as_dict()
    assert d["verletzt"] is False
    assert d["schema_version"] == 1
    assert "abweichung" in d


# ---------------------------------------------------------------------------
# AP5: validate_slo_definition()
# ---------------------------------------------------------------------------

def test_validate_slo_valid():
    from app.core.slo_definitions import get_process_kernel_slos, validate_slo_definition
    for slo in get_process_kernel_slos().slos:
        result = validate_slo_definition(slo)
        assert result.valid, f"SLO {slo.slo_id} ungueltig: {result.violations}"


def test_validate_slo_leerer_dienst():
    from app.core.slo_definitions import (
        SLODefinition, SLOTyp, SLOMessfenster, validate_slo_definition, SLOViolationCode
    )
    slo = SLODefinition("SLO-X", "  ", None, SLOTyp.VERFUEGBARKEIT, "Test", 99.0, 0.5, SLOMessfenster.TAGE_30)
    result = validate_slo_definition(slo)
    assert not result.valid
    assert any(v.code == SLOViolationCode.DIENST_LEER for v in result.violations)


def test_validate_slo_verfuegbarkeit_ueber_100():
    from app.core.slo_definitions import (
        SLODefinition, SLOTyp, SLOMessfenster, validate_slo_definition, SLOViolationCode
    )
    slo = SLODefinition("SLO-X", "test", None, SLOTyp.VERFUEGBARKEIT, "Test", 101.0, 0.5, SLOMessfenster.TAGE_30)
    result = validate_slo_definition(slo)
    assert not result.valid
    assert any(v.code == SLOViolationCode.VERFUEGBARKEIT_UEBER_100 for v in result.violations)


def test_validate_slo_as_dict():
    from app.core.slo_definitions import get_process_kernel_slos, validate_slo_definition
    slo = get_process_kernel_slos().by_slo_id("SLO-API-VERF-01")
    result = validate_slo_definition(slo)
    d = result.as_dict()
    assert d["valid"] is True
    assert d["schema_version"] == 1


# ---------------------------------------------------------------------------
# AP3/AP6: API-Endpoints
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


from fastapi.testclient import TestClient


def test_api_approval_rules(client):
    resp = client.get("/api/v1/process/agent/approval-rules")
    assert resp.status_code == 200
    body = resp.json()
    assert body["regel_count"] >= 8
    assert body["schema_version"] == 1


def test_api_approval_evaluate_kritisch(client):
    resp = client.post("/api/v1/process/agent/approval-evaluate", json={
        "aktions_typ": "BELEG_STORNIEREN",
        "kontext": {},
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["risiko_stufe"] == "KRITISCH"
    assert body["requires_human_approval"] is True


def test_api_approval_evaluate_niedrig(client):
    resp = client.post("/api/v1/process/agent/approval-evaluate", json={
        "aktions_typ": "DASHBOARD_LADEN",
        "kontext": {},
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["risiko_stufe"] == "NIEDRIG"
    assert body["requires_human_approval"] is False


def test_api_approval_evaluate_fehlender_aktionstyp(client):
    resp = client.post("/api/v1/process/agent/approval-evaluate", json={"kontext": {}})
    assert resp.status_code == 422


def test_api_slo_registry_all(client):
    resp = client.get("/api/v1/process/slo/registry")
    assert resp.status_code == 200
    body = resp.json()
    assert body["slo_count"] >= 8
    assert "api_gateway" in body["dienste"]
    assert body["schema_version"] == 1


def test_api_slo_registry_filtered(client):
    resp = client.get("/api/v1/process/slo/registry?dienst=api_gateway")
    assert resp.status_code == 200
    body = resp.json()
    assert body["dienst_filter"] == "api_gateway"
    assert body["slo_count"] >= 3


def test_api_slo_check_erfuellt(client):
    resp = client.post("/api/v1/process/slo/check", json={
        "slo_id": "SLO-API-VERF-01",
        "ist_wert": 99.95,
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "ERFUELLT"
    assert body["verletzt"] is False


def test_api_slo_check_verletzt(client):
    resp = client.post("/api/v1/process/slo/check", json={
        "slo_id": "SLO-API-VERF-01",
        "ist_wert": 98.0,
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "VERLETZT"
    assert body["verletzt"] is True


def test_api_slo_check_unbekannt(client):
    resp = client.post("/api/v1/process/slo/check", json={
        "slo_id": "SLO-API-VERF-01",
        "ist_wert": None,
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["status"] == "UNBEKANNT"


def test_api_slo_check_not_found(client):
    resp = client.post("/api/v1/process/slo/check", json={
        "slo_id": "SLO-NICHT-VORHANDEN",
        "ist_wert": 99.0,
    })
    assert resp.status_code == 404
