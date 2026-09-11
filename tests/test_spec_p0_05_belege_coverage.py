"""SPEC-P0-05: Beleg-/Report-Vertraege — echte App + Postgres, keine Mock-DB.

Pure Helper werden als Unit getestet. HTTP-Pfade brauchen `require_db` und
assertieren konkrete Statuscodes/Shapes.
"""
from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.api.v1.endpoints import financial_reports as fr
from app.api.v1.endpoints import sales_invoice_einvoice as ei
from app.api.v1.endpoints.sales_invoice_einvoice import EInvoiceExportRequest
from app.main import app

pytestmark = pytest.mark.unit

TENANT = "00000000-0000-0000-0000-000000000001"
HEADERS = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-Id": TENANT,
}
client = TestClient(app, raise_server_exceptions=False)

FR_BASE = "/api/v1/finance/financial-reports"
SA_BASE = "/api/v1/agrar/sammelabrechnung"
EI_BASE = "/api/v1/sales/invoices"
PERIOD = "2026-03"


# ── Pure Helpers (kein I/O) ───────────────────────────────────────────────────


def test_financial_report_empty_builders_and_row_flattening():
    bs = fr._empty_balance_sheet(PERIOD, date(2026, 3, 31))
    assert bs.is_balanced is True
    assert bs.total_assets == Decimal("0.00")
    assert bs.assets == []

    pl = fr._empty_profit_loss(PERIOD)
    assert pl.net_income == Decimal("0.00")

    bwa = fr._empty_bwa(PERIOD)
    assert bwa.items == []
    assert bwa.net_result == Decimal("0.00")

    filled = fr.BalanceSheet(
        period=PERIOD,
        as_of_date=date(2026, 3, 31),
        assets=[
            fr.BalanceSheetItem(
                account_number="1000",
                account_name="Kasse",
                account_type="ASSET",
                balance=Decimal("10.00"),
            )
        ],
        liabilities=[
            fr.BalanceSheetItem(
                account_number="1600",
                account_name="Kreditor",
                account_type="LIABILITY",
                balance=Decimal("4.00"),
            )
        ],
        equity=[
            fr.BalanceSheetItem(
                account_number="3000",
                account_name="EK",
                account_type="EQUITY",
                balance=Decimal("6.00"),
            )
        ],
        total_assets=Decimal("10.00"),
        total_liabilities=Decimal("4.00"),
        total_equity=Decimal("6.00"),
        is_balanced=True,
    )
    rows = fr._report_to_rows("balance-sheet", filled)
    assert rows[0][0].startswith("Bericht:")
    assert any(r[0] == "1000" for r in rows)
    assert any(r[0] == "1600" for r in rows)


def test_einvoice_input_mapping_from_sales_invoice_dict():
    invoice = {
        "number": "RE-100",
        "date": "2026-03-01",
        "dueDate": "2026-03-31",
        "paymentTerms": "net14",
        "customerId": "C1",
        "subtotalNet": 100,
        "totalTax": 19,
        "totalGross": 119,
        "lines": [{"article": "Weizen", "qty": 2, "price": 50, "vatRate": 19}],
    }
    supplier = {"name": "VALEO", "country_code": "DE", "vat_id": ""}
    customer = {"name": "Kunde", "country_code": "DE"}
    overrides = EInvoiceExportRequest(buyer_reference="LEITWEG-1")

    mapped = ei._invoice_to_einvoice_input(invoice, supplier, customer, overrides)
    assert mapped["invoice_number"] == "RE-100"
    assert mapped["buyer_reference"] == "LEITWEG-1"
    assert len(mapped["lines"]) == 1
    assert mapped["lines"][0]["quantity"] == 2.0
    assert mapped["total_gross"] == 119.0


# ── HTTP-Vertraege gegen laufende App + Postgres ──────────────────────────────


@pytest.mark.parametrize("path", ["/balance-sheet", "/profit-loss", "/bwa"])
def test_financial_report_endpoints_return_structured_payload(require_db, path):
    resp = client.get(
        f"{FR_BASE}{path}",
        params={"period": PERIOD, "tenant_id": "system"},
        headers=HEADERS,
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert isinstance(body, dict)
    assert body.get("period") == PERIOD or "period" in body or "items" in body or "assets" in body or "revenue" in body


def test_financial_report_export_json_and_unknown_type(require_db):
    ok = client.get(
        f"{FR_BASE}/export/balance-sheet",
        params={"period": PERIOD, "format": "json", "tenant_id": "system"},
        headers=HEADERS,
    )
    assert ok.status_code == 200, ok.text
    payload = ok.json()
    assert payload["report_type"] == "balance-sheet"
    assert payload["format"] == "json"
    assert "data" in payload

    bad = client.get(
        f"{FR_BASE}/export/not-a-report",
        params={"period": PERIOD, "format": "json"},
        headers=HEADERS,
    )
    assert bad.status_code == 400, bad.text


def test_financial_report_export_excel_and_pdf_bytes(require_db):
    excel = client.get(
        f"{FR_BASE}/export/balance-sheet",
        params={"period": PERIOD, "format": "excel", "tenant_id": "system"},
        headers=HEADERS,
    )
    assert excel.status_code == 200, excel.text
    assert "spreadsheet" in excel.headers.get("content-type", "")
    assert len(excel.content) > 32

    pdf = client.get(
        f"{FR_BASE}/export/balance-sheet",
        params={"period": PERIOD, "format": "pdf", "tenant_id": "system"},
        headers=HEADERS,
    )
    assert pdf.status_code == 200, pdf.text
    assert pdf.headers.get("content-type") == "application/pdf"
    assert pdf.content[:4] == b"%PDF"


def test_financial_report_periodenvergleich_and_missing_beleg(require_db):
    vgl = client.get(
        f"{FR_BASE}/periodenvergleich",
        params={
            "periode_aktuell": PERIOD,
            "periode_vergleich": "2026-02",
            "konto_klasse": "4",
        },
        headers=HEADERS,
    )
    assert vgl.status_code == 200, vgl.text
    body = vgl.json()
    assert "zeilen" in body
    assert "count" in body
    assert isinstance(body["zeilen"], list)

    missing = client.get(
        f"{FR_BASE}/beleg-drilldown/{uuid.uuid4()}",
        headers=HEADERS,
    )
    assert missing.status_code == 404, missing.text


def test_sammelabrechnung_validation_and_lifecycle(require_db):
    invalid = client.post(
        SA_BASE,
        json={
            "bezeichnung": "T",
            "abrechnungsperiode": "2026-08",
            "harvest_acceptance_ids": ["nur-eine"],
        },
        headers=HEADERS,
    )
    assert invalid.status_code == 422, invalid.text

    create = client.post(
        SA_BASE,
        json={
            "bezeichnung": f"IT-{uuid.uuid4().hex[:6]}",
            "abrechnungsperiode": "2026-08",
            "harvest_acceptance_ids": [str(uuid.uuid4()), str(uuid.uuid4())],
        },
        headers=HEADERS,
    )
    assert create.status_code == 201, create.text
    created = create.json()
    assert created["status"] == "ENTWURF"
    sid = created["id"]

    listed = client.get(SA_BASE, headers=HEADERS)
    assert listed.status_code == 200, listed.text
    assert isinstance(listed.json(), list)

    calc = client.post(f"{SA_BASE}/{sid}/berechnen", headers=HEADERS)
    assert calc.status_code == 200, calc.text
    assert calc.json()["status"] == "BERECHNET"

    book = client.post(f"{SA_BASE}/{sid}/buchen", headers=HEADERS)
    assert book.status_code == 200, book.text
    assert book.json().get("gebucht") is True

    # Nach Buchung kein Loeschen mehr
    deleted = client.delete(f"{SA_BASE}/{sid}", headers=HEADERS)
    assert deleted.status_code == 409, deleted.text


def test_sammelabrechnung_delete_draft(require_db):
    create = client.post(
        SA_BASE,
        json={
            "bezeichnung": f"DEL-{uuid.uuid4().hex[:6]}",
            "abrechnungsperiode": "2026-08",
            "harvest_acceptance_ids": [str(uuid.uuid4()), str(uuid.uuid4())],
        },
        headers=HEADERS,
    )
    assert create.status_code == 201, create.text
    sid = create.json()["id"]

    resp = client.delete(f"{SA_BASE}/{sid}", headers=HEADERS)
    assert resp.status_code == 204, resp.text

    missing = client.delete(f"{SA_BASE}/{uuid.uuid4()}", headers=HEADERS)
    assert missing.status_code == 404, missing.text


def test_einvoice_unknown_invoice_is_404(require_db):
    missing = f"INV-MISSING-{uuid.uuid4().hex[:8]}"
    for method, path in (
        ("POST", f"{EI_BASE}/{missing}/einvoice/xrechnung"),
        ("POST", f"{EI_BASE}/{missing}/einvoice/zugferd"),
        ("GET", f"{EI_BASE}/{missing}/einvoice/xrechnung"),
    ):
        if method == "POST":
            resp = client.post(path, json={}, headers=HEADERS)
        else:
            resp = client.get(path, headers=HEADERS)
        assert resp.status_code == 404, f"{method} {path}: {resp.status_code} {resp.text}"
