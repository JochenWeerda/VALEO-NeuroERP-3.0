from __future__ import annotations

import json
from decimal import Decimal
from typing import Any
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api.v1.endpoints.feeding_supply import router
from app.auth.deps import get_current_user
from app.core.database import SessionLocal, get_db
from app.core.tenant import get_tenant_id
from app.main import app

BASE = "/api/v1/agrar/rations-optimization"
TENANT = "00000000-0000-0000-0000-000000000001"
HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-Id": TENANT}
client = TestClient(app, raise_server_exceptions=False)


def _published_plan() -> tuple[dict[str, Any], str]:
    suffix = uuid4().hex[:8]
    feed = client.post(f"{BASE}/feed-catalog/feeds", headers=HEADERS, json={
        "artikel_nummer": f"SUP-{suffix}", "name": f"Versorgungsfutter {suffix}",
        "art": "Grundfutter", "feed_kind": "forage", "approval_status": "approved",
        "verfuegbar_t": "0.1",
    })
    assert feed.status_code == 201, feed.text
    feed_id = feed.json()["id"]
    product = client.post(f"{BASE}/feed-catalog/feeds/{feed_id}/products", headers=HEADERS, json={
        "sku": f"SUP-P-{suffix}", "display_name": "Lose Ware",
        "packaging_unit": "t", "package_size": "1",
    })
    assert product.status_code == 201, product.text
    business = client.post(f"{BASE}/feeding/businesses", headers=HEADERS, json={
        "name": f"Versorgungsbetrieb {suffix}",
    })
    assert business.status_code == 201, business.text
    group = client.post(f"{BASE}/lifecycle/groups", headers=HEADERS, json={
        "name": f"Versorgungsgruppe {suffix}", "external_ref": f"sup-{suffix}",
        "animal_count": 10, "business_id": business.json()["id"],
    })
    assert group.status_code == 201, group.text
    ration = client.post(f"{BASE}/lifecycle/rations", headers=HEADERS, json={
        "group_id": group.json()["id"], "name": f"Versorgungsration {suffix}",
        "source": "editor", "snapshot": {"ration": [
            {"feed_id": feed_id, "feed_name": feed.json()["name"], "kg_fm": 10, "mixing_sequence": 1},
            {"feed_id": f"unknown-{suffix}", "feed_name": "Unbekannter Bestand", "kg_fm": 1, "mixing_sequence": 2},
        ]},
    })
    assert ration.status_code == 201, ration.text
    version_id = ration.json()["versions"][0]["id"]
    for current, target, reason in (
        ("draft", "in_review", None), ("in_review", "approved", "Versorgung fachlich geprueft"),
    ):
        transitioned = client.post(f"{BASE}/lifecycle/versions/{version_id}/transitions", headers=HEADERS, json={
            "expected_status": current, "target_status": target, "reason": reason,
        })
        assert transitioned.status_code == 200, transitioned.text
    published = client.post(f"{BASE}/feeding/plans/publish", headers=HEADERS, json={
        "source_ration_version_id": version_id, "animal_count": 10,
        "dosing_step_kg": "0.1", "rounding_mode": "nearest",
        "valid_from": "2026-07-16", "valid_until": "2026-08-31",
        "reason": "Versorgungsplan fuer API-Abnahmetest freigeben",
        "idempotency_key": f"supply-plan-{uuid4()}",
    })
    assert published.status_code == 201, published.text
    return published.json(), feed_id


def test_plan_supply_projects_safety_reach_unknown_stock_and_trade_rounding() -> None:
    plan, feed_id = _published_plan()
    response = client.get(f"{BASE}/feeding/supply?horizon_days=30&safety_pct=10", headers=HEADERS)
    assert response.status_code == 200, response.text
    known = next(row for row in response.json() if row["plan_version_id"] == plan["id"] and row["feed_id"] == feed_id)
    assert float(known["daily_demand_kg"]) == 100
    assert float(known["net_demand_kg"]) == 3000
    assert float(known["safety_quantity_kg"]) == 300
    assert float(known["stock_kg"]) == 100
    assert float(known["reach_days"]) == 1
    assert float(known["shortage_kg"]) == 3200
    assert float(known["suggested_order_kg"]) == 4000
    assert float(known["order_rounding_delta_kg"]) == 800
    assert known["status"] == "critical"
    unknown = next(row for row in response.json() if row["plan_version_id"] == plan["id"] and row["feed_id"] != feed_id)
    assert unknown["stock_kg"] is None
    assert unknown["shortage_kg"] is None
    assert unknown["suggested_order_kg"] is None
    assert unknown["status"] == "unknown"
    readiness = client.get(f"{BASE}/readiness/materials", headers=HEADERS)
    assert readiness.status_code == 200, readiness.text
    planned = next(row for row in readiness.json() if row["feed_id"] == feed_id)
    assert planned["daily_kg"] == 100.0


def test_procurement_handoff_is_idempotent_audited_and_does_not_create_order() -> None:
    plan, feed_id = _published_plan()
    db = SessionLocal()
    try:
        purchase_orders_before = db.execute(text("""SELECT COUNT(*)
          FROM domain_procurement.proc_purchase_orders WHERE tenant_id=:tenant_id"""),
          {"tenant_id": TENANT}).scalar_one()
    finally:
        db.close()
    key = f"supply-handoff-{uuid4()}"
    payload = {"plan_version_id": plan["id"], "feed_id": feed_id,
               "horizon_days": 30, "safety_pct": 10, "idempotency_key": key,
               "reason": "Unterdeckung kontrolliert an den Einkauf uebergeben"}
    created = client.post(f"{BASE}/feeding/supply/procurement-handoffs", headers=HEADERS, json=payload)
    assert created.status_code == 201, created.text
    repeated = client.post(f"{BASE}/feeding/supply/procurement-handoffs", headers=HEADERS, json=payload)
    assert repeated.status_code == 201
    assert repeated.json()["id"] == created.json()["id"]
    conflict = client.post(f"{BASE}/feeding/supply/procurement-handoffs", headers=HEADERS, json={
        **payload, "safety_pct": 11,
    })
    assert conflict.status_code == 409
    listed = client.get(f"{BASE}/feeding/supply/procurement-handoffs", headers=HEADERS)
    assert listed.status_code == 200
    assert any(row["id"] == created.json()["id"] for row in listed.json())

    db = SessionLocal()
    try:
        events = db.execute(text("""SELECT payload FROM public.outbox_events
          WHERE tenant_id=:tenant_id AND event_type='feeding.supply.procurement_handoff.created'
            AND aggregate_id=:id"""), {"tenant_id": TENANT, "id": created.json()["id"]}).scalars().all()
        assert len(events) == 1
        assert Decimal(json.loads(events[0])["payload"]["suggested_order_kg"]) == Decimal("4000")
        purchase_orders_after = db.execute(text("""SELECT COUNT(*)
          FROM domain_procurement.proc_purchase_orders WHERE tenant_id=:tenant_id"""),
          {"tenant_id": TENANT}).scalar_one()
        assert purchase_orders_after == purchase_orders_before
    finally:
        db.close()


def test_unknown_stock_cannot_be_handed_off_and_roles_are_enforced() -> None:
    plan, feed_id = _published_plan()
    unknown = next(row for row in client.get(f"{BASE}/feeding/supply", headers=HEADERS).json()
                   if row["plan_version_id"] == plan["id"] and row["feed_id"] != feed_id)
    blocked = client.post(f"{BASE}/feeding/supply/procurement-handoffs", headers=HEADERS, json={
        "plan_version_id": plan["id"], "feed_id": unknown["feed_id"],
        "horizon_days": 30, "safety_pct": 10, "idempotency_key": f"unknown-{uuid4()}",
        "reason": "Unbekannten Bestand nicht als Nullbestand behandeln",
    })
    assert blocked.status_code == 409
    assert "unbekannt" in blocked.json()["detail"]

    local = FastAPI()
    local.include_router(router)
    local.dependency_overrides[get_current_user] = lambda: {"sub": "crm-only", "roles": ["CRM_LESEN"]}
    local.dependency_overrides[get_tenant_id] = lambda: TENANT
    local.dependency_overrides[get_db] = lambda: object()
    with TestClient(local, raise_server_exceptions=False) as role_client:
        assert role_client.get("/feeding/supply").status_code == 403
        assert role_client.post("/feeding/supply/procurement-handoffs", json={
            "plan_version_id": "plan", "feed_id": "feed", "horizon_days": 30,
            "safety_pct": 10, "idempotency_key": "role-test-key",
            "reason": "Ausreichend langer Testgrund",
        }).status_code == 403
