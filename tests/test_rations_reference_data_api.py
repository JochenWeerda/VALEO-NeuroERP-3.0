from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.v1.endpoints import rations_reference_data
from app.auth.deps import get_current_user
from app.core.database import get_db
from app.core.tenant import get_tenant_id
from app.main import app


BASE = "/api/v1/agrar/rations-optimization/reference-data"
TENANT = "00000000-0000-0000-0000-000000000001"
HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-Id": TENANT}
client = TestClient(app, raise_server_exceptions=False)


def test_seeded_reference_catalog_and_basis_conversion_are_available() -> None:
    nutrients = client.get(f"{BASE}/nutrients", headers=HEADERS)
    assert nutrients.status_code == 200, nutrients.text
    nutrient_rows = nutrients.json()
    assert {"dry_matter", "crude_protein", "net_energy_lactation"} <= {
        row["code"] for row in nutrient_rows
    }
    assert all(row["source"] and row["revision"] == 1 for row in nutrient_rows)

    units = client.get(f"{BASE}/units", headers=HEADERS)
    assert units.status_code == 200, units.text
    assert {"kg", "g", "MJ_per_kg"} <= {row["code"] for row in units.json()}

    quantity = client.post(
        f"{BASE}/convert-basis",
        headers=HEADERS,
        json={
            "value": "10",
            "from_basis": "fresh_matter",
            "to_basis": "dry_matter",
            "dry_matter_pct": "35",
            "kind": "quantity",
            "precision": 3,
            "rounding_mode": "half_up",
        },
    )
    assert quantity.status_code == 200, quantity.text
    assert Decimal(quantity.json()["value"]) == Decimal("3.500")

    concentration = client.post(
        f"{BASE}/convert-basis",
        headers=HEADERS,
        json={
            "value": "170",
            "from_basis": "fresh_matter",
            "to_basis": "dry_matter",
            "dry_matter_pct": "35",
            "kind": "concentration",
            "precision": 3,
        },
    )
    assert concentration.status_code == 200, concentration.text
    assert Decimal(concentration.json()["value"]) == Decimal("485.714")

    invalid = client.post(
        f"{BASE}/convert-basis",
        headers=HEADERS,
        json={
            "value": "10",
            "from_basis": "fresh_matter",
            "to_basis": "dry_matter",
            "dry_matter_pct": "0",
        },
    )
    assert invalid.status_code == 422


def test_reference_endpoints_enforce_feed_read_role() -> None:
    local_app = FastAPI()
    local_app.include_router(rations_reference_data.router)
    local_app.dependency_overrides[get_current_user] = lambda: {
        "sub": str(uuid4()), "roles": ["CRM_LESEN"]
    }
    local_app.dependency_overrides[get_tenant_id] = lambda: TENANT
    local_app.dependency_overrides[get_db] = lambda: object()

    with TestClient(local_app, raise_server_exceptions=False) as local_client:
        assert local_client.get("/reference-data/nutrients").status_code == 403
        assert local_client.get("/reference-data/units").status_code == 403
        assert local_client.post(
            "/reference-data/convert-basis",
            json={
                "value": "1", "from_basis": "fresh_matter", "to_basis": "dry_matter",
                "dry_matter_pct": "35",
            },
        ).status_code == 403
