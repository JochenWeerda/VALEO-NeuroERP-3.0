"""
Wave 28 — SLA-Eskalations-Engine + OTel Span-Contracts

Gap 013: >=95% SLA-Einhaltung, standardisierte Eskalationsknoten
Gap 039: End-to-End Tracing UI→API→DB→Worker, MTTR -40%

Testet:
  AP1: evaluate_sla_breach() — OK/WARNUNG/KRITISCH/BLOCKIERT
  AP2: SpanContract, SpanRegistry, get_process_kernel_spans()
  AP3/AP4: API-Endpoints SLA-Eskalationen + OTel Span-Registry
  AP5: validate_sla_policy() — Konsistenzpruefung
  AP6: get_default_sla_eskalations_policies() — 6 Default-Policies
"""
from __future__ import annotations

import pytest
from decimal import Decimal
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# AP1: evaluate_sla_breach()
# ---------------------------------------------------------------------------

def _make_policy(
    policy_id: str = "TEST-SLA",
    prozess_key: str = "test_prozess",
    warnung: str = "8",
    kritisch: str = "16",
    max_h: str = "24",
    rolle: str = "teamleiter",
):
    from app.core.sla_eskalation_engine import SLAEskalationsPolicy
    return SLAEskalationsPolicy(
        policy_id=policy_id,
        prozess_key=prozess_key,
        schritt_id=None,
        bezeichnung="Test-Policy",
        warnung_stunden=Decimal(warnung),
        kritisch_stunden=Decimal(kritisch),
        max_stunden=Decimal(max_h),
        benachrichtigungs_rolle=rolle,
    )


def test_evaluate_sla_breach_ok():
    from app.core.sla_eskalation_engine import evaluate_sla_breach, EskalationsStufe
    policy = _make_policy()
    result = evaluate_sla_breach(policy, "inst-001", Decimal("4"))
    assert result.stufe == EskalationsStufe.OK
    assert result.ueberschreitung_stunden == Decimal("0")
    assert result.verbleibend_bis_warnung == Decimal("4")   # 8 - 4
    assert result.verbleibend_bis_kritisch == Decimal("12")  # 16 - 4
    assert not result.eskalation_erforderlich
    assert not result.prozess_blockiert


def test_evaluate_sla_breach_warnung():
    from app.core.sla_eskalation_engine import evaluate_sla_breach, EskalationsStufe
    policy = _make_policy()
    result = evaluate_sla_breach(policy, "inst-002", Decimal("10"))
    assert result.stufe == EskalationsStufe.WARNUNG
    assert result.ueberschreitung_stunden == Decimal("2")  # 10 - 8
    assert result.verbleibend_bis_warnung is None
    assert result.verbleibend_bis_kritisch == Decimal("6")  # 16 - 10
    assert not result.eskalation_erforderlich


def test_evaluate_sla_breach_kritisch():
    from app.core.sla_eskalation_engine import evaluate_sla_breach, EskalationsStufe
    policy = _make_policy()
    result = evaluate_sla_breach(policy, "inst-003", Decimal("20"))
    assert result.stufe == EskalationsStufe.KRITISCH
    assert result.ueberschreitung_stunden == Decimal("4")  # 20 - 16
    assert result.verbleibend_bis_warnung is None
    assert result.verbleibend_bis_kritisch is None
    assert result.eskalation_erforderlich
    assert not result.prozess_blockiert


def test_evaluate_sla_breach_blockiert():
    from app.core.sla_eskalation_engine import evaluate_sla_breach, EskalationsStufe
    policy = _make_policy()
    result = evaluate_sla_breach(policy, "inst-004", Decimal("30"))
    assert result.stufe == EskalationsStufe.BLOCKIERT
    assert result.ueberschreitung_stunden == Decimal("6")  # 30 - 24
    assert result.eskalation_erforderlich
    assert result.prozess_blockiert


def test_evaluate_sla_breach_exact_warnung_threshold():
    """Grenzwert-Test: ist_dauer == warnung_stunden → WARNUNG (inklusiv)."""
    from app.core.sla_eskalation_engine import evaluate_sla_breach, EskalationsStufe
    policy = _make_policy()
    result = evaluate_sla_breach(policy, "inst-005", Decimal("8"))
    assert result.stufe == EskalationsStufe.WARNUNG
    assert result.ueberschreitung_stunden == Decimal("0")


def test_evaluate_sla_breach_exact_kritisch_threshold():
    from app.core.sla_eskalation_engine import evaluate_sla_breach, EskalationsStufe
    policy = _make_policy()
    result = evaluate_sla_breach(policy, "inst-006", Decimal("16"))
    assert result.stufe == EskalationsStufe.KRITISCH


def test_evaluate_sla_breach_exact_max_threshold():
    from app.core.sla_eskalation_engine import evaluate_sla_breach, EskalationsStufe
    policy = _make_policy()
    result = evaluate_sla_breach(policy, "inst-007", Decimal("24"))
    assert result.stufe == EskalationsStufe.BLOCKIERT
    assert result.ueberschreitung_stunden == Decimal("0")


def test_evaluate_sla_breach_zero_duration():
    from app.core.sla_eskalation_engine import evaluate_sla_breach, EskalationsStufe
    policy = _make_policy()
    result = evaluate_sla_breach(policy, "inst-008", Decimal("0"))
    assert result.stufe == EskalationsStufe.OK
    assert result.verbleibend_bis_warnung == Decimal("8")


def test_evaluate_sla_breach_decimal_duration():
    """Fliesskomma-Stunden (z.B. 30 Min = 0.5h) korrekt ausgewertet."""
    from app.core.sla_eskalation_engine import evaluate_sla_breach, EskalationsStufe
    policy = _make_policy(warnung="1", kritisch="2", max_h="4")
    result = evaluate_sla_breach(policy, "inst-009", Decimal("0.5"))
    assert result.stufe == EskalationsStufe.OK
    assert result.verbleibend_bis_warnung == Decimal("0.5")


def test_evaluate_sla_breach_as_dict_complete():
    from app.core.sla_eskalation_engine import evaluate_sla_breach, EskalationsStufe
    policy = _make_policy()
    result = evaluate_sla_breach(policy, "inst-010", Decimal("20"))
    d = result.as_dict()
    assert d["policy_id"] == "TEST-SLA"
    assert d["stufe"] == "KRITISCH"
    assert d["eskalation_erforderlich"] is True
    assert d["prozess_blockiert"] is False
    assert d["benachrichtigungs_rolle"] == "teamleiter"
    assert d["schema_version"] == 1


def test_evaluate_sla_breach_benachrichtigungs_rolle_propagiert():
    policy = _make_policy(rolle="buchhalter")
    from app.core.sla_eskalation_engine import evaluate_sla_breach
    result = evaluate_sla_breach(policy, "inst-011", Decimal("1"))
    assert result.benachrichtigungs_rolle == "buchhalter"


# ---------------------------------------------------------------------------
# AP5: validate_sla_policy()
# ---------------------------------------------------------------------------

def test_validate_sla_policy_valid():
    from app.core.sla_eskalation_engine import validate_sla_policy
    policy = _make_policy()
    result = validate_sla_policy(policy)
    assert result.valid is True
    assert result.violations == []


def test_validate_sla_policy_warnung_gleich_kritisch():
    from app.core.sla_eskalation_engine import validate_sla_policy, SLAPolicyViolationCode
    policy = _make_policy(warnung="8", kritisch="8", max_h="24")
    result = validate_sla_policy(policy)
    assert not result.valid
    codes = [v.code for v in result.violations]
    assert SLAPolicyViolationCode.WARNUNG_GROESSER_KRITISCH in codes


def test_validate_sla_policy_warnung_groesser_kritisch():
    from app.core.sla_eskalation_engine import validate_sla_policy, SLAPolicyViolationCode
    policy = _make_policy(warnung="16", kritisch="8", max_h="24")
    result = validate_sla_policy(policy)
    assert not result.valid
    codes = [v.code for v in result.violations]
    assert SLAPolicyViolationCode.WARNUNG_GROESSER_KRITISCH in codes


def test_validate_sla_policy_kritisch_groesser_max():
    from app.core.sla_eskalation_engine import validate_sla_policy, SLAPolicyViolationCode
    policy = _make_policy(warnung="8", kritisch="24", max_h="16")
    result = validate_sla_policy(policy)
    assert not result.valid
    codes = [v.code for v in result.violations]
    assert SLAPolicyViolationCode.KRITISCH_GROESSER_MAX in codes


def test_validate_sla_policy_null_wert():
    from app.core.sla_eskalation_engine import validate_sla_policy, SLAPolicyViolationCode
    policy = _make_policy(warnung="0", kritisch="8", max_h="24")
    result = validate_sla_policy(policy)
    assert not result.valid
    codes = [v.code for v in result.violations]
    assert SLAPolicyViolationCode.SCHWELLENWERT_NULL_ODER_NEGATIV in codes


def test_validate_sla_policy_negativer_wert():
    from app.core.sla_eskalation_engine import validate_sla_policy, SLAPolicyViolationCode
    policy = _make_policy(warnung="-2", kritisch="8", max_h="24")
    result = validate_sla_policy(policy)
    assert not result.valid
    codes = [v.code for v in result.violations]
    assert SLAPolicyViolationCode.SCHWELLENWERT_NULL_ODER_NEGATIV in codes


def test_validate_sla_policy_leerer_prozess_key():
    from app.core.sla_eskalation_engine import (
        validate_sla_policy, SLAEskalationsPolicy, SLAPolicyViolationCode
    )
    policy = SLAEskalationsPolicy(
        policy_id="TEST",
        prozess_key="  ",
        schritt_id=None,
        bezeichnung="Test",
        warnung_stunden=Decimal("8"),
        kritisch_stunden=Decimal("16"),
        max_stunden=Decimal("24"),
    )
    result = validate_sla_policy(policy)
    assert not result.valid
    codes = [v.code for v in result.violations]
    assert SLAPolicyViolationCode.PROZESS_KEY_LEER in codes


def test_validate_sla_policy_as_dict():
    from app.core.sla_eskalation_engine import validate_sla_policy
    policy = _make_policy()
    result = validate_sla_policy(policy)
    d = result.as_dict()
    assert d["valid"] is True
    assert d["violation_count"] == 0
    assert d["schema_version"] == 1


# ---------------------------------------------------------------------------
# AP6: get_default_sla_eskalations_policies()
# ---------------------------------------------------------------------------

def test_default_policies_count():
    from app.core.sla_eskalation_engine import get_default_sla_eskalations_policies
    policies = get_default_sla_eskalations_policies()
    assert len(policies) == 6


def test_default_policies_all_valid():
    from app.core.sla_eskalation_engine import get_default_sla_eskalations_policies, validate_sla_policy
    for policy in get_default_sla_eskalations_policies():
        result = validate_sla_policy(policy)
        assert result.valid, f"Policy {policy.policy_id} ist ungueltig: {result.violations}"


def test_default_policies_agrar_settlement_gesamt():
    from app.core.sla_eskalation_engine import get_default_sla_eskalations_policies
    policies = {p.policy_id: p for p in get_default_sla_eskalations_policies()}
    p = policies["SLA-AS-GESAMT"]
    assert p.prozess_key == "agrar_settlement"
    assert p.schritt_id is None
    assert p.warnung_stunden == Decimal("24")
    assert p.kritisch_stunden == Decimal("48")
    assert p.max_stunden == Decimal("72")


def test_default_policies_serializable():
    from app.core.sla_eskalation_engine import get_default_sla_eskalations_policies
    for policy in get_default_sla_eskalations_policies():
        d = policy.as_dict()
        assert "policy_id" in d
        assert "schema_version" in d
        assert d["schema_version"] == 1


def test_default_policies_intrastat_consistent_thresholds():
    """Intrastat-Policy muss monoton steigende Schwellenwerte haben."""
    from app.core.sla_eskalation_engine import get_default_sla_eskalations_policies
    policies = {p.policy_id: p for p in get_default_sla_eskalations_policies()}
    p = policies["SLA-INTRASTAT-MELDUNG"]
    assert p.warnung_stunden < p.kritisch_stunden < p.max_stunden


# ---------------------------------------------------------------------------
# AP2: SpanContract + SpanRegistry
# ---------------------------------------------------------------------------

def test_span_contract_valid_name():
    from app.core.otel_span_contracts import SpanContract, SpanKind, SamplingRegel, SpanAttributeSchema
    sc = SpanContract(
        span_name="valeo.agrar.settlement_create",
        kind=SpanKind.INTERNAL,
        domain="agrar",
        operation="settlement_create",
        beschreibung="Test",
        sampling=SamplingRegel.ALWAYS,
    )
    assert sc.validate_name() is True


def test_span_contract_invalid_name_wrong_prefix():
    from app.core.otel_span_contracts import SpanContract, SpanKind, SamplingRegel
    sc = SpanContract(
        span_name="otel.agrar.settlement_create",
        kind=SpanKind.INTERNAL,
        domain="agrar",
        operation="settlement_create",
        beschreibung="Test",
        sampling=SamplingRegel.ALWAYS,
    )
    assert sc.validate_name() is False


def test_span_contract_invalid_name_missing_part():
    from app.core.otel_span_contracts import SpanContract, SpanKind, SamplingRegel
    sc = SpanContract(
        span_name="valeo.agrar",
        kind=SpanKind.INTERNAL,
        domain="agrar",
        operation="settlement_create",
        beschreibung="Test",
        sampling=SamplingRegel.ALWAYS,
    )
    assert sc.validate_name() is False


def test_span_contract_as_dict_complete():
    from app.core.otel_span_contracts import SpanContract, SpanKind, SamplingRegel
    sc = SpanContract(
        span_name="valeo.finance.ap_invoice_post",
        kind=SpanKind.INTERNAL,
        domain="finance",
        operation="ap_invoice_post",
        beschreibung="Verbucht Kreditorenrechnung",
        sampling=SamplingRegel.ALWAYS,
    )
    d = sc.as_dict()
    assert d["span_name"] == "valeo.finance.ap_invoice_post"
    assert d["convention_valid"] is True
    assert d["kind"] == "INTERNAL"
    assert d["sampling"] == "ALWAYS"
    assert d["schema_version"] == 1


def test_span_registry_by_domain():
    from app.core.otel_span_contracts import get_process_kernel_spans
    registry = get_process_kernel_spans()
    agrar = registry.by_domain("agrar")
    assert len(agrar) >= 4
    for c in agrar:
        assert c.domain == "agrar"


def test_span_registry_by_name():
    from app.core.otel_span_contracts import get_process_kernel_spans
    registry = get_process_kernel_spans()
    c = registry.by_name("valeo.agrar.sla_evaluate")
    assert c is not None
    assert c.operation == "sla_evaluate"


def test_span_registry_by_name_not_found():
    from app.core.otel_span_contracts import get_process_kernel_spans
    registry = get_process_kernel_spans()
    assert registry.by_name("valeo.unknown.no_such_span") is None


def test_span_registry_all_names_valid_convention():
    """Alle registrierten Span-Contracts muessen der Naming-Convention entsprechen."""
    from app.core.otel_span_contracts import get_process_kernel_spans
    registry = get_process_kernel_spans()
    violations = registry.validate_all_names()
    assert violations == [], f"Convention-Verletzungen: {violations}"


def test_span_registry_no_otel_library_import():
    """app/core/otel_span_contracts.py darf kein 'opentelemetry' importieren."""
    import importlib
    import sys
    # Pruefe ob opentelemetry im Modul-Namespace ist
    import app.core.otel_span_contracts as m
    assert not hasattr(m, "opentelemetry"), \
        "otel_span_contracts importiert opentelemetry — verletzt Schichtgrenzen"
    # Pruefe Source-Code direkt
    import inspect
    src = inspect.getsource(m)
    assert "import opentelemetry" not in src
    assert "from opentelemetry" not in src


def test_span_registry_has_all_domains():
    from app.core.otel_span_contracts import get_process_kernel_spans
    registry = get_process_kernel_spans()
    domains = {c.domain for c in registry.contracts}
    for expected in ("agrar", "finance", "workflow", "compliance", "process"):
        assert expected in domains, f"Domain '{expected}' fehlt in Registry"


def test_span_registry_as_dict():
    from app.core.otel_span_contracts import get_process_kernel_spans
    registry = get_process_kernel_spans()
    d = registry.as_dict()
    assert "contract_count" in d
    assert "domains" in d
    assert "convention_violations" in d
    assert d["convention_violations"] == []
    assert d["schema_version"] == 1


def test_span_attribute_schema_pflicht_keys():
    from app.core.otel_span_contracts import get_process_kernel_spans
    registry = get_process_kernel_spans()
    c = registry.by_name("valeo.agrar.settlement_create")
    assert c is not None
    schema_dict = c.attribute_schema.as_dict()
    assert "valeo.tenant_id" in schema_dict["pflicht_keys"]
    assert "valeo.settlement_id" in schema_dict["pflicht_keys"]


def test_span_contract_sampling_ratio():
    from app.core.otel_span_contracts import get_process_kernel_spans, SamplingRegel
    registry = get_process_kernel_spans()
    c = registry.by_name("valeo.agrar.sla_evaluate")
    assert c is not None
    assert c.sampling == SamplingRegel.RATIO
    assert c.sampling_ratio_pct == 25.0


def test_span_contract_sampling_never():
    from app.core.otel_span_contracts import get_process_kernel_spans, SamplingRegel
    registry = get_process_kernel_spans()
    c = registry.by_name("valeo.process.sla_policy_validate")
    assert c is not None
    assert c.sampling == SamplingRegel.NEVER


# ---------------------------------------------------------------------------
# AP3/AP4: API-Endpoints
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


def test_api_sla_eskalationen_all(client):
    resp = client.get("/api/v1/process/sla/eskalationen?ist_dauer_stunden=10")
    assert resp.status_code == 200
    body = resp.json()
    assert body["policy_count"] == 6
    assert "auswertungen" in body
    assert body["ist_dauer_stunden"] in ("10", "10.0")


def test_api_sla_eskalationen_zero_duration(client):
    resp = client.get("/api/v1/process/sla/eskalationen")
    assert resp.status_code == 200
    body = resp.json()
    for aw in body["auswertungen"]:
        assert aw["stufe"] == "OK"


def test_api_sla_eskalationen_by_prozess(client):
    resp = client.get("/api/v1/process/sla/eskalationen/agrar_settlement?ist_dauer_stunden=30")
    assert resp.status_code == 200
    body = resp.json()
    assert body["prozess_key"] == "agrar_settlement"
    assert body["policy_count"] == 3


def test_api_sla_eskalationen_by_prozess_not_found(client):
    resp = client.get("/api/v1/process/sla/eskalationen/unbekannter_prozess")
    assert resp.status_code == 404


def test_api_sla_eskalationen_blockiert(client):
    """Mit sehr grosser Ist-Dauer muessen alle BLOCKIERT sein."""
    resp = client.get("/api/v1/process/sla/eskalationen?ist_dauer_stunden=9999")
    assert resp.status_code == 200
    body = resp.json()
    for aw in body["auswertungen"]:
        assert aw["stufe"] == "BLOCKIERT"


def test_api_otel_span_registry(client):
    resp = client.get("/api/v1/process/otel/span-registry")
    assert resp.status_code == 200
    body = resp.json()
    assert body["contract_count"] >= 12
    assert body["convention_violations"] == []
    assert "agrar" in body["domains"]


def test_api_otel_span_registry_domain_filter(client):
    resp = client.get("/api/v1/process/otel/span-registry?domain=finance")
    assert resp.status_code == 200
    body = resp.json()
    assert body["domain_filter"] == "finance"
    assert body["contract_count"] >= 3
    for c in body["contracts"]:
        assert c["domain"] == "finance"


def test_api_otel_span_registry_empty_domain(client):
    resp = client.get("/api/v1/process/otel/span-registry?domain=nonexistent_domain")
    assert resp.status_code == 200
    body = resp.json()
    assert body["contract_count"] == 0
    assert body["contracts"] == []


def test_api_otel_span_registry_schema_version(client):
    resp = client.get("/api/v1/process/otel/span-registry")
    assert resp.status_code == 200
    body = resp.json()
    assert body["schema_version"] == 1
