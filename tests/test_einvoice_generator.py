"""
Tests für Slice-006 E-Rechnung XRechnung/ZUGFeRD Generator.

Verifiziert EN-16931-Pflichtfelder (XRechnung 3.0 UBL 2.1 und ZUGFeRD 2.x CII).
"""
from __future__ import annotations

import re
from xml.etree import ElementTree as ET

import pytest

from app.services.einvoice_generator import (
    EInvoiceInput,
    build_xrechnung_xml,
    build_zugferd_cii_xml,
    set_xrechnung_generator,
)


NS_UBL = {
    "ubl": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}

NS_CII = {
    "rsm": "urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100",
    "ram": "urn:un:unece:uncefact:data:standard:ReusableAggregateBusinessInformationEntity:100",
    "udt": "urn:un:unece:uncefact:data:standard:UnqualifiedDataType:100",
}


@pytest.fixture
def sample_invoice() -> EInvoiceInput:
    """Beispiel-Verkaufsrechnung mit zwei Positionen und 19% USt."""
    return {
        "invoice_number": "RE-2026-00042",
        "invoice_date": "2026-05-27",
        "invoice_type_code": "380",
        "currency": "EUR",
        "buyer_reference": "Bestellung-12345",
        "payment_due_date": "2026-06-26",
        "payment_terms_text": "Zahlbar innerhalb 30 Tagen ohne Abzug",
        "supplier": {
            "name": "VALEO Agrar Handel GmbH",
            "street": "Hauptstr. 1",
            "postal_code": "10115",
            "city": "Berlin",
            "country_code": "DE",
            "vat_id": "DE123456789",
            "email": "rechnung@valeo-agrar.de",
        },
        "customer": {
            "name": "Landwirt Müller GbR",
            "street": "Dorfstr. 5",
            "postal_code": "21339",
            "city": "Lüneburg",
            "country_code": "DE",
            "vat_id": "DE987654321",
        },
        "lines": [
            {
                "line_id": "1",
                "article": "Weizensaatgut Premium",
                "description": "Weizensaatgut Premium, 25 kg",
                "quantity": 10.0,
                "unit_code": "KGM",
                "unit_price_net": 50.00,
                "line_net_amount": 500.00,
                "vat_rate_percent": 7.0,
                "vat_category_code": "S",
            },
            {
                "line_id": "2",
                "article": "Pflanzenschutzmittel",
                "description": "Fungizid 5L",
                "quantity": 4.0,
                "unit_code": "LTR",
                "unit_price_net": 125.00,
                "line_net_amount": 500.00,
                "vat_rate_percent": 19.0,
                "vat_category_code": "S",
            },
        ],
        "total_net": 1000.00,
        "total_vat": 130.00,  # 7% von 500 = 35, 19% von 500 = 95
        "total_gross": 1130.00,
    }


class TestXRechnungBuilder:
    """Slice-006: EN-16931-Pflichtfelder für UBL-XRechnung."""

    def test_xml_is_well_formed(self, sample_invoice):
        xml = build_xrechnung_xml(sample_invoice)
        root = ET.fromstring(xml)
        assert root.tag.endswith("}Invoice")

    def test_customization_id_is_xrechnung_3(self, sample_invoice):
        xml = build_xrechnung_xml(sample_invoice)
        root = ET.fromstring(xml)
        cust = root.find("cbc:CustomizationID", NS_UBL)
        assert cust is not None
        assert "xrechnung_3.0" in cust.text

    def test_bt1_invoice_number(self, sample_invoice):
        xml = build_xrechnung_xml(sample_invoice)
        root = ET.fromstring(xml)
        bt1 = root.find("cbc:ID", NS_UBL)
        assert bt1 is not None
        assert bt1.text == "RE-2026-00042"

    def test_bt2_issue_date(self, sample_invoice):
        xml = build_xrechnung_xml(sample_invoice)
        root = ET.fromstring(xml)
        bt2 = root.find("cbc:IssueDate", NS_UBL)
        assert bt2 is not None
        assert bt2.text == "2026-05-27"

    def test_bt3_invoice_type_code_380(self, sample_invoice):
        xml = build_xrechnung_xml(sample_invoice)
        root = ET.fromstring(xml)
        bt3 = root.find("cbc:InvoiceTypeCode", NS_UBL)
        assert bt3 is not None
        assert bt3.text == "380"

    def test_bt5_currency_eur(self, sample_invoice):
        xml = build_xrechnung_xml(sample_invoice)
        root = ET.fromstring(xml)
        bt5 = root.find("cbc:DocumentCurrencyCode", NS_UBL)
        assert bt5 is not None
        assert bt5.text == "EUR"

    def test_bt10_buyer_reference(self, sample_invoice):
        xml = build_xrechnung_xml(sample_invoice)
        root = ET.fromstring(xml)
        bt10 = root.find("cbc:BuyerReference", NS_UBL)
        assert bt10 is not None
        assert bt10.text == "Bestellung-12345"

    def test_bt31_supplier_vat_id(self, sample_invoice):
        xml = build_xrechnung_xml(sample_invoice)
        assert "<cbc:CompanyID>DE123456789</cbc:CompanyID>" in xml

    def test_bt48_customer_vat_id(self, sample_invoice):
        xml = build_xrechnung_xml(sample_invoice)
        assert "<cbc:CompanyID>DE987654321</cbc:CompanyID>" in xml

    def test_legal_monetary_total_amounts(self, sample_invoice):
        xml = build_xrechnung_xml(sample_invoice)
        root = ET.fromstring(xml)
        totals = root.find("cac:LegalMonetaryTotal", NS_UBL)
        assert totals is not None
        assert totals.find("cbc:LineExtensionAmount", NS_UBL).text == "1000.00"
        assert totals.find("cbc:TaxExclusiveAmount", NS_UBL).text == "1000.00"
        assert totals.find("cbc:TaxInclusiveAmount", NS_UBL).text == "1130.00"
        assert totals.find("cbc:PayableAmount", NS_UBL).text == "1130.00"

    def test_tax_subtotals_per_vat_rate(self, sample_invoice):
        xml = build_xrechnung_xml(sample_invoice)
        root = ET.fromstring(xml)
        tax_total = root.find("cac:TaxTotal", NS_UBL)
        assert tax_total is not None
        subtotals = tax_total.findall("cac:TaxSubtotal", NS_UBL)
        assert len(subtotals) == 2
        rates = sorted(
            float(s.find("cac:TaxCategory/cbc:Percent", NS_UBL).text)
            for s in subtotals
        )
        assert rates == [7.0, 19.0]

    def test_invoice_lines_count_and_fields(self, sample_invoice):
        xml = build_xrechnung_xml(sample_invoice)
        root = ET.fromstring(xml)
        lines = root.findall("cac:InvoiceLine", NS_UBL)
        assert len(lines) == 2
        ln1 = lines[0]
        assert ln1.find("cbc:ID", NS_UBL).text == "1"
        qty = ln1.find("cbc:InvoicedQuantity", NS_UBL)
        assert qty is not None
        assert qty.get("unitCode") == "KGM"
        assert ln1.find("cbc:LineExtensionAmount", NS_UBL).text == "500.00"

    def test_external_generator_hook(self, sample_invoice):
        """External generator wird verwendet, wenn registriert; bei Exception → Fallback."""
        def fake_generator(_data):
            return "<custom-marker/>"
        set_xrechnung_generator(fake_generator)
        try:
            assert build_xrechnung_xml(sample_invoice) == "<custom-marker/>"
        finally:
            set_xrechnung_generator(None)
        xml = build_xrechnung_xml(sample_invoice)
        assert "<custom-marker/>" not in xml
        assert xml.startswith("<?xml")

    def test_xml_escapes_special_characters(self):
        data: EInvoiceInput = {
            "invoice_number": "RE&2026<TEST>",
            "invoice_date": "2026-05-27",
            "currency": "EUR",
            "supplier": {"name": "A & B GmbH"},
            "customer": {"name": "C \"Quote\" D"},
            "lines": [],
            "total_net": 0,
            "total_vat": 0,
            "total_gross": 0,
        }
        xml = build_xrechnung_xml(data)
        ET.fromstring(xml)
        assert "&amp;" in xml
        assert "&lt;TEST&gt;" in xml


class TestZugferdCIIBuilder:
    """Slice-006: ZUGFeRD CII (EN 16931) für PDF/A-3-Embedding."""

    def test_cii_xml_is_well_formed(self, sample_invoice):
        xml = build_zugferd_cii_xml(sample_invoice)
        root = ET.fromstring(xml)
        assert root.tag.endswith("}CrossIndustryInvoice")

    def test_cii_guideline_is_en16931(self, sample_invoice):
        xml = build_zugferd_cii_xml(sample_invoice)
        assert "urn:cen.eu:en16931:2017" in xml

    def test_cii_document_id_and_type_code(self, sample_invoice):
        xml = build_zugferd_cii_xml(sample_invoice)
        root = ET.fromstring(xml)
        doc = root.find("rsm:ExchangedDocument", NS_CII)
        assert doc is not None
        assert doc.find("ram:ID", NS_CII).text == "RE-2026-00042"
        assert doc.find("ram:TypeCode", NS_CII).text == "380"

    def test_cii_issue_date_compact_format(self, sample_invoice):
        """ZUGFeRD verlangt YYYYMMDD-Format mit format='102'."""
        xml = build_zugferd_cii_xml(sample_invoice)
        m = re.search(r'format="102">(\d{8})</udt:DateTimeString>', xml)
        assert m is not None
        assert m.group(1) == "20260527"

    def test_cii_grand_total(self, sample_invoice):
        xml = build_zugferd_cii_xml(sample_invoice)
        assert "<ram:GrandTotalAmount>1130.00</ram:GrandTotalAmount>" in xml
        assert "<ram:LineTotalAmount>1000.00</ram:LineTotalAmount>" in xml

    def test_cii_invoice_lines(self, sample_invoice):
        xml = build_zugferd_cii_xml(sample_invoice)
        root = ET.fromstring(xml)
        txn = root.find("rsm:SupplyChainTradeTransaction", NS_CII)
        items = txn.findall("ram:IncludedSupplyChainTradeLineItem", NS_CII)
        assert len(items) == 2


class TestSalesInvoiceEndpoints:
    """Slice-006: API-Endpoints für SalesInvoice."""

    def test_router_registered_with_three_routes(self):
        from app.api.v1.endpoints.sales_invoice_einvoice import router
        paths = [r.path for r in router.routes]
        assert any("xrechnung" in p for p in paths)
        assert any("zugferd" in p for p in paths)
        assert len(router.routes) == 3

    def test_router_paths_include_invoice_number_param(self):
        from app.api.v1.endpoints.sales_invoice_einvoice import router
        paths = [r.path for r in router.routes]
        assert all("{invoice_number}" in p for p in paths)


class TestRounding:
    """Sicherstellen: Geldwerte werden mit 2 Nachkommastellen formatiert."""

    def test_rounding_half_up(self):
        data: EInvoiceInput = {
            "invoice_number": "X1",
            "invoice_date": "2026-05-27",
            "supplier": {"name": "S"},
            "customer": {"name": "C"},
            "lines": [
                {
                    "line_id": "1",
                    "article": "A",
                    "quantity": 1,
                    "unit_price_net": 0.105,
                    "line_net_amount": 0.105,
                    "vat_rate_percent": 19.0,
                    "vat_category_code": "S",
                },
            ],
            "total_net": 0.105,
            "total_vat": 0.020,
            "total_gross": 0.125,
        }
        xml = build_xrechnung_xml(data)
        assert "<cbc:PayableAmount currencyID=\"EUR\">0.13</cbc:PayableAmount>" in xml
