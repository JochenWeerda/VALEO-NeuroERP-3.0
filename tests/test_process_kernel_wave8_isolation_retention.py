"""Wave 8 Paket A - AP2 Tenant-Isolation-Guard + AP5 GoBD-Retention Tests"""
from __future__ import annotations

import pytest
from datetime import date, datetime
import uuid

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.core.tenant_isolation_guard import (
    IsolationDecision,
    IsolationAuditLog,
    CrossTenantAccessAttempt,
    VerbundSharingPolicy,
    TenantIsolationGuard,
    RessourcentypSharingPolicy,
)
from app.core.gobd_retention import (
    RetentionKlasse,
    RetentionEreignis,
    RetentionRegel,
    RetentionPruefung,
    build_default_retention_regeln,
)


# ---------------------------------------------------------------------------
# AP2: TenantIsolationGuard Tests (min. 8)
# ---------------------------------------------------------------------------

def test_guard_gleicher_tenant_allowed():
    """Gleicher Tenant -> ALLOWED ohne Audit-Log-Eintrag."""
    guard = TenantIsolationGuard()
    decision = guard.check("tenant-a", "tenant-a", "ap_invoice")
    assert decision == IsolationDecision.ALLOWED
    assert len(guard.audit_log.entries) == 0


def test_guard_fremder_tenant_denied():
    """Kein Verbund konfiguriert -> DENIED."""
    guard = TenantIsolationGuard()
    decision = guard.check("tenant-a", "tenant-b", "ap_invoice")
    assert decision == IsolationDecision.DENIED


def test_guard_verbund_feldbuch_erlaubt():
    """Verbundmitglieder mit feldbuch_schlag -> VERBUND_ALLOWED."""
    policy = VerbundSharingPolicy(
        verbund_id="verbund-1",
        mitglieder_tenant_ids=["tenant-a", "tenant-b"],
    )
    guard = TenantIsolationGuard(verbund_policies=[policy])
    decision = guard.check("tenant-a", "tenant-b", RessourcentypSharingPolicy.FELDBUCH_SCHLAG.value)
    assert decision == IsolationDecision.VERBUND_ALLOWED


def test_guard_verbund_ap_invoice_denied():
    """Verbundmitglieder, aber ap_invoice niemals erlaubt -> DENIED."""
    policy = VerbundSharingPolicy(
        verbund_id="verbund-1",
        mitglieder_tenant_ids=["tenant-a", "tenant-b"],
    )
    guard = TenantIsolationGuard(verbund_policies=[policy])
    decision = guard.check("tenant-a", "tenant-b", RessourcentypSharingPolicy.AP_INVOICE.value)
    assert decision == IsolationDecision.DENIED


def test_guard_audit_log_denied_protokolliert():
    """DENIED-Zugriff erzeugt Eintrag im Audit-Log."""
    guard = TenantIsolationGuard()
    guard.check("tenant-a", "tenant-b", "payment_run")
    assert len(guard.audit_log.entries) == 1
    entry = guard.audit_log.entries[0]
    assert entry.decision == IsolationDecision.DENIED
    assert entry.requesting_tenant == "tenant-a"
    assert entry.resource_tenant == "tenant-b"
    assert entry.resource_type == "payment_run"


def test_guard_audit_log_verbund_protokolliert():
    """VERBUND_ALLOWED-Zugriff wird ebenfalls protokolliert."""
    policy = VerbundSharingPolicy(
        verbund_id="verbund-1",
        mitglieder_tenant_ids=["tenant-a", "tenant-b"],
    )
    guard = TenantIsolationGuard(verbund_policies=[policy])
    guard.check("tenant-a", "tenant-b", "feldbuch_schlag")
    assert len(guard.audit_log.entries) == 1
    assert guard.audit_log.entries[0].decision == IsolationDecision.VERBUND_ALLOWED


def test_guard_denied_count():
    """denied_count() zaehlt nur DENIED-Eintraege."""
    guard = TenantIsolationGuard()
    guard.check("tenant-a", "tenant-b", "ap_invoice")
    guard.check("tenant-a", "tenant-b", "journal_entry")
    assert guard.audit_log.denied_count() == 2
    assert len(guard.audit_log.entries) == 2


def test_guard_audit_log_append_only():
    """Bestehende Eintraege bleiben unveraenderlich (append-only)."""
    guard = TenantIsolationGuard()
    guard.check("tenant-a", "tenant-b", "ap_invoice")
    first_attempt_id = guard.audit_log.entries[0].attempt_id
    guard.check("tenant-a", "tenant-b", "journal_entry")
    assert guard.audit_log.entries[0].attempt_id == first_attempt_id
    assert len(guard.audit_log.entries) == 2


# ---------------------------------------------------------------------------
# Additional IsolationAuditLog and VerbundSharingPolicy Tests
# ---------------------------------------------------------------------------

def test_verbund_sharing_policy_ist_mitglied():
    policy = VerbundSharingPolicy(
        verbund_id="verbund-x",
        mitglieder_tenant_ids=["tenant-a", "tenant-b"],
    )
    assert policy.ist_mitglied("tenant-a") is True
    assert policy.ist_mitglied("tenant-c") is False


def test_verbund_sharing_policy_ressourcentyp_erlaubt():
    policy = VerbundSharingPolicy(
        verbund_id="verbund-x",
        mitglieder_tenant_ids=["tenant-a"],
    )
    assert policy.ressourcentyp_erlaubt("feldbuch_schlag") is True
    assert policy.ressourcentyp_erlaubt("qualitaetsprotokoll") is True
    assert policy.ressourcentyp_erlaubt("ap_invoice") is False
    assert policy.ressourcentyp_erlaubt("payment_run") is False
    assert policy.ressourcentyp_erlaubt("journal_entry") is False


def test_isolation_audit_log_denied_entries():
    """denied_entries() liefert nur DENIED-Eintraege."""
    log = IsolationAuditLog()
    denied_attempt = CrossTenantAccessAttempt(
        attempt_id=str(uuid.uuid4()),
        requesting_tenant="a",
        resource_tenant="b",
        resource_type="ap_invoice",
        decision=IsolationDecision.DENIED,
        timestamp=datetime.utcnow(),
    )
    verbund_attempt = CrossTenantAccessAttempt(
        attempt_id=str(uuid.uuid4()),
        requesting_tenant="a",
        resource_tenant="b",
        resource_type="feldbuch_schlag",
        decision=IsolationDecision.VERBUND_ALLOWED,
        timestamp=datetime.utcnow(),
    )
    log.append(denied_attempt)
    log.append(verbund_attempt)
    assert log.denied_count() == 1
    assert len(log.denied_entries()) == 1
    assert log.denied_entries()[0].decision == IsolationDecision.DENIED


def test_guard_schema_version():
    guard = TenantIsolationGuard()
    assert guard.schema_version == 1


def test_cross_tenant_access_attempt_schema_version():
    attempt = CrossTenantAccessAttempt(
        attempt_id=str(uuid.uuid4()),
        requesting_tenant="a",
        resource_tenant="b",
        resource_type="ap_invoice",
        decision=IsolationDecision.DENIED,
        timestamp=datetime.utcnow(),
    )
    assert attempt.schema_version == 1


def test_verbund_sharing_policy_schema_version():
    policy = VerbundSharingPolicy(
        verbund_id="v1",
        mitglieder_tenant_ids=["t1"],
    )
    assert policy.schema_version == 1


# ---------------------------------------------------------------------------
# AP5: GoBD-Retention Tests (min. 7)
# ---------------------------------------------------------------------------

def test_retention_regeln_mindestens_8():
    """build_default_retention_regeln() liefert mindestens 8 Eintraege."""
    regeln = build_default_retention_regeln()
    assert len(regeln) >= 8


def test_retention_aufbewahrungsjahre_10j():
    """STANDARD_10J -> aufbewahrungsjahre == 10."""
    regel = RetentionRegel(
        dokumenttyp="ap_invoice",
        klasse=RetentionKlasse.STANDARD_10J,
        beginnt_mit=RetentionEreignis.JAHRESABSCHLUSS,
        beschreibung="Test",
    )
    assert regel.aufbewahrungsjahre == 10


def test_retention_aufbewahrungsjahre_6j():
    """KUERZER_6J -> aufbewahrungsjahre == 6."""
    regel = RetentionRegel(
        dokumenttyp="reklamation",
        klasse=RetentionKlasse.KUERZER_6J,
        beginnt_mit=RetentionEreignis.VERTRAGSENDE,
        beschreibung="Test",
    )
    assert regel.aufbewahrungsjahre == 6


def test_retention_darf_nicht_geloescht():
    """Innerhalb der Aufbewahrungsfrist -> darf_geloescht_werden() == False."""
    pruefung = RetentionPruefung(
        pruefung_id=str(uuid.uuid4()),
        dokumenttyp="ap_invoice",
        dokumentdatum=date(2020, 1, 1),
        ereignisdatum=date(2020, 12, 31),
        aufbewahrungsjahre=10,
    )
    heute = date(2025, 6, 1)  # innerhalb der 10-Jahres-Frist (endet 2030-12-31)
    assert pruefung.darf_geloescht_werden(heute) is False


def test_retention_darf_geloescht():
    """Frist abgelaufen -> darf_geloescht_werden() == True."""
    pruefung = RetentionPruefung(
        pruefung_id=str(uuid.uuid4()),
        dokumenttyp="ap_invoice",
        dokumentdatum=date(2010, 1, 1),
        ereignisdatum=date(2010, 12, 31),
        aufbewahrungsjahre=10,
    )
    heute = date(2025, 1, 1)  # nach Ablauf (endet 2020-12-31)
    assert pruefung.darf_geloescht_werden(heute) is True


def test_retention_verbleibende_tage_positiv():
    """Innerhalb der Frist -> verbleibende_tage() > 0."""
    pruefung = RetentionPruefung(
        pruefung_id=str(uuid.uuid4()),
        dokumenttyp="journal_entry",
        dokumentdatum=date(2022, 1, 1),
        ereignisdatum=date(2022, 12, 31),
        aufbewahrungsjahre=10,
    )
    heute = date(2025, 1, 1)
    assert pruefung.verbleibende_tage(heute) > 0


def test_retention_verbleibende_tage_null():
    """Frist abgelaufen -> verbleibende_tage() == 0 (nie negativ)."""
    pruefung = RetentionPruefung(
        pruefung_id=str(uuid.uuid4()),
        dokumenttyp="reklamation",
        dokumentdatum=date(2010, 1, 1),
        ereignisdatum=date(2010, 12, 31),
        aufbewahrungsjahre=6,
    )
    heute = date(2025, 1, 1)  # weit nach Ablauf der 6-Jahres-Frist (endet 2016-12-31)
    assert pruefung.verbleibende_tage(heute) == 0


def test_retention_dokumenttyp_ap_invoice_vorhanden():
    """ap_invoice muss in den Default-Retention-Regeln enthalten sein."""
    regeln = build_default_retention_regeln()
    typen = [r.dokumenttyp for r in regeln]
    assert "ap_invoice" in typen


def test_retention_aufzubewahren_bis_korrekt():
    """aufzubewahren_bis = ereignisdatum + aufbewahrungsjahre Jahre."""
    pruefung = RetentionPruefung(
        pruefung_id=str(uuid.uuid4()),
        dokumenttyp="payment_run",
        dokumentdatum=date(2015, 3, 15),
        ereignisdatum=date(2015, 3, 15),
        aufbewahrungsjahre=10,
    )
    assert pruefung.aufzubewahren_bis == date(2025, 3, 15)


def test_retention_regel_schema_version():
    """RetentionRegel hat schema_version == 1."""
    regel = RetentionRegel(
        dokumenttyp="test",
        klasse=RetentionKlasse.STANDARD_10J,
        beginnt_mit=RetentionEreignis.ERSTELLUNGSDATUM,
        beschreibung="Test",
    )
    assert regel.schema_version == 1


def test_retention_pruefung_schema_version():
    """RetentionPruefung hat schema_version == 1."""
    pruefung = RetentionPruefung(
        pruefung_id=str(uuid.uuid4()),
        dokumenttyp="test",
        dokumentdatum=date(2020, 1, 1),
        ereignisdatum=date(2020, 12, 31),
        aufbewahrungsjahre=10,
    )
    assert pruefung.schema_version == 1


def test_retention_alle_dokumenttypen_haben_beschreibung():
    """Alle Default-Regeln haben eine nicht-leere Beschreibung."""
    regeln = build_default_retention_regeln()
    for r in regeln:
        assert r.beschreibung, f"Dokumenttyp {r.dokumenttyp!r} hat keine Beschreibung"


def test_retention_psm_protokoll_vorhanden():
    """psm_protokoll muss in den Default-Regeln enthalten sein."""
    regeln = build_default_retention_regeln()
    typen = [r.dokumenttyp for r in regeln]
    assert "psm_protokoll" in typen


def test_retention_reklamation_6_jahre():
    """Reklamation hat 6-Jahres-Frist."""
    regeln = build_default_retention_regeln()
    reklamation = next(r for r in regeln if r.dokumenttyp == "reklamation")
    assert reklamation.aufbewahrungsjahre == 6
    assert reklamation.klasse == RetentionKlasse.KUERZER_6J


# ---------------------------------------------------------------------------
# API Tests (min. 2)
# ---------------------------------------------------------------------------

def _make_test_app() -> FastAPI:
    """Erstellt eine isolierte Test-App fuer Wave-8-AP2/AP5-Endpoints."""
    from fastapi import APIRouter, Query

    test_router = APIRouter(prefix="/reporting", tags=["reporting-test"])
    _guard = TenantIsolationGuard()

    @test_router.get("/retention-regeln")
    def get_retention_regeln():
        regeln = build_default_retention_regeln()
        return {"regeln": regeln, "count": len(regeln), "schema_version": 1}

    @test_router.get("/isolation/check")
    def check_isolation(
        requesting_tenant: str = Query(...),
        resource_tenant: str = Query(...),
        resource_type: str = Query(...),
    ):
        decision = _guard.check(requesting_tenant, resource_tenant, resource_type)
        return {
            "requesting_tenant": requesting_tenant,
            "resource_tenant": resource_tenant,
            "resource_type": resource_type,
            "decision": decision,
            "schema_version": 1,
        }

    app = FastAPI()
    app.include_router(test_router)
    return app


@pytest.fixture()
def api_client():
    app = _make_test_app()
    with TestClient(app) as client:
        yield client


def test_api_retention_regeln_get(api_client: TestClient):
    """GET /reporting/retention-regeln gibt count >= 8 zurueck."""
    response = api_client.get("/reporting/retention-regeln")
    assert response.status_code == 200
    data = response.json()
    assert data["count"] >= 8
    assert data["schema_version"] == 1
    assert len(data["regeln"]) >= 8


def test_api_isolation_check(api_client: TestClient):
    """GET /reporting/isolation/check gibt decision zurueck."""
    response = api_client.get(
        "/reporting/isolation/check",
        params={
            "requesting_tenant": "tenant-a",
            "resource_tenant": "tenant-b",
            "resource_type": "ap_invoice",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == IsolationDecision.DENIED
    assert data["requesting_tenant"] == "tenant-a"
    assert data["schema_version"] == 1
