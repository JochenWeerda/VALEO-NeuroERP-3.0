"""
Unit tests for:
  - kontrakt_klassen.py  (varianten enum)
  - kontrakt_hedging.py  (mark-to-market P&L, cancel)
  - erechnung_import.py  (format detection)
  - price_calculation.py (sorte_klasse discount, kalkulationsweg)
"""
from __future__ import annotations

import asyncio
from datetime import date
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Helpers to build fake DB sessions that raise immediately (no table)
# ---------------------------------------------------------------------------

def _raising_db():
    """Return a SQLAlchemy Session mock that raises on execute()."""
    db = MagicMock()
    db.execute.side_effect = Exception("table does not exist")
    return db


def _empty_db():
    """Return a SQLAlchemy Session mock that returns no rows."""
    db = MagicMock()
    result = MagicMock()
    result.mappings.return_value.all.return_value = []
    result.first.return_value = None
    db.execute.return_value = result
    return db


TENANT = "test-tenant"


# ---------------------------------------------------------------------------
# kontrakt_klassen — varianten
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_kontrakt_klasse_varianten():
    """VALID_VARIANTEN must contain the four required values."""
    from app.api.v1.endpoints.kontrakt_klassen import VALID_VARIANTEN

    assert "FIXPREIS" in VALID_VARIANTEN
    assert "BASIS" in VALID_VARIANTEN
    assert "PRAEMIE" in VALID_VARIANTEN
    assert "POOLPREIS" in VALID_VARIANTEN


@pytest.mark.unit
def test_kontrakt_klasse_list_fallback():
    """list_kontrakt_klassen returns [] when DB raises (migration_hint path)."""
    from app.api.v1.endpoints.kontrakt_klassen import list_kontrakt_klassen

    result = list_kontrakt_klassen(db=_raising_db(), tenant_id=TENANT)
    assert result == []


@pytest.mark.unit
def test_kontrakt_klasse_create_returns_object():
    """create_kontrakt_klasse returns KontraktKlasseOut even if DB raises."""
    from app.api.v1.endpoints.kontrakt_klassen import KontraktKlasseCreate, create_kontrakt_klasse

    payload = KontraktKlasseCreate(
        name="Standard-Weizen",
        variante="FIXPREIS",
        parität="EXW",
    )
    result = create_kontrakt_klasse(payload=payload, db=_raising_db(), tenant_id=TENANT)
    assert result.name == "Standard-Weizen"
    assert result.variante == "FIXPREIS"
    assert result.id is not None


# ---------------------------------------------------------------------------
# kontrakt_hedging — mark-to-market P&L
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_hedge_mark_to_market_pnl():
    """
    Hedge at 220 EUR/t, current price 225 EUR/t, menge=100t
    pnl = (225 - 220) * 100 = 500 EUR
    """
    from app.api.v1.endpoints.kontrakt_hedging import HedgeMarkToMarket, mark_to_market

    # DB returns the hedge row with the original price + menge
    db = MagicMock()
    row = MagicMock()
    row.__getitem__ = lambda self, key: {"futures_preis_eur": 220.0, "hedge_menge_t": 100.0}[key]
    result_mock = MagicMock()
    result_mock.mappings.return_value.first.return_value = row
    db.execute.return_value = result_mock

    payload = HedgeMarkToMarket(
        aktueller_futures_preis=225.0,
        bewertungsdatum=date(2026, 5, 17),
    )
    result = mark_to_market(
        kontrakt_id="K-001",
        hedge_id="H-001",
        payload=payload,
        db=db,
        tenant_id=TENANT,
    )
    assert result.unrealized_pnl_eur == pytest.approx(500.0)
    assert result.futures_preis_eur == 220.0
    assert result.hedge_menge_t == 100.0


@pytest.mark.unit
def test_hedge_mark_to_market_pnl_fallback():
    """When DB raises, P&L is 0 (fallback: basis=0, menge=0)."""
    from app.api.v1.endpoints.kontrakt_hedging import HedgeMarkToMarket, mark_to_market

    payload = HedgeMarkToMarket(
        aktueller_futures_preis=225.0,
        bewertungsdatum=date(2026, 5, 17),
    )
    result = mark_to_market(
        kontrakt_id="K-001",
        hedge_id="H-001",
        payload=payload,
        db=_raising_db(),
        tenant_id=TENANT,
    )
    assert result.unrealized_pnl_eur == pytest.approx(0.0)


@pytest.mark.unit
def test_hedge_cancel_sets_storniert():
    """DELETE /hedges/{id} calls UPDATE ... SET status='STORNIERT'."""
    from app.api.v1.endpoints.kontrakt_hedging import cancel_hedge

    db = MagicMock()
    response = cancel_hedge(
        kontrakt_id="K-001",
        hedge_id="H-001",
        db=db,
        tenant_id=TENANT,
    )
    # Verify execute was called and SQL contains STORNIERT
    assert db.execute.called
    sql_text = str(db.execute.call_args[0][0])
    assert "STORNIERT" in sql_text
    assert response.status_code == 204


# ---------------------------------------------------------------------------
# erechnung_import — format detection
# ---------------------------------------------------------------------------

def _make_upload_file(filename: str, content: bytes) -> Any:
    uf = MagicMock()
    uf.filename = filename
    uf.read = AsyncMock(return_value=content)
    return uf


@pytest.mark.unit
def test_erechnung_zugferd_detected():
    """XML with CrossIndustryInvoice → ZUGFERD_2_1."""
    from app.api.v1.endpoints.erechnung_import import import_erechnung

    content = b"""<?xml version="1.0"?>
<rsm:CrossIndustryInvoice xmlns:rsm="urn:un:unece:uncefact:data:standard:CrossIndustryInvoice:100">
  <ram:ID>RE-2026-001</ram:ID>
</rsm:CrossIndustryInvoice>"""

    file = _make_upload_file("rechnung.xml", content)
    result = asyncio.run(
        import_erechnung(file=file, db=_raising_db(), tenant_id=TENANT)
    )
    assert result.format == "ZUGFERD_2_1"
    assert result.status == "ERKANNT"


@pytest.mark.unit
def test_erechnung_xrechnung_detected():
    """XML with ubl:Invoice → XRECHNUNG_3_0."""
    from app.api.v1.endpoints.erechnung_import import import_erechnung

    content = b"""<?xml version="1.0"?>
<ubl:Invoice xmlns:ubl="urn:oasis:names:specification:ubl:schema:xsd:Invoice-2">
  <cbc:ID>XR-2026-042</cbc:ID>
</ubl:Invoice>"""

    file = _make_upload_file("xrechnung.xml", content)
    result = asyncio.run(
        import_erechnung(file=file, db=_raising_db(), tenant_id=TENANT)
    )
    assert result.format == "XRECHNUNG_3_0"
    assert result.status == "ERKANNT"


@pytest.mark.unit
def test_erechnung_unknown_format():
    """Non-XML file → UNKNOWN format."""
    from app.api.v1.endpoints.erechnung_import import import_erechnung

    content = b"This is a plain text invoice document without XML markup."
    file = _make_upload_file("rechnung.txt", content)

    result = asyncio.run(
        import_erechnung(file=file, db=_raising_db(), tenant_id=TENANT)
    )
    assert result.format == "UNKNOWN"
    assert result.status == "ERKANNT"


@pytest.mark.unit
def test_erechnung_rechnungsnummer_extracted_zugferd():
    """ZUGFeRD: ram:ID parsed as rechnungsnummer."""
    from app.api.v1.endpoints.erechnung_import import import_erechnung

    content = b"""<rsm:CrossIndustryInvoice>
  <ram:ID>RE-2026-999</ram:ID>
  <ram:TaxBasisTotalAmount currencyID="EUR">1000.00</ram:TaxBasisTotalAmount>
  <ram:TaxTotalAmount currencyID="EUR">190.00</ram:TaxTotalAmount>
  <ram:GrandTotalAmount currencyID="EUR">1190.00</ram:GrandTotalAmount>
</rsm:CrossIndustryInvoice>"""

    file = _make_upload_file("re.xml", content)
    result = asyncio.run(
        import_erechnung(file=file, db=_raising_db(), tenant_id=TENANT)
    )
    assert result.rechnungsnummer == "RE-2026-999"
    assert result.betrag_netto == pytest.approx(1000.0)
    assert result.betrag_brutto == pytest.approx(1190.0)
    assert result.steuer_betrag == pytest.approx(190.0)


@pytest.mark.unit
def test_erechnung_xrechnung_supplier_and_amounts_extracted():
    from app.api.v1.endpoints.erechnung_import import import_erechnung

    content = b"""<ubl:Invoice>
  <cbc:ID>XR-2026-100</cbc:ID>
  <cac:AccountingSupplierParty><cbc:Name>Lieferant GmbH</cbc:Name></cac:AccountingSupplierParty>
  <cbc:TaxExclusiveAmount>200.00</cbc:TaxExclusiveAmount>
  <cbc:TaxAmount>38.00</cbc:TaxAmount>
  <cbc:PayableAmount>238.00</cbc:PayableAmount>
</ubl:Invoice>"""
    file = _make_upload_file("xrechnung.xml", content)
    result = asyncio.run(import_erechnung(file=file, db=_raising_db(), tenant_id=TENANT))
    assert result.lieferant_name == "Lieferant GmbH"
    assert result.betrag_brutto == pytest.approx(238.0)


@pytest.mark.unit
def test_erechnung_import_persists_when_db_available():
    from app.api.v1.endpoints.erechnung_import import import_erechnung

    db = MagicMock()
    file = _make_upload_file("rechnung.txt", b"plain")
    result = asyncio.run(import_erechnung(file=file, db=db, tenant_id=TENANT))
    assert result.status == "ERKANNT"
    assert db.execute.called
    db.commit.assert_called_once()


@pytest.mark.unit
def test_erechnung_list_imports_and_fallback():
    from app.api.v1.endpoints.erechnung_import import list_imports

    db = MagicMock()
    db.execute.return_value.mappings.return_value.all.return_value = [
        {
            "import_id": "IMP-1",
            "format": "XRECHNUNG_3_0",
            "status": "ERKANNT",
            "rechnungsnummer": "XR-1",
            "lieferant_name": "L",
            "betrag_netto": 1.0,
            "betrag_brutto": 1.19,
            "steuer_betrag": 0.19,
            "fehler_details": None,
        }
    ]
    assert list_imports(db=db, tenant_id=TENANT)[0]["import_id"] == "IMP-1"
    assert list_imports(db=_raising_db(), tenant_id=TENANT) == []


@pytest.mark.unit
def test_erechnung_buchen_updates_import_and_creates_op():
    from app.api.v1.endpoints.erechnung_import import buchen

    db = MagicMock()
    first = MagicMock()
    first.fetchone.return_value = ("RE-1", "Lieferant", 119.0)
    db.execute.side_effect = [first, MagicMock(), MagicMock()]

    result = buchen("IMP-1", db=db, tenant_id=TENANT)
    assert result["status"] == "gebucht"
    assert result["journal_entry_id"]
    assert db.commit.call_count == 2


@pytest.mark.unit
def test_erechnung_buchen_tolerates_missing_import_table():
    from app.api.v1.endpoints.erechnung_import import buchen

    result = buchen("IMP-404", db=_raising_db(), tenant_id=TENANT)
    assert result["status"] == "gebucht"


# ---------------------------------------------------------------------------
# price_calculation — sorte_klasse + kalkulationsweg
# ---------------------------------------------------------------------------

@pytest.mark.unit
def test_preis_kalkulation_sorte_c_discount():
    """sorte_klasse=C → netto_preis = basis * (1 - 0%) * 0.95 (no customer discount)."""
    from app.api.v1.endpoints.price_calculation import PreisKalkulationInput, berechne_preis

    # DB: returns basis=100, rabatt=0
    db = MagicMock()

    def execute_side_effect(sql_obj, params=None):
        sql = str(sql_obj)
        result = MagicMock()
        if "preislisten" in sql:
            row = MagicMock()
            row.__getitem__ = lambda self, i: 100.0
            row.__iter__ = lambda self: iter([100.0])

            def _first():
                return (100.0,)

            result.first = _first
        else:
            result.first.return_value = None
        return result

    db.execute.side_effect = execute_side_effect

    payload = PreisKalkulationInput(
        artikel_nr="WEI-001",
        kunden_nr="K-999",
        menge=10.0,
        einheit="T",
        lieferdatum=date(2026, 9, 1),
        sorte_klasse="C",
    )
    result = berechne_preis(payload=payload, db=db, tenant_id=TENANT)
    # netto = 100 * (1 - 0%) * 0.95 = 95.0
    assert result.netto_preis == pytest.approx(95.0)
    assert result.basis_preis == pytest.approx(100.0)


@pytest.mark.unit
def test_preis_kalkulation_sorte_b_discount():
    """sorte_klasse=B → faktor 0.98."""
    from app.api.v1.endpoints.price_calculation import PreisKalkulationInput, berechne_preis

    db = MagicMock()

    def execute_side_effect(sql_obj, params=None):
        result = MagicMock()
        result.first.return_value = None
        return result

    db.execute.side_effect = execute_side_effect

    payload = PreisKalkulationInput(
        artikel_nr="WEI-002",
        kunden_nr="K-888",
        menge=5.0,
        einheit="T",
        lieferdatum=date(2026, 9, 1),
        sorte_klasse="B",
    )
    result = berechne_preis(payload=payload, db=db, tenant_id=TENANT)
    # basis=0.0 fallback → netto = 0 * 0.98 = 0
    assert result.netto_preis == pytest.approx(0.0)
    # Sorte-Faktor should be reflected in kalkulationsweg
    assert any("B" in step for step in result.kalkulationsweg)


@pytest.mark.unit
def test_preis_kalkulation_includes_kalkulationsweg():
    """Result must include a non-empty kalkulationsweg list."""
    from app.api.v1.endpoints.price_calculation import PreisKalkulationInput, berechne_preis

    payload = PreisKalkulationInput(
        artikel_nr="ART-001",
        kunden_nr="KD-001",
        menge=1.0,
        einheit="T",
        lieferdatum=date(2026, 10, 1),
    )
    result = berechne_preis(payload=payload, db=_raising_db(), tenant_id=TENANT)
    assert isinstance(result.kalkulationsweg, list)
    assert len(result.kalkulationsweg) > 0


@pytest.mark.unit
def test_preis_kalkulation_fallback_on_db_error():
    """All DB errors → status=FALLBACK, basis=0."""
    from app.api.v1.endpoints.price_calculation import PreisKalkulationInput, berechne_preis

    payload = PreisKalkulationInput(
        artikel_nr="ART-X",
        kunden_nr="KD-X",
        menge=1.0,
        einheit="T",
        lieferdatum=date(2026, 10, 1),
    )
    result = berechne_preis(payload=payload, db=_raising_db(), tenant_id=TENANT)
    assert result.status == "FALLBACK"
    assert result.basis_preis == pytest.approx(0.0)


@pytest.mark.unit
def test_preis_kalkulation_brutto_is_netto_plus_19pct():
    """brutto_preis = netto_preis * 1.19 for any netto."""
    from app.api.v1.endpoints.price_calculation import PreisKalkulationInput, berechne_preis

    payload = PreisKalkulationInput(
        artikel_nr="ART-001",
        kunden_nr="KD-001",
        menge=1.0,
        einheit="T",
        lieferdatum=date(2026, 10, 1),
    )
    result = berechne_preis(payload=payload, db=_raising_db(), tenant_id=TENANT)
    assert result.brutto_preis == pytest.approx(result.netto_preis * 1.19, rel=1e-4)
