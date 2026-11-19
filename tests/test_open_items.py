"""
Tests for open items (OP) management endpoints (app/api/v1/endpoints/open_items.py).

Covers the read schema, the read endpoints and the removal of the manual write paths (19.11.2026).
"""

import pytest
from decimal import Decimal
from datetime import date
from pydantic import ValidationError
from starlette.testclient import TestClient

from app.core.config import settings
from conftest import skip_if_db_unavailable


@pytest.fixture(scope="module")
def client():
    from app.main import app
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture(scope="module")
def auth_headers():
    return {
        "Authorization": f"Bearer {settings.API_DEV_TOKEN or 'dev-token'}",
        "X-Tenant-ID": "test-tenant",
    }



def _import_schemas():
    from app.api.v1.endpoints.open_items import OpenItemBase, OpenItem
    return {"OpenItemBase": OpenItemBase, "OpenItem": OpenItem}


class TestOpenItemBaseSchema:
    def test_requires_rechnungsnr_datum_faelligkeit_betrag_offen(self):
        S = _import_schemas()
        with pytest.raises(ValidationError):
            S["OpenItemBase"]()

    def test_valid_open_item_base(self):
        S = _import_schemas()
        item = S["OpenItemBase"](
            rechnungsnr="RE-2026-001",
            rechnungsdatum=date(2026, 3, 1),
            faelligkeit=date(2026, 3, 31),
            op_betrag=Decimal("5000.00"),
            offen=Decimal("5000.00"),
        )
        assert item.rechnungsnr == "RE-2026-001"
        assert item.konto_typ == "debitoren"
        assert item.op_status == "offen"
        assert item.waehrung == "EUR"
        assert item.mahn_stufe == 0
        assert item.zahlbar is True

    def test_defaults(self):
        S = _import_schemas()
        item = S["OpenItemBase"](
            rechnungsnr="R-1",
            rechnungsdatum=date(2026, 1, 1),
            faelligkeit=date(2026, 1, 31),
            op_betrag=Decimal("100"),
            offen=Decimal("100"),
        )
        assert item.saldo == Decimal("0.00")
        assert item.kunde_id is None
        assert item.lieferant_id is None
        assert item.skonto_prozent is None


class TestOpenItemStatusMachine:
    """Status machine: offen -> teilweise|geschlossen; terminal states."""

    def test_valid_statuses(self):
        S = _import_schemas()
        for status in ("offen", "teilweise", "geschlossen", "storniert"):
            item = S["OpenItemBase"](
                rechnungsnr="R-1",
                rechnungsdatum=date(2026, 1, 1),
                faelligkeit=date(2026, 1, 31),
                op_betrag=Decimal("100"),
                offen=Decimal("100"),
                op_status=status,
            )
            assert item.op_status == status

    def test_konto_typ_values(self):
        S = _import_schemas()
        for typ in ("debitoren", "kreditoren"):
            item = S["OpenItemBase"](
                rechnungsnr="R-1",
                rechnungsdatum=date(2026, 1, 1),
                faelligkeit=date(2026, 1, 31),
                op_betrag=Decimal("100"),
                offen=Decimal("100"),
                konto_typ=typ,
            )
            assert item.konto_typ == typ


class TestOpenItemEndpoints:
    def test_list_open_items(self, client, auth_headers):
        resp = client.get("/api/v1/finance/open-items", headers=auth_headers)
        skip_if_db_unavailable(resp)
        assert resp.status_code == 200
        body = resp.json()
        assert "items" in body
        assert "summary" in body

    def test_get_open_item_404(self, client, auth_headers):
        resp = client.get("/api/v1/finance/open-items/nonexistent-id", headers=auth_headers)
        skip_if_db_unavailable(resp)
        assert resp.status_code == 404

    def test_manuelle_schreibwege_sind_entfernt(self, client, auth_headers):
        """OPs entstehen aus der Belegbuchung und werden ueber den Bankabgleich ausgeglichen."""
        from app.api.v1.endpoints import open_items

        wege = {(m, r.path) for r in open_items.router.routes for m in getattr(r, "methods", ())}
        assert wege == {("GET", "/open-items"), ("GET", "/open-items/{op_id}"),
                        ("GET", "/open-items/{op_id}/settlements"), ("POST", "/open-items/{entity_id}/actions/mahnen")}
        assert client.post("/api/v1/finance/open-items/batch-settle", headers=auth_headers,
                           json={"items": []}).status_code in (404, 405)
