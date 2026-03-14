"""
Wave 23 — Nebenkosten-Automatik + Intrastat-Meldungsmodell Tests

AP1/AP6: compute_nebenkosten() fuer alle Kostenarten; NebenkostenBreakdown
AP2/AP5: IntrastatMeldung; validate_intrastat_meldung() Vollstaendigkeitspruefung
AP3:     API-Endpoint nebenkosten-preview
AP4:     API-Endpoints intrastat/meldungen GET + POST + validate
"""
from __future__ import annotations

from decimal import Decimal

import pytest

from app.core.nebenkosten_engine import (
    NEBENKOSTEN_SCHEMA_VERSION,
    NebenkostenArt,
    NebenkostenInput,
    NebenkostenModus,
    NebenkostenRule,
    compute_nebenkosten,
    get_default_nebenkosten_rules,
)
from app.core.intrastat_model import (
    INTRASTAT_SCHEMA_VERSION,
    EU_MITGLIEDSTAATEN,
    IntrastatMeldestatus,
    IntrastatRichtung,
    IntrastatViolationCode,
    WarenbewegungsPosition,
    IntrastatMeldung,
    build_stub_intrastat_meldung,
    validate_intrastat_meldung,
)


# ===========================================================================
# AP1/AP6: NebenkostenEngine — Grundlagen
# ===========================================================================

def _base_input(**kwargs) -> NebenkostenInput:
    defaults = dict(
        settlement_id="S-001",
        tenant_id="t1",
        billing_qty_tons=Decimal("100.0"),
        transport_km=Decimal("50.0"),
        storage_days=Decimal("10"),
        weighing_count=1,
    )
    defaults.update(kwargs)
    return NebenkostenInput(**defaults)


def test_compute_fracht_pro_km():
    rule = NebenkostenRule(
        rule_id="NB-FRACHT-KM",
        art=NebenkostenArt.FRACHT,
        modus=NebenkostenModus.PRO_KM,
        rate=Decimal("0.20"),
    )
    inp = _base_input(transport_km=Decimal("100"))
    bd = compute_nebenkosten(inp, [rule])
    assert bd.total == Decimal("20.00")  # 100 km * 0.20


def test_compute_lagergeld_pro_tag_tonne():
    rule = NebenkostenRule(
        rule_id="NB-LAGER",
        art=NebenkostenArt.LAGERGELD,
        modus=NebenkostenModus.PRO_TAG_TONNE,
        rate=Decimal("0.15"),
    )
    inp = _base_input(billing_qty_tons=Decimal("50"), storage_days=Decimal("4"))
    bd = compute_nebenkosten(inp, [rule])
    # 50 t * 4 Tage * 0.15 = 30.00
    assert bd.total == Decimal("30.00")


def test_compute_verwiegung_pauschale():
    rule = NebenkostenRule(
        rule_id="NB-VERWIEG",
        art=NebenkostenArt.VERWIEGUNG,
        modus=NebenkostenModus.PAUSCHALE,
        rate=Decimal("12.00"),
    )
    inp = _base_input(weighing_count=3)
    bd = compute_nebenkosten(inp, [rule])
    # 3 Vorgaenge * 12.00 = 36.00
    assert bd.total == Decimal("36.00")


def test_compute_reinigung_pro_tonne():
    rule = NebenkostenRule(
        rule_id="NB-REINIGUNG",
        art=NebenkostenArt.REINIGUNG,
        modus=NebenkostenModus.PRO_TONNE,
        rate=Decimal("0.80"),
    )
    inp = _base_input(billing_qty_tons=Decimal("100"))
    bd = compute_nebenkosten(inp, [rule])
    assert bd.total == Decimal("80.00")


def test_compute_sonstige_pauschale():
    rule = NebenkostenRule(
        rule_id="NB-SONST",
        art=NebenkostenArt.SONSTIGE,
        modus=NebenkostenModus.PAUSCHALE,
        rate=Decimal("50.00"),
    )
    inp = _base_input()
    bd = compute_nebenkosten(inp, [rule])
    assert bd.total == Decimal("50.00")


def test_min_amount_applied():
    rule = NebenkostenRule(
        rule_id="NB-FRACHT-MIN",
        art=NebenkostenArt.FRACHT,
        modus=NebenkostenModus.PRO_KM,
        rate=Decimal("0.05"),
        min_amount=Decimal("20.00"),
    )
    inp = _base_input(transport_km=Decimal("10"))  # raw = 0.50 < min 20.00
    bd = compute_nebenkosten(inp, [rule])
    assert bd.total == Decimal("20.00")


def test_max_amount_applied():
    rule = NebenkostenRule(
        rule_id="NB-FRACHT-MAX",
        art=NebenkostenArt.FRACHT,
        modus=NebenkostenModus.PRO_KM,
        rate=Decimal("2.00"),
        max_amount=Decimal("100.00"),
    )
    inp = _base_input(transport_km=Decimal("200"))  # raw = 400 > max 100
    bd = compute_nebenkosten(inp, [rule])
    assert bd.total == Decimal("100.00")


def test_inactive_rule_skipped():
    rule = NebenkostenRule(
        rule_id="NB-INACTIVE",
        art=NebenkostenArt.FRACHT,
        modus=NebenkostenModus.PRO_KM,
        rate=Decimal("1.00"),
        active=False,
    )
    inp = _base_input(transport_km=Decimal("100"))
    bd = compute_nebenkosten(inp, [rule])
    assert bd.total == Decimal("0.00")
    assert len(bd.positions) == 0


def test_multiple_rules_total():
    rules = [
        NebenkostenRule("NB-A", NebenkostenArt.FRACHT, NebenkostenModus.PRO_KM, Decimal("0.10")),
        NebenkostenRule("NB-B", NebenkostenArt.REINIGUNG, NebenkostenModus.PRO_TONNE, Decimal("0.50")),
    ]
    inp = _base_input(transport_km=Decimal("100"), billing_qty_tons=Decimal("50"))
    bd = compute_nebenkosten(inp, rules)
    # 100 * 0.10 = 10.00 + 50 * 0.50 = 25.00 → total 35.00
    assert bd.total == Decimal("35.00")
    assert len(bd.positions) == 2


def test_breakdown_total_by_art():
    rules = [
        NebenkostenRule("NB-F", NebenkostenArt.FRACHT, NebenkostenModus.PRO_KM, Decimal("0.20")),
        NebenkostenRule("NB-R", NebenkostenArt.REINIGUNG, NebenkostenModus.PRO_TONNE, Decimal("1.00")),
    ]
    inp = _base_input(transport_km=Decimal("50"), billing_qty_tons=Decimal("30"))
    bd = compute_nebenkosten(inp, rules)
    tba = bd.total_by_art
    assert tba["FRACHT"] == Decimal("10.00")
    assert tba["REINIGUNG"] == Decimal("30.00")


def test_breakdown_as_dict():
    rules = get_default_nebenkosten_rules()
    inp = _base_input()
    bd = compute_nebenkosten(inp, rules)
    d = bd.as_dict()
    assert d["settlement_id"] == "S-001"
    assert d["schema_version"] == NEBENKOSTEN_SCHEMA_VERSION
    assert "total" in d
    assert "total_by_art" in d
    assert "positions" in d
    assert isinstance(d["positions"], list)


def test_breakdown_position_fields():
    rule = NebenkostenRule(
        "NB-FRACHT-KM",
        NebenkostenArt.FRACHT,
        NebenkostenModus.PRO_KM,
        Decimal("0.18"),
        description="Frachtkosten EUR/km",
    )
    bd = compute_nebenkosten(_base_input(transport_km=Decimal("100")), [rule])
    pos = bd.positions[0]
    d = pos.as_dict()
    assert d["art"] == "FRACHT"
    assert d["rule_id"] == "NB-FRACHT-KM"
    assert d["basis_unit"] == "km"
    assert d["currency"] == "EUR"


# ===========================================================================
# AP6: Standard-Regelset
# ===========================================================================

def test_default_rules_count():
    rules = get_default_nebenkosten_rules()
    assert len(rules) == 4


def test_default_rules_arts():
    rules = get_default_nebenkosten_rules()
    arts = {r.art for r in rules}
    assert NebenkostenArt.FRACHT in arts
    assert NebenkostenArt.LAGERGELD in arts
    assert NebenkostenArt.VERWIEGUNG in arts
    assert NebenkostenArt.REINIGUNG in arts


def test_default_rules_all_active():
    rules = get_default_nebenkosten_rules()
    assert all(r.active for r in rules)


def test_default_rules_serializable():
    rules = get_default_nebenkosten_rules()
    for r in rules:
        d = r.as_dict()
        assert "rule_id" in d
        assert "art" in d
        assert "rate" in d


def test_default_rules_compute_sensible():
    """Standard-Regelset produziert sinnvolle Betraege fuer typische Mengen."""
    inp = _base_input(
        billing_qty_tons=Decimal("100"),
        transport_km=Decimal("80"),
        storage_days=Decimal("7"),
        weighing_count=2,
    )
    bd = compute_nebenkosten(inp, get_default_nebenkosten_rules())
    # Muss positiv und serialisierbar sein
    assert bd.total > Decimal("0")
    d = bd.as_dict()
    assert float(d["total"]) > 0


# ===========================================================================
# AP2: IntrastatMeldung — Strukturpruefung
# ===========================================================================

def _valid_position(pid: str = "P-001") -> WarenbewegungsPosition:
    return WarenbewegungsPosition(
        position_id=pid,
        cn8_code="10019900",
        warenbezeichnung="Weichweizen",
        ursprungsland="FR",
        bestimmungsland="DE",
        warenwert_eur=Decimal("45000.00"),
        eigenmasse_kg=Decimal("200000.000"),
    )


def _valid_meldung(meldung_id: str = "INTRA-001") -> IntrastatMeldung:
    return IntrastatMeldung(
        meldung_id=meldung_id,
        tenant_id="t1",
        meldezeitraum="2026-03",
        richtung=IntrastatRichtung.EINGANG,
        meldender_name="Agrar GmbH",
        meldender_ust_id="DE123456789",
        meldender_betriebsstaette="12345678",
        positionen=[_valid_position()],
    )


def test_intrastat_meldung_gesamtwert():
    m = _valid_meldung()
    assert m.gesamtwert_eur == Decimal("45000.00")


def test_intrastat_meldung_gesamtmasse():
    m = _valid_meldung()
    assert m.gesamtmasse_kg == Decimal("200000.000")


def test_intrastat_meldung_positions_count():
    m = _valid_meldung()
    assert m.positions_count == 1


def test_intrastat_meldung_schema_version():
    m = _valid_meldung()
    assert m.schema_version == INTRASTAT_SCHEMA_VERSION


def test_intrastat_meldung_as_dict():
    m = _valid_meldung()
    d = m.as_dict()
    assert d["meldung_id"] == "INTRA-001"
    assert d["richtung"] == "EINGANG"
    assert d["schema_version"] == INTRASTAT_SCHEMA_VERSION
    assert "positionen" in d
    assert len(d["positionen"]) == 1


def test_warenbewegungsposition_as_dict():
    pos = _valid_position()
    d = pos.as_dict()
    assert d["cn8_code"] == "10019900"
    assert d["ursprungsland"] == "FR"
    assert d["bestimmungsland"] == "DE"


# ===========================================================================
# AP5: validate_intrastat_meldung() — Vollstaendigkeitspruefung
# ===========================================================================

def test_valid_meldung_passes_validation():
    m = _valid_meldung()
    result = validate_intrastat_meldung(m)
    assert result.valid is True
    assert result.violation_count == 0


def test_validation_result_schema_version():
    m = _valid_meldung()
    result = validate_intrastat_meldung(m)
    assert result.schema_version == INTRASTAT_SCHEMA_VERSION


def test_validation_as_dict():
    m = _valid_meldung()
    result = validate_intrastat_meldung(m)
    d = result.as_dict()
    assert d["valid"] is True
    assert d["violation_count"] == 0
    assert isinstance(d["violations"], list)


def test_missing_meldezeitraum():
    m = _valid_meldung()
    m.meldezeitraum = ""
    result = validate_intrastat_meldung(m)
    assert result.valid is False
    codes = [v.code for v in result.violations]
    assert IntrastatViolationCode.MISSING_MELDEZEITRAUM in codes


def test_missing_meldender_name():
    m = _valid_meldung()
    m.meldender_name = "  "
    result = validate_intrastat_meldung(m)
    assert result.valid is False
    codes = [v.code for v in result.violations]
    assert IntrastatViolationCode.MISSING_MELDENDER in codes


def test_missing_ust_id():
    m = _valid_meldung()
    m.meldender_ust_id = ""
    result = validate_intrastat_meldung(m)
    codes = [v.code for v in result.violations]
    assert IntrastatViolationCode.MISSING_UST_ID in codes


def test_no_positionen():
    m = _valid_meldung()
    m.positionen = []
    result = validate_intrastat_meldung(m)
    codes = [v.code for v in result.violations]
    assert IntrastatViolationCode.MISSING_POSITIONEN in codes


def test_invalid_cn8_code():
    m = _valid_meldung()
    m.positionen[0].cn8_code = "1234"  # zu kurz
    result = validate_intrastat_meldung(m)
    codes = [v.code for v in result.violations]
    assert IntrastatViolationCode.POSITION_INVALID_CN8 in codes


def test_missing_cn8_code():
    m = _valid_meldung()
    m.positionen[0].cn8_code = ""
    result = validate_intrastat_meldung(m)
    codes = [v.code for v in result.violations]
    assert IntrastatViolationCode.POSITION_MISSING_CN8 in codes


def test_invalid_ursprungsland():
    m = _valid_meldung()
    m.positionen[0].ursprungsland = "XX"  # kein EU-Staat
    result = validate_intrastat_meldung(m)
    codes = [v.code for v in result.violations]
    assert IntrastatViolationCode.POSITION_INVALID_URSPRUNGSLAND in codes


def test_invalid_bestimmungsland():
    m = _valid_meldung()
    m.positionen[0].bestimmungsland = "US"  # kein EU-Staat
    result = validate_intrastat_meldung(m)
    codes = [v.code for v in result.violations]
    assert IntrastatViolationCode.POSITION_INVALID_BESTIMMUNGSLAND in codes


def test_negative_warenwert():
    m = _valid_meldung()
    m.positionen[0].warenwert_eur = Decimal("-100.00")
    result = validate_intrastat_meldung(m)
    codes = [v.code for v in result.violations]
    assert IntrastatViolationCode.POSITION_NEGATIVE_WARENWERT in codes


def test_negative_eigenmasse():
    m = _valid_meldung()
    m.positionen[0].eigenmasse_kg = Decimal("-50.0")
    result = validate_intrastat_meldung(m)
    codes = [v.code for v in result.violations]
    assert IntrastatViolationCode.POSITION_NEGATIVE_EIGENMASSE in codes


def test_multiple_violations():
    m = _valid_meldung()
    m.meldezeitraum = ""
    m.meldender_name = ""
    m.positionen[0].cn8_code = "BAD"
    result = validate_intrastat_meldung(m)
    assert result.valid is False
    assert result.violation_count >= 3


def test_eu_mitgliedstaaten_set():
    assert "DE" in EU_MITGLIEDSTAATEN
    assert "FR" in EU_MITGLIEDSTAATEN
    assert "PL" in EU_MITGLIEDSTAATEN
    assert "US" not in EU_MITGLIEDSTAATEN
    assert "GB" not in EU_MITGLIEDSTAATEN  # Brexit


def test_stub_meldung_is_valid():
    m = build_stub_intrastat_meldung("INTRA-STUB-001", "t1")
    result = validate_intrastat_meldung(m)
    assert result.valid is True


def test_stub_meldung_fields():
    m = build_stub_intrastat_meldung("INTRA-STUB-002", "t1", meldezeitraum="2026-04")
    assert m.meldezeitraum == "2026-04"
    assert m.richtung == IntrastatRichtung.EINGANG
    assert m.positions_count == 1


# ===========================================================================
# AP3 + AP4: API-Endpoints via TestClient
# ===========================================================================

@pytest.fixture(scope="module")
def client():
    from app.main import app
    from fastapi.testclient import TestClient
    return TestClient(app, raise_server_exceptions=True)


def test_nebenkosten_preview_endpoint(client):
    resp = client.get(
        "/api/v1/process/settlement/nebenkosten-preview/S-W23-001",
        headers={"X-Tenant-ID": "tenant-test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["settlement_id"] == "S-W23-001"
    assert data["schema_version"] == 1
    assert "nebenkosten" in data
    nb = data["nebenkosten"]
    assert "total" in nb
    assert "positions" in nb
    assert len(nb["positions"]) > 0


def test_nebenkosten_preview_has_total_by_art(client):
    resp = client.get(
        "/api/v1/process/settlement/nebenkosten-preview/S-W23-002",
        headers={"X-Tenant-ID": "tenant-test"},
    )
    data = resp.json()
    nb = data["nebenkosten"]
    assert "total_by_art" in nb
    assert isinstance(nb["total_by_art"], dict)


def test_nebenkosten_preview_rule_count(client):
    resp = client.get(
        "/api/v1/process/settlement/nebenkosten-preview/S-ANY",
        headers={"X-Tenant-ID": "tenant-test"},
    )
    data = resp.json()
    assert data["rule_count"] == 4  # Standard-Regelset hat 4 Regeln


def test_intrastat_meldungen_list_empty(client):
    resp = client.get(
        "/api/v1/compliance/intrastat/meldungen",
        headers={"X-Tenant-ID": "tenant-test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "meldungen" in data
    assert data["schema_version"] == 1


def test_intrastat_meldungen_create(client):
    resp = client.post(
        "/api/v1/compliance/intrastat/meldungen",
        json={"meldung_id": "INTRA-API-001", "meldezeitraum": "2026-03", "richtung": "EINGANG"},
        headers={"X-Tenant-ID": "tenant-test"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "meldung" in data
    assert "validation_result" in data
    assert data["schema_version"] == 1
    assert data["validation_result"]["valid"] is True


def test_intrastat_validate_endpoint(client):
    resp = client.get(
        "/api/v1/compliance/intrastat/meldungen/INTRA-STUB/validate",
        headers={"X-Tenant-ID": "tenant-test"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is True
    assert data["schema_version"] == INTRASTAT_SCHEMA_VERSION
    assert "violations" in data
