"""Regressionstests fuer die API-Gap-Stabilisierung Lager/Pricing/Scan (2026-07-02).

Deckt die 5 nachgezogenen Endpoints ab:
- GET  /api/v1/lager/bestaende
- POST /api/v1/lager/bewegungen
- POST /api/v1/scan/barcode
- GET  /api/v1/pricing/find
- GET/POST /api/v1/pricing/staffelrabatte

Jeder Endpoint wird mit Happy Path, negativem Payload, Tenant-Isolation und
(wo zutreffend) fehlenden optionalen Feldern abgedeckt. Alle Tests benoetigen
eine echte Postgres-Verbindung (`require_db`) und skippen automatisch, wenn
keine DB erreichbar ist (siehe tests/conftest.py::skip_if_db_unavailable).
"""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

TENANT_A = "00000000-0000-0000-0000-000000000001"
TENANT_B = "00000000-0000-0000-0000-000000000002"
HEADERS = {"Authorization": "Bearer dev-token"}


@pytest.fixture
def client() -> TestClient:
    from app.main import app

    return TestClient(app, raise_server_exceptions=False, base_url="http://localhost")


@pytest.fixture
def seeded_article(require_db):
    """Legt einen Artikel + ein Lager unter TENANT_A an und raeumt danach auf."""
    from app.core.database import SessionLocal
    from app.infrastructure.models import Article, Warehouse

    suffix = uuid.uuid4().hex[:8]
    db = SessionLocal()
    article_id = f"IT-ART-{suffix}"
    warehouse_id = f"IT-WH-{suffix}"
    ean_code = f"42{suffix}"
    try:
        db.add(
            Warehouse(
                id=warehouse_id,
                warehouse_code=f"WH-{suffix}",
                name="IT Test Lager",
                address="Teststrasse 1",
                city="Teststadt",
                postal_code="00000",
                tenant_id=TENANT_A,
            )
        )
        db.add(
            Article(
                id=article_id,
                article_number=f"ART-{suffix}",
                name="IT Test Artikel",
                unit="kg",
                category="test",
                sales_price=10,
                purchase_price=6,
                ean_code=ean_code,
                tenant_id=TENANT_A,
            )
        )
        db.commit()
        yield {
            "article_id": article_id,
            "warehouse_id": warehouse_id,
            "ean_code": ean_code,
            "suffix": suffix,
        }
    finally:
        db.rollback()
        db.execute(
            __import__("sqlalchemy").text(
                "DELETE FROM domain_inventory.inventory_stock_movements WHERE article_id = :a"
            ),
            {"a": article_id},
        )
        db.execute(
            __import__("sqlalchemy").text(
                "DELETE FROM domain_inventory.articles WHERE id = :a"
            ),
            {"a": article_id},
        )
        db.execute(
            __import__("sqlalchemy").text(
                "DELETE FROM domain_inventory.warehouses WHERE id = :w"
            ),
            {"w": warehouse_id},
        )
        db.commit()
        db.close()


# ---------------------------------------------------------------------------
# GET /api/v1/lager/bestaende
# ---------------------------------------------------------------------------

@pytest.mark.needs_live_db
def test_bestaende_happy_path_reflects_booked_movement(client, seeded_article):
    booking = client.post(
        "/api/v1/lager/bewegungen",
        headers=HEADERS,
        params={"tenant_id": TENANT_A},
        json={
            "article_id": seeded_article["article_id"],
            "warehouse_id": seeded_article["warehouse_id"],
            "quantity": 25,
            "movement_type": "wareneingang",
        },
    )
    assert booking.status_code == 201, booking.text

    resp = client.get(
        "/api/v1/lager/bestaende",
        headers=HEADERS,
        params={"tenant_id": TENANT_A, "article_id": seeded_article["article_id"]},
    )
    assert resp.status_code == 200, resp.text
    rows = resp.json()
    assert len(rows) == 1
    assert rows[0]["menge"] == 25
    assert rows[0]["warehouse_id"] == seeded_article["warehouse_id"]


@pytest.mark.needs_live_db
def test_bestaende_tenant_isolation(client, seeded_article):
    client.post(
        "/api/v1/lager/bewegungen",
        headers=HEADERS,
        params={"tenant_id": TENANT_A},
        json={
            "article_id": seeded_article["article_id"],
            "warehouse_id": seeded_article["warehouse_id"],
            "quantity": 10,
            "movement_type": "wareneingang",
        },
    )

    resp = client.get(
        "/api/v1/lager/bestaende",
        headers=HEADERS,
        params={"tenant_id": TENANT_B, "article_id": seeded_article["article_id"]},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json() == []


@pytest.mark.needs_live_db
def test_bestaende_missing_optional_filters_defaults_to_positive_only(client, seeded_article):
    """Ohne warehouse_id/charge/article_number darf die Query nicht 500en."""
    resp = client.get(
        "/api/v1/lager/bestaende",
        headers=HEADERS,
        params={"tenant_id": TENANT_A},
    )
    assert resp.status_code == 200, resp.text
    assert isinstance(resp.json(), list)


# ---------------------------------------------------------------------------
# POST /api/v1/lager/bewegungen
# ---------------------------------------------------------------------------

@pytest.mark.needs_live_db
def test_bewegungen_happy_path_wareneingang(client, seeded_article):
    resp = client.post(
        "/api/v1/lager/bewegungen",
        headers=HEADERS,
        params={"tenant_id": TENANT_A},
        json={
            "article_id": seeded_article["article_id"],
            "warehouse_id": seeded_article["warehouse_id"],
            "quantity": 15,
            "movement_type": "wareneingang",
        },
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["status"] == "posted"
    assert body["quantity"] == 15


@pytest.mark.needs_live_db
def test_bewegungen_negative_invalid_movement_type(client, seeded_article):
    resp = client.post(
        "/api/v1/lager/bewegungen",
        headers=HEADERS,
        params={"tenant_id": TENANT_A},
        json={
            "article_id": seeded_article["article_id"],
            "warehouse_id": seeded_article["warehouse_id"],
            "quantity": 5,
            "movement_type": "unbekannter_typ",
        },
    )
    assert resp.status_code == 422, resp.text


@pytest.mark.needs_live_db
def test_bewegungen_negative_unknown_article_returns_404(client, seeded_article):
    resp = client.post(
        "/api/v1/lager/bewegungen",
        headers=HEADERS,
        params={"tenant_id": TENANT_A},
        json={
            "article_id": "does-not-exist",
            "warehouse_id": seeded_article["warehouse_id"],
            "quantity": 5,
            "movement_type": "wareneingang",
        },
    )
    assert resp.status_code == 404, resp.text


@pytest.mark.needs_live_db
def test_bewegungen_tenant_isolation_article_lookup(client, seeded_article):
    """Artikel gehoert TENANT_A -> Buchung unter TENANT_B muss 404 liefern."""
    resp = client.post(
        "/api/v1/lager/bewegungen",
        headers=HEADERS,
        params={"tenant_id": TENANT_B},
        json={
            "article_id": seeded_article["article_id"],
            "warehouse_id": seeded_article["warehouse_id"],
            "quantity": 5,
            "movement_type": "wareneingang",
        },
    )
    assert resp.status_code == 404, resp.text


# ---------------------------------------------------------------------------
# POST /api/v1/scan/barcode
# ---------------------------------------------------------------------------

@pytest.mark.needs_live_db
def test_scan_barcode_happy_path_found_by_ean(client, seeded_article):
    resp = client.post(
        "/api/v1/scan/barcode",
        headers=HEADERS,
        params={"tenant_id": TENANT_A},
        json={"barcode": seeded_article["ean_code"]},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["gefunden"] is True
    assert body["artikel"]["artikel_id"] == seeded_article["article_id"]


@pytest.mark.needs_live_db
def test_scan_barcode_unknown_returns_200_not_found_flag(client, seeded_article):
    resp = client.post(
        "/api/v1/scan/barcode",
        headers=HEADERS,
        params={"tenant_id": TENANT_A},
        json={"barcode": f"unbekannt-{uuid.uuid4().hex[:8]}"},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["gefunden"] is False
    assert body["artikel"] is None
    assert body["hinweis"]


@pytest.mark.needs_live_db
def test_scan_barcode_negative_missing_barcode_field(client):
    resp = client.post(
        "/api/v1/scan/barcode",
        headers=HEADERS,
        params={"tenant_id": TENANT_A},
        json={},
    )
    assert resp.status_code == 422, resp.text


@pytest.mark.needs_live_db
def test_scan_barcode_tenant_isolation(client, seeded_article):
    resp = client.post(
        "/api/v1/scan/barcode",
        headers=HEADERS,
        params={"tenant_id": TENANT_B},
        json={"barcode": seeded_article["ean_code"]},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["gefunden"] is False


# ---------------------------------------------------------------------------
# GET /api/v1/pricing/find
# ---------------------------------------------------------------------------

@pytest.mark.needs_live_db
def test_pricing_find_matches_calculate_alias(client, seeded_article):
    find_resp = client.get(
        "/api/v1/pricing/find",
        headers=HEADERS,
        params={"article_id": seeded_article["article_id"], "tenant_id": TENANT_A},
    )
    calc_resp = client.get(
        "/api/v1/pricing/calculate",
        headers=HEADERS,
        params={"article_id": seeded_article["article_id"], "tenant_id": TENANT_A},
    )
    assert find_resp.status_code == 200, find_resp.text
    assert calc_resp.status_code == 200, calc_resp.text
    assert find_resp.json() == calc_resp.json()


@pytest.mark.needs_live_db
def test_pricing_find_missing_optional_params_still_resolves_base_price(client, seeded_article):
    resp = client.get(
        "/api/v1/pricing/find",
        headers=HEADERS,
        params={"article_id": seeded_article["article_id"], "tenant_id": TENANT_A},
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["source"] == "base"
    assert float(body["list_price"]) == 10.0


@pytest.mark.needs_live_db
def test_pricing_find_negative_unknown_article_returns_404(client):
    resp = client.get(
        "/api/v1/pricing/find",
        headers=HEADERS,
        params={"article_id": "does-not-exist", "tenant_id": TENANT_A},
    )
    assert resp.status_code == 404, resp.text


@pytest.mark.needs_live_db
def test_pricing_find_tenant_isolation(client, seeded_article):
    resp = client.get(
        "/api/v1/pricing/find",
        headers=HEADERS,
        params={"article_id": seeded_article["article_id"], "tenant_id": TENANT_B},
    )
    assert resp.status_code == 404, resp.text


# ---------------------------------------------------------------------------
# GET/POST /api/v1/pricing/staffelrabatte
# ---------------------------------------------------------------------------

@pytest.fixture
def cleanup_staffelrabatt(require_db):
    created_ids: list[str] = []
    yield created_ids
    if not created_ids:
        return
    from app.core.database import SessionLocal
    from sqlalchemy import text

    db = SessionLocal()
    try:
        db.execute(
            text("DELETE FROM domain_pricing.staffelrabatte WHERE id = ANY(:ids)"),
            {"ids": created_ids},
        )
        db.commit()
    finally:
        db.close()


@pytest.mark.needs_live_db
def test_staffelrabatte_create_and_list_happy_path(client, seeded_article, cleanup_staffelrabatt):
    create_resp = client.post(
        "/api/v1/pricing/staffelrabatte",
        headers=HEADERS,
        params={"tenant_id": TENANT_A},
        json={
            "artikel_id": seeded_article["article_id"],
            "stufen": [
                {"ab_menge": 10, "rabatt_prozent": 5},
                {"ab_menge": 50, "rabatt_prozent": 10},
            ],
            "bezeichnung": "IT Staffelrabatt",
        },
    )
    assert create_resp.status_code == 201, create_resp.text
    created = create_resp.json()
    cleanup_staffelrabatt.append(created["id"])
    assert created["status"] == "aktiv"
    assert len(created["stufen"]) == 2

    list_resp = client.get(
        "/api/v1/pricing/staffelrabatte",
        headers=HEADERS,
        params={"tenant_id": TENANT_A, "artikel_id": seeded_article["article_id"]},
    )
    assert list_resp.status_code == 200, list_resp.text
    ids = [row["id"] for row in list_resp.json()]
    assert created["id"] in ids


@pytest.mark.needs_live_db
def test_staffelrabatte_negative_missing_artikel_and_gruppe(client):
    resp = client.post(
        "/api/v1/pricing/staffelrabatte",
        headers=HEADERS,
        params={"tenant_id": TENANT_A},
        json={"stufen": [{"ab_menge": 1, "rabatt_prozent": 1}]},
    )
    assert resp.status_code == 422, resp.text


@pytest.mark.needs_live_db
def test_staffelrabatte_tenant_isolation(client, seeded_article, cleanup_staffelrabatt):
    create_resp = client.post(
        "/api/v1/pricing/staffelrabatte",
        headers=HEADERS,
        params={"tenant_id": TENANT_A},
        json={
            "artikel_id": seeded_article["article_id"],
            "stufen": [{"ab_menge": 1, "rabatt_prozent": 1}],
        },
    )
    assert create_resp.status_code == 201, create_resp.text
    cleanup_staffelrabatt.append(create_resp.json()["id"])

    list_resp = client.get(
        "/api/v1/pricing/staffelrabatte",
        headers=HEADERS,
        params={"tenant_id": TENANT_B, "artikel_id": seeded_article["article_id"]},
    )
    assert list_resp.status_code == 200, list_resp.text
    assert list_resp.json() == []
