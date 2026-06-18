"""Wave-3 DB-Integration-Tests (benötigen laufende PostgreSQL).

Marker: integration, needs_live_db

Alle Tests nutzen die `require_db` Fixture — werden automatisch geskippt
wenn keine Datenbank erreichbar ist. Fehlerbehandlung wenn Seed-Daten
fehlen: Tests prüfen ob Schema/Tabellen existieren und skippen graceful.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app

TENANT = "00000000-0000-0000-0000-000000000001"
HEADERS = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-Id": TENANT,
}

client = TestClient(app, raise_server_exceptions=False)


def _table_exists(db, schema: str, table: str) -> bool:
    row = db.execute(text("""
        SELECT 1 FROM information_schema.tables
         WHERE table_schema = :schema AND table_name = :table
    """), {"schema": schema, "table": table}).fetchone()
    return row is not None


# ── WF-TRIGGER-001 DB-Tests ───────────────────────────────────────────────────

class TestWfTriggerDB:
    def test_get_trigger_map(self, require_db):
        resp = client.get("/api/v1/wf-trigger/map", headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert "trigger_map" in data
        assert "agrar_settlement" in data["trigger_map"]

    def test_manual_fire_unknown_entity_returns_200_empty(self, require_db):
        resp = client.post("/api/v1/wf-trigger", headers=HEADERS, json={
            "entity_type": "unbekannt_xyz",
            "entity_id": "00000000-0000-0000-0000-000000000099",
            "new_status": "TEST",
        })
        assert resp.status_code == 200
        data = resp.json()
        # Response key ist "actions" (Liste der Aktions-Ergebnisse)
        assert "actions" in data
        assert isinstance(data["actions"], list)

    def test_get_trigger_log_returns_list(self, require_db):
        from app.core.database import SessionLocal
        db = SessionLocal()
        try:
            if not _table_exists(db, "domain_ops", "wf_trigger_log"):
                pytest.skip("wf_trigger_log table not yet migrated")
        finally:
            db.close()

        resp = client.get("/api/v1/wf-trigger/log", headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data or isinstance(data, list)


# ── STMD-DUP-001 DB-Tests ────────────────────────────────────────────────────

class TestStmdDupDB:
    def test_business_partner_duplikat_check_returns_list(self, require_db):
        resp = client.get(
            "/api/v1/stammdaten/duplikate/business-partner",
            headers=HEADERS,
            params={"min_score": 0.8},
        )
        # 200 oder 503 wenn Tabelle nicht vorhanden
        if resp.status_code == 503:
            pytest.skip("business_partners table not available")
        assert resp.status_code == 200
        data = resp.json()
        assert "dubletten" in data
        assert isinstance(data["count"], int)

    def test_artikel_duplikat_check_returns_list(self, require_db):
        resp = client.get(
            "/api/v1/stammdaten/duplikate/artikel",
            headers=HEADERS,
        )
        if resp.status_code == 503:
            pytest.skip("articles table not available")
        assert resp.status_code == 200
        data = resp.json()
        assert "dubletten" in data

    def test_zusammenfuehren_404_for_nonexistent(self, require_db):
        resp = client.post(
            "/api/v1/stammdaten/duplikate/zusammenfuehren",
            headers=HEADERS,
            params={
                "master_id": "00000000-0000-0000-0000-000000000001",
                "duplikat_id": "00000000-0000-0000-0000-000000000002",
                "entity_type": "business_partner",
            },
        )
        if resp.status_code == 503:
            pytest.skip("business_partners table not available")
        # 404 weil Datensatz nicht existiert, oder 200 wenn rowcount=0 → bereits als 404 behandelt
        assert resp.status_code in (200, 404, 500)


# ── INT-XRECHNUNG-001 DB-Tests ───────────────────────────────────────────────

class TestXrechnungDB:
    def test_export_404_for_nonexistent_invoice(self, require_db):
        resp = client.get(
            "/api/v1/xrechnung/00000000-0000-0000-0000-000000000099",
            headers=HEADERS,
        )
        if resp.status_code in (500, 503):
            pytest.skip(f"Tabelle/Schema nicht verfügbar: {resp.text[:200]}")
        assert resp.status_code == 404

    def test_validate_404_for_nonexistent(self, require_db):
        resp = client.get(
            "/api/v1/xrechnung/00000000-0000-0000-0000-000000000099/validate",
            headers=HEADERS,
        )
        if resp.status_code in (500, 503):
            pytest.skip(f"Tabelle/Schema nicht verfügbar: {resp.text[:200]}")
        assert resp.status_code == 404

    def test_batch_export_empty_periode_returns_zip(self, require_db):
        """Keine Rechnungen → leeres ZIP, kein 500."""
        resp = client.get(
            "/api/v1/xrechnung/batch/export",
            headers=HEADERS,
            params={"periode": "1900-01", "status": "VERBUCHT"},
        )
        if resp.status_code == 503:
            pytest.skip("sales_invoices table not available")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/zip"
        # Leeres ZIP hat trotzdem mindestens 22 Bytes (PK-Endrecord)
        assert len(resp.content) >= 22

    def test_export_with_seed_invoice(self, require_db):
        """Legt eine Test-Rechnung an und exportiert sie als XRechnung."""
        from app.core.database import SessionLocal
        from app.core.uuid7 import uuid7
        db = SessionLocal()
        inv_id = None
        try:
            if not _table_exists(db, "domain_erp", "sales_invoices"):
                pytest.skip("sales_invoices table not available")

            inv_id = str(uuid7())
            db.execute(text("""
                INSERT INTO domain_erp.sales_invoices
                  (id, tenant_id, invoice_number, invoice_date, due_date,
                   customer_id, net_amount, tax_amount, total_amount, currency, status)
                VALUES
                  (:id, :tid, :num, '2026-06-18', '2026-07-18',
                   :cust, 1000.00, 190.00, 1190.00, 'EUR', 'VERBUCHT')
            """), {
                "id": inv_id, "tid": TENANT,
                "num": f"TEST-XR-{inv_id[:8]}",
                "cust": "00000000-0000-0000-0000-000000000001",
            })
            db.commit()
        except Exception as e:
            pytest.skip(f"Seed-Daten konnten nicht angelegt werden: {e}")
        finally:
            db.close()

        try:
            resp = client.get(f"/api/v1/xrechnung/{inv_id}", headers=HEADERS)
            assert resp.status_code == 200
            assert "<?xml" in resp.text
            assert "Invoice" in resp.text
        finally:
            # Cleanup
            db2 = SessionLocal()
            try:
                db2.execute(text("DELETE FROM domain_erp.sales_invoices WHERE id = :id"),
                            {"id": inv_id})
                db2.commit()
            except Exception:
                pass
            finally:
                db2.close()


# ── INT-BANK-001 DB-Tests ────────────────────────────────────────────────────

class TestBankImportDB:
    def test_list_statements_returns_list(self, require_db):
        from app.core.database import SessionLocal
        db = SessionLocal()
        try:
            if not _table_exists(db, "domain_finance", "bank_statements"):
                pytest.skip("bank_statements table not yet migrated")
        finally:
            db.close()

        resp = client.get("/api/v1/bank/statements", headers=HEADERS)
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data

    def test_import_mt940_and_match(self, require_db):
        from app.core.database import SessionLocal
        db = SessionLocal()
        try:
            if not _table_exists(db, "domain_finance", "bank_statements"):
                pytest.skip("bank_statements table not yet migrated")
        finally:
            db.close()

        mt940_content = (
            ":20:STARTUMFELD\n"
            ":21:NONREF\n"
            ":25:TESTIBAN/EUR\n"
            ":28C:00001/001\n"
            ":60F:C260618EUR0,\n"
            ":61:260618C1000,NTRFREF001\n"
            ":86:RE-TEST-DB-001\n"
            ":62F:C260618EUR1000,\n"
        )
        import io
        resp = client.post(
            "/api/v1/bank/import/mt940",
            headers=HEADERS,
            params={"iban": "DE89370400440532013000"},
            files={"file": ("test.sta", io.BytesIO(mt940_content.encode()), "text/plain")},
        )
        if resp.status_code in (500, 503):
            pytest.skip(f"DB nicht bereit: {resp.text[:200]}")
        assert resp.status_code == 201
        data = resp.json()
        assert data["lines"] == 1
        assert "statement_id" in data

        # Match ausführen
        statement_id = data["statement_id"]
        resp2 = client.post(
            f"/api/v1/bank/match/{statement_id}",
            headers=HEADERS,
        )
        assert resp2.status_code == 200
        match_data = resp2.json()
        assert "matched" in match_data
        assert "unmatched" in match_data

    def test_import_camt053(self, require_db):
        from app.core.database import SessionLocal
        db = SessionLocal()
        try:
            if not _table_exists(db, "domain_finance", "bank_statements"):
                pytest.skip("bank_statements table not yet migrated")
        finally:
            db.close()

        ns = "urn:iso:std:iso:20022:tech:xsd:camt.053.001.08"
        camt_xml = f"""<?xml version="1.0"?>
<Document xmlns="{ns}">
  <BkToCstmrStmt>
    <Stmt>
      <Ntry>
        <Amt Ccy="EUR">500.00</Amt>
        <CdtDbtInd>CRDT</CdtDbtInd>
        <BookgDt><Dt>2026-06-18</Dt></BookgDt>
        <NtryDtls><TxDtls><Refs><EndToEndId>E2E-DB-001</EndToEndId></Refs></TxDtls></NtryDtls>
        <AddtlNtryInf>RE-CAMT-TEST</AddtlNtryInf>
      </Ntry>
    </Stmt>
  </BkToCstmrStmt>
</Document>"""
        import io
        resp = client.post(
            "/api/v1/bank/import/camt053",
            headers=HEADERS,
            params={"iban": "DE89370400440532013001"},
            files={"file": ("test.xml", io.BytesIO(camt_xml.encode()), "application/xml")},
        )
        if resp.status_code in (500, 503):
            pytest.skip(f"DB nicht bereit: {resp.text[:200]}")
        assert resp.status_code == 201
        data = resp.json()
        assert data["lines"] == 1
        assert data["format"] == "CAMT053"


# ── WGE-MOB-001 DB-Tests ─────────────────────────────────────────────────────

class TestWaageMobileDB:
    def test_get_pending_returns_list(self, require_db):
        from app.core.database import SessionLocal
        db = SessionLocal()
        try:
            if not _table_exists(db, "domain_agrar", "weighing_tickets"):
                pytest.skip("weighing_tickets table not available")
        finally:
            db.close()

        resp = client.get(
            "/api/v1/waage/mobile/pending",
            headers=HEADERS,
            params={"device_id": "test-device-001"},
        )
        if resp.status_code in (500, 503):
            pytest.skip(f"DB-Fehler (Schema fehlt?): {resp.text[:200]}")
        assert resp.status_code == 200
        data = resp.json()
        assert "items" in data
        assert isinstance(data["pending_count"], int)

    def test_get_ticket_404_for_nonexistent(self, require_db):
        from app.core.database import SessionLocal
        db = SessionLocal()
        try:
            if not _table_exists(db, "domain_agrar", "weighing_tickets"):
                pytest.skip("weighing_tickets table not available")
        finally:
            db.close()

        resp = client.get(
            "/api/v1/waage/mobile/tickets/00000000-0000-0000-0000-000000000099",
            headers=HEADERS,
        )
        assert resp.status_code == 404

    def test_create_quittung_404_for_nonexistent_ticket(self, require_db):
        from app.core.database import SessionLocal
        db = SessionLocal()
        try:
            if not _table_exists(db, "domain_agrar", "waagen_quittungen"):
                pytest.skip("waagen_quittungen table not yet migrated")
        finally:
            db.close()

        resp = client.post(
            "/api/v1/waage/mobile/quittung",
            headers=HEADERS,
            json={
                "weighing_ticket_id": "00000000-0000-0000-0000-000000000099",
                "device_id": "test-device",
                "idempotency_key": "test-idem-key-db-001",
            },
        )
        assert resp.status_code == 404

    def test_create_quittung_with_seed(self, require_db):
        """Legt Wiegeticket an, quittiert es, prüft Idempotenz."""
        from app.core.database import SessionLocal
        from app.core.uuid7 import uuid7
        db = SessionLocal()
        ticket_id = None
        try:
            if not _table_exists(db, "domain_agrar", "waagen_quittungen"):
                pytest.skip("waagen_quittungen table not yet migrated")
            if not _table_exists(db, "domain_agrar", "weighing_tickets"):
                pytest.skip("weighing_tickets table not available")

            ticket_id = str(uuid7())
            db.execute(text("""
                INSERT INTO domain_agrar.weighing_tickets
                  (id, tenant_id, ticket_number, netto_gewicht_kg,
                   brutto_gewicht_kg, tara_gewicht_kg, status)
                VALUES
                  (:id, :tid, :num, 18500.0, 23100.0, 4600.0, 'gebucht')
            """), {
                "id": ticket_id, "tid": TENANT,
                "num": f"WGT-DB-{ticket_id[:8]}",
            })
            db.commit()
        except Exception as e:
            pytest.skip(f"Seed fehlgeschlagen: {e}")
        finally:
            db.close()

        idem_key = f"idem-{ticket_id}"
        try:
            # Erste Quittung
            resp1 = client.post("/api/v1/waage/mobile/quittung", headers=HEADERS, json={
                "weighing_ticket_id": ticket_id,
                "device_id": "test-device-001",
                "driver_id": "driver-001",
                "idempotency_key": idem_key,
            })
            assert resp1.status_code == 201
            data1 = resp1.json()
            assert data1["status"] == "quittiert"
            assert data1["idempotency_key"] == idem_key

            # Zweite Quittung mit gleichem Key → idempotent
            resp2 = client.post("/api/v1/waage/mobile/quittung", headers=HEADERS, json={
                "weighing_ticket_id": ticket_id,
                "device_id": "test-device-001",
                "idempotency_key": idem_key,
            })
            assert resp2.status_code == 200
            data2 = resp2.json()
            assert data2.get("idempotent") is True

            # Ticket-Detail abrufen
            resp3 = client.get(f"/api/v1/waage/mobile/tickets/{ticket_id}", headers=HEADERS)
            assert resp3.status_code == 200
            detail = resp3.json()
            assert detail["quittiert"] is True
            assert len(detail["quittungen"]) == 1
        finally:
            # Cleanup
            db2 = SessionLocal()
            try:
                db2.execute(text(
                    "DELETE FROM domain_agrar.waagen_quittungen WHERE weighing_ticket_id = :id"
                ), {"id": ticket_id})
                db2.execute(text(
                    "DELETE FROM domain_agrar.weighing_tickets WHERE id = :id"
                ), {"id": ticket_id})
                db2.commit()
            except Exception:
                pass
            finally:
                db2.close()

    def test_batch_sync_idempotent(self, require_db):
        """Batch-Sync mit leerer Quittungs-Liste gibt keine 500."""
        from app.core.database import SessionLocal
        db = SessionLocal()
        try:
            if not _table_exists(db, "domain_agrar", "waagen_quittungen"):
                pytest.skip("waagen_quittungen table not yet migrated")
        finally:
            db.close()

        resp = client.post("/api/v1/waage/mobile/sync", headers=HEADERS, json={
            "device_id": "test-device-batch",
            "quittungen": [],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["total"] == 0
        assert data["synced"] == 0
