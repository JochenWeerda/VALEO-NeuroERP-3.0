"""
Wave 21 — Preisformel-Engine + Settlement-Journal-Bridge + E2E-Referenz Tests

AP1/AP5: evaluate_price() fuer alle drei Preistypen; PriceDeviationAlert
AP2:     JournalEntryDraft (Soll/Haben-Balance, Buchungszeilen, GoBD-Felder)
AP3/AP4: API-Endpoints price-preview und journal-preview
AP6:     E2ESettlementReference (Vollstaendigkeit, Coverage, missing_refs)
"""
from __future__ import annotations

from decimal import Decimal

import pytest

from app.core.price_formula_engine import (
    DEVIATION_THRESHOLD_PCT,
    PRICE_SCHEMA_VERSION,
    FixedPriceSpec,
    FormulaPriceSpec,
    PriceDeviationAlert,
    PriceEvaluation,
    PriceType,
    TerminmarktPriceSpec,
    build_deviation_alert,
    evaluate_price,
)
from app.core.settlement_journal_bridge import (
    JOURNAL_SCHEMA_VERSION,
    JournalSide,
    build_settlement_journal_draft,
)
from app.core.settlement_e2e_reference import (
    E2E_SCHEMA_VERSION,
    build_e2e_reference,
    validate_e2e_reference,
)


# ===========================================================================
# AP1: FixedPriceSpec
# ===========================================================================

def test_fixed_price_evaluation():
    spec = FixedPriceSpec(price_eur_per_ton=Decimal("220.00"))
    ev = evaluate_price(spec)
    assert ev.price_type == PriceType.FIXED
    assert ev.effective_price_eur_per_ton == Decimal("220.00")
    assert ev.deviation_alert is False
    assert ev.deviation_pct is None


def test_fixed_price_audit_trail():
    spec = FixedPriceSpec(price_eur_per_ton=Decimal("215.50"))
    ev = evaluate_price(spec)
    assert ev.audit_trail["type"] == "fixed"
    assert "price_eur_per_ton" in ev.audit_trail


def test_fixed_price_schema_version():
    ev = evaluate_price(FixedPriceSpec(price_eur_per_ton=Decimal("200.00")))
    assert ev.schema_version == PRICE_SCHEMA_VERSION


# ===========================================================================
# AP1: FormulaPriceSpec
# ===========================================================================

def test_formula_price_positive_surcharge():
    spec = FormulaPriceSpec(
        base_price_eur_per_ton=Decimal("220.00"),
        surcharge_eur_per_ton=Decimal("5.00"),
    )
    ev = evaluate_price(spec)
    assert ev.price_type == PriceType.FORMULA
    assert ev.effective_price_eur_per_ton == Decimal("225.00")


def test_formula_price_negative_surcharge():
    spec = FormulaPriceSpec(
        base_price_eur_per_ton=Decimal("220.00"),
        surcharge_eur_per_ton=Decimal("-10.00"),
    )
    ev = evaluate_price(spec)
    assert ev.effective_price_eur_per_ton == Decimal("210.00")


def test_formula_price_zero_surcharge():
    spec = FormulaPriceSpec(base_price_eur_per_ton=Decimal("218.75"))
    ev = evaluate_price(spec)
    assert ev.effective_price_eur_per_ton == Decimal("218.75")


def test_formula_price_audit_trail():
    spec = FormulaPriceSpec(
        base_price_eur_per_ton=Decimal("220.00"),
        surcharge_eur_per_ton=Decimal("3.50"),
    )
    ev = evaluate_price(spec)
    trail = ev.audit_trail
    assert trail["type"] == "formula"
    assert "base_price_eur_per_ton" in trail
    assert "surcharge_eur_per_ton" in trail
    assert "effective_price_eur_per_ton" in trail


# ===========================================================================
# AP1: TerminmarktPriceSpec
# ===========================================================================

def test_terminmarkt_price_with_spread():
    spec = TerminmarktPriceSpec(
        market_reference_id="MATIF_WEIZEN_MAR26",
        settlement_price_eur_per_ton=Decimal("225.50"),
        basis_spread_eur_per_ton=Decimal("-3.00"),
    )
    ev = evaluate_price(spec)
    assert ev.price_type == PriceType.TERMINMARKT
    assert ev.effective_price_eur_per_ton == Decimal("222.50")


def test_terminmarkt_price_audit_trail():
    spec = TerminmarktPriceSpec(
        market_reference_id="CBOT_CORN_DEC26",
        settlement_price_eur_per_ton=Decimal("180.00"),
    )
    ev = evaluate_price(spec)
    trail = ev.audit_trail
    assert trail["type"] == "terminmarkt"
    assert trail["market_reference_id"] == "CBOT_CORN_DEC26"
    assert "basis_spread_eur_per_ton" in trail


# ===========================================================================
# AP5: Abweichungs-Alert
# ===========================================================================

def test_no_deviation_alert_without_reference():
    spec = FixedPriceSpec(price_eur_per_ton=Decimal("220.00"))
    ev = evaluate_price(spec)
    assert ev.deviation_alert is False
    assert ev.deviation_pct is None


def test_no_deviation_alert_within_threshold():
    spec = FixedPriceSpec(price_eur_per_ton=Decimal("222.00"))
    ev = evaluate_price(spec, reference_price=Decimal("220.00"))
    # 2/220 * 100 = 0.91% — unter 5%
    assert ev.deviation_alert is False


def test_deviation_alert_above_threshold():
    spec = FixedPriceSpec(price_eur_per_ton=Decimal("235.00"))
    ev = evaluate_price(spec, reference_price=Decimal("220.00"))
    # (235-220)/220 * 100 = 6.82% — ueber 5%
    assert ev.deviation_alert is True
    assert ev.deviation_pct > DEVIATION_THRESHOLD_PCT


def test_deviation_alert_exactly_at_threshold_no_alert():
    # Genau 5% = kein Alert (nur > 5%)
    spec = FixedPriceSpec(price_eur_per_ton=Decimal("231.00"))
    ev = evaluate_price(spec, reference_price=Decimal("220.00"))
    # (231-220)/220 * 100 = 5.0% — nicht ueber Schwelle
    assert ev.deviation_alert is False


def test_build_deviation_alert_returns_none_when_no_alert():
    spec = FixedPriceSpec(price_eur_per_ton=Decimal("222.00"))
    ev = evaluate_price(spec, reference_price=Decimal("220.00"))
    alert = build_deviation_alert("S-001", ev)
    assert alert is None


def test_build_deviation_alert_returns_alert_when_triggered():
    spec = FixedPriceSpec(price_eur_per_ton=Decimal("240.00"))
    ev = evaluate_price(spec, reference_price=Decimal("220.00"))
    alert = build_deviation_alert("S-001", ev)
    assert alert is not None
    assert isinstance(alert, PriceDeviationAlert)
    assert alert.settlement_id == "S-001"


def test_deviation_alert_as_dict():
    spec = FixedPriceSpec(price_eur_per_ton=Decimal("240.00"))
    ev = evaluate_price(spec, reference_price=Decimal("220.00"))
    alert = build_deviation_alert("S-001", ev)
    d = alert.as_dict()
    assert d["settlement_id"] == "S-001"
    assert d["schema_version"] == PRICE_SCHEMA_VERSION
    assert "deviation_pct" in d
    assert "threshold_pct" in d


def test_price_evaluation_as_dict():
    spec = TerminmarktPriceSpec(
        market_reference_id="MATIF_WEIZEN_MAR26",
        settlement_price_eur_per_ton=Decimal("225.00"),
    )
    ev = evaluate_price(spec, reference_price=Decimal("220.00"))
    d = ev.as_dict()
    assert d["price_type"] == "TERMINMARKT"
    assert d["schema_version"] == PRICE_SCHEMA_VERSION
    assert "effective_price_eur_per_ton" in d
    assert "audit_trail" in d


# ===========================================================================
# AP2: JournalEntryDraft
# ===========================================================================

def _draft():
    return build_settlement_journal_draft(
        settlement_id="S-001",
        tenant_id="t1",
        gross_amount=Decimal("5000.00"),
        total_deductions=Decimal("250.00"),
        net_amount=Decimal("4750.00"),
    )


def test_journal_draft_is_balanced():
    draft = _draft()
    assert draft.balanced is True
    assert draft.soll_total == draft.haben_total


def test_journal_draft_soll_equals_gross():
    draft = _draft()
    assert draft.soll_total == Decimal("5000.00")


def test_journal_draft_haben_lines():
    draft = _draft()
    haben_lines = [l for l in draft.lines if l.side == JournalSide.HABEN]
    assert len(haben_lines) == 2  # Abzuege + Verbindlichkeit


def test_journal_draft_gobd_fields():
    draft = _draft()
    assert draft.beleg_nr.startswith("BLG-")
    assert draft.buchungsdatum != ""
    assert draft.settlement_id == "S-001"
    assert draft.process_definition_key == "agrar_settlement"
    assert draft.workflow_version == "1.0"


def test_journal_draft_schema_version():
    draft = _draft()
    assert draft.schema_version == JOURNAL_SCHEMA_VERSION


def test_journal_draft_no_deductions_still_balanced():
    draft = build_settlement_journal_draft(
        settlement_id="S-002",
        tenant_id="t1",
        gross_amount=Decimal("3000.00"),
        total_deductions=Decimal("0.00"),
        net_amount=Decimal("3000.00"),
    )
    assert draft.balanced is True
    haben_lines = [l for l in draft.lines if l.side == JournalSide.HABEN]
    assert len(haben_lines) == 1  # nur Verbindlichkeit, keine Abzuege


def test_journal_draft_with_vat_balanced():
    draft = build_settlement_journal_draft(
        settlement_id="S-003",
        tenant_id="t1",
        gross_amount=Decimal("5000.00"),
        total_deductions=Decimal("0.00"),
        net_amount=Decimal("5000.00"),
        vat_rate=Decimal("19"),
    )
    assert draft.balanced is True
    soll_lines = [l for l in draft.lines if l.side == JournalSide.SOLL]
    assert len(soll_lines) == 2  # Wareneinkauf + Vorsteuer


def test_journal_draft_as_dict():
    draft = _draft()
    d = draft.as_dict()
    assert d["balanced"] is True
    assert d["schema_version"] == JOURNAL_SCHEMA_VERSION
    assert isinstance(d["lines"], list)
    assert "soll_total" in d
    assert "haben_total" in d


# ===========================================================================
# AP6: E2ESettlementReference
# ===========================================================================

def test_e2e_reference_complete():
    ref = build_e2e_reference(
        "S-001", "t1",
        kontrakt_id="KNT-001",
        annahme_id="ANH-001",
        charge_id="CHG-001",
        qualitaet_id="QP-001",
        journal_entry_id="JE-001",
    )
    assert ref.complete is True
    assert ref.missing_refs == []
    assert ref.coverage_pct == 100.0


def test_e2e_reference_partial():
    ref = build_e2e_reference(
        "S-001", "t1",
        kontrakt_id="KNT-001",
        annahme_id="ANH-001",
    )
    assert ref.complete is False
    assert "charge_id" in ref.missing_refs
    assert "qualitaet_id" in ref.missing_refs
    assert "journal_entry_id" in ref.missing_refs
    assert ref.coverage_pct == 40.0


def test_e2e_reference_empty():
    ref = build_e2e_reference("S-001", "t1")
    assert ref.complete is False
    assert len(ref.missing_refs) == 5
    assert ref.coverage_pct == 0.0


def test_validate_e2e_reference_complete():
    ref = build_e2e_reference(
        "S-001", "t1",
        kontrakt_id="KNT-001",
        annahme_id="ANH-001",
        charge_id="CHG-001",
        qualitaet_id="QP-001",
        journal_entry_id="JE-001",
    )
    result = validate_e2e_reference(ref)
    assert result.valid is True
    assert result.coverage_pct == 100.0


def test_validate_e2e_reference_incomplete():
    ref = build_e2e_reference("S-001", "t1", kontrakt_id="KNT-001")
    result = validate_e2e_reference(ref)
    assert result.valid is False
    assert len(result.missing_refs) > 0


def test_e2e_reference_as_dict():
    ref = build_e2e_reference("S-001", "t1", kontrakt_id="KNT-001")
    d = ref.as_dict()
    assert d["settlement_id"] == "S-001"
    assert d["schema_version"] == E2E_SCHEMA_VERSION
    assert "missing_refs" in d
    assert "coverage_pct" in d
    assert "complete" in d


def test_e2e_reference_process_metadata():
    ref = build_e2e_reference("S-001", "t1")
    assert ref.process_definition_key == "agrar_settlement"
    assert ref.workflow_version == "1.0"


# ===========================================================================
# AP3 + AP4: API-Endpoints via TestClient
# ===========================================================================

@pytest.fixture(scope="module")
def client():
    from app.main import app
    from fastapi.testclient import TestClient
    return TestClient(app, raise_server_exceptions=True)


def test_price_preview_endpoint(client):
    resp = client.get(
        "/api/v1/process/settlement/price-preview/S-W21-001",
        headers={"X-Tenant-ID": "tenant-test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["settlement_id"] == "S-W21-001"
    assert data["schema_version"] == 1
    assert "price_evaluation" in data
    ev = data["price_evaluation"]
    assert ev["price_type"] == "TERMINMARKT"
    assert "effective_price_eur_per_ton" in ev
    assert "audit_trail" in ev


def test_price_preview_deviation_alert_field(client):
    resp = client.get(
        "/api/v1/process/settlement/price-preview/S-ANY",
        headers={"X-Tenant-ID": "tenant-test"},
    )
    data = resp.json()
    assert "deviation_alert" in data  # kann None oder dict sein


def test_journal_preview_endpoint(client):
    resp = client.get(
        "/api/v1/process/settlement/journal-preview/S-W21-001",
        headers={"X-Tenant-ID": "tenant-test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["settlement_id"] == "S-W21-001"
    assert data["schema_version"] == 1
    draft = data["journal_draft"]
    assert draft["balanced"] is True
    assert "lines" in draft
    assert draft["schema_version"] == JOURNAL_SCHEMA_VERSION


def test_journal_preview_has_e2e_reference(client):
    resp = client.get(
        "/api/v1/process/settlement/journal-preview/S-W21-001",
        headers={"X-Tenant-ID": "tenant-test"},
    )
    data = resp.json()
    assert "e2e_reference" in data
    assert "e2e_validation" in data
    e2e = data["e2e_reference"]
    assert e2e["settlement_id"] == "S-W21-001"
    assert "missing_refs" in e2e
    assert "coverage_pct" in e2e


def test_journal_preview_soll_haben_lines(client):
    resp = client.get(
        "/api/v1/process/settlement/journal-preview/S-W21-001",
        headers={"X-Tenant-ID": "tenant-test"},
    )
    data = resp.json()
    lines = data["journal_draft"]["lines"]
    sides = {l["side"] for l in lines}
    assert "SOLL" in sides
    assert "HABEN" in sides
