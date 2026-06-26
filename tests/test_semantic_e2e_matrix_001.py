"""SEMANTIC-E2E-MATRIX-001 — Semantische Prozessketten-Tests.

Prüft Business-Outcomes (Belegkettenverknüpfung, Salden, Status-Übergänge)
der 4 kritischen ERP-Prozessketten ohne Datenbank-Session.
"""
import pytest

from app.services.semantic_e2e_chain_service import (
    ChainStepStatus,
    FiBuChain,
    O2CChain,
    P2PChain,
    WMSAgrChain,
)

pytestmark = pytest.mark.unit


# ══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture()
def valid_o2c_ctx() -> dict:
    return {
        "customer": {"id": "cust-1", "customer_number": "DE10001", "name": "Agrar GmbH"},
        "offer": {"id": "off-1", "customer_id": "cust-1", "status": "accepted", "total_net": 5000.0},
        "order": {
            "id": "ord-1",
            "customer_id": "cust-1",
            "source_offer_id": "off-1",
            "status": "confirmed",
            "total_net": 5000.0,
        },
        "delivery_note": {"id": "dn-1", "customer_id": "cust-1", "sales_order_id": "ord-1"},
        "invoice": {
            "id": "inv-1",
            "customer_id": "cust-1",
            "delivery_note_id": "dn-1",
            "total_gross": 5950.0,
            "invoice_number": "RE-2026-00001",
        },
        "payment": {"invoice_id": "inv-1", "amount": 5950.0, "op_status": "ausgeziffert"},
    }


@pytest.fixture()
def valid_p2p_ctx() -> dict:
    return {
        "supplier": {"id": "sup-1"},
        "purchase_order": {
            "id": "po-1",
            "supplier_id": "sup-1",
            "status": "ordered",
            "total_net": 3000.0,
        },
        "goods_receipt": {
            "id": "gr-1",
            "purchase_order_id": "po-1",
            "received_qty": 100,
            "received_at": "2026-06-01T08:00:00",
        },
        "three_way_match": {
            "purchase_order_id": "po-1",
            "goods_receipt_id": "gr-1",
            "match_status": "matched",
            "price_deviation_pct": 0.5,
        },
        "ap_invoice": {
            "id": "ap-1",
            "supplier_id": "sup-1",
            "op_id": "op-sup-1",
            "total_gross": 3570.0,
        },
    }


@pytest.fixture()
def valid_fibu_ctx() -> dict:
    return {
        "open_item": {
            "id": "op-1",
            "op_status": "offen",
            "offen": 5950.0,
            "faelligkeit": "2026-07-01",
        },
        "payment": {"op_id": "op-1", "amount": 5950.0},
        "cleared_op": {"op_status": "ausgeziffert", "offen": 0.0},
        "datev_export": {"status": "exported", "file_path": "/exports/datev_2026_06.zip", "entry_count": 12},
    }


@pytest.fixture()
def valid_wms_ctx() -> dict:
    return {
        "harvest_acceptance": {"id": "acc-1", "status": "waage_abgeschlossen", "netto_gewicht_kg": 24000},
        "weighing_ticket": {"id": "wt-1", "harvest_acceptance_id": "acc-1", "netto_kg": 24000},
        "lot": {"id": "lot-1", "weighing_ticket_id": "wt-1", "lot_number": "WZ-2026-00123"},
        "silo_cell": {"id": "cell-1", "lot_id": "lot-1", "current_stock_kg": 24000, "capacity_kg": 30000},
        "qs_result": {"lot_id": "lot-1", "status": "freigegeben"},
        "trace": {"lot_id": "lot-1", "harvest_acceptance_id": "acc-1", "silo_cell_id": "cell-1"},
    }


# ══════════════════════════════════════════════════════════════════════════════
# O2C — Order-to-Cash
# ══════════════════════════════════════════════════════════════════════════════

class TestO2CChain:
    def test_happy_path_all_steps_ok(self, valid_o2c_ctx):
        result = O2CChain().run(valid_o2c_ctx)
        assert result.all_ok, f"Fehler: {result.invariant_violations}"
        assert len(result.steps) == 6

    def test_chain_id(self, valid_o2c_ctx):
        result = O2CChain().run(valid_o2c_ctx)
        assert result.chain_id == "o2c-crm360"

    def test_step_names_in_order(self, valid_o2c_ctx):
        result = O2CChain().run(valid_o2c_ctx)
        assert [s.name for s in result.steps] == [
            "kunde", "angebot", "auftrag", "lieferschein", "rechnung", "zahlungseingang"
        ]

    def test_missing_customer_id_fails_kunde_step(self, valid_o2c_ctx):
        valid_o2c_ctx["customer"] = {"customer_number": "DE10001"}  # kein id
        result = O2CChain().run(valid_o2c_ctx)
        kunde = result.steps[0]
        assert kunde.status == ChainStepStatus.failed
        assert any("id" in e for e in kunde.invariant_errors)

    def test_sales_order_id_mismatch_fails_lieferschein(self, valid_o2c_ctx):
        valid_o2c_ctx["delivery_note"]["sales_order_id"] = "FALSCHER-ID"
        result = O2CChain().run(valid_o2c_ctx)
        ls = next(s for s in result.steps if s.name == "lieferschein")
        assert ls.status == ChainStepStatus.failed
        assert any("sales_order_id" in e or "Auftrag-ID" in e for e in ls.invariant_errors)

    def test_missing_invoice_number_fails_rechnung(self, valid_o2c_ctx):
        valid_o2c_ctx["invoice"]["invoice_number"] = None
        result = O2CChain().run(valid_o2c_ctx)
        re = next(s for s in result.steps if s.name == "rechnung")
        assert re.status == ChainStepStatus.failed

    def test_op_not_ausgeziffert_fails_zahlungseingang(self, valid_o2c_ctx):
        valid_o2c_ctx["payment"]["op_status"] = "offen"
        result = O2CChain().run(valid_o2c_ctx)
        pay = next(s for s in result.steps if s.name == "zahlungseingang")
        assert pay.status == ChainStepStatus.failed

    def test_negative_total_fails_angebot(self, valid_o2c_ctx):
        valid_o2c_ctx["offer"]["total_net"] = -100
        result = O2CChain().run(valid_o2c_ctx)
        angebot = result.steps[1]
        assert angebot.status == ChainStepStatus.failed

    def test_customer_id_propagation_to_all_docs(self, valid_o2c_ctx):
        """Alle Belege müssen dieselbe customer_id referenzieren."""
        result = O2CChain().run(valid_o2c_ctx)
        assert result.all_ok
        # Order → customer_id check wird intern geprüft; kein Step darf fehlen
        assert not result.failed_steps

    def test_source_offer_id_on_order_required(self, valid_o2c_ctx):
        valid_o2c_ctx["order"]["source_offer_id"] = None
        result = O2CChain().run(valid_o2c_ctx)
        auftrag = next(s for s in result.steps if s.name == "auftrag")
        # source_offer_id=None statt off-1 → Mismatch
        assert auftrag.status == ChainStepStatus.failed

    def test_failed_steps_summary(self, valid_o2c_ctx):
        valid_o2c_ctx["invoice"]["total_gross"] = 0
        result = O2CChain().run(valid_o2c_ctx)
        assert len(result.failed_steps) >= 1
        assert not result.all_ok


# ══════════════════════════════════════════════════════════════════════════════
# P2P — Procure-to-Pay
# ══════════════════════════════════════════════════════════════════════════════

class TestP2PChain:
    def test_happy_path_all_steps_ok(self, valid_p2p_ctx):
        result = P2PChain().run(valid_p2p_ctx)
        assert result.all_ok, f"Fehler: {result.invariant_violations}"
        assert len(result.steps) == 5

    def test_chain_id(self, valid_p2p_ctx):
        assert P2PChain().run(valid_p2p_ctx).chain_id == "p2p-procure-to-pay"

    def test_step_names_in_order(self, valid_p2p_ctx):
        result = P2PChain().run(valid_p2p_ctx)
        assert [s.name for s in result.steps] == [
            "lieferant", "bestellung", "wareneingang", "drei_wege_match", "eingangsrechnung"
        ]

    def test_drei_wege_match_preisabweichung_unter_toleranz_ok(self, valid_p2p_ctx):
        valid_p2p_ctx["three_way_match"]["price_deviation_pct"] = 1.99
        result = P2PChain().run(valid_p2p_ctx)
        assert result.all_ok

    def test_drei_wege_match_preisabweichung_ueber_toleranz_fails(self, valid_p2p_ctx):
        valid_p2p_ctx["three_way_match"]["price_deviation_pct"] = 3.5
        result = P2PChain().run(valid_p2p_ctx)
        match = next(s for s in result.steps if s.name == "drei_wege_match")
        assert match.status == ChainStepStatus.failed
        assert any("Preisabweichung" in e for e in match.invariant_errors)

    def test_goods_receipt_missing_received_at_fails(self, valid_p2p_ctx):
        valid_p2p_ctx["goods_receipt"]["received_at"] = None
        result = P2PChain().run(valid_p2p_ctx)
        gr = next(s for s in result.steps if s.name == "wareneingang")
        assert gr.status == ChainStepStatus.failed

    def test_ap_invoice_missing_op_id_fails(self, valid_p2p_ctx):
        valid_p2p_ctx["ap_invoice"]["op_id"] = None
        result = P2PChain().run(valid_p2p_ctx)
        ap = next(s for s in result.steps if s.name == "eingangsrechnung")
        assert ap.status == ChainStepStatus.failed

    def test_supplier_id_propagated_to_po_and_invoice(self, valid_p2p_ctx):
        result = P2PChain().run(valid_p2p_ctx)
        assert result.all_ok  # interne cross-ref-Prüfungen bestanden

    def test_zero_received_qty_fails_wareneingang(self, valid_p2p_ctx):
        valid_p2p_ctx["goods_receipt"]["received_qty"] = 0
        result = P2PChain().run(valid_p2p_ctx)
        gr = next(s for s in result.steps if s.name == "wareneingang")
        assert gr.status == ChainStepStatus.failed


# ══════════════════════════════════════════════════════════════════════════════
# FiBu — OP → Zahlung → Auszifferung → DATEV
# ══════════════════════════════════════════════════════════════════════════════

class TestFiBuChain:
    def test_happy_path_all_steps_ok(self, valid_fibu_ctx):
        result = FiBuChain().run(valid_fibu_ctx)
        assert result.all_ok, f"Fehler: {result.invariant_violations}"
        assert len(result.steps) == 4  # ohne closing

    def test_chain_id(self, valid_fibu_ctx):
        assert FiBuChain().run(valid_fibu_ctx).chain_id == "fibu-op-to-datev"

    def test_step_names_without_closing(self, valid_fibu_ctx):
        result = FiBuChain().run(valid_fibu_ctx)
        assert [s.name for s in result.steps] == [
            "offener_posten", "zahlung", "auszifferung", "datev_export"
        ]

    def test_with_periodenabschluss_step_added(self, valid_fibu_ctx):
        valid_fibu_ctx["closing"] = {
            "status": "closed",
            "locked_at": "2026-06-30T23:59:59",
            "balance": 0.0,
        }
        result = FiBuChain().run(valid_fibu_ctx)
        assert result.all_ok
        assert len(result.steps) == 5
        assert any(s.name == "periodenabschluss" for s in result.steps)

    def test_op_not_offen_fails(self, valid_fibu_ctx):
        valid_fibu_ctx["open_item"]["op_status"] = "ausgeziffert"
        result = FiBuChain().run(valid_fibu_ctx)
        op = result.steps[0]
        assert op.status == ChainStepStatus.failed

    def test_auszifferung_restbetrag_nicht_null_fails(self, valid_fibu_ctx):
        valid_fibu_ctx["cleared_op"]["offen"] = 50.0  # Restbetrag vorhanden
        result = FiBuChain().run(valid_fibu_ctx)
        cleared = next(s for s in result.steps if s.name == "auszifferung")
        assert cleared.status == ChainStepStatus.failed
        assert any("50.00" in e for e in cleared.invariant_errors)

    def test_datev_export_zero_entries_fails(self, valid_fibu_ctx):
        valid_fibu_ctx["datev_export"]["entry_count"] = 0
        result = FiBuChain().run(valid_fibu_ctx)
        de = next(s for s in result.steps if s.name == "datev_export")
        assert de.status == ChainStepStatus.failed

    def test_datev_export_missing_file_path_fails(self, valid_fibu_ctx):
        valid_fibu_ctx["datev_export"]["file_path"] = None
        result = FiBuChain().run(valid_fibu_ctx)
        de = next(s for s in result.steps if s.name == "datev_export")
        assert de.status == ChainStepStatus.failed

    def test_payment_op_id_mismatch_fails(self, valid_fibu_ctx):
        valid_fibu_ctx["payment"]["op_id"] = "ANDERER-OP"
        result = FiBuChain().run(valid_fibu_ctx)
        zahlung = next(s for s in result.steps if s.name == "zahlung")
        assert zahlung.status == ChainStepStatus.failed

    def test_op_missing_faelligkeit_fails(self, valid_fibu_ctx):
        valid_fibu_ctx["open_item"]["faelligkeit"] = None
        result = FiBuChain().run(valid_fibu_ctx)
        op = result.steps[0]
        assert op.status == ChainStepStatus.failed

    def test_closing_without_locked_at_fails(self, valid_fibu_ctx):
        valid_fibu_ctx["closing"] = {"status": "closed", "locked_at": None, "balance": 0.0}
        result = FiBuChain().run(valid_fibu_ctx)
        closing_step = next(s for s in result.steps if s.name == "periodenabschluss")
        assert closing_step.status == ChainStepStatus.failed


# ══════════════════════════════════════════════════════════════════════════════
# WMS/Agrar — Annahme → Waage → Lot → Silo → QS → Trace
# ══════════════════════════════════════════════════════════════════════════════

class TestWMSAgrChain:
    def test_happy_path_all_steps_ok(self, valid_wms_ctx):
        result = WMSAgrChain().run(valid_wms_ctx)
        assert result.all_ok, f"Fehler: {result.invariant_violations}"
        assert len(result.steps) == 6

    def test_chain_id(self, valid_wms_ctx):
        assert WMSAgrChain().run(valid_wms_ctx).chain_id == "wms-agr-annahme-trace"

    def test_step_names_in_order(self, valid_wms_ctx):
        result = WMSAgrChain().run(valid_wms_ctx)
        assert [s.name for s in result.steps] == [
            "annahme", "waage", "lot", "silozelle", "qs_freigabe", "traceability"
        ]

    def test_silo_ueberfuellung_fails(self, valid_wms_ctx):
        valid_wms_ctx["silo_cell"]["current_stock_kg"] = 35000
        valid_wms_ctx["silo_cell"]["capacity_kg"] = 30000
        result = WMSAgrChain().run(valid_wms_ctx)
        silo = next(s for s in result.steps if s.name == "silozelle")
        assert silo.status == ChainStepStatus.failed
        assert any("Überfüllung" in e for e in silo.invariant_errors)

    def test_qs_status_gesperrt_still_valid(self, valid_wms_ctx):
        valid_wms_ctx["qs_result"]["status"] = "gesperrt"
        result = WMSAgrChain().run(valid_wms_ctx)
        assert result.all_ok  # gesperrt ist valider Status

    def test_qs_status_unbekannt_fails(self, valid_wms_ctx):
        valid_wms_ctx["qs_result"]["status"] = "abgelehnt"  # nicht in erlaubter Liste
        result = WMSAgrChain().run(valid_wms_ctx)
        qs = next(s for s in result.steps if s.name == "qs_freigabe")
        assert qs.status == ChainStepStatus.failed

    def test_weighing_ticket_wrong_acceptance_id_fails(self, valid_wms_ctx):
        valid_wms_ctx["weighing_ticket"]["harvest_acceptance_id"] = "ANDERE-ANNAHME"
        result = WMSAgrChain().run(valid_wms_ctx)
        waage = next(s for s in result.steps if s.name == "waage")
        assert waage.status == ChainStepStatus.failed

    def test_missing_lot_number_fails(self, valid_wms_ctx):
        valid_wms_ctx["lot"]["lot_number"] = None
        result = WMSAgrChain().run(valid_wms_ctx)
        lot = next(s for s in result.steps if s.name == "lot")
        assert lot.status == ChainStepStatus.failed

    def test_trace_missing_silo_cell_id_fails(self, valid_wms_ctx):
        valid_wms_ctx["trace"]["silo_cell_id"] = None
        result = WMSAgrChain().run(valid_wms_ctx)
        trace = next(s for s in result.steps if s.name == "traceability")
        assert trace.status == ChainStepStatus.failed

    def test_zero_netto_gewicht_fails_annahme(self, valid_wms_ctx):
        valid_wms_ctx["harvest_acceptance"]["netto_gewicht_kg"] = 0
        result = WMSAgrChain().run(valid_wms_ctx)
        annahme = result.steps[0]
        assert annahme.status == ChainStepStatus.failed


# ══════════════════════════════════════════════════════════════════════════════
# Cross-Chain: invariant_violations report
# ══════════════════════════════════════════════════════════════════════════════

class TestInvariantViolationsReport:
    def test_violations_aggregated_from_all_failed_steps(self, valid_o2c_ctx):
        valid_o2c_ctx["invoice"]["invoice_number"] = None
        valid_o2c_ctx["payment"]["op_status"] = "offen"
        result = O2CChain().run(valid_o2c_ctx)
        violations = result.invariant_violations
        assert len(violations) >= 2

    def test_no_violations_on_clean_chain(self, valid_o2c_ctx):
        result = O2CChain().run(valid_o2c_ctx)
        assert result.invariant_violations == []

    def test_failed_steps_returns_only_failed(self, valid_p2p_ctx):
        valid_p2p_ctx["goods_receipt"]["received_qty"] = 0
        result = P2PChain().run(valid_p2p_ctx)
        failed = result.failed_steps
        assert all(s.status != ChainStepStatus.ok for s in failed)
