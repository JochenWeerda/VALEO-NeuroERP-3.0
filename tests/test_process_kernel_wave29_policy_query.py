"""
Wave 29 — Policy-as-Code Engine + Query-Vertrags-Registry

Gap 014: Policy-as-Code mit Tenant Overrides — 100% Ausnahmen regelbasiert dokumentiert
Gap 031: Query-Vertraege (keine undefined) — Frontend-Clients erhalten typisierte Felder

Testet:
  AP1: evaluate_policy_set() — ERLAUBT/ABGELEHNT/WARNUNG/ESKALATION
  AP2: apply_tenant_overrides(), validate_policy_set()
  AP3: API-Endpoints /process/policy-rules
  AP4: QueryContract, QueryRegistry, get_process_kernel_queries()
  AP5: validate_query_result()
  AP6: API-Endpoint /process/query-registry
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------

def _make_policy_set(
    policy_set_id: str = "PS-TEST",
    prozess_key: str = "test_prozess",
):
    from app.core.policy_code_engine import (
        PolicySet, PolicyRegel, PolicyBedingung,
        PolicyBedingungsTyp, PolicyAktion,
    )
    return PolicySet(
        policy_set_id=policy_set_id,
        prozess_key=prozess_key,
        bezeichnung="Test PolicySet",
        regeln=[
            PolicyRegel(
                regel_id="R-001",
                bezeichnung="Grossbetrag ablehnen",
                bedingungen=[PolicyBedingung(PolicyBedingungsTyp.GROESSER_GLEICH, "betrag", 10000)],
                aktion=PolicyAktion.ABGELEHNT,
                prioritaet=10,
                pflicht=True,
            ),
            PolicyRegel(
                regel_id="R-002",
                bezeichnung="Mittelbereich eskalieren",
                bedingungen=[
                    PolicyBedingung(PolicyBedingungsTyp.GROESSER_GLEICH, "betrag", 5000),
                    PolicyBedingung(PolicyBedingungsTyp.KLEINER, "betrag", 10000),
                ],
                aktion=PolicyAktion.ESKALATION,
                prioritaet=20,
                pflicht=False,
            ),
            PolicyRegel(
                regel_id="R-003",
                bezeichnung="Kleinbetrag erlaubt",
                bedingungen=[PolicyBedingung(PolicyBedingungsTyp.KLEINER, "betrag", 5000)],
                aktion=PolicyAktion.ERLAUBT,
                prioritaet=30,
                pflicht=False,
            ),
        ],
    )


# ---------------------------------------------------------------------------
# AP1: PolicyBedingung.evaluate()
# ---------------------------------------------------------------------------

def test_bedingung_gleich_true():
    from app.core.policy_code_engine import PolicyBedingung, PolicyBedingungsTyp
    b = PolicyBedingung(PolicyBedingungsTyp.GLEICH, "status", "AKTIV")
    assert b.evaluate({"status": "AKTIV"}) is True


def test_bedingung_gleich_false():
    from app.core.policy_code_engine import PolicyBedingung, PolicyBedingungsTyp
    b = PolicyBedingung(PolicyBedingungsTyp.GLEICH, "status", "AKTIV")
    assert b.evaluate({"status": "INAKTIV"}) is False


def test_bedingung_ungleich():
    from app.core.policy_code_engine import PolicyBedingung, PolicyBedingungsTyp
    b = PolicyBedingung(PolicyBedingungsTyp.UNGLEICH, "land", "DE")
    assert b.evaluate({"land": "FR"}) is True
    assert b.evaluate({"land": "DE"}) is False


def test_bedingung_groesser():
    from app.core.policy_code_engine import PolicyBedingung, PolicyBedingungsTyp
    b = PolicyBedingung(PolicyBedingungsTyp.GROESSER, "betrag", 1000)
    assert b.evaluate({"betrag": 2000}) is True
    assert b.evaluate({"betrag": 1000}) is False


def test_bedingung_groesser_gleich():
    from app.core.policy_code_engine import PolicyBedingung, PolicyBedingungsTyp
    b = PolicyBedingung(PolicyBedingungsTyp.GROESSER_GLEICH, "betrag", 1000)
    assert b.evaluate({"betrag": 1000}) is True
    assert b.evaluate({"betrag": 999}) is False


def test_bedingung_kleiner_gleich():
    from app.core.policy_code_engine import PolicyBedingung, PolicyBedingungsTyp
    b = PolicyBedingung(PolicyBedingungsTyp.KLEINER_GLEICH, "feuchte", 15.0)
    assert b.evaluate({"feuchte": 15.0}) is True
    assert b.evaluate({"feuchte": 15.1}) is False


def test_bedingung_enthaelt_in_liste():
    from app.core.policy_code_engine import PolicyBedingung, PolicyBedingungsTyp
    b = PolicyBedingung(PolicyBedingungsTyp.ENTHAELT, "rollen", "admin")
    assert b.evaluate({"rollen": ["admin", "user"]}) is True
    assert b.evaluate({"rollen": ["user"]}) is False


def test_bedingung_nicht_leer_true():
    from app.core.policy_code_engine import PolicyBedingung, PolicyBedingungsTyp
    b = PolicyBedingung(PolicyBedingungsTyp.NICHT_LEER, "protokoll_id")
    assert b.evaluate({"protokoll_id": "PROT-001"}) is True


def test_bedingung_nicht_leer_false_none():
    from app.core.policy_code_engine import PolicyBedingung, PolicyBedingungsTyp
    b = PolicyBedingung(PolicyBedingungsTyp.NICHT_LEER, "protokoll_id")
    assert b.evaluate({"protokoll_id": None}) is False
    assert b.evaluate({}) is False
    assert b.evaluate({"protokoll_id": ""}) is False


def test_bedingung_fehlendes_feld_false():
    from app.core.policy_code_engine import PolicyBedingung, PolicyBedingungsTyp
    b = PolicyBedingung(PolicyBedingungsTyp.GLEICH, "status", "AKTIV")
    assert b.evaluate({}) is False


# ---------------------------------------------------------------------------
# AP1: evaluate_policy_set()
# ---------------------------------------------------------------------------

def test_evaluate_policy_set_abgelehnt():
    from app.core.policy_code_engine import evaluate_policy_set, PolicyAktion
    ps = _make_policy_set()
    result = evaluate_policy_set(ps, {"betrag": 15000})
    assert result.wirksame_aktion == PolicyAktion.ABGELEHNT
    assert result.abgelehnt is True


def test_evaluate_policy_set_eskalation():
    from app.core.policy_code_engine import evaluate_policy_set, PolicyAktion
    ps = _make_policy_set()
    result = evaluate_policy_set(ps, {"betrag": 7500})
    assert result.wirksame_aktion == PolicyAktion.ESKALATION
    assert result.eskalation_erforderlich is True
    assert not result.abgelehnt


def test_evaluate_policy_set_erlaubt():
    from app.core.policy_code_engine import evaluate_policy_set, PolicyAktion
    ps = _make_policy_set()
    result = evaluate_policy_set(ps, {"betrag": 1000})
    assert result.wirksame_aktion == PolicyAktion.ERLAUBT
    assert not result.abgelehnt
    assert not result.eskalation_erforderlich


def test_evaluate_policy_set_kein_treffer():
    """Kein Treffer → implizit ERLAUBT."""
    from app.core.policy_code_engine import evaluate_policy_set, PolicyAktion
    ps = _make_policy_set()
    result = evaluate_policy_set(ps, {"unbekanntes_feld": 999})
    assert result.kein_treffer is True
    assert result.wirksame_aktion == PolicyAktion.ERLAUBT


def test_evaluate_policy_set_abgelehnt_beats_warnung():
    """ABGELEHNT hat hoechsten Rang — schlaegt WARNUNG."""
    from app.core.policy_code_engine import (
        evaluate_policy_set, PolicyAktion, PolicySet, PolicyRegel,
        PolicyBedingung, PolicyBedingungsTyp,
    )
    ps = PolicySet(
        policy_set_id="PS-PRIO",
        prozess_key="test",
        bezeichnung="Prioritaetstest",
        regeln=[
            PolicyRegel(
                regel_id="R-W",
                bezeichnung="Warnung",
                bedingungen=[PolicyBedingung(PolicyBedingungsTyp.GLEICH, "x", 1)],
                aktion=PolicyAktion.WARNUNG,
                prioritaet=50,
            ),
            PolicyRegel(
                regel_id="R-A",
                bezeichnung="Abgelehnt",
                bedingungen=[PolicyBedingung(PolicyBedingungsTyp.GLEICH, "x", 1)],
                aktion=PolicyAktion.ABGELEHNT,
                prioritaet=10,
            ),
        ],
    )
    result = evaluate_policy_set(ps, {"x": 1})
    assert result.wirksame_aktion == PolicyAktion.ABGELEHNT
    assert len(result.treffer) == 2


def test_evaluate_policy_set_as_dict():
    from app.core.policy_code_engine import evaluate_policy_set
    ps = _make_policy_set()
    result = evaluate_policy_set(ps, {"betrag": 500})
    d = result.as_dict()
    assert d["abgelehnt"] is False
    assert d["schema_version"] == 1
    assert "treffer" in d


# ---------------------------------------------------------------------------
# AP2: apply_tenant_overrides()
# ---------------------------------------------------------------------------

def test_apply_tenant_overrides_deaktiviert_regel():
    from app.core.policy_code_engine import apply_tenant_overrides, TenantPolicyOverride
    base = _make_policy_set()
    override = TenantPolicyOverride(
        tenant_id="tenant-sued",
        policy_set_id="PS-TEST",
        deaktivierte_regel_ids=["R-002"],
    )
    merged = apply_tenant_overrides(base, override)
    ids = [r.regel_id for r in merged.regeln]
    assert "R-002" not in ids
    assert "R-001" in ids  # Pflicht-Regel bleibt


def test_apply_tenant_overrides_pflicht_nicht_deaktivierbar():
    from app.core.policy_code_engine import apply_tenant_overrides, TenantPolicyOverride
    base = _make_policy_set()
    # R-001 ist pflicht=True
    override = TenantPolicyOverride(
        tenant_id="tenant-nord",
        policy_set_id="PS-TEST",
        deaktivierte_regel_ids=["R-001"],
    )
    merged = apply_tenant_overrides(base, override)
    ids = [r.regel_id for r in merged.regeln]
    assert "R-001" in ids  # Pflicht-Regel bleibt erhalten


def test_apply_tenant_overrides_zusaetzliche_regeln():
    from app.core.policy_code_engine import (
        apply_tenant_overrides, TenantPolicyOverride,
        PolicyRegel, PolicyBedingung, PolicyBedingungsTyp, PolicyAktion,
    )
    base = _make_policy_set()
    extra_regel = PolicyRegel(
        regel_id="R-TENANT",
        bezeichnung="Tenant-spezifische Sonderregel",
        bedingungen=[PolicyBedingung(PolicyBedingungsTyp.GLEICH, "land", "AT")],
        aktion=PolicyAktion.WARNUNG,
        prioritaet=15,
    )
    override = TenantPolicyOverride(
        tenant_id="tenant-austria",
        policy_set_id="PS-TEST",
        zusaetzliche_regeln=[extra_regel],
    )
    merged = apply_tenant_overrides(base, override)
    ids = [r.regel_id for r in merged.regeln]
    assert "R-TENANT" in ids
    assert len(merged.regeln) == len(base.regeln) + 1


def test_apply_tenant_overrides_bezeichnung_enthaelt_tenant():
    from app.core.policy_code_engine import apply_tenant_overrides, TenantPolicyOverride
    base = _make_policy_set()
    override = TenantPolicyOverride(tenant_id="tenant-abc", policy_set_id="PS-TEST")
    merged = apply_tenant_overrides(base, override)
    assert "tenant-abc" in merged.bezeichnung


def test_apply_tenant_overrides_keine_mutation():
    from app.core.policy_code_engine import apply_tenant_overrides, TenantPolicyOverride
    base = _make_policy_set()
    original_count = len(base.regeln)
    override = TenantPolicyOverride(
        tenant_id="t",
        policy_set_id="PS-TEST",
        deaktivierte_regel_ids=["R-002"],
    )
    apply_tenant_overrides(base, override)
    assert len(base.regeln) == original_count  # Original unveraendert


# ---------------------------------------------------------------------------
# AP2: validate_policy_set()
# ---------------------------------------------------------------------------

def test_validate_policy_set_valid():
    from app.core.policy_code_engine import validate_policy_set
    ps = _make_policy_set()
    result = validate_policy_set(ps)
    assert result.valid is True


def test_validate_policy_set_leerer_prozess_key():
    from app.core.policy_code_engine import validate_policy_set, PolicySet, PolicyViolationCode
    ps = PolicySet(policy_set_id="PS-X", prozess_key="  ", bezeichnung="Test", regeln=[])
    result = validate_policy_set(ps)
    assert not result.valid
    assert any(v.code == PolicyViolationCode.PROZESS_KEY_LEER for v in result.violations)


def test_validate_policy_set_doppelte_regel_id():
    from app.core.policy_code_engine import (
        validate_policy_set, PolicySet, PolicyRegel,
        PolicyBedingung, PolicyBedingungsTyp, PolicyAktion, PolicyViolationCode,
    )
    doppel = PolicyRegel(
        regel_id="R-DOPPELT",
        bezeichnung="Doppelte Regel",
        bedingungen=[PolicyBedingung(PolicyBedingungsTyp.GLEICH, "x", 1)],
        aktion=PolicyAktion.WARNUNG,
    )
    ps = PolicySet(
        policy_set_id="PS-X", prozess_key="test", bezeichnung="Test",
        regeln=[doppel, doppel],
    )
    result = validate_policy_set(ps)
    assert not result.valid
    assert any(v.code == PolicyViolationCode.DOPPELTE_REGEL_ID for v in result.violations)


def test_validate_policy_set_konflikt_erlaubt_abgelehnt():
    from app.core.policy_code_engine import (
        validate_policy_set, PolicySet, PolicyRegel,
        PolicyBedingung, PolicyBedingungsTyp, PolicyAktion, PolicyViolationCode,
    )
    b = PolicyBedingung(PolicyBedingungsTyp.GLEICH, "status", "AKTIV")
    ps = PolicySet(
        policy_set_id="PS-K", prozess_key="test", bezeichnung="Konflikt",
        regeln=[
            PolicyRegel("R-E", "Erlaubt", [b], PolicyAktion.ERLAUBT),
            PolicyRegel("R-A", "Abgelehnt", [b], PolicyAktion.ABGELEHNT),
        ],
    )
    result = validate_policy_set(ps)
    assert not result.valid
    assert any(v.code == PolicyViolationCode.KONFLIKT_ERLAUBT_ABGELEHNT for v in result.violations)


def test_validate_policy_set_as_dict():
    from app.core.policy_code_engine import validate_policy_set
    ps = _make_policy_set()
    result = validate_policy_set(ps)
    d = result.as_dict()
    assert d["valid"] is True
    assert d["violation_count"] == 0
    assert d["schema_version"] == 1


def test_default_agrar_policy_sets_all_valid():
    from app.core.policy_code_engine import get_default_agrar_policy_sets, validate_policy_set
    for ps in get_default_agrar_policy_sets():
        result = validate_policy_set(ps)
        assert result.valid, f"PolicySet {ps.policy_set_id} ungueltig: {result.violations}"


# ---------------------------------------------------------------------------
# AP4: QueryContract + QueryRegistry
# ---------------------------------------------------------------------------

def test_query_registry_contract_count():
    from app.core.query_contracts import get_process_kernel_queries
    registry = get_process_kernel_queries()
    assert len(registry.contracts) >= 6


def test_query_registry_by_prozess_key():
    from app.core.query_contracts import get_process_kernel_queries
    registry = get_process_kernel_queries()
    agrar_contracts = registry.by_prozess_key("agrar_settlement")
    assert len(agrar_contracts) >= 2
    for c in agrar_contracts:
        assert c.prozess_key == "agrar_settlement"


def test_query_registry_by_query_id():
    from app.core.query_contracts import get_process_kernel_queries
    registry = get_process_kernel_queries()
    c = registry.by_query_id("agrar.settlement.list")
    assert c is not None
    assert c.prozess_key == "agrar_settlement"


def test_query_registry_by_query_id_not_found():
    from app.core.query_contracts import get_process_kernel_queries
    registry = get_process_kernel_queries()
    assert registry.by_query_id("nonexistent.query") is None


def test_query_contract_pflicht_felder():
    from app.core.query_contracts import get_process_kernel_queries
    registry = get_process_kernel_queries()
    c = registry.by_query_id("agrar.settlement.list")
    assert c is not None
    pflicht = c.pflicht_felder
    namen = [f.name for f in pflicht]
    assert "settlement_id" in namen
    assert "status" in namen


def test_query_contract_nullable_felder():
    from app.core.query_contracts import get_process_kernel_queries
    registry = get_process_kernel_queries()
    c = registry.by_query_id("agrar.settlement.list")
    assert c is not None
    nullable = [f.name for f in c.nullable_felder]
    assert "lieferant_name" in nullable


def test_query_contract_as_dict():
    from app.core.query_contracts import get_process_kernel_queries
    registry = get_process_kernel_queries()
    c = registry.by_query_id("agrar.settlement.list")
    d = c.as_dict()
    assert d["query_id"] == "agrar.settlement.list"
    assert d["feld_count"] >= 6
    assert d["schema_version"] == 1
    assert "pflicht_felder" in d
    assert "nullable_felder" in d


def test_query_registry_as_dict():
    from app.core.query_contracts import get_process_kernel_queries
    registry = get_process_kernel_queries()
    d = registry.as_dict()
    assert "contract_count" in d
    assert "prozess_keys" in d
    assert d["schema_version"] == 1


# ---------------------------------------------------------------------------
# AP5: validate_query_result()
# ---------------------------------------------------------------------------

def test_validate_query_result_valid():
    from app.core.query_contracts import get_process_kernel_queries, validate_query_result
    registry = get_process_kernel_queries()
    contract = registry.by_query_id("agrar.settlement.list")
    result_dict = {
        "settlement_id": "SET-2024-001",
        "lieferant_id": "LF-001",
        "lieferant_name": "Muster GmbH",
        "status": "OFFEN",
        "brutto_eur": "12500.00",
        "menge_tonnen": "28.4",
        "kampagne": "2024",
        "erstellt_am": "2024-09-01T08:00:00Z",
    }
    vr = validate_query_result(contract, result_dict)
    assert vr.valid is True
    assert vr.violations == []


def test_validate_query_result_nullable_field_none_ok():
    from app.core.query_contracts import get_process_kernel_queries, validate_query_result
    registry = get_process_kernel_queries()
    contract = registry.by_query_id("agrar.settlement.list")
    result_dict = {
        "settlement_id": "SET-001",
        "lieferant_id": "LF-001",
        "lieferant_name": None,   # nullable=True → OK
        "status": "OFFEN",
        "brutto_eur": "1000",
        "menge_tonnen": "10",
        "kampagne": None,          # nullable=True → OK
        "erstellt_am": "2024-01-01T00:00:00Z",
    }
    vr = validate_query_result(contract, result_dict)
    assert vr.valid is True


def test_validate_query_result_pflichtfeld_fehlt():
    from app.core.query_contracts import (
        get_process_kernel_queries, validate_query_result, QueryViolationCode
    )
    registry = get_process_kernel_queries()
    contract = registry.by_query_id("agrar.settlement.list")
    result_dict = {
        "lieferant_id": "LF-001",
        "status": "OFFEN",
        "brutto_eur": "1000",
        "menge_tonnen": "10",
        "erstellt_am": "2024-01-01T00:00:00Z",
        # settlement_id fehlt
    }
    vr = validate_query_result(contract, result_dict)
    assert not vr.valid
    codes = [v.code for v in vr.violations]
    assert QueryViolationCode.PFLICHTFELD_FEHLT in codes


def test_validate_query_result_nullable_verletzung():
    from app.core.query_contracts import (
        get_process_kernel_queries, validate_query_result, QueryViolationCode
    )
    registry = get_process_kernel_queries()
    contract = registry.by_query_id("agrar.settlement.list")
    result_dict = {
        "settlement_id": None,    # nullable=False → Verletzung
        "lieferant_id": "LF-001",
        "lieferant_name": None,
        "status": "OFFEN",
        "brutto_eur": "1000",
        "menge_tonnen": "10",
        "kampagne": None,
        "erstellt_am": "2024-01-01T00:00:00Z",
    }
    vr = validate_query_result(contract, result_dict)
    assert not vr.valid
    codes = [v.code for v in vr.violations]
    assert QueryViolationCode.NULLABLE_VERLETZUNG in codes


def test_validate_query_result_enum_wert_unbekannt():
    from app.core.query_contracts import (
        get_process_kernel_queries, validate_query_result, QueryViolationCode
    )
    registry = get_process_kernel_queries()
    contract = registry.by_query_id("agrar.settlement.list")
    result_dict = {
        "settlement_id": "SET-001",
        "lieferant_id": "LF-001",
        "lieferant_name": None,
        "status": "UNGUELTIG_STATUS",   # Nicht in enum_werte
        "brutto_eur": "1000",
        "menge_tonnen": "10",
        "kampagne": None,
        "erstellt_am": "2024-01-01T00:00:00Z",
    }
    vr = validate_query_result(contract, result_dict)
    assert not vr.valid
    codes = [v.code for v in vr.violations]
    assert QueryViolationCode.ENUM_WERT_UNBEKANNT in codes


def test_validate_query_result_strict_unbekanntes_feld():
    from app.core.query_contracts import (
        get_process_kernel_queries, validate_query_result, QueryViolationCode
    )
    registry = get_process_kernel_queries()
    contract = registry.by_query_id("agrar.settlement.list")
    result_dict = {
        "settlement_id": "SET-001",
        "lieferant_id": "LF-001",
        "lieferant_name": None,
        "status": "OFFEN",
        "brutto_eur": "1000",
        "menge_tonnen": "10",
        "kampagne": None,
        "erstellt_am": "2024-01-01T00:00:00Z",
        "undefiniertes_feld": "xyz",   # strict=True → Violation
    }
    vr = validate_query_result(contract, result_dict, strict=True)
    assert not vr.valid
    codes = [v.code for v in vr.violations]
    assert QueryViolationCode.UNERWARTETES_FELD in codes


def test_validate_query_result_strict_false_unbekanntes_feld_ok():
    from app.core.query_contracts import get_process_kernel_queries, validate_query_result
    registry = get_process_kernel_queries()
    contract = registry.by_query_id("agrar.settlement.list")
    result_dict = {
        "settlement_id": "SET-001",
        "lieferant_id": "LF-001",
        "lieferant_name": None,
        "status": "OFFEN",
        "brutto_eur": "1000",
        "menge_tonnen": "10",
        "kampagne": None,
        "erstellt_am": "2024-01-01T00:00:00Z",
        "extra_feld": "xyz",   # strict=False (default) → kein Fehler
    }
    vr = validate_query_result(contract, result_dict, strict=False)
    assert vr.valid is True


def test_validate_query_result_as_dict():
    from app.core.query_contracts import get_process_kernel_queries, validate_query_result
    registry = get_process_kernel_queries()
    contract = registry.by_query_id("agrar.settlement.list")
    result_dict = {
        "settlement_id": "SET-001",
        "lieferant_id": "LF-001",
        "lieferant_name": None,
        "status": "OFFEN",
        "brutto_eur": "1000",
        "menge_tonnen": "10",
        "kampagne": None,
        "erstellt_am": "2024-01-01T00:00:00Z",
    }
    vr = validate_query_result(contract, result_dict)
    d = vr.as_dict()
    assert d["valid"] is True
    assert d["schema_version"] == 1


# ---------------------------------------------------------------------------
# AP3/AP6: API-Endpoints
# ---------------------------------------------------------------------------

@pytest.fixture
def client():
    from app.main import app
    return TestClient(app)


def test_api_policy_rules_by_prozess_key(client):
    resp = client.get("/api/v1/process/policy-rules/agrar_settlement")
    assert resp.status_code == 200
    body = resp.json()
    assert body["prozess_key"] == "agrar_settlement"
    assert body["policy_set_count"] >= 1
    assert "policy_sets" in body


def test_api_policy_rules_not_found(client):
    resp = client.get("/api/v1/process/policy-rules/unbekannter_prozess")
    assert resp.status_code == 404


def test_api_policy_rules_wareneingang(client):
    resp = client.get("/api/v1/process/policy-rules/wareneingang")
    assert resp.status_code == 200
    body = resp.json()
    assert body["policy_set_count"] >= 1


def test_api_policy_rules_evaluate_abgelehnt(client):
    resp = client.post("/api/v1/process/policy-rules/evaluate", json={
        "prozess_key": "agrar_settlement",
        "kontext": {"brutto_eur": 75000, "netto_tonnen": 50, "lieferant_typ": "MITGLIED"},
    })
    assert resp.status_code == 200
    body = resp.json()
    # Grossbetrag-Regel greift: 75000 >= 50000 → ESKALATION (keine ABGELEHNT-Regel fuer dieses Feld)
    assert body["wirksame_aktion"] in ("ESKALATION", "ERLAUBT", "ABGELEHNT", "WARNUNG")
    assert "schema_version" in body


def test_api_policy_rules_evaluate_negativgewicht_abgelehnt(client):
    resp = client.post("/api/v1/process/policy-rules/evaluate", json={
        "prozess_key": "agrar_settlement",
        "kontext": {"netto_tonnen": -5, "brutto_eur": 1000},
    })
    assert resp.status_code == 200
    body = resp.json()
    assert body["wirksame_aktion"] == "ABGELEHNT"
    assert body["abgelehnt"] is True


def test_api_policy_rules_evaluate_fehlender_prozess_key(client):
    resp = client.post("/api/v1/process/policy-rules/evaluate", json={
        "kontext": {"betrag": 1000},
    })
    assert resp.status_code == 422


def test_api_query_registry_all(client):
    resp = client.get("/api/v1/process/query-registry")
    assert resp.status_code == 200
    body = resp.json()
    assert body["contract_count"] >= 6
    assert "agrar_settlement" in body["prozess_keys"]
    assert body["schema_version"] == 1


def test_api_query_registry_filtered(client):
    resp = client.get("/api/v1/process/query-registry?prozess_key=agrar_settlement")
    assert resp.status_code == 200
    body = resp.json()
    assert body["prozess_key_filter"] == "agrar_settlement"
    assert body["contract_count"] >= 2
    for c in body["contracts"]:
        assert c["prozess_key"] == "agrar_settlement"


def test_api_query_registry_empty_filter(client):
    resp = client.get("/api/v1/process/query-registry?prozess_key=nonexistent")
    assert resp.status_code == 200
    body = resp.json()
    assert body["contract_count"] == 0
