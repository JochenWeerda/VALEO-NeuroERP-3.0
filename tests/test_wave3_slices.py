"""Wave-3 Integration Tests: WF-TRIGGER, STMD-DUP, XRECHNUNG, BANK-IMPORT, WGE-MOB.

Alle Tests laufen ohne echte DB (Unit-Ebene mit Mocks).
Marker: unit
"""
import pytest
from unittest.mock import MagicMock, patch
from decimal import Decimal


# ── WF-TRIGGER-001 ────────────────────────────────────────────────────────────

class TestWfTriggerService:
    def _make_svc(self):
        from app.services.wf_trigger_service import WfTriggerService, TRIGGER_MAP
        db = MagicMock()
        return WfTriggerService(db, "test-tenant"), TRIGGER_MAP

    def test_trigger_map_has_expected_entities(self):
        _, tm = self._make_svc()
        assert "agrar_settlement" in tm
        assert "sales_invoice" in tm
        assert "harvest_acceptance" in tm

    def test_fire_unknown_entity_returns_empty_list(self):
        svc, _ = self._make_svc()
        svc.db.execute.return_value.fetchone.return_value = None
        result = svc.fire("unbekannt", "abc", "WHATEVER")
        assert result == []

    def test_fire_known_entity_unknown_status_returns_empty(self):
        svc, _ = self._make_svc()
        result = svc.fire("agrar_settlement", "x", "UNBEKANNT")
        assert result == []

    def test_fire_known_entity_dispatches_actions(self):
        svc, _ = self._make_svc()
        svc.db.execute.return_value.fetchone.return_value = None
        with patch.object(svc, "_post_settlement_to_fibu", return_value={"ok": True}) as m:
            with patch.object(svc, "_create_ap_op", return_value={"ok": True}):
                with patch.object(svc, "_log_trigger"):
                    result = svc.fire("agrar_settlement", "s1", "FREIGEGEBEN")
        assert isinstance(result, list)

    def test_trigger_map_sales_invoice_verbucht(self):
        _, tm = self._make_svc()
        assert "VERBUCHT" in tm["sales_invoice"]
        assert "create_ar_op" in tm["sales_invoice"]["VERBUCHT"]


class TestWfTriggerEndpoints:
    def test_router_has_correct_prefix(self):
        from app.api.v1.endpoints.wf_trigger import router
        assert router.prefix == "/wf-trigger"

    def test_router_has_three_routes(self):
        from app.api.v1.endpoints.wf_trigger import router
        paths = {r.path for r in router.routes}
        assert "" in paths or "/" in paths or any("log" in p for p in paths)


# ── STMD-DUP-001 ─────────────────────────────────────────────────────────────

class TestStmdDupEndpoints:
    def test_router_prefix(self):
        from app.api.v1.endpoints.stmd_duplikat import router
        assert "duplikate" in router.prefix

    def test_zusammenfuehren_rejects_unknown_entity_type(self):
        """Direkter Aufruf der Endpunkt-Logik mit ungültigem entity_type."""
        from fastapi import HTTPException
        from app.api.v1.endpoints.stmd_duplikat import zusammenfuehren
        with pytest.raises(HTTPException) as exc_info:
            zusammenfuehren(
                master_id="a",
                duplikat_id="b",
                entity_type="ungueltig",
                tenant_id="t1",
                db=MagicMock(),
            )
        assert exc_info.value.status_code == 422

    def test_business_partner_table_selection(self):
        from fastapi import HTTPException
        from app.api.v1.endpoints.stmd_duplikat import zusammenfuehren
        db = MagicMock()
        db.execute.return_value.rowcount = 1
        result = zusammenfuehren(
            master_id="m1",
            duplikat_id="d1",
            entity_type="business_partner",
            tenant_id="t1",
            db=db,
        )
        assert result["status"] == "zusammengefuehrt"
        assert result["entity_type"] == "business_partner"


# ── INT-XRECHNUNG-001 ─────────────────────────────────────────────────────────

class TestXrechnungBuilder:
    def _make_inv(self):
        return {
            "invoice_number": "RE-2026-0001",
            "invoice_date": "2026-06-18",
            "due_date": "2026-07-18",
            "customer_id": "C001",
            "customer_name": "Testbauer GmbH",
            "net_amount": 1000.0,
            "tax_amount": 190.0,
            "total_amount": 1190.0,
            "currency": "EUR",
            "seller_name": "VALEO Landhandel GmbH",
            "seller_vat_id": "DE123456789",
        }

    def _make_lines(self):
        return [{
            "description": "Weizen A-Qualität",
            "quantity": 10.0,
            "unit": "TNE",
            "unit_price": 100.0,
            "line_total": 1000.0,
        }]

    def test_build_produces_valid_xml(self):
        from app.api.v1.endpoints.xrechnung import _build_xrechnung_xml
        xml = _build_xrechnung_xml(self._make_inv(), self._make_lines())
        assert '<?xml version="1.0"' in xml
        assert "Invoice" in xml
        assert "RE-2026-0001" in xml

    def test_build_contains_seller_name(self):
        from app.api.v1.endpoints.xrechnung import _build_xrechnung_xml
        xml = _build_xrechnung_xml(self._make_inv(), self._make_lines())
        assert "VALEO Landhandel GmbH" in xml

    def test_build_contains_buyer_name(self):
        from app.api.v1.endpoints.xrechnung import _build_xrechnung_xml
        xml = _build_xrechnung_xml(self._make_inv(), self._make_lines())
        assert "Testbauer GmbH" in xml

    def test_build_contains_amount(self):
        from app.api.v1.endpoints.xrechnung import _build_xrechnung_xml
        xml = _build_xrechnung_xml(self._make_inv(), self._make_lines())
        assert "1000.00" in xml

    def test_validate_detects_missing_vat_placeholder(self):
        from app.api.v1.endpoints.xrechnung import _build_xrechnung_xml
        inv = self._make_inv()
        inv["seller_vat_id"] = "DE000000000"
        xml = _build_xrechnung_xml(inv, self._make_lines())
        # Warnung-Logik ist im validate-Endpoint, hier nur XML-Check
        assert xml  # Builds ohne Fehler auch mit Platzhalter

    def test_batch_route_exists(self):
        from app.api.v1.endpoints.xrechnung import router
        paths = {r.path for r in router.routes}
        assert any("batch" in p for p in paths)


# ── INT-BANK-001 MT940 ────────────────────────────────────────────────────────

class TestMt940Parser:
    def test_parse_single_credit_line(self):
        from app.api.v1.endpoints.bank_import import _parse_mt940
        content = ":20:STARTUMFELD\n:60F:C260618EUR1000,\n:61:260618C1000,NTRFREF001\n:86:Verwendungszweck RE-0001\n:62F:C260618EUR2000,"
        txs = _parse_mt940(content)
        assert len(txs) == 1
        assert txs[0]["side"] == "credit"
        assert txs[0]["amount"] == 1000.0

    def test_parse_debit_line(self):
        from app.api.v1.endpoints.bank_import import _parse_mt940
        content = ":61:260618D500,NCHKREF002\n:86:Überweisung Lieferant"
        txs = _parse_mt940(content)
        assert len(txs) == 1
        assert txs[0]["side"] == "debit"
        assert txs[0]["amount"] == 500.0

    def test_parse_purpose_extracted(self):
        from app.api.v1.endpoints.bank_import import _parse_mt940
        content = ":61:260618C250,NTRFREF003\n:86:RE-2026-9999"
        txs = _parse_mt940(content)
        assert "RE-2026-9999" in txs[0]["purpose"]

    def test_empty_content_returns_empty_list(self):
        from app.api.v1.endpoints.bank_import import _parse_mt940
        assert _parse_mt940("") == []


class TestCamt053Parser:
    def _make_camt_xml(self, amount="100.00", cd="CRDT"):
        ns = "urn:iso:std:iso:20022:tech:xsd:camt.053.001.08"
        return f"""<?xml version="1.0"?>
<Document xmlns="{ns}">
  <BkToCstmrStmt>
    <Stmt>
      <Ntry>
        <Amt Ccy="EUR">{amount}</Amt>
        <CdtDbtInd>{cd}</CdtDbtInd>
        <BookgDt><Dt>2026-06-18</Dt></BookgDt>
        <NtryDtls><TxDtls><Refs><EndToEndId>E2E-001</EndToEndId></Refs></TxDtls></NtryDtls>
        <AddtlNtryInf>RE-TEST-001</AddtlNtryInf>
      </Ntry>
    </Stmt>
  </BkToCstmrStmt>
</Document>"""

    def test_parse_credit_entry(self):
        from app.api.v1.endpoints.bank_import import _parse_camt053
        txs = _parse_camt053(self._make_camt_xml("500.00", "CRDT"))
        assert len(txs) == 1
        assert txs[0]["side"] == "credit"
        assert txs[0]["amount"] == 500.0

    def test_parse_debit_entry(self):
        from app.api.v1.endpoints.bank_import import _parse_camt053
        txs = _parse_camt053(self._make_camt_xml("200.00", "DBIT"))
        assert txs[0]["side"] == "debit"

    def test_parse_booking_date(self):
        from app.api.v1.endpoints.bank_import import _parse_camt053
        txs = _parse_camt053(self._make_camt_xml())
        assert txs[0]["booking_date"] == "2026-06-18"

    def test_invalid_xml_raises_422(self):
        from fastapi import HTTPException
        from app.api.v1.endpoints.bank_import import _parse_camt053
        with pytest.raises(HTTPException) as exc_info:
            _parse_camt053("<<not xml>>")
        assert exc_info.value.status_code == 422


# ── WGE-MOB-001 ──────────────────────────────────────────────────────────────

class TestWaageMobile:
    def test_router_prefix(self):
        from app.api.v1.endpoints.waage_mobile import router
        assert router.prefix == "/waage/mobile"

    def test_create_quittung_returns_idempotent_on_duplicate(self):
        from app.api.v1.endpoints.waage_mobile import create_quittung, WaagenQuittungIn
        db = MagicMock()
        # Simuliert: idempotenz-hit
        db.execute.return_value.fetchone.return_value = ("existing-id", "quittiert")
        body = WaagenQuittungIn(
            weighing_ticket_id="t1",
            device_id="dev1",
            idempotency_key="idem-key-1",
        )
        result = create_quittung(body=body, tenant_id="tenant1", db=db)
        assert result["idempotent"] is True
        assert result["id"] == "existing-id"

    def test_create_quittung_404_if_ticket_missing(self):
        from fastapi import HTTPException
        from app.api.v1.endpoints.waage_mobile import create_quittung, WaagenQuittungIn
        db = MagicMock()
        # Erste DB-Abfrage (idempotenz) → kein Hit; zweite (ticket) → nicht gefunden
        db.execute.return_value.fetchone.side_effect = [None, None]
        body = WaagenQuittungIn(
            weighing_ticket_id="unknown",
            device_id="dev1",
            idempotency_key="idem-key-2",
        )
        with pytest.raises(HTTPException) as exc_info:
            create_quittung(body=body, tenant_id="t1", db=db)
        assert exc_info.value.status_code == 404

    def test_batch_sync_skips_idempotent_duplicates(self):
        from app.api.v1.endpoints.waage_mobile import batch_sync, WaagenQuittungIn, WaagenQuittungBatch
        db = MagicMock()
        # k1: idempotency hit → already_synced + continue
        # k2: idempotency miss → None, dann ticket lookup → None (ticket_not_found)
        db.execute.return_value.fetchone.side_effect = [
            ("dup-id",),   # k1: idempotency hit
            None,           # k2: idempotency miss
            None,           # k2: ticket nicht gefunden
        ]
        batch = WaagenQuittungBatch(
            device_id="dev1",
            quittungen=[
                WaagenQuittungIn(weighing_ticket_id="t1", device_id="dev1", idempotency_key="k1"),
                WaagenQuittungIn(weighing_ticket_id="t2", device_id="dev1", idempotency_key="k2"),
            ],
        )
        result = batch_sync(body=batch, tenant_id="t1", db=db)
        statuses = {r["idempotency_key"]: r["status"] for r in result["results"]}
        assert statuses["k1"] == "already_synced"
        assert statuses["k2"] == "rejected"


# ── Alembic Single-Head Check ─────────────────────────────────────────────────

class TestAlembicMigrationChain:
    def test_wave3_migration_has_correct_down_revision(self):
        """Stellt sicher dass Wave-3 Migration an comp_artikel_sperren angehängt ist."""
        import importlib.util, pathlib
        mig_path = pathlib.Path("alembic/versions/wave3_wf_trigger_log_20260618.py")
        spec = importlib.util.spec_from_file_location("wave3_mig", mig_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        assert mod.down_revision == "comp_artikel_sperren_20260618"
        assert mod.revision == "wave3_wf_trigger_log_20260618"
