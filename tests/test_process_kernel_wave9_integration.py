"""Wave 9 Paket A — Integration Tests: EDI, API-Gateway-Manifest, Zertifikate."""
from __future__ import annotations

import pytest
from datetime import date, datetime
import uuid

from app.core.edi_integration import (
    EdiNachricht,
    EdiNachrichtenTyp,
    EdiPartner,
    EdiNachrichtStore,
    EdiVerarbeitungsStatus,
    SepaZahlungsAuftrag,
    parse_edi_nachricht,
)
from app.core.api_gateway_manifest import (
    ApiAccessDecision,
    ApiGatewayRegistry,
    ApiPartnerManifest,
    ApiPartnerTyp,
    ApiScope,
)
from app.core.zertifikate import (
    Zertifikat,
    ZertifikatStatus,
    ZertifikatStore,
    ZertifikatTyp,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_edi_nachricht(
    status: EdiVerarbeitungsStatus = EdiVerarbeitungsStatus.EMPFANGEN,
    empfaenger_gln: str = "4012345000016",
) -> EdiNachricht:
    return EdiNachricht(
        nachricht_id=str(uuid.uuid4()),
        typ=EdiNachrichtenTyp.ORDERS_D97A,
        absender_gln="4099999000001",
        empfaenger_gln=empfaenger_gln,
        interchange_control_ref="ICR-001",
        empfangen_am=datetime.utcnow(),
        payload_raw="UNB+UNOA:3+4099999000001:14+4012345000016:14+230101:1200+1",
        status=status,
    )


def _make_partner_manifest(
    scopes: list[ApiScope] | None = None,
    aktiv: bool = True,
    tenant_id: str = "tenant-1",
    rate_limit_rpm: int = 60,
    ip_whitelist: list[str] | None = None,
) -> ApiPartnerManifest:
    return ApiPartnerManifest(
        partner_id=str(uuid.uuid4()),
        name="Test-Partner",
        typ=ApiPartnerTyp.SUPPLIER,
        tenant_id=tenant_id,
        erlaubte_scopes=scopes or [ApiScope.READ_CONTRACTS],
        rate_limit_rpm=rate_limit_rpm,
        aktiv=aktiv,
        ip_whitelist=ip_whitelist or [],
    )


def _make_zertifikat(
    gueltig_von: date = date(2025, 1, 1),
    gueltig_bis: date = date(2026, 12, 31),
    status: ZertifikatStatus = ZertifikatStatus.GUELTIG,
    tenant_id: str = "tenant-1",
) -> Zertifikat:
    return Zertifikat(
        zertifikat_id=str(uuid.uuid4()),
        tenant_id=tenant_id,
        typ=ZertifikatTyp.QS_GAP,
        zertifizierungsstelle="DQS GmbH",
        gueltig_von=gueltig_von,
        gueltig_bis=gueltig_bis,
        status=status,
    )


# ---------------------------------------------------------------------------
# EdiNachricht + EdiPartner Tests (min. 8)
# ---------------------------------------------------------------------------

def test_edi_partner_unterstuetzt_typ():
    partner = EdiPartner(
        partner_id="p-001",
        gln="4099999000001",
        name="Lieferant A",
        tenant_id="tenant-1",
        aktive_nachrichtentypen=[EdiNachrichtenTyp.ORDERS_D97A, EdiNachrichtenTyp.INVOIC_D01B],
    )
    assert partner.unterstuetzt(EdiNachrichtenTyp.ORDERS_D97A) is True


def test_edi_partner_unterstuetzt_nicht():
    partner = EdiPartner(
        partner_id="p-002",
        gln="4099999000002",
        name="Lieferant B",
        tenant_id="tenant-1",
        aktive_nachrichtentypen=[EdiNachrichtenTyp.ORDERS_D97A],
    )
    assert partner.unterstuetzt(EdiNachrichtenTyp.PRICAT_D96A) is False


def test_edi_nachricht_markiere_verarbeitet():
    n = _make_edi_nachricht()
    doc_id = str(uuid.uuid4())
    result = n.markiere_verarbeitet(doc_id)
    assert result.status == EdiVerarbeitungsStatus.VERARBEITET
    assert result.dokument_id == doc_id
    assert result.verarbeitet_am is not None


def test_edi_nachricht_markiere_fehler():
    n = _make_edi_nachricht()
    result = n.markiere_fehler("Unbekannter Artikel in Position 3")
    assert result.status == EdiVerarbeitungsStatus.FEHLER
    assert result.fehler_beschreibung == "Unbekannter Artikel in Position 3"


def test_parse_edi_leer():
    ergebnis = parse_edi_nachricht("", EdiNachrichtenTyp.ORDERS_D97A)
    assert ergebnis.success is False
    assert ergebnis.fehler_beschreibung is not None


def test_parse_edi_kein_unb_header():
    # Zu lang genug, aber kein UNB-Header
    raw = "ORDERS+BEGIN+SEGMENT+WITHOUT+PROPER+EDIFACT+HEADER+HERE"
    ergebnis = parse_edi_nachricht(raw, EdiNachrichtenTyp.ORDERS_D97A)
    assert ergebnis.success is False
    assert "UNB" in ergebnis.fehler_beschreibung


def test_parse_edi_mit_unb_header():
    raw = "UNB+UNOA:3+4099999000001:14+4012345000016:14+230101:1200+1+UNH+1+ORDERS:D:97A:UN:EAN008"
    ergebnis = parse_edi_nachricht(raw, EdiNachrichtenTyp.ORDERS_D97A)
    assert ergebnis.success is True
    assert ergebnis.dokument_id is not None


def test_edi_store_offene_nachrichten():
    store = EdiNachrichtStore()
    gln = "4012345000016"
    # Eine offene, eine verarbeitete
    n_offen = _make_edi_nachricht(status=EdiVerarbeitungsStatus.EMPFANGEN, empfaenger_gln=gln)
    n_verarbeitet = EdiNachricht(
        nachricht_id=str(uuid.uuid4()),
        typ=EdiNachrichtenTyp.INVOIC_D01B,
        absender_gln="4099999000001",
        empfaenger_gln=gln,
        interchange_control_ref="ICR-002",
        empfangen_am=datetime.utcnow(),
        payload_raw="UNB+UNOA:3",
        status=EdiVerarbeitungsStatus.VERARBEITET,
    )
    store.add_nachricht(n_offen)
    store.add_nachricht(n_verarbeitet)
    offene = store.offene_nachrichten(gln)
    assert len(offene) == 1
    assert offene[0].nachricht_id == n_offen.nachricht_id


# ---------------------------------------------------------------------------
# SepaZahlungsAuftrag Tests (min. 3)
# ---------------------------------------------------------------------------

def test_sepa_ist_valide_true():
    auftrag = SepaZahlungsAuftrag(
        auftrag_id=str(uuid.uuid4()),
        tenant_id="tenant-1",
        glaeubiger_iban="DE89370400440532013000",
        glaeubiger_bic="COBADEFFXXX",
        schuldner_iban="DE02200505501015871393",
        schuldner_name="Max Mustermann",
        betrag_eur=1234.56,
        verwendungszweck="Rechnung 2026-001",
        faelligkeitsdatum=date(2026, 4, 1),
    )
    assert auftrag.ist_valide() is True


def test_sepa_ist_valide_false_betrag():
    auftrag = SepaZahlungsAuftrag(
        auftrag_id=str(uuid.uuid4()),
        tenant_id="tenant-1",
        glaeubiger_iban="DE89370400440532013000",
        glaeubiger_bic="COBADEFFXXX",
        schuldner_iban="DE02200505501015871393",
        schuldner_name="Max Mustermann",
        betrag_eur=0.0,
        verwendungszweck="Rechnung 2026-002",
        faelligkeitsdatum=date(2026, 4, 1),
    )
    assert auftrag.ist_valide() is False


def test_sepa_schema_version():
    auftrag = SepaZahlungsAuftrag(
        auftrag_id=str(uuid.uuid4()),
        tenant_id="tenant-1",
        glaeubiger_iban="DE89370400440532013000",
        glaeubiger_bic="COBADEFFXXX",
        schuldner_iban="DE02200505501015871393",
        schuldner_name="Max Mustermann",
        betrag_eur=100.0,
        verwendungszweck="Test",
        faelligkeitsdatum=date(2026, 4, 1),
    )
    assert auftrag.schema_version == 1


# ---------------------------------------------------------------------------
# ApiGatewayRegistry Tests (min. 8)
# ---------------------------------------------------------------------------

def test_gateway_allowed():
    registry = ApiGatewayRegistry()
    p = _make_partner_manifest(scopes=[ApiScope.READ_CONTRACTS], aktiv=True, tenant_id="t1")
    registry.add_partner(p)
    decision = registry.pruefe_api_zugriff(p.partner_id, ApiScope.READ_CONTRACTS, "t1")
    assert decision == ApiAccessDecision.ALLOWED


def test_gateway_denied_kein_scope():
    registry = ApiGatewayRegistry()
    p = _make_partner_manifest(scopes=[ApiScope.READ_CONTRACTS], aktiv=True, tenant_id="t1")
    registry.add_partner(p)
    decision = registry.pruefe_api_zugriff(p.partner_id, ApiScope.WRITE_INVOICES, "t1")
    assert decision == ApiAccessDecision.DENIED


def test_gateway_denied_inaktiv():
    registry = ApiGatewayRegistry()
    p = _make_partner_manifest(scopes=[ApiScope.READ_CONTRACTS], aktiv=False, tenant_id="t1")
    registry.add_partner(p)
    decision = registry.pruefe_api_zugriff(p.partner_id, ApiScope.READ_CONTRACTS, "t1")
    assert decision == ApiAccessDecision.PARTNER_INAKTIV


def test_gateway_denied_falsche_tenant():
    registry = ApiGatewayRegistry()
    p = _make_partner_manifest(scopes=[ApiScope.READ_CONTRACTS], aktiv=True, tenant_id="t1")
    registry.add_partner(p)
    decision = registry.pruefe_api_zugriff(p.partner_id, ApiScope.READ_CONTRACTS, "t2")
    assert decision == ApiAccessDecision.DENIED


def test_gateway_rate_limited():
    registry = ApiGatewayRegistry()
    p = _make_partner_manifest(
        scopes=[ApiScope.READ_CONTRACTS], aktiv=True, tenant_id="t1", rate_limit_rpm=2
    )
    registry.add_partner(p)
    # Consume all slots
    registry.pruefe_api_zugriff(p.partner_id, ApiScope.READ_CONTRACTS, "t1")
    registry.pruefe_api_zugriff(p.partner_id, ApiScope.READ_CONTRACTS, "t1")
    # Third request should be rate-limited
    decision = registry.pruefe_api_zugriff(p.partner_id, ApiScope.READ_CONTRACTS, "t1")
    assert decision == ApiAccessDecision.RATE_LIMITED


def test_gateway_reset_rate_limits():
    registry = ApiGatewayRegistry()
    p = _make_partner_manifest(
        scopes=[ApiScope.READ_CONTRACTS], aktiv=True, tenant_id="t1", rate_limit_rpm=1
    )
    registry.add_partner(p)
    # Consume the single slot
    registry.pruefe_api_zugriff(p.partner_id, ApiScope.READ_CONTRACTS, "t1")
    # Rate limited
    assert registry.pruefe_api_zugriff(p.partner_id, ApiScope.READ_CONTRACTS, "t1") == ApiAccessDecision.RATE_LIMITED
    # Reset
    registry.reset_rate_limits()
    # Now allowed again
    decision = registry.pruefe_api_zugriff(p.partner_id, ApiScope.READ_CONTRACTS, "t1")
    assert decision == ApiAccessDecision.ALLOWED


def test_gateway_ip_whitelist_erlaubt():
    registry = ApiGatewayRegistry()
    p = _make_partner_manifest(
        scopes=[ApiScope.READ_CONTRACTS],
        aktiv=True,
        tenant_id="t1",
        ip_whitelist=["10.0.0.1", "10.0.0.2"],
    )
    registry.add_partner(p)
    decision = registry.pruefe_api_zugriff(p.partner_id, ApiScope.READ_CONTRACTS, "t1", client_ip="10.0.0.1")
    assert decision == ApiAccessDecision.ALLOWED


def test_gateway_ip_whitelist_denied():
    registry = ApiGatewayRegistry()
    p = _make_partner_manifest(
        scopes=[ApiScope.READ_CONTRACTS],
        aktiv=True,
        tenant_id="t1",
        ip_whitelist=["10.0.0.1"],
    )
    registry.add_partner(p)
    decision = registry.pruefe_api_zugriff(p.partner_id, ApiScope.READ_CONTRACTS, "t1", client_ip="192.168.1.100")
    assert decision == ApiAccessDecision.DENIED


# ---------------------------------------------------------------------------
# Zertifikat Tests (min. 7)
# ---------------------------------------------------------------------------

def test_zertifikat_ist_gueltig():
    z = _make_zertifikat(
        gueltig_von=date(2025, 1, 1),
        gueltig_bis=date(2027, 12, 31),
        status=ZertifikatStatus.GUELTIG,
    )
    assert z.ist_gueltig(date(2026, 3, 12)) is True


def test_zertifikat_ist_abgelaufen():
    z = _make_zertifikat(
        gueltig_von=date(2024, 1, 1),
        gueltig_bis=date(2025, 6, 30),
        status=ZertifikatStatus.GUELTIG,
    )
    # After the expiry date, ist_gueltig() returns False even if status field is GUELTIG
    assert z.ist_gueltig(date(2026, 1, 1)) is False


def test_zertifikat_tage_bis_ablauf_positiv():
    z = _make_zertifikat(
        gueltig_von=date(2025, 1, 1),
        gueltig_bis=date(2026, 12, 31),
    )
    tage = z.tage_bis_ablauf(date(2026, 3, 12))
    assert tage > 0


def test_zertifikat_tage_bis_ablauf_negativ():
    z = _make_zertifikat(
        gueltig_von=date(2024, 1, 1),
        gueltig_bis=date(2025, 1, 1),
    )
    tage = z.tage_bis_ablauf(date(2026, 1, 1))
    assert tage < 0


def test_zertifikat_store_ablaufende():
    store = ZertifikatStore()
    heute = date(2026, 3, 12)
    # Zertifikat läuft in 15 Tagen ab
    z = _make_zertifikat(
        gueltig_von=date(2025, 1, 1),
        gueltig_bis=date(2026, 3, 27),  # 15 Tage nach heute
        status=ZertifikatStatus.GUELTIG,
    )
    store.add(z)
    ablaufende = store.ablaufende_zertifikate(tage_vorwarnung=30, datum=heute)
    assert len(ablaufende) == 1
    assert ablaufende[0].zertifikat_id == z.zertifikat_id


def test_zertifikat_store_ablaufende_nicht():
    store = ZertifikatStore()
    heute = date(2026, 3, 12)
    # Zertifikat läuft in 60 Tagen ab — soll NICHT in ablaufende(30) erscheinen
    z = _make_zertifikat(
        gueltig_von=date(2025, 1, 1),
        gueltig_bis=date(2026, 5, 11),  # 60 Tage nach heute
        status=ZertifikatStatus.GUELTIG,
    )
    store.add(z)
    ablaufende = store.ablaufende_zertifikate(tage_vorwarnung=30, datum=heute)
    assert len(ablaufende) == 0


def test_zertifikat_schema_version():
    z = _make_zertifikat()
    assert z.schema_version == 1


# ---------------------------------------------------------------------------
# API Tests (min. 2)
# ---------------------------------------------------------------------------

def test_api_zertifikat_post():
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app, raise_server_exceptions=True)
    payload = {
        "art": "qs_gap",
        "standard": "QS",
        "nummer": "QS-2025-9999",
        "gueltig_bis": "2026-12-31",
    }
    resp = client.post("/api/v1/zertifikate", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert "id" in data
    assert data["nummer"] == "QS-2025-9999"


def test_api_edi_nachricht_mit_unb():
    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app, raise_server_exceptions=True)
    payload = {
        "typ": "ORDERS_D97A",
        "absender_gln": "4099999000001",
        "empfaenger_gln": "4012345000016",
        "interchange_control_ref": "ICR-TEST-001",
        "payload_raw": "UNB+UNOA:3+4099999000001:14+4012345000016:14+230101:1200+1+UNH+1+ORDERS:D:97A:UN:EAN008",
    }
    resp = client.post("/api/v1/edi/nachrichten", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["success"] is True
    assert "nachricht_id" in data
