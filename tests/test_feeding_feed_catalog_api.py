from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import feeding_feed_catalog, futter_stamm
from app.auth.deps import get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.main import app


BASE = "/api/v1/agrar/rations-optimization/feed-catalog"
TENANT = "00000000-0000-0000-0000-000000000001"
HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-Id": TENANT}
client = TestClient(app, raise_server_exceptions=False)


def test_feed_catalog_full_journey_solver_adapter_history_and_tenant_isolation() -> None:
    suffix = str(uuid4())[:8]
    created = client.post(f"{BASE}/feeds", headers=HEADERS, json={
        "artikel_nummer": f"FEED-{suffix}", "name": f"Maissilage {suffix}",
        "art": "Grundfutter", "feed_kind": "forage", "approval_status": "approved",
        "trockensubstanz": "35", "protein": "8.1", "energie": "10.7", "preis_pro_t": "42",
    })
    assert created.status_code == 201, created.text
    feed = created.json()
    feed_id = feed["id"]
    assert feed["revision"] == 1
    assert Decimal(str(feed["solver_feed"]["cp"])) == Decimal("81.0")

    for code, value, unit in (
        ("dry_matter", "35", "percent"),
        ("crude_protein", "81", "g_per_kg"),
        ("metabolizable_energy", "10.7", "MJ_per_kg"),
    ):
        response = client.post(f"{BASE}/feeds/{feed_id}/reference-values", headers=HEADERS, json={
            "nutrient_code": code, "value": value, "unit_code": unit,
            "basis": "dry_matter" if code != "dry_matter" else "fresh_matter",
            "source_type": "reference", "source_ref": "Golden API test",
        })
        assert response.status_code == 201, response.text

    product = client.post(f"{BASE}/feeds/{feed_id}/products", headers=HEADERS, json={
        "sku": f"SKU-{suffix}", "display_name": "Lose Ware", "packaging_unit": "t",
        "package_size": "1", "minimum_order_qty": "5", "price_eur_t": "49", "freight_eur_t": "7",
    })
    assert product.status_code == 201, product.text

    detail = client.get(f"{BASE}/feeds/{feed_id}", headers=HEADERS)
    assert detail.status_code == 200, detail.text
    body = detail.json()
    assert len(body["reference_values"]) == 3
    assert len(body["products"]) == 1
    assert Decimal(str(body["solver_feed"]["price"])) == Decimal("0.16")

    invalid_value = client.post(f"{BASE}/feeds/{feed_id}/reference-values", headers=HEADERS, json={
        "nutrient_code": "crude_protein", "value": "81", "unit_code": "MJ_per_kg",
        "basis": "dry_matter", "source_type": "reference",
    })
    assert invalid_value.status_code == 409

    updated = client.patch(f"{BASE}/feeds/{feed_id}", headers=HEADERS, json={
        "expected_revision": 1, "reason": "Herkunft fachlich geprueft", "name": f"Maissilage geprüft {suffix}",
    })
    assert updated.status_code == 200, updated.text
    assert updated.json()["revision"] == 2
    stale = client.patch(f"{BASE}/feeds/{feed_id}", headers=HEADERS, json={
        "expected_revision": 1, "reason": "Veralteter Browser", "name": "Nicht speichern",
    })
    assert stale.status_code == 409

    history = client.get(f"{BASE}/feeds/{feed_id}/history", headers=HEADERS)
    assert history.status_code == 200
    assert [row["revision"] for row in history.json()] == [2, 1]

    foreign = client.get(f"{BASE}/feeds/{feed_id}", headers={
        "Authorization": "Bearer dev-token", "X-Tenant-Id": str(uuid4()),
    })
    assert foreign.status_code == 404


def test_feed_catalog_enforces_read_and_write_roles() -> None:
    local = FastAPI()
    local.include_router(feeding_feed_catalog.router)
    local.dependency_overrides[get_current_user] = lambda: {"sub": "crm-user", "roles": ["CRM_LESEN"]}
    local.dependency_overrides[get_tenant_id] = lambda: TENANT
    local.dependency_overrides[get_db] = lambda: object()
    with TestClient(local, raise_server_exceptions=False) as local_client:
        assert local_client.get("/feed-catalog/feeds").status_code == 403
        assert local_client.post("/feed-catalog/feeds", json={
            "artikel_nummer": "X", "name": "X", "art": "X", "feed_kind": "other",
        }).status_code == 403

    legacy = FastAPI()
    legacy.include_router(futter_stamm.router)
    legacy.dependency_overrides[get_current_user] = lambda: {"sub": "crm-user", "roles": ["CRM_LESEN"]}
    legacy.dependency_overrides[get_tenant_id] = lambda: TENANT
    legacy.dependency_overrides[get_db] = lambda: object()
    with TestClient(legacy, raise_server_exceptions=False) as legacy_client:
        assert legacy_client.get("/einzelfuttermittel").status_code == 403
        assert legacy_client.post("/einzelfuttermittel", json={
            "artikel_nummer": "X", "name": "X", "art": "X",
        }).status_code == 403
