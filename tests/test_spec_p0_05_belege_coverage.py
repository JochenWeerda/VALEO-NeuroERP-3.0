"""SPEC-P0-05: Beleg-/Report-Pfade auf ≥70% (Fortsetzung A6).

Zielmodule:
  - financial_reports.py
  - rohware_sammelabrechnung.py
  - sales_invoice_einvoice.py

Strategie: direkte Helper-/Endpoint-Aufrufe mit MagicMock-DB (keine Vollsuite).
"""
from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.api.v1.endpoints import financial_reports as fr
from app.api.v1.endpoints import rohware_sammelabrechnung as sa
from app.api.v1.endpoints import sales_invoice_einvoice as ei
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.main import app

pytestmark = pytest.mark.unit

TENANT = "00000000-0000-0000-0000-000000000001"
HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-Id": TENANT}
client = TestClient(app, raise_server_exceptions=False)


def _override(db: MagicMock):
    def _db():
        yield db

    def _tenant():
        return TENANT

    app.dependency_overrides[get_db] = _db
    app.dependency_overrides[get_tenant_id] = _tenant


def _clear_overrides():
    app.dependency_overrides.pop(get_db, None)
    app.dependency_overrides.pop(get_tenant_id, None)


# ── financial_reports helpers + export branches ───────────────────────────────


def test_fr_empty_helpers_and_report_to_rows():
    bs = fr._empty_balance_sheet("2026-03", date(2026, 3, 31))
    assert bs.is_balanced is True
    assert bs.total_assets == Decimal("0.00")

    pl = fr._empty_profit_loss("2026-03")
    assert pl.net_income == Decimal("0.00")

    bwa = fr._empty_bwa("2026-03")
    assert bwa.items == []

    item_a = fr.BalanceSheetItem(
        account_number="1000", account_name="Kasse", account_type="ASSET", balance=Decimal("10")
    )
    item_liab = fr.BalanceSheetItem(
        account_number="1600", account_name="Kreditor", account_type="LIABILITY", balance=Decimal("4")
    )
    item_l = fr.BalanceSheetItem(
        account_number="3000", account_name="EK", account_type="EQUITY", balance=Decimal("6")
    )
    filled = fr.BalanceSheet(
        period="2026-03",
        as_of_date=date(2026, 3, 31),
        assets=[item_a],
        liabilities=[item_liab],
        equity=[item_l],
        total_assets=Decimal("10"),
        total_liabilities=Decimal("4"),
        total_equity=Decimal("6"),
        is_balanced=True,
    )
    rows_bs = fr._report_to_rows("balance-sheet", filled)
    assert any("Aktiva" in r[0] for r in rows_bs)

    pl_filled = fr.ProfitLoss(
        period="2026-03",
        revenue=[fr.ProfitLossItem(account_number="4000", account_name="Erlös", account_type="REVENUE", amount=Decimal("5"))],
        expenses=[fr.ProfitLossItem(account_number="5000", account_name="Aufwand", account_type="EXPENSE", amount=Decimal("2"))],
        total_revenue=Decimal("5"),
        total_expenses=Decimal("2"),
        net_income=Decimal("3"),
    )
    rows_pl = fr._report_to_rows("profit-loss", pl_filled)
    assert any("Aufwendungen" in r[0] for r in rows_pl)

    bwa_item = fr.BWAItem(
        position="1",
        description="Umsatz",
        current_period=Decimal("1"),
        previous_period=Decimal("0"),
        year_to_date=Decimal("1"),
        percentage=Decimal("100"),
    )
    bwa_filled = fr.BWA(
        period="2026-03",
        items=[bwa_item],
        total_revenue=Decimal("1"),
        total_costs=Decimal("0"),
        net_result=Decimal("1"),
    )
    rows_bwa = fr._report_to_rows("bwa", bwa_filled)
    assert len(rows_bwa) >= 3


@pytest.mark.asyncio
async def test_fr_export_excel_and_pdf_and_unknown():
    db = MagicMock()
    empty = fr._empty_balance_sheet("2026-03", date(2026, 3, 31))
    with patch.object(fr, "get_balance_sheet", return_value=empty):
        excel = await fr.export_report("balance-sheet", "2026-03", "excel", TENANT, db)
        assert excel.media_type and "spreadsheet" in excel.media_type

        pdf = await fr.export_report("balance-sheet", "2026-03", "pdf", TENANT, db)
        assert pdf.media_type == "application/pdf"

        with pytest.raises(HTTPException) as exc:
            await fr.export_report("nope", "2026-03", "json", TENANT, db)
        assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_fr_core_report_handlers_with_rows_and_fallbacks():
    from sqlalchemy.exc import OperationalError, ProgrammingError

    db = MagicMock()
    db.execute.return_value.fetchall.return_value = [
        ("1000", "Kasse", "ASSET", None, 100, 0),
        ("2000", "Kreditor", "LIABILITY", None, 0, 40),
        ("3000", "Eigenkapital", "EQUITY", None, 0, 60),
        ("9999", "Other", "OTHER", None, 5, 5),  # zero-ish after skip rules
    ]
    bs = await fr.get_balance_sheet("2026-03", None, TENANT, db)
    assert bs.total_assets == Decimal("100")
    assert len(bs.assets) == 1
    assert len(bs.liabilities) == 1
    assert len(bs.equity) == 1

    db_pl = MagicMock()
    db_pl.execute.return_value.fetchall.side_effect = [
        [("4000", "Umsatz", "REVENUE", 200, 0)],
        [("5000", "Waren", "EXPENSE", 50, 0)],
    ]
    pl = await fr.get_profit_loss("2026-03", TENANT, db_pl)
    assert pl.total_revenue == Decimal("200")
    assert pl.total_expenses == Decimal("50")
    assert pl.net_income == Decimal("150")

    # BWA baut auf get_profit_loss; leere Zeilen reichen fuer Happy-Path
    db_bwa = MagicMock()
    db_bwa.execute.return_value.fetchall.return_value = []
    bwa = await fr.get_bwa("2026-03", TENANT, db_bwa)
    assert bwa.period == "2026-03"
    assert len(bwa.items) >= 4

    # Januar -> Vorperiode Dezember Vorjahr
    bwa_jan = await fr.get_bwa("2026-01", TENANT, db_bwa)
    assert bwa_jan.period == "2026-01"

    db_dd = MagicMock()
    db_dd.execute.return_value.fetchall.return_value = [
        ("ln1", "je1", "acc1", 10, 0, "desc", "ref", "JE-1", date(2026, 3, 2), "Buchung"),
    ]
    lines = await fr.get_report_drilldown("1000", "2026-03", TENANT, 50, db_dd)
    assert lines[0]["entry_number"] == "JE-1"

    db_err = MagicMock()
    db_err.execute.side_effect = OperationalError("stmt", {}, Exception("x"))
    empty_bs = await fr.get_balance_sheet("2026-03", None, TENANT, db_err)
    assert empty_bs.total_assets == Decimal("0.00")
    empty_pl = await fr.get_profit_loss("2026-03", TENANT, db_err)
    assert empty_pl.total_revenue == Decimal("0.00")
    empty_dd = await fr.get_report_drilldown("1000", "2026-03", TENANT, 10, db_err)
    assert empty_dd == []

    with patch.object(fr, "get_profit_loss", side_effect=ProgrammingError("stmt", {}, Exception("x"))):
        empty_bwa = await fr.get_bwa("2026-03", TENANT, MagicMock())
        assert empty_bwa.items == []

    with patch.object(fr, "get_profit_loss", side_effect=RuntimeError("unexpected")):
        soft_bwa = await fr.get_bwa("2026-03", TENANT, MagicMock())
        assert soft_bwa.items == []

    # export json + profit-loss/bwa branches + generic exception path
    with patch.object(fr, "get_profit_loss", return_value=fr._empty_profit_loss("2026-03")):
        js = await fr.export_report("profit-loss", "2026-03", "json", TENANT, db)
        assert js["format"] == "json"
    with patch.object(fr, "get_bwa", return_value=fr._empty_bwa("2026-03")):
        js2 = await fr.export_report("bwa", "2026-03", "json", TENANT, db)
        assert js2["report_type"] == "bwa"
    with patch.object(fr, "get_balance_sheet", side_effect=RuntimeError("boom")):
        with pytest.raises(HTTPException) as boom:
            await fr.export_report("balance-sheet", "2026-03", "json", TENANT, db)
        assert boom.value.status_code == 500

    # Beleg-Drilldown DB-Fehler -> 503
    db_beleg_err = MagicMock()
    db_beleg_err.execute.side_effect = OperationalError("stmt", {}, Exception("x"))
    with pytest.raises(HTTPException) as beleg503:
        await fr.get_beleg_drilldown("je-x", TENANT, db_beleg_err)
    assert beleg503.value.status_code == 503


@pytest.mark.asyncio
async def test_fr_periodenvergleich_and_beleg_drilldown():
    db = MagicMock()
    db.execute.return_value.fetchall.return_value = [
        ("4000", "Erlöse", "REVENUE", 100.0, 80.0),
        ("5000", "Aufwand", "EXPENSE", 40.0, 0.0),
    ]
    result = await fr.get_periodenvergleich("2026-03", "2026-02", "4", TENANT, 50, db)
    assert result["count"] == 2
    assert result["zeilen"][0]["delta_eur"] == 20.0

    db2 = MagicMock()
    db2.execute.return_value.fetchall.side_effect = Exception("boom")
    # OperationalError path: patch execute to raise ProgrammingError-like
    from sqlalchemy.exc import OperationalError

    db3 = MagicMock()
    db3.execute.side_effect = OperationalError("stmt", {}, Exception("db"))
    soft = await fr.get_periodenvergleich("2026-03", "2026-02", None, TENANT, 10, db3)
    assert soft["count"] == 0

    header = (
        "je-1",
        "JE-1",
        date(2026, 3, 1),
        "Test",
        "posted",
        10.0,
        10.0,
        "manual",
        "settlement",
        "REF-1",
        "2026-03",
    )
    db4 = MagicMock()

    def _exec(sql, params=None):
        result = MagicMock()
        sql_s = str(sql)
        if "journal_entry_lines" in sql_s:
            result.fetchall.return_value = [
                ("ln-1", "1000", "Kasse", 10.0, 0.0, "Zeile", "R1"),
            ]
        else:
            result.fetchone.return_value = header
        return result

    db4.execute.side_effect = _exec
    beleg = await fr.get_beleg_drilldown("je-1", TENANT, db4)
    assert beleg["entry_number"] == "JE-1"
    assert len(beleg["lines"]) == 1

    db5 = MagicMock()
    db5.execute.return_value.fetchone.return_value = None
    with pytest.raises(HTTPException) as missing:
        await fr.get_beleg_drilldown("missing", TENANT, db5)
    assert missing.value.status_code == 404


# ── rohware_sammelabrechnung mocked lifecycle ─────────────────────────────────


def test_sa_list_create_calculate_book_delete():
    db = MagicMock()

    # list: mappings().all()
    list_row = {
        "id": "s1",
        "bezeichnung": "A",
        "abrechnungsperiode": "2026-08",
        "status": "ENTWURF",
        "positionen": [],
        "summe_menge_kg": 0,
        "summe_betrag_eur": 0,
        "erstellt_am": "2026-08-01",
    }
    db.execute.return_value.mappings.return_value.all.return_value = [list_row]
    assert sa.list_sammelabrechnungen(db, TENANT)[0]["id"] == "s1"

    # list exception → []
    db_fail = MagicMock()
    db_fail.execute.side_effect = RuntimeError("no table")
    assert sa.list_sammelabrechnungen(db_fail, TENANT) == []

    payload = sa.SammelabrechnungCreate(
        bezeichnung="Test",
        abrechnungsperiode="2026-08",
        harvest_acceptance_ids=["ha-1", "ha-2"],
    )
    created = sa.create_sammelabrechnung(payload, db, TENANT)
    assert created["status"] == "ENTWURF"
    assert created["id"]

    # create with DB error still returns object
    db_err = MagicMock()
    db_err.execute.side_effect = RuntimeError("insert fail")
    created2 = sa.create_sammelabrechnung(payload, db_err, TENANT)
    assert created2["status"] == "ENTWURF"

    # berechnen with header + HA rows
    ha_ids = ["ha-1", "ha-2"]
    header = {
        "bezeichnung": "S",
        "abrechnungsperiode": "2026-08",
        "harvest_acceptance_ids": ha_ids,
        "erstellt_am": "2026-08-01",
    }
    ha_row = {
        "lieferant_id": "L1",
        "artikel_nr": "WEI",
        "menge_netto_kg": 2000.0,
        "qualitaet_feuchte": 14.0,
        "qualitaet_besatz": 1.0,
        "preis_eur_t": 200.0,
    }

    def _berechnen_exec(sql, params=None):
        result = MagicMock()
        sql_s = str(sql)
        if "harvest_acceptances" in sql_s:
            result.mappings.return_value.first.return_value = ha_row
        elif "SELECT *" in sql_s or "sammelabrechnungen" in sql_s and "UPDATE" not in sql_s:
            result.mappings.return_value.first.return_value = header
        else:
            result.mappings.return_value.first.return_value = None
        return result

    db_calc = MagicMock()
    db_calc.execute.side_effect = _berechnen_exec
    calc = sa.berechnen("sid-1", db_calc, TENANT)
    assert calc["status"] == "BERECHNET"
    assert calc["summe_menge_kg"] == 4000.0
    assert calc["summe_betrag_eur"] == 800.0  # 2t * 200 * 2 positions

    # buchen with OP path
    db_book = MagicMock()
    db_book.execute.return_value.fetchone.return_value = (500.0, "Sammel")
    booked = sa.buchen("sid-1", db_book, TENANT)
    assert booked["gebucht"] is True
    assert "buchungsnr" in booked

    # delete ENTWURF
    db_del = MagicMock()
    db_del.execute.return_value.mappings.return_value.first.return_value = {"status": "ENTWURF"}
    resp = sa.delete_sammelabrechnung("sid-1", db_del, TENANT)
    assert resp.status_code == 204

    # delete not found / wrong status / db unavailable
    db_nf = MagicMock()
    db_nf.execute.return_value.mappings.return_value.first.return_value = None
    with pytest.raises(HTTPException) as nf:
        sa.delete_sammelabrechnung("x", db_nf, TENANT)
    assert nf.value.status_code == 404

    db_conflict = MagicMock()
    db_conflict.execute.return_value.mappings.return_value.first.return_value = {"status": "GEBUCHT"}
    with pytest.raises(HTTPException) as conflict:
        sa.delete_sammelabrechnung("x", db_conflict, TENANT)
    assert conflict.value.status_code == 409

    db_unavail = MagicMock()
    db_unavail.execute.side_effect = RuntimeError("down")
    with pytest.raises(HTTPException) as unavail:
        sa.delete_sammelabrechnung("x", db_unavail, TENANT)
    assert unavail.value.status_code == 503


def test_sa_delete_via_http():
    db = MagicMock()
    db.execute.return_value.mappings.return_value.first.return_value = {"status": "ENTWURF"}
    _override(db)
    try:
        resp = client.delete(f"/api/v1/agrar/sammelabrechnung/{uuid.uuid4()}", headers=HEADERS)
        assert resp.status_code in (204, 404, 503), resp.text
    finally:
        _clear_overrides()


# ── sales_invoice_einvoice helpers + happy generation ─────────────────────────


def test_ei_helpers_and_generate_paths():
    invoice = {
        "number": "RE-1",
        "date": "2026-03-01",
        "dueDate": "2026-03-31",
        "paymentTerms": "net14",
        "customerId": "C1",
        "subtotalNet": 100,
        "totalTax": 19,
        "totalGross": 119,
        "lines": [{"article": "Weizen", "qty": 2, "price": 50, "vatRate": 19}],
    }
    supplier = {"name": "VALEO", "country_code": "DE"}
    customer = {"name": "Kunde", "country_code": "DE"}
    overrides = ei.EInvoiceExportRequest(
        buyer_reference="LEITWEG-1",
        supplier={"vat_id": "DE123"},  # type: ignore[arg-type]
        customer={"city": "Berlin"},  # type: ignore[arg-type]
    )
    ein = ei._invoice_to_einvoice_input(invoice, supplier, customer, overrides)
    assert ein["invoice_number"] == "RE-1"
    assert len(ein["lines"]) == 1
    assert ein["buyer_reference"] == "LEITWEG-1"
    assert ein["supplier"]["vat_id"] == "DE123"
    assert ein["customer"]["city"] == "Berlin"

    db = MagicMock()
    db.execute.return_value.fetchone.return_value = (
        "Firma",
        "Str. 1",
        "26122",
        "Oldenburg",
        "DE",
        "DE99",
        "a@b.de",
    )
    party = ei._resolve_supplier_party(db, TENANT)
    assert party["city"] == "Oldenburg"

    db_fail = MagicMock()
    db_fail.execute.side_effect = RuntimeError("no tenants")
    fallback = ei._resolve_supplier_party(db_fail, TENANT)
    assert fallback["name"] == TENANT

    with patch.object(ei, "register_artifact", side_effect=RuntimeError("gobd")):
        ei._register_xml_artifact(db, TENANT, "RE-1", "<xml/>", "x.xml", "xrechnung")

    with patch.object(ei, "register_artifact") as reg:
        ei._register_xml_artifact(db, TENANT, "RE-1", "<xml/>", "x.xml", "xrechnung")
        reg.assert_called_once()

    with patch.object(ei, "_load_sales_invoice", return_value=invoice), patch.object(
        ei, "_resolve_supplier_party", return_value=supplier
    ), patch.object(ei, "_resolve_customer_party", return_value=customer), patch.object(
        ei, "build_xrechnung_xml", return_value="<Invoice/>"
    ), patch.object(ei, "_register_xml_artifact"):
        resp = ei.generate_xrechnung("RE-1", ei.EInvoiceExportRequest(), db, TENANT)
        assert resp.media_type == "application/xml"
        assert b"<Invoice/>" in resp.body

        get_resp = ei.get_xrechnung("RE-1", db, TENANT)
        assert get_resp.media_type == "application/xml"

    with patch.object(ei, "_load_sales_invoice", return_value=invoice), patch.object(
        ei, "_resolve_supplier_party", return_value=supplier
    ), patch.object(ei, "_resolve_customer_party", return_value=customer), patch.object(
        ei, "build_zugferd_pdf", return_value=b"%PDF-1.4"
    ), patch(
        "app.services.einvoice_generator.build_zugferd_cii_xml", return_value="<CII/>"
    ), patch.object(ei, "_register_xml_artifact"):
        z = ei.generate_zugferd("RE-1", ei.EInvoiceExportRequest(), db, TENANT)
        assert z.media_type == "application/pdf"

    with patch.object(ei, "_load_sales_invoice", return_value=invoice), patch.object(
        ei, "_resolve_supplier_party", return_value=supplier
    ), patch.object(ei, "_resolve_customer_party", return_value=customer), patch.object(
        ei, "build_zugferd_pdf", side_effect=RuntimeError("missing factur-x")
    ):
        with pytest.raises(HTTPException) as zug:
            ei.generate_zugferd("RE-1", ei.EInvoiceExportRequest(), db, TENANT)
        assert zug.value.status_code == 503

    with patch.object(ei, "get_repository", return_value=MagicMock()), patch.object(
        ei, "get_from_store", return_value=None
    ):
        with pytest.raises(HTTPException) as miss:
            ei._load_sales_invoice(db, "MISSING")
        assert miss.value.status_code == 404
