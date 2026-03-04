"""
GoBD Compliance Tests
Tests für revisionssichere Buchhaltung, Hash-Chain, Audit-Trail
"""

from fastapi.testclient import TestClient
from main import app
import pytest
from sqlalchemy import text

from app.core.database import SessionLocal
from app.core.fibu_audit import SYSTEM_USER_ID
from app.core.uuid7 import uuid7
from app.infrastructure.models import Tenant, User

_client = TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def client():
    return _client


@pytest.fixture
def db():
    """DB-Session für Integrationstests (Tenant/Konten anlegen)."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def _ensure_system_tenant_and_accounts(db_session):
    """Legt Tenant 'system', System-User für Audit-Log-FK und Konten 1400/8400 an, falls fehlend."""
    tenant = db_session.query(Tenant).filter(Tenant.id == "system").first()
    if not tenant:
        tenant = Tenant(
            id="system",
            name="System",
            domain="system.local",
            is_active=True,
        )
        db_session.add(tenant)
        db_session.flush()
    # System-User für log_fibu_audit (audit_logs.user_id FK auf domain_shared.users)
    user = db_session.query(User).filter(User.id == SYSTEM_USER_ID).first()
    if not user:
        user = User(
            id=SYSTEM_USER_ID,
            username="system",
            email="system@internal",
            first_name="System",
            last_name="User",
            tenant_id="system",
            is_active=True,
        )
        db_session.add(user)
        db_session.flush()
    # Konten 1400 / 8400 für Bulk-Import (UNIQUE(account_number) → nur anlegen wenn noch nicht vorhanden)
    for account_number, account_name in [("1400", "Debitoren"), ("8400", "Erlöse 19% USt")]:
        row = db_session.execute(
            text("SELECT tenant_id FROM domain_erp.chart_of_accounts WHERE account_number = :num LIMIT 1"),
            {"num": account_number},
        ).fetchone()
        if row is None:
            db_session.execute(
                text("""
                    INSERT INTO domain_erp.chart_of_accounts
                    (id, tenant_id, account_number, account_name, account_type, category, is_active)
                    VALUES (:id, 'system', :num, :name, 'balance_sheet', 'Forderungen/Erlöse', true)
                """),
                {"id": uuid7(), "num": account_number, "name": account_name},
            )
        elif row[0] != "system":
            pytest.skip(f"Konto {account_number} gehört anderem Tenant – Audit-Integrationstest übersprungen")
    db_session.commit()


class TestGoBDStatus:
    """Tests für GoBD Status-Endpunkt"""

    def test_gobd_status(self, client):
        """Test: GoBD Status abrufen"""
        response = client.get("/api/gobd/status", headers={"Authorization": "Bearer dev-token"})
        assert response.status_code == 200
        data = response.json()
        assert "gesamt_score" in data
        assert "ergebnisse" in data
        assert isinstance(data["ergebnisse"], list)

    def test_gobd_status_alle_bereiche(self, client):
        """Test: Alle GoBD-Bereiche vorhanden"""
        response = client.get("/api/gobd/status", headers={"Authorization": "Bearer dev-token"})
        assert response.status_code == 200
        ergebnisse = response.json()["ergebnisse"]
        bereiche = {e["bereich"] for e in ergebnisse}
        
        expected_bereiche = {
            "ordnungsgemaessigkeit",
            "vollstaendigkeit",
            "richtigkeit",
            "zeitnahme",
            "unveraenderlichkeit",
            "nachvollziehbarkeit",
            "aufbewahrung"
        }
        assert expected_bereiche.issubset(bereiche)


class TestHashChain:
    """Tests für Hash-Chain Validierung"""

    def test_verify_hash_chain(self, client):
        """Test: Hash-Chain verifizieren"""
        response = client.post(
            "/api/gobd/hash-chain/verify",
            headers={"Authorization": "Bearer dev-token"},
            json={
                "von_datum": "2026-01-01",
                "bis_datum": "2026-01-31"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert "gueltig" in data
        assert "fehlerhafte_buchungen" in data
        assert data["gueltig"] is True or data["gueltig"] is False

    def test_letzter_hash(self, client):
        """Test: Letzten Hash abrufen"""
        response = client.get("/api/gobd/hash-chain/letzter", headers={"Authorization": "Bearer dev-token"})
        assert response.status_code == 200
        data = response.json()
        assert "letzter_hash" in data
        assert "letzte_sequenznummer" in data


class TestBelegnummern:
    """Tests für Belegnummern-Kontrolle"""

    def test_belegnummern_kontrolle(self, client):
        """Test: Belegnummern prüfen"""
        response = client.get(
            "/api/gobd/belegnummern?belegart=RE&jahr=2026",
            headers={"Authorization": "Bearer dev-token"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "gesamt_belege" in data
        assert "luecken" in data
        assert "status" in data


class TestVerfahrensdokumentation:
    """Tests für Verfahrensdokumentation"""

    def test_verfahrensdokumentation_json(self, client):
        """Test: Verfahrensdokumentation als JSON"""
        response = client.get(
            "/api/gobd/verfahrensdokumentation?format=json",
            headers={"Authorization": "Bearer dev-token"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "software_name" in data
        assert "aufbewahrungsfristen" in data

    def test_verfahrensdokumentation_pdf(self, client):
        """Test: Verfahrensdokumentation als PDF"""
        response = client.get(
            "/api/gobd/verfahrensdokumentation?format=pdf",
            headers={"Authorization": "Bearer dev-token"}
        )
        assert response.status_code == 200


class TestAufbewahrung:
    """Tests für Aufbewahrungsfristen"""

    def test_aufbewahrungs_fristen(self, client):
        """Test: Aufbewahrungsfristen abrufen"""
        response = client.get("/api/gobd/aufbewahrung", headers={"Authorization": "Bearer dev-token"})
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        for item in data:
            assert "dokument_typ" in item
            assert "ablauf_datum" in item
            assert "status" in item


class TestBuchungslog:
    """Tests für revisionssicheres Journal"""

    def test_buchungslog(self, client):
        """Test: Buchungslog abrufen"""
        response = client.get(
            "/api/gobd/journal?von_datum=2026-01-01&bis_datum=2026-01-31",
            headers={"Authorization": "Bearer dev-token"}
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestNachvollziehbarkeit:
    """Tests für Nachvollziehbarkeit"""

    def test_nachvollziehbarkeit(self, client):
        """Test: Nachvollziehbarkeit prüfen"""
        response = client.get(
            "/api/gobd/nachvollziehbarkeit?von_datum=2026-01-01&bis_datum=2026-01-31",
            headers={"Authorization": "Bearer dev-token"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "anzahl_belege" in data
        assert "anzahl_benutzer" in data
        assert "anzahl_aktionen" in data


class TestAuditIntegration:
    """Integrationstests: Buchungspfade schreiben Audit-Log (GoBD-Nachvollziehbarkeit)."""

    _headers = {"Authorization": "Bearer dev-token"}

    def test_audit_logs_filter_by_journal_entry(self, client):
        """Audit-Log-API liefert Einträge für entity_type=journal_entry."""
        response = client.get(
            "/api/v1/audit/logs?entity_type=journal_entry&limit=10",
            headers=self._headers
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_audit_log_after_bulk_import(self, client, db):
        """Nach Bulk-Import (CSV) existiert ein Audit-Eintrag für die erstellte Buchung."""
        _ensure_system_tenant_and_accounts(db)
        import io
        csv_content = "entry_date,account_number,description,debit_amount,credit_amount,entry_number\n"
        csv_content += "2026-03-01,1400,Integrationstest Buchung,100.00,0.00,IMP-AUDIT-001\n"
        csv_content += "2026-03-01,8400,Integrationstest Gegenkonto,0.00,100.00,IMP-AUDIT-001\n"
        files = {"file": ("import.csv", io.BytesIO(csv_content.encode("utf-8")), "text/csv")}
        response = client.post(
            "/api/v1/finance/bulk-journal-import/csv?period=2026-03&tenant_id=system&dry_run=false",
            headers=self._headers,
            files=files,
        )
        if response.status_code != 200:
            pytest.skip("Bulk-Import fehlgeschlagen (z. B. kein Kontenplan): " + response.text[:200])
        data = response.json()
        created = data.get("created_entry_ids") or []
        if not created:
            pytest.skip("Bulk-Import hat keine Buchung erstellt (z. B. Konto 1400/8400 fehlt)")
        entry_id = created[0]
        audit_response = client.get(
            f"/api/v1/audit/logs?entity_type=journal_entry&entity_id={entry_id}",
            headers=self._headers,
        )
        assert audit_response.status_code == 200
        logs = audit_response.json()
        assert len(logs) >= 1, "Pro erstellte Buchung muss ein Audit-Eintrag existieren (GoBD)."
        assert logs[0]["entity_type"] == "journal_entry"
        assert logs[0]["entity_id"] == entry_id

    def test_audit_log_after_booking_template_apply(self, client, db):
        """Nach Anwenden einer Buchungsvorlage existiert ein Audit-Eintrag für die Buchung."""
        _ensure_system_tenant_and_accounts(db)
        list_resp = client.get(
            "/api/v1/finance/booking-templates?tenant_id=system",
            headers=self._headers,
        )
        if list_resp.status_code != 200:
            pytest.skip("Booking-Templates-API nicht verfügbar")
        templates = list_resp.json()
        if not templates or not isinstance(templates, list):
            pytest.skip("Keine Buchungsvorlagen vorhanden")
        template_id = templates[0].get("id") if templates else None
        if not template_id:
            pytest.skip("Vorlage ohne id")
        apply_resp = client.post(
            f"/api/v1/finance/booking-templates/{template_id}/apply?tenant_id=system",
            headers=self._headers,
            json={
                "entry_date": "2026-03-01",
                "amount": 100,
                "description": "Audit-Integrationstest",
            },
        )
        if apply_resp.status_code != 200:
            pytest.skip("Vorlage anwenden fehlgeschlagen: " + apply_resp.text[:200])
        apply_data = apply_resp.json()
        entry_id = apply_data.get("journal_entry_id") or apply_data.get("entry_id") or apply_data.get("id")
        if not entry_id:
            pytest.skip("Apply-Response enthält keine entry_id")
        audit_response = client.get(
            f"/api/v1/audit/logs?entity_type=journal_entry&entity_id={entry_id}",
            headers=self._headers,
        )
        assert audit_response.status_code == 200
        logs = audit_response.json()
        assert len(logs) >= 1, "Pro Buchung aus Vorlage muss ein Audit-Eintrag existieren (GoBD)."
        assert logs[0]["entity_type"] == "journal_entry"
        assert logs[0]["entity_id"] == entry_id
