"""Wave 83 — Unit-Tests fuer einvoice_generator, feed_production_chain_service,
finance_datev_service, closing_checklists_service (pure domain functions)."""

from __future__ import annotations

import pytest
from datetime import date, datetime
from types import SimpleNamespace


# ---------------------------------------------------------------------------
# Helpers — shared invoice fixture
# ---------------------------------------------------------------------------

def _make_invoice_input():
    supplier = {
        "name": "Agrar GmbH", "street": "Hauptstr. 1", "postal_code": "12345",
        "city": "Berlin", "country_code": "DE", "vat_id": "DE123456789",
        "email": "info@agrar.de",
    }
    customer = {
        "name": "Bauer AG", "street": "Dorfstr. 5", "postal_code": "54321",
        "city": "Hamburg", "country_code": "DE", "vat_id": "DE987654321",
        "email": "bauer@ag.de",
    }
    line = {
        "line_id": "1", "article": "Weizen", "description": "Winterweizen",
        "quantity": 100.0, "unit_code": "TNE", "unit_price_net": 200.0,
        "line_net_amount": 20000.0, "vat_rate_percent": 7.0, "vat_category_code": "S",
    }
    return {
        "invoice_number": "INV-2024-001",
        "invoice_date": "2024-01-15",
        "invoice_type_code": "380",
        "currency": "EUR",
        "supplier": supplier,
        "customer": customer,
        "lines": [line],
        "total_net": 20000.0,
        "total_vat": 1400.0,
        "total_gross": 21400.0,
        "payment_terms_text": "30 Tage netto",
        "payment_due_date": "2024-02-15",
        "buyer_reference": "PO-2024-001",
    }


# ---------------------------------------------------------------------------
# einvoice_generator — build_xrechnung_xml  (pure XML generation)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_build_xrechnung_xml_returns_string() -> None:
    from app.services.einvoice_generator import build_xrechnung_xml
    xml = build_xrechnung_xml(_make_invoice_input())
    assert isinstance(xml, str)


@pytest.mark.unit
def test_build_xrechnung_xml_has_xml_declaration() -> None:
    from app.services.einvoice_generator import build_xrechnung_xml
    xml = build_xrechnung_xml(_make_invoice_input())
    assert xml.startswith("<?xml")


@pytest.mark.unit
def test_build_xrechnung_xml_contains_invoice_number() -> None:
    from app.services.einvoice_generator import build_xrechnung_xml
    xml = build_xrechnung_xml(_make_invoice_input())
    assert "INV-2024-001" in xml


@pytest.mark.unit
def test_build_xrechnung_xml_contains_supplier_name() -> None:
    from app.services.einvoice_generator import build_xrechnung_xml
    xml = build_xrechnung_xml(_make_invoice_input())
    assert "Agrar GmbH" in xml


@pytest.mark.unit
def test_build_xrechnung_xml_contains_currency() -> None:
    from app.services.einvoice_generator import build_xrechnung_xml
    xml = build_xrechnung_xml(_make_invoice_input())
    assert "EUR" in xml


@pytest.mark.unit
def test_build_zugferd_cii_xml_returns_string() -> None:
    from app.services.einvoice_generator import build_zugferd_cii_xml
    xml = build_zugferd_cii_xml(_make_invoice_input())
    assert isinstance(xml, str)


@pytest.mark.unit
def test_build_zugferd_cii_xml_contains_invoice_number() -> None:
    from app.services.einvoice_generator import build_zugferd_cii_xml
    xml = build_zugferd_cii_xml(_make_invoice_input())
    assert "INV-2024-001" in xml


@pytest.mark.unit
def test_build_zugferd_cii_xml_contains_xml_header() -> None:
    from app.services.einvoice_generator import build_zugferd_cii_xml
    xml = build_zugferd_cii_xml(_make_invoice_input())
    assert xml.startswith("<?xml")


# ---------------------------------------------------------------------------
# feed_production_chain_service — compute_verbrauch, fehlende_komponenten
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_compute_verbrauch_basic() -> None:
    from app.services.feed_production_chain_service import compute_verbrauch
    k1 = SimpleNamespace(komponente_name="Weizen", anteil=0.6, einzelfutter_id="EF-001", sortierung=1)
    k2 = SimpleNamespace(komponente_name="Mais", anteil=0.4, einzelfutter_id="EF-002", sortierung=2)
    result = compute_verbrauch(10.0, [k1, k2])
    assert isinstance(result, list)
    assert len(result) == 2


@pytest.mark.unit
def test_compute_verbrauch_amounts_sum_to_total() -> None:
    from app.services.feed_production_chain_service import compute_verbrauch
    k1 = SimpleNamespace(komponente_name="Weizen", anteil=0.5, einzelfutter_id="EF-001", sortierung=1)
    k2 = SimpleNamespace(komponente_name="Mais", anteil=0.5, einzelfutter_id="EF-002", sortierung=2)
    result = compute_verbrauch(10.0, [k1, k2])
    total = sum(r["menge_t"] for r in result)
    assert total == pytest.approx(10.0)


@pytest.mark.unit
def test_compute_verbrauch_result_has_required_keys() -> None:
    from app.services.feed_production_chain_service import compute_verbrauch
    k1 = SimpleNamespace(komponente_name="Weizen", anteil=1.0, einzelfutter_id="EF-001", sortierung=1)
    result = compute_verbrauch(5.0, [k1])
    for key in ("einzelfutter_id", "name", "anteil", "menge_t"):
        assert key in result[0]


@pytest.mark.unit
def test_compute_verbrauch_proportional_amounts() -> None:
    from app.services.feed_production_chain_service import compute_verbrauch
    k1 = SimpleNamespace(komponente_name="Weizen", anteil=0.5, einzelfutter_id="EF-001", sortierung=1)
    result = compute_verbrauch(10.0, [k1])
    assert result[0]["menge_t"] == pytest.approx(5.0)


@pytest.mark.unit
def test_fehlende_komponenten_sufficient_stock_empty() -> None:
    from app.services.feed_production_chain_service import compute_verbrauch, fehlende_komponenten
    k1 = SimpleNamespace(komponente_name="Weizen", anteil=1.0, einzelfutter_id="EF-001", sortierung=1)
    snap = compute_verbrauch(5.0, [k1])
    result = fehlende_komponenten(snap, {"EF-001": 100})
    assert result == []


@pytest.mark.unit
def test_fehlende_komponenten_insufficient_stock_reported() -> None:
    from app.services.feed_production_chain_service import compute_verbrauch, fehlende_komponenten
    k1 = SimpleNamespace(komponente_name="Mais", anteil=1.0, einzelfutter_id="EF-002", sortierung=1)
    snap = compute_verbrauch(10.0, [k1])
    result = fehlende_komponenten(snap, {"EF-002": 0})
    assert len(result) == 1
    assert "Mais" in result[0]


@pytest.mark.unit
def test_fehlende_komponenten_missing_from_stock_reported() -> None:
    from app.services.feed_production_chain_service import compute_verbrauch, fehlende_komponenten
    k1 = SimpleNamespace(komponente_name="Soja", anteil=1.0, einzelfutter_id="EF-003", sortierung=1)
    snap = compute_verbrauch(3.0, [k1])
    result = fehlende_komponenten(snap, {})  # EF-003 not in stock dict at all
    assert len(result) >= 1


# ---------------------------------------------------------------------------
# finance_datev_service — datev_row, datev_csv  (pure DATEV export)
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_datev_row_returns_list() -> None:
    from app.services.finance_datev_service import datev_row
    row = datev_row(1500.50, "debitoren", date(2024, 1, 15), "RE-001", "Weizen")
    assert isinstance(row, list)


@pytest.mark.unit
def test_datev_row_decimal_comma_format() -> None:
    from app.services.finance_datev_service import datev_row
    row = datev_row(1500.50, "debitoren", date(2024, 1, 15), "RE-001", "Weizen")
    # DATEV format uses comma as decimal separator
    assert "," in row[0]
    assert "." not in row[0]


@pytest.mark.unit
def test_datev_row_date_formatted() -> None:
    from app.services.finance_datev_service import datev_row
    row = datev_row(100.0, "debitoren", date(2024, 3, 5), "RE-002", "Test")
    assert "05032024" in row[4]


@pytest.mark.unit
def test_datev_row_kreditoren_type() -> None:
    from app.services.finance_datev_service import datev_row
    row_deb = datev_row(100.0, "debitoren", date(2024, 1, 1), "BE-001", "Test")
    row_kred = datev_row(100.0, "kreditoren", date(2024, 1, 1), "BE-001", "Test")
    # Konten differ between debitor and kreditor
    assert row_deb[2] != row_kred[2] or row_deb[3] != row_kred[3]


@pytest.mark.unit
def test_datev_csv_has_header() -> None:
    from app.services.finance_datev_service import datev_csv, datev_row
    row = datev_row(500.0, "debitoren", date(2024, 1, 15), "RE-003", "Hafer")
    csv_out = datev_csv([row])
    first_line = csv_out.split("\n")[0]
    assert "Umsatz" in first_line or "Konto" in first_line


@pytest.mark.unit
def test_datev_csv_contains_amount() -> None:
    from app.services.finance_datev_service import datev_csv, datev_row
    row = datev_row(9999.99, "debitoren", date(2024, 1, 15), "RE-004", "Roggen")
    csv_out = datev_csv([row])
    assert "9999" in csv_out


# ---------------------------------------------------------------------------
# closing_checklists_service — build_closing_checklist_response  (pure mapping)
# ---------------------------------------------------------------------------

def _make_checklist_row(status="approved"):
    now = datetime.now()
    return ("CL-001", "2024-01", "monatsabschluss", "TPL-001", status,
            75.0, 20, 15, 10, 10, None, now, now, None, None)


@pytest.mark.unit
def test_build_closing_checklist_response_returns_response() -> None:
    from app.services.closing_checklists_service import build_closing_checklist_response, ClosingChecklistResponse
    result = build_closing_checklist_response(_make_checklist_row(), items_data=[])
    assert isinstance(result, ClosingChecklistResponse)


@pytest.mark.unit
def test_build_closing_checklist_response_id_mapped() -> None:
    from app.services.closing_checklists_service import build_closing_checklist_response
    result = build_closing_checklist_response(_make_checklist_row(), items_data=[])
    assert result.id == "CL-001"


@pytest.mark.unit
def test_build_closing_checklist_approved_can_close() -> None:
    from app.services.closing_checklists_service import build_closing_checklist_response
    result = build_closing_checklist_response(_make_checklist_row("approved"), items_data=[])
    assert result.approval_can_close is True


@pytest.mark.unit
def test_build_closing_checklist_pending_cannot_close() -> None:
    from app.services.closing_checklists_service import build_closing_checklist_response
    result = build_closing_checklist_response(_make_checklist_row("pending"), items_data=[])
    assert result.approval_can_close is False


@pytest.mark.unit
def test_build_closing_checklist_progress_percentage_mapped() -> None:
    from app.services.closing_checklists_service import build_closing_checklist_response
    result = build_closing_checklist_response(_make_checklist_row(), items_data=[])
    assert result.progress_percentage == pytest.approx(75.0)


@pytest.mark.unit
def test_build_closing_checklist_items_data_passed_through() -> None:
    from app.services.closing_checklists_service import build_closing_checklist_response
    items = [{"id": "ITEM-001", "name": "Kontenabstimmung", "status": "done"}]
    result = build_closing_checklist_response(_make_checklist_row(), items_data=items)
    assert result.items == items
