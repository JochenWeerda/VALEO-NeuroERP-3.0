from __future__ import annotations

from fastapi.testclient import TestClient

from services.inventory.main import app

client = TestClient(app)


def test_create_and_list_epcis_event() -> None:
    payload = {
        "event_type": "ObjectEvent",
        "biz_step": "receiving",
        "read_point": "WH1/DOCK-1",
        "sku": "SKU-TEST",
        "quantity": 5.0,
        "extensions": {"poNumber": "PO-123"},
    }
    resp = client.post("/api/v1/inventory/epcis/events", json=payload)
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["event_type"] == "ObjectEvent"
    assert data["sku"] == "SKU-TEST"
    assert data["extensions"]["poNumber"] == "PO-123"

    listing = client.get("/api/v1/inventory/epcis/events")
    assert listing.status_code == 200
    items = listing.json()["items"]
    assert len(items) >= 1

