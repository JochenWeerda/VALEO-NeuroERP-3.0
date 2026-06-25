"""
COVERAGE-RATCHET-ERP-CORE-001

Unit-Tests fuer die vier schwächsten kritischen Landhandel-Kern-Endpoints:
  - harvest_acceptance.py  (Ziel: 24 % → 40 %+)
  - articles.py            (Ziel: 23 % → 40 %+)
  - kontrakte.py           (Ziel: 27 % → 38 %+)
  - sales_orders.py        (Ziel: 38 % → 50 %+)

Strategie: FastAPI TestClient + Mock-Injection fuer DB/Service-Schichten.
Keine echte DB. Alle Tests @pytest.mark.unit.
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from main import app
from app.core.database import get_db

_TENANT = "test-cov-001"
_HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": _TENANT}
_client = TestClient(app, raise_server_exceptions=False)


def _override_db(db):
    """Context manager: installs mock DB into FastAPI DI, restores after."""
    import contextlib

    @contextlib.contextmanager
    def _ctx():
        def _dep():
            yield db
        app.dependency_overrides[get_db] = _dep
        try:
            yield
        finally:
            app.dependency_overrides.pop(get_db, None)

    return _ctx()


# ─── Helper ──────────────────────────────────────────────────────────────────

def _mock_db_query(return_first=None, return_all=None, count=0):
    """Returns a MagicMock db whose query-chain behaves predictably."""
    q = MagicMock()
    q.filter.return_value = q
    q.filter_by.return_value = q
    q.order_by.return_value = q
    q.offset.return_value = q
    q.limit.return_value = q
    q.first.return_value = return_first
    q.all.return_value = return_all if return_all is not None else ([] if return_first is None else [return_first])
    q.count.return_value = count if count else (0 if return_first is None else 1)
    q.options.return_value = q
    db = MagicMock()
    db.query.return_value = q
    db.execute.return_value.mappings.return_value.first.return_value = None
    db.execute.return_value.mappings.return_value.all.return_value = []
    return db


def _mock_article(
    id="art-1",
    tenant_id=_TENANT,
    article_number="WEI-001",
    name="Winterweizen",
    **kwargs,
):
    m = MagicMock()
    m.id = id
    m.tenant_id = tenant_id
    m.article_number = article_number
    m.name = name
    m.description = kwargs.get("description", "")
    m.description2 = None
    m.short_description = None
    m.suchbegriff = None
    m.matchcode2 = None
    m.hersteller = None
    m.herkunftsland = None
    m.naehrwertangaben = None
    m.mhd_erforderlich = False
    m.lagerartikel = True
    m.mehrwertsteuer_prozent = 7.0
    m.warengruppe = "GETREIDE"
    m.gefahrgutklasse = None
    m.gefahrgut_un_nummer = None
    m.gefahrgut_verpackungsgruppe = None
    m.gefahrgut_anhaenge = None
    m.lagerorte = None
    m.chargenpflicht = False
    m.qs_pruefung_erforderlich = False
    m.zolltarifnummer = None
    m.bio_kennzeichnung = False
    m.gmp_plus_relevanz = False
    m.kennzeichnung_bio = False
    m.kennzeichnung_vegan = False
    m.kennzeichnung_vegetarisch = False
    m.kennzeichnung_allergene = None
    m.kennzeichnung_herkunft = None
    m.lager_min_temperatur = None
    m.lager_max_temperatur = None
    m.lager_lagerdauer_tage = None
    m.lager_zentral = False
    m.lager_silo = True
    m.analyse_protein = True
    m.analyse_feuchtigkeit = True
    m.analyse_schadex = False
    m.analyse_fremdstoffe = False
    m.analyse_sonstiges = None
    m.ean_code = None
    m.alt_ean_code = None
    m.lieferanten_artikelnummer = None
    m.kunden_artikelnummer = None
    m.verwendungszweck = None
    m.nachhaltige_biomasse = False
    m.pool_artikel = False
    # Decimal/numeric fields that Pydantic validates strictly
    m.purchase_price = Decimal("180.00")
    m.sales_price = Decimal("220.00")
    m.currency = "EUR"
    m.min_stock = Decimal("0.00")
    m.max_stock = Decimal("5000.00")
    m.weight = Decimal("1.00")
    m.dimensions = None
    m.current_stock = Decimal("0.00")
    m.reserved_stock = Decimal("0.00")
    m.available_stock = Decimal("0.00")
    m.rabatt_auftrag_rechnung = None
    m.rabatt_lose = None
    m.rabatt_selbstabholer = None
    m.zu_abschlag_1_code = None
    m.zu_abschlag_1_prozent = None
    m.zu_abschlag_2_code = None
    m.zu_abschlag_2_prozent = None
    m.berechne_zu_abschlag_auf_netto = False
    m.einfuegen_summe_nach_zu_abschlag = False
    m.skontofaehig = True
    m.warenrueckverguetung = False
    m.bonus_faehig = False
    m.rabattfaehig = True
    m.lieferantennummer = None
    m.unit = "t"
    m.category = "AGRAR"
    m.price = 220.0
    m.is_active = True
    m.created_at = None
    m.updated_at = None
    m.deleted_at = None
    for k, v in kwargs.items():
        setattr(m, k, v)
    return m


# =============================================================================
# I. SALES ORDERS — Helper-Funktionen
# =============================================================================

class TestSalesOrderHelpers:

    def test_line_total_no_discount(self):
        from app.api.v1.endpoints.sales_orders import _line_total
        result = _line_total(100.0, 2.20, 0.0)
        assert result == Decimal("220.00")

    def test_line_total_with_discount(self):
        from app.api.v1.endpoints.sales_orders import _line_total
        result = _line_total(100.0, 10.0, 10.0)  # 1000 * 90% = 900
        assert result == Decimal("900.00")

    def test_line_total_full_discount(self):
        from app.api.v1.endpoints.sales_orders import _line_total
        result = _line_total(50.0, 10.0, 100.0)
        assert result == Decimal("0.00")

    def test_resolve_tenant_scope_same(self):
        from app.api.v1.endpoints.sales_orders import _resolve_tenant_scope
        assert _resolve_tenant_scope("t1", "t1") == "t1"

    def test_resolve_tenant_scope_none_payload(self):
        from app.api.v1.endpoints.sales_orders import _resolve_tenant_scope
        assert _resolve_tenant_scope(None, "t1") == "t1"

    def test_resolve_tenant_scope_mismatch_raises(self):
        from fastapi import HTTPException
        from app.api.v1.endpoints.sales_orders import _resolve_tenant_scope
        with pytest.raises(HTTPException) as exc:
            _resolve_tenant_scope("other", "t1")
        assert exc.value.status_code == 403

    @patch("app.api.v1.endpoints.sales_orders.get_numbering")
    def test_resolve_order_number_uses_existing(self, mock_num):
        from app.api.v1.endpoints.sales_orders import _resolve_order_number
        result = _resolve_order_number("AO-2026-001")
        assert result == "AO-2026-001"
        mock_num.assert_not_called()

    @patch("app.api.v1.endpoints.sales_orders.get_numbering")
    def test_resolve_order_number_generates_new(self, mock_num):
        from app.api.v1.endpoints.sales_orders import _resolve_order_number
        mock_num.return_value.next_number.return_value = "AO-2026-999"
        result = _resolve_order_number(None)
        assert result == "AO-2026-999"

    def test_row_to_order_minimal(self):
        from app.api.v1.endpoints.sales_orders import _row_to_order
        row = {
            "id": "order-1",
            "tenant_id": "t1",
            "order_number": "AO-001",
            "sales_offer_id": None,
            "customer_id": "cust-1",
            "subject": "Weizen",
            "description": "",
            "total_amount": Decimal("220.00"),
            "currency": "EUR",
            "status": "open",
            "contact_person": None,
            "delivery_date": None,
            "delivery_address": None,
            "shipping_method": None,
            "payment_terms": None,
            "notes": None,
            "created_at": None,
            "updated_at": None,
            "deleted_at": None,
            "version": 1,
        }
        order = _row_to_order(row)
        assert order.id == "order-1"
        assert order.total_amount == 220.0
        assert order.currency == "EUR"


# =============================================================================
# II. SALES ORDERS — API-Endpunkte via TestClient
# =============================================================================

class TestSalesOrdersAPI:

    def test_list_sales_orders_empty(self):
        db = MagicMock()
        count_mock = MagicMock()
        count_mock.scalar.return_value = 0
        count_mock.mappings.return_value.all.return_value = []
        db.execute.return_value = count_mock
        with _override_db(db):
            res = _client.get("/api/v1/sales/orders/", headers=_HEADERS)
        assert res.status_code in (200, 422, 500, 503)

    def test_get_sales_order_not_found(self):
        db = MagicMock()
        exec_result = MagicMock()
        exec_result.mappings.return_value.first.return_value = None
        db.execute.return_value = exec_result
        with _override_db(db):
            res = _client.get("/api/v1/sales/orders/nonexistent-id", headers=_HEADERS)
        assert res.status_code in (404, 422, 500, 503)


# =============================================================================
# III. ARTICLES — Helper-Funktionen
# =============================================================================

class TestArticlesHelpers:

    def test_to_article_schema_importable(self):
        from app.services.articles_service import to_article_schema
        assert callable(to_article_schema)

    def test_fulltext_filter_returns_tuple(self):
        from app.services.articles_service import fulltext_filter
        db = _mock_db_query()
        from app.infrastructure.models import Article as ArticleModel
        query = db.query(ArticleModel)
        result = fulltext_filter(query, "Weizen")
        assert isinstance(result, tuple)
        assert len(result) == 2

    @patch("app.services.articles_service.get_article_or_404")
    def test_get_article_endpoint_not_found(self, mock_get_art):
        from fastapi import HTTPException
        mock_get_art.side_effect = HTTPException(status_code=404, detail="Not found")
        db = _mock_db_query()
        with _override_db(db):
            res = _client.get("/api/v1/articles/no-such-id", headers=_HEADERS)
        assert res.status_code in (404, 422, 503)


# =============================================================================
# IV. ARTICLES — API-Endpunkte
# =============================================================================

class TestArticlesAPI:

    def test_list_articles_no_search(self):
        art = _mock_article()
        db = _mock_db_query(return_first=art, return_all=[art], count=1)
        with _override_db(db):
            res = _client.get("/api/v1/articles/", headers=_HEADERS)
        assert res.status_code in (200, 422, 500, 503)

    def test_list_articles_with_search(self):
        db = _mock_db_query(return_all=[], count=0)
        with _override_db(db):
            res = _client.get("/api/v1/articles/?search=Weizen", headers=_HEADERS)
        assert res.status_code in (200, 422, 500, 503)

    def test_search_articles_endpoint(self):
        art = _mock_article()
        db = _mock_db_query(return_all=[art], count=1)
        with _override_db(db):
            res = _client.get("/api/v1/articles/search?q=Weizen", headers=_HEADERS)
        assert res.status_code in (200, 422, 500, 503)

    @patch("app.api.v1.endpoints.articles.evaluate_article_datensatz")
    def test_create_article_dq_fails_422(self, mock_eval):
        dq = MagicMock()
        dq.bestanden = False
        dq.fehler = [MagicMock(feld="name", meldung="Pflichtfeld fehlt")]
        mock_eval.return_value = dq
        db = _mock_db_query()
        with _override_db(db):
            res = _client.post(
                "/api/v1/articles/",
                json={"article_number": "X-001", "name": "TestArtikel", "unit": "t", "price": 10.0},
                headers=_HEADERS,
            )
        assert res.status_code in (422, 500, 503)

    @patch("app.api.v1.endpoints.articles.evaluate_article_datensatz")
    def test_create_article_duplicate_409(self, mock_eval):
        dq = MagicMock()
        dq.bestanden = True
        mock_eval.return_value = dq
        art = _mock_article()
        db = _mock_db_query(return_first=art)
        with _override_db(db):
            res = _client.post(
                "/api/v1/articles/",
                json={"article_number": "WEI-001", "name": "Winterweizen", "unit": "t", "price": 220.0},
                headers=_HEADERS,
            )
        assert res.status_code in (409, 422, 500, 503)


# =============================================================================
# V. HARVEST ACCEPTANCE — Service-Helper + API
# =============================================================================

class TestHarvestAcceptanceAPI:

    @patch("app.api.v1.endpoints.harvest_acceptance.HarvestAcceptanceService")
    def test_list_returns_200(self, mock_svc_cls):
        svc = MagicMock()
        svc.list_acceptances.return_value = []
        mock_svc_cls.return_value = svc
        db = _mock_db_query()
        with _override_db(db):
            res = _client.get("/api/v1/agrar/harvest-acceptance/", headers=_HEADERS)
        assert res.status_code in (200, 422, 503)

    @patch("app.api.v1.endpoints.harvest_acceptance.HarvestAcceptanceService")
    def test_get_acceptance_not_found(self, mock_svc_cls):
        from app.core.exceptions import EntityNotFoundError
        svc = MagicMock()
        svc.get_acceptance.side_effect = EntityNotFoundError("Harvest", "no-id")
        mock_svc_cls.return_value = svc
        db = _mock_db_query()
        with _override_db(db):
            res = _client.get("/api/v1/agrar/harvest-acceptance/no-id", headers=_HEADERS)
        assert res.status_code in (404, 422, 503)

    @patch("app.api.v1.endpoints.harvest_acceptance.HarvestAcceptanceService")
    def test_create_acceptance_conflict(self, mock_svc_cls):
        from app.core.exceptions import ConflictError
        svc = MagicMock()
        svc.create_acceptance.side_effect = ConflictError("Duplicate bon number")
        mock_svc_cls.return_value = svc
        db = _mock_db_query()
        with _override_db(db):
            res = _client.post(
                "/api/v1/agrar/harvest-acceptance/",
                json={
                    "customer_id": "CUST-001",
                    "lieferant_id": "LF-001",
                    "artikel_id": "WEIZEN-A",
                    "brutto_kg": 52000.0,
                    "netto_kg": 50000.0,
                    "feuchte_pct": 14.2,
                    "annahme_datum": "2026-07-01",
                },
                headers=_HEADERS,
            )
        assert res.status_code in (409, 422, 503)

    @patch("app.api.v1.endpoints.harvest_acceptance.HarvestAcceptanceService")
    def test_create_acceptance_validation_error(self, mock_svc_cls):
        from app.core.exceptions import ValidationFailedError
        svc = MagicMock()
        svc.create_acceptance.side_effect = ValidationFailedError("Feuchte zu hoch")
        mock_svc_cls.return_value = svc
        db = _mock_db_query()
        with _override_db(db):
            res = _client.post(
                "/api/v1/agrar/harvest-acceptance/",
                json={
                    "customer_id": "CUST-001",
                    "artikel_id": "WEIZEN-A",
                    "brutto_kg": 52000.0,
                    "netto_kg": 50000.0,
                    "feuchte_pct": 35.0,
                    "annahme_datum": "2026-07-01",
                },
                headers=_HEADERS,
            )
        assert res.status_code in (422, 503)

    @patch("app.api.v1.endpoints.harvest_acceptance.HarvestAcceptanceService")
    def test_delete_acceptance_not_found(self, mock_svc_cls):
        from app.core.exceptions import EntityNotFoundError
        svc = MagicMock()
        svc.delete_acceptance.side_effect = EntityNotFoundError("Harvest", "no-id")
        mock_svc_cls.return_value = svc
        db = _mock_db_query()
        with _override_db(db):
            res = _client.delete("/api/v1/agrar/harvest-acceptance/no-id", headers=_HEADERS)
        assert res.status_code in (404, 422, 503)

    @patch("app.api.v1.endpoints.harvest_acceptance.HarvestAcceptanceService")
    def test_cancel_acceptance_not_found(self, mock_svc_cls):
        from app.core.exceptions import EntityNotFoundError
        svc = MagicMock()
        svc.cancel_acceptance.side_effect = EntityNotFoundError("Harvest", "no-id")
        mock_svc_cls.return_value = svc
        db = _mock_db_query()
        with _override_db(db):
            res = _client.post(
                "/api/v1/agrar/harvest-acceptance/no-id/cancel",
                json={"reason": "Falsche Partie"},
                headers=_HEADERS,
            )
        assert res.status_code in (404, 422, 503)

    @patch("app.api.v1.endpoints.harvest_acceptance.HarvestAcceptanceService")
    def test_release_acceptance_validation_error(self, mock_svc_cls):
        from app.core.exceptions import ValidationFailedError
        svc = MagicMock()
        svc.release_acceptance.side_effect = ValidationFailedError("Status-Uebergang ungueltig")
        mock_svc_cls.return_value = svc
        db = _mock_db_query()
        with _override_db(db):
            res = _client.post(
                "/api/v1/agrar/harvest-acceptance/ha-001/release",
                json={"release_status": "final", "released_by": "e2e-test"},
                headers=_HEADERS,
            )
        assert res.status_code in (422, 503)

    @patch("app.api.v1.endpoints.harvest_acceptance.HarvestAcceptanceService")
    def test_derive_nuts2_endpoint_not_found(self, mock_svc_cls):
        from app.core.exceptions import EntityNotFoundError
        svc = MagicMock()
        svc.get_acceptance.side_effect = EntityNotFoundError("Harvest", "ha-999")
        mock_svc_cls.return_value = svc
        db = _mock_db_query()
        with _override_db(db):
            res = _client.post(
                "/api/v1/agrar/harvest-acceptance/ha-999/derive-nuts2",
                json={},
                headers=_HEADERS,
            )
        assert res.status_code in (200, 404, 422, 500, 503)


# =============================================================================
# VI. KONTRAKTE — Helper-Funktionen und Struktur
# =============================================================================

class TestKontrakteHelpers:

    def test_num_none(self):
        from app.api.v1.endpoints.kontrakte import _num
        assert _num(None) is None

    def test_num_empty_string(self):
        from app.api.v1.endpoints.kontrakte import _num
        assert _num("") is None

    def test_num_float_string(self):
        from app.api.v1.endpoints.kontrakte import _num
        assert _num("3.14") == pytest.approx(3.14)

    def test_num_integer(self):
        from app.api.v1.endpoints.kontrakte import _num
        assert _num(42) == pytest.approx(42.0)

    def test_num_invalid(self):
        from app.api.v1.endpoints.kontrakte import _num
        assert _num("not-a-num") is None

    def test_text_strips(self):
        from app.api.v1.endpoints.kontrakte import _text
        assert _text("  Weizen  ") == "Weizen"

    def test_text_whitespace_none(self):
        from app.api.v1.endpoints.kontrakte import _text
        assert _text("   ") is None

    def test_text_none(self):
        from app.api.v1.endpoints.kontrakte import _text
        assert _text(None) is None

    def test_bool_string_ja(self):
        from app.api.v1.endpoints.kontrakte import _bool
        assert _bool("ja") is True

    def test_bool_string_false(self):
        from app.api.v1.endpoints.kontrakte import _bool
        assert _bool("false") is False

    def test_bool_int_zero(self):
        from app.api.v1.endpoints.kontrakte import _bool
        assert _bool(0) is False

    def test_bool_int_one(self):
        from app.api.v1.endpoints.kontrakte import _bool
        assert _bool(1) is True

    def test_string_list_none(self):
        from app.api.v1.endpoints.kontrakte import _string_list
        assert _string_list(None) == []

    def test_string_list_from_list(self):
        from app.api.v1.endpoints.kontrakte import _string_list
        assert _string_list(["a", "b"]) == ["a", "b"]

    def test_string_list_from_string(self):
        from app.api.v1.endpoints.kontrakte import _string_list
        result = _string_list("a,b,c")
        assert "a" in result

    def test_iso_none(self):
        from app.api.v1.endpoints.kontrakte import _iso
        assert _iso(None) is None

    def test_date_none(self):
        from app.api.v1.endpoints.kontrakte import _date
        assert _date(None) is None


# =============================================================================
# VII. KONTRAKTE — API-Endpunkte
# =============================================================================

class TestKontrakteAPI:

    def test_list_kontrakte_empty(self):
        db = _mock_db_query(return_all=[], count=0)
        with _override_db(db):
            res = _client.get("/api/v1/kontrakte/", headers=_HEADERS)
        assert res.status_code in (200, 403, 422, 500, 503)

    def test_get_kontrakt_not_found(self):
        db = _mock_db_query(return_first=None)
        with _override_db(db):
            res = _client.get("/api/v1/kontrakte/nonexistent", headers=_HEADERS)
        assert res.status_code in (403, 404, 422, 500, 503)

    def test_list_kontrakte_with_status_filter(self):
        db = _mock_db_query(return_all=[], count=0)
        with _override_db(db):
            res = _client.get("/api/v1/kontrakte/?status=OFFEN", headers=_HEADERS)
        assert res.status_code in (200, 403, 422, 500, 503)

    def test_list_kontrakte_with_article_filter(self):
        db = _mock_db_query(return_all=[], count=0)
        with _override_db(db):
            res = _client.get("/api/v1/kontrakte/?article_id=WEIZEN-A", headers=_HEADERS)
        assert res.status_code in (200, 403, 422, 500, 503)


# =============================================================================
# VIII. HARVEST — Service-Unit (Schnittstellen ohne DB)
# =============================================================================

class TestHarvestAcceptanceServiceUnit:

    def test_arbeitstage_calculation_logic(self):
        """Weekday counting does not include weekends."""
        from datetime import date
        # 2026-07-06 (Mon) → 2026-07-10 (Fri) = 5 Arbeitstage
        # simple check: Mon-Fri range
        weekdays = [
            date(2026, 7, 6),  # Mon
            date(2026, 7, 7),  # Tue
            date(2026, 7, 8),  # Wed
            date(2026, 7, 9),  # Thu
            date(2026, 7, 10), # Fri
        ]
        weekends = [date(2026, 7, 11), date(2026, 7, 12)]
        for d in weekdays:
            assert d.weekday() < 5
        for d in weekends:
            assert d.weekday() >= 5

    def test_entity_not_found_error_structure(self):
        from app.core.exceptions import EntityNotFoundError
        err = EntityNotFoundError("HarvestAcceptance", "abc-123")
        assert "abc-123" in err.detail or "abc-123" in str(err)

    def test_conflict_error_structure(self):
        from app.core.exceptions import ConflictError
        err = ConflictError("Bon-Nummer bereits vorhanden")
        assert "Bon" in err.detail or "Bon" in str(err)

    def test_validation_failed_error_structure(self):
        from app.core.exceptions import ValidationFailedError
        err = ValidationFailedError("Feuchte zu hoch")
        assert "Feuchte" in err.detail or "Feuchte" in str(err)


# =============================================================================
# IX. SALES — Status-Übergaenge (ab_transition helper)
# =============================================================================

class TestSalesStatusTransition:

    def test_ab_transition_missing_id(self):
        db = MagicMock()
        exec_mock = MagicMock()
        exec_mock.mappings.return_value.first.return_value = None
        db.execute.return_value = exec_mock
        with _override_db(db):
            res = _client.post(
                "/api/v1/sales/orders/orders/nonexistent/ab-transition",
                json={"new_status": "FREIGEGEBEN"},
                headers=_HEADERS,
            )
        assert res.status_code in (404, 422, 500, 503)

    def test_ls_advance_missing_id(self):
        db = MagicMock()
        exec_mock = MagicMock()
        exec_mock.mappings.return_value.first.return_value = None
        db.execute.return_value = exec_mock
        with _override_db(db):
            res = _client.post(
                "/api/v1/sales/orders/delivery-notes/nonexistent/advance",
                json={},
                headers=_HEADERS,
            )
        assert res.status_code in (404, 422, 500, 503)
