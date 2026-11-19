"""
Tests für Einkauf-Features:
  - 3-Wege-Match (PO/GR/IR)
  - ERS (Evaluated Receipt Settlement)
  - RFQ (Request for Quotation)
  - Einkaufs-KPIs
"""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch


# ─────────────────────────────────────────────────────────────────────────────
# Hilfsfunktionen — direkt aus Modul importieren (keine DB nötig)
# ─────────────────────────────────────────────────────────────────────────────

from app.api.v1.endpoints.purchase_invoice_verification import _compute_match_status


# ─────────────────────────────────────────────────────────────────────────────
# 3-Wege-Match — Unit Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestThreeWayMatch:
    def test_3way_match_success(self):
        """po=1000, gr=980, inv=985 → Toleranz 2% → GEMATCHT oder TOLERANZ."""
        # reference = min(1000, 980) = 980
        # base = max(1000, 980) = 1000
        # variance_amount = |985 - 980| = 5
        # variance_percent = 5 / 1000 * 100 = 0.5% → innerhalb 2% → TOLERANZ
        status, variance_amount, variance_percent = _compute_match_status(
            po_amount=1000.0,
            gr_amount=980.0,
            invoice_amount=985.0,
            tolerance_percent=2.0,
        )
        assert status in ("GEMATCHT", "TOLERANZ")
        assert variance_percent <= 2.0

    def test_3way_match_differenz(self):
        """po=1000, gr=500, inv=1000 → DIFFERENZ."""
        # reference = min(1000, 500) = 500
        # base = max(1000, 500) = 1000
        # variance_amount = |1000 - 500| = 500
        # variance_percent = 500 / 1000 * 100 = 50% → weit über 2% → DIFFERENZ
        status, variance_amount, variance_percent = _compute_match_status(
            po_amount=1000.0,
            gr_amount=500.0,
            invoice_amount=1000.0,
            tolerance_percent=2.0,
        )
        assert status == "DIFFERENZ"
        assert variance_percent > 2.0

    def test_3way_match_toleranz_boundary(self):
        """Varianz exakt an der Toleranzgrenze → TOLERANZ."""
        # po=1000, gr=1000, invoice=1020 → variance=20, percent=2.0 → TOLERANZ
        status, variance_amount, variance_percent = _compute_match_status(
            po_amount=1000.0,
            gr_amount=1000.0,
            invoice_amount=1020.0,
            tolerance_percent=2.0,
        )
        assert status == "TOLERANZ"
        assert abs(variance_percent - 2.0) < 1e-6

    def test_3way_match_exact_match(self):
        """Exakt gleiche Beträge → GEMATCHT."""
        status, variance_amount, variance_percent = _compute_match_status(
            po_amount=500.0,
            gr_amount=500.0,
            invoice_amount=500.0,
            tolerance_percent=2.0,
        )
        assert status == "GEMATCHT"
        assert variance_amount == 0.0

    def test_3way_match_missing_amounts_returns_offen(self):
        """Fehlende Beträge → OFFEN."""
        status, _, _ = _compute_match_status(
            po_amount=None,
            gr_amount=500.0,
            invoice_amount=500.0,
            tolerance_percent=2.0,
        )
        assert status == "OFFEN"


# ─────────────────────────────────────────────────────────────────────────────
# ERS — Unit Tests (mit Mock-DB)
# ─────────────────────────────────────────────────────────────────────────────

class TestErs:
    def _make_mock_db(self):
        db = MagicMock()
        db.execute.return_value.fetchone.return_value = None
        db.execute.return_value.fetchall.return_value = []
        db.execute.return_value.scalar.return_value = None
        return db

    def test_ers_creates_invoice_for_qualified_supplier(self):
        """ERS erzeugt Rechnung wenn Lieferant qualifiziert ist."""
        from app.api.v1.endpoints.ers_settlement import trigger_ers, ErsRunRequest

        db = self._make_mock_db()
        # Supplier-Query: qualifiziert
        supplier_row = MagicMock()
        supplier_row.__getitem__ = lambda self, i: [1, True, 2.0][i]
        supplier_row.__bool__ = lambda self: True

        inv_row = MagicMock()
        inv_row.__getitem__ = lambda self, i: [42, None][i]

        execute_results = []

        def side_effect(query, params=None):
            result = MagicMock()
            sql = str(query) if hasattr(query, '__str__') else ""
            if "ers_suppliers" in sql and "INSERT" not in sql and "UPDATE" not in sql:
                result.fetchone.return_value = (1, True, 2.0)
            elif "ers_invoices" in sql and "INSERT" in sql:
                result.fetchone.return_value = (42, None)
            else:
                result.fetchone.return_value = None
                result.fetchall.return_value = []
            return result

        db.execute.side_effect = side_effect

        body = ErsRunRequest(gr_id="gr-001", supplier_id="sup-001")

        with patch(
            "app.api.v1.endpoints.ers_settlement._fetch_gr_amount", return_value=950.0
        ):
            result = trigger_ers(body=body, db=db, tenant_id="tenant-1")

        assert result["success"] is True
        assert result["event"] == "invoice_auto_created"

    def test_ers_skips_non_qualified_supplier(self):
        """ERS überspringt nicht-qualifizierte Lieferanten."""
        from app.api.v1.endpoints.ers_settlement import trigger_ers, ErsRunRequest

        db = self._make_mock_db()

        def side_effect(query, params=None):
            result = MagicMock()
            result.fetchone.return_value = None  # Lieferant nicht gefunden → nicht qualifiziert
            return result

        db.execute.side_effect = side_effect

        body = ErsRunRequest(gr_id="gr-002", supplier_id="sup-999")

        result = trigger_ers(body=body, db=db, tenant_id="tenant-1")

        assert result["success"] is False
        assert "nicht ERS-qualifiziert" in result["reason"]


# RFQ-Persistenz: tests/test_rfq_integration.py (echte DB, keine Mocks)

# ─────────────────────────────────────────────────────────────────────────────
# KPIs — Unit Tests
# ─────────────────────────────────────────────────────────────────────────────

class TestEinkaufKpis:
    @staticmethod
    def _leeres_docflow():
        db = MagicMock()
        ergebnis = db.execute.return_value
        ergebnis.one.return_value = (None, None)
        ergebnis.scalar.return_value = None
        ergebnis.fetchmany.return_value = []
        return db

    def test_kpis_returns_required_fields(self):
        """Ohne Bestellungen in DocFlow: alle Pflichtfelder, Kennzahlen leer."""
        from app.api.v1.endpoints.einkauf_kpis import get_kpis

        result = get_kpis(date_from="2026-01-01", date_to="2026-12-31", db=self._leeres_docflow(), tenant_id="tenant-1")
        assert result["on_time_delivery_rate"] is None and result["fill_rate"] is None
        assert result["avg_lead_time_days"] is None and result["price_variance"] is None
        assert result["top_5_suppliers_by_spend"] == [] and result["abc_analysis"] == {}

    def test_kpis_with_no_dates(self):
        """Ohne Datumsangaben gilt der ganze Zeitraum."""
        from app.api.v1.endpoints.einkauf_kpis import get_kpis

        db = self._leeres_docflow()
        get_kpis(date_from=None, date_to=None, db=db, tenant_id="t1")
        params = db.execute.call_args_list[0].args[1]
        assert (params["date_from"], params["date_to"]) == ("1900-01-01", "2999-12-31")

    def test_kpis_verschweigen_keinen_datenbankfehler(self):
        """Bis 16.11.2026 lieferte jeder Fehler still None - so blieben Abfragen auf nie vorhandene Spalten unbemerkt."""
        from app.api.v1.endpoints.einkauf_kpis import get_kpis

        db = MagicMock()
        db.execute.side_effect = RuntimeError("Spalte fehlt")
        with pytest.raises(RuntimeError):
            get_kpis(date_from=None, date_to=None, db=db, tenant_id="t1")
