"""Integrationstests Logistik (Touren + Fracht) — echte DB + API, keine Runtime-DDL."""

from __future__ import annotations

import os
import subprocess
import sys
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.database import SessionLocal
from main import app

pytestmark = [pytest.mark.integration, pytest.mark.needs_live_db]

TENANT_ID = "00000000-0000-0000-0000-000000000001"
HEADERS = {"Authorization": "Bearer dev-token", "X-Tenant-ID": TENANT_ID}
client = TestClient(app, raise_server_exceptions=False, base_url="http://localhost")

LOGISTICS_REVISION = "log_logistics_core_20260612"


def _logistics_tables_ready() -> bool:
    db = SessionLocal()
    try:
        n = db.execute(
            text(
                "SELECT count(*) FROM information_schema.tables "
                "WHERE table_schema = 'domain_logistics' "
                "AND table_name IN ('tours','tour_stops','tour_events','freight_tariffs')"
            ),
        ).scalar()
        return int(n or 0) == 4
    finally:
        db.close()


def _ensure_logistics_schema() -> None:
    if _logistics_tables_ready():
        return
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", LOGISTICS_REVISION],
        text=True,
        capture_output=True,
        env={**os.environ},
        timeout=180,
        check=False,
    )
    if result.returncode != 0 or not _logistics_tables_ready():
        pytest.skip(
            "Logistik-Schema nicht migrierbar: "
            f"{(result.stderr or '')[-400:]}{(result.stdout or '')[-200:]}"
        )


def _purge_tour(tour_id: str) -> None:
    db = SessionLocal()
    try:
        db.execute(text("DELETE FROM domain_logistics.tour_events WHERE tour_id = :id"), {"id": tour_id})
        db.execute(text("DELETE FROM domain_logistics.tour_stops WHERE tour_id = :id"), {"id": tour_id})
        db.execute(text("DELETE FROM domain_logistics.tours WHERE id = :id"), {"id": tour_id})
        db.commit()
    finally:
        db.close()


def _purge_tariff(tariff_id: str) -> None:
    db = SessionLocal()
    try:
        db.execute(
            text("DELETE FROM domain_logistics.freight_tariffs WHERE id = :id"),
            {"id": tariff_id},
        )
        db.commit()
    finally:
        db.close()


@pytest.fixture
def logistics_db(require_db):
    _ensure_logistics_schema()
    yield None


class TestLogisticsIntegration:
    def test_create_tour_list_and_detail(self, logistics_db):
        suffix = uuid.uuid4().hex[:8]
        vehicle_id = f"IT-LOG-{suffix}"
        created = client.post(
            "/api/v1/logistik/tours",
            json={
                "vehicle_id": vehicle_id,
                "driver_id": "driver-1",
                "status": "GEPLANT",
                "stops": [{"address": "Testweg 1", "lat": 52.5, "lng": 13.4, "stop_order": 0}],
            },
            headers=HEADERS,
        )
        assert created.status_code == 201, created.text
        tour_id = created.json()["id"]
        try:
            listed = client.get("/api/v1/logistik/tours", params={"vehicle_id": vehicle_id}, headers=HEADERS)
            assert listed.status_code == 200
            ids = [r["id"] for r in listed.json()]
            assert tour_id in ids

            detail = client.get(f"/api/v1/logistik/tours/{tour_id}", headers=HEADERS)
            assert detail.status_code == 200
            body = detail.json()
            assert body["id"] == tour_id
            assert len(body.get("stops") or []) >= 1
        finally:
            _purge_tour(tour_id)

    def test_tour_cancel_fail_closed_and_stop_cancel(self, logistics_db):
        """LOG-LIFE-001: Stopp- und Tour-Storno, Doppel-Storno → 409."""
        suffix = uuid.uuid4().hex[:10]
        vehicle_id = f"IT-CANCEL-{suffix}"
        created = client.post(
            "/api/v1/logistik/tours",
            json={
                "vehicle_id": vehicle_id,
                "driver_id": "driver-cancel",
                "status": "GEPLANT",
                "stops": [{"address": "Cancel-Stopp", "stop_order": 0}],
            },
            headers=HEADERS,
        )
        assert created.status_code == 201, created.text
        tour_id = created.json()["id"]
        stop_id = created.json()["stops"][0]["id"]
        try:
            no_tenant = client.post(
                f"/api/v1/logistik/tours/{tour_id}/cancel",
                json={"grund": "x"},
                headers={"Authorization": "Bearer dev-token"},
            )
            assert no_tenant.status_code == 422

            sc = client.post(
                f"/api/v1/logistik/tours/{tour_id}/stops/{stop_id}/cancel",
                json={"grund": "IT Stopp"},
                headers=HEADERS,
            )
            assert sc.status_code == 200, sc.text
            assert sc.json().get("status", "").upper() == "STORNIERT"

            sc2 = client.post(
                f"/api/v1/logistik/tours/{tour_id}/stops/{stop_id}/cancel",
                json={},
                headers=HEADERS,
            )
            assert sc2.status_code == 409

            tc = client.post(
                f"/api/v1/logistik/tours/{tour_id}/cancel",
                json={"grund": "IT Tour"},
                headers=HEADERS,
            )
            assert tc.status_code == 200, tc.text
            body = tc.json()
            assert body.get("status", "").upper() == "STORNIERT"
            assert "STORNO" in (body.get("notes") or "")

            tc2 = client.post(
                f"/api/v1/logistik/tours/{tour_id}/cancel",
                json={},
                headers=HEADERS,
            )
            assert tc2.status_code == 409
        finally:
            _purge_tour(tour_id)

    def test_freight_tariff_create_and_simulate(self, logistics_db):
        carrier = f"IT-CARRIER-{uuid.uuid4().hex[:8]}"
        created = client.post(
            "/api/v1/logistik/freight-tariffs",
            json={
                "carrier_id": carrier,
                "zone_from": "10",
                "zone_to": "20",
                "weight_from_kg": 0.0,
                "weight_to_kg": 999999.0,
                "price_per_100kg": 12.5,
                "min_charge": 5.0,
            },
            headers=HEADERS,
        )
        assert created.status_code == 201, created.text
        tariff_id = created.json()["id"]
        try:
            sim = client.get(
                "/api/v1/logistik/freight-cost/simulate",
                params={
                    "carrier_id": carrier,
                    "distance_km": 100.0,
                    "weight_kg": 100.0,
                    "postal_code_from": "10115",
                    "postal_code_to": "20095",
                },
                headers=HEADERS,
            )
            assert sim.status_code == 200, sim.text
            data = sim.json()
            assert data["carrier_id"] == carrier
            assert data["freight_cost_eur"] == pytest.approx(12.5)
        finally:
            _purge_tariff(tariff_id)

    def test_freight_simulate_requires_tenant(self, logistics_db):
        r = client.get(
            "/api/v1/logistik/freight-cost/simulate",
            params={
                "carrier_id": "x",
                "distance_km": 1.0,
                "weight_kg": 1.0,
                "postal_code_from": "10115",
                "postal_code_to": "20095",
            },
            headers={"Authorization": "Bearer dev-token"},
        )
        assert r.status_code == 422

    def test_freight_simulate_not_visible_for_other_tenant(self, logistics_db):
        carrier = f"IT-TENANT-WALL-{uuid.uuid4().hex[:8]}"
        created = client.post(
            "/api/v1/logistik/freight-tariffs",
            json={
                "carrier_id": carrier,
                "zone_from": "10",
                "zone_to": "20",
                "weight_from_kg": 0.0,
                "weight_to_kg": 999999.0,
                "price_per_100kg": 20.0,
                "min_charge": 1.0,
            },
            headers=HEADERS,
        )
        assert created.status_code == 201, created.text
        tariff_id = created.json()["id"]
        other = {**HEADERS, "X-Tenant-ID": "11111111-1111-1111-1111-111111111111"}
        try:
            sim = client.get(
                "/api/v1/logistik/freight-cost/simulate",
                params={
                    "carrier_id": carrier,
                    "distance_km": 100.0,
                    "weight_kg": 100.0,
                    "postal_code_from": "10115",
                    "postal_code_to": "20095",
                },
                headers=other,
            )
            assert sim.status_code == 404, sim.text
        finally:
            _purge_tariff(tariff_id)

    def test_freight_create_tariff_requires_tenant(self, logistics_db):
        r = client.post(
            "/api/v1/logistik/freight-tariffs",
            json={
                "carrier_id": f"IT-NO-TENANT-{uuid.uuid4().hex[:6]}",
                "zone_from": "10",
                "zone_to": "20",
                "weight_from_kg": 0.0,
                "weight_to_kg": 999999.0,
                "price_per_100kg": 1.0,
                "min_charge": 0.0,
            },
            headers={"Authorization": "Bearer dev-token"},
        )
        assert r.status_code == 422

    def test_freight_list_without_tenant_header_only_global(self, logistics_db):
        carrier = f"IT-LIST-WALL-{uuid.uuid4().hex[:8]}"
        created = client.post(
            "/api/v1/logistik/freight-tariffs",
            json={
                "carrier_id": carrier,
                "zone_from": "10",
                "zone_to": "20",
                "weight_from_kg": 0.0,
                "weight_to_kg": 999999.0,
                "price_per_100kg": 20.0,
                "min_charge": 1.0,
            },
            headers=HEADERS,
        )
        assert created.status_code == 201, created.text
        tariff_id = created.json()["id"]
        try:
            listed = client.get(
                "/api/v1/logistik/freight-tariffs",
                params={"carrier_id": carrier},
                headers={"Authorization": "Bearer dev-token"},
            )
            assert listed.status_code == 200
            assert listed.json() == []
        finally:
            _purge_tariff(tariff_id)

    def test_freight_calculate_requires_tenant(self, logistics_db):
        r = client.post(
            "/api/v1/logistik/freight-cost/calculate",
            json={
                "carrier_id": "x",
                "distance_km": 1.0,
                "weight_kg": 1.0,
                "postal_code_from": "10115",
                "postal_code_to": "20095",
            },
            headers={"Authorization": "Bearer dev-token"},
        )
        assert r.status_code == 422

    def test_freight_list_with_tenant_returns_own_tariff(self, logistics_db):
        carrier = f"IT-LIST-OWN-{uuid.uuid4().hex[:8]}"
        created = client.post(
            "/api/v1/logistik/freight-tariffs",
            json={
                "carrier_id": carrier,
                "zone_from": "10",
                "zone_to": "20",
                "weight_from_kg": 0.0,
                "weight_to_kg": 999999.0,
                "price_per_100kg": 15.0,
                "min_charge": 2.0,
            },
            headers=HEADERS,
        )
        assert created.status_code == 201, created.text
        tariff_id = created.json()["id"]
        try:
            listed = client.get(
                "/api/v1/logistik/freight-tariffs",
                params={"carrier_id": carrier},
                headers=HEADERS,
            )
            assert listed.status_code == 200
            rows = listed.json()
            ids = [r["id"] for r in rows]
            assert tariff_id in ids
        finally:
            _purge_tariff(tariff_id)

    def test_chain_lifecycle_ls_tour_hints_freight_supply_read(self, logistics_db):
        """Audit Bruchstelle 2: Read-Spine LS → Tour-Hints → Fracht simulate → Ketten-Übersicht (Read)."""
        ls = client.get(
            "/api/v1/logistik/sales-delivery-note-by-ref",
            params={"ref": "DEMO-LS-001"},
            headers=HEADERS,
        )
        if ls.status_code != 200:
            pytest.skip("DEMO-LS-001 nicht vorhanden — zuerst seed_demo_sales.py (optional seed_demo_logistics_spine.py)")

        carrier = f"IT-CHAIN-{uuid.uuid4().hex[:8]}"
        tariff_id: str | None = None
        tour_id: str | None = None
        try:
            tcreate = client.post(
                "/api/v1/logistik/freight-tariffs",
                json={
                    "carrier_id": carrier,
                    "zone_from": "10",
                    "zone_to": "20",
                    "weight_from_kg": 0.0,
                    "weight_to_kg": 999999.0,
                    "price_per_100kg": 11.0,
                    "min_charge": 3.0,
                },
                headers=HEADERS,
            )
            assert tcreate.status_code == 201, tcreate.text
            tariff_id = tcreate.json()["id"]

            sim = client.get(
                "/api/v1/logistik/freight-cost/simulate",
                params={
                    "carrier_id": carrier,
                    "distance_km": 100.0,
                    "weight_kg": 100.0,
                    "postal_code_from": "10115",
                    "postal_code_to": "20095",
                },
                headers=HEADERS,
            )
            assert sim.status_code == 200, sim.text
            assert sim.json().get("freight_cost_eur") is not None

            vehicle_id = f"IT-CHAIN-TOUR-{uuid.uuid4().hex[:8]}"
            created = client.post(
                "/api/v1/logistik/tours",
                json={
                    "vehicle_id": vehicle_id,
                    "driver_id": "chain-driver",
                    "status": "GEPLANT",
                    "stops": [
                        {
                            "address": "Ketten-Test Stopp",
                            "stop_order": 0,
                            "delivery_note_ref": "DEMO-LS-001",
                        }
                    ],
                },
                headers=HEADERS,
            )
            assert created.status_code == 201, created.text
            tour_id = created.json()["id"]

            detail = client.get(
                f"/api/v1/logistik/tours/{tour_id}",
                params={"include_delivery_hints": "true"},
                headers=HEADERS,
            )
            assert detail.status_code == 200, detail.text
            stops = detail.json().get("stops") or []
            assert len(stops) >= 1
            hint = stops[0].get("delivery_note_hint")
            assert hint is not None
            assert hint.get("delivery_note_number") == "DEMO-LS-001"

            tickets = client.get(
                "/api/v1/supply-chain/traceability/tickets",
                params={"limit": 5},
                headers=HEADERS,
            )
            assert tickets.status_code == 200, tickets.text
            body = tickets.json()
            assert "items" in body

            cancel = client.post(
                f"/api/v1/logistik/tours/{tour_id}/cancel",
                json={"grund": "IT Ketten-Lifecycle"},
                headers=HEADERS,
            )
            assert cancel.status_code == 200, cancel.text
            assert cancel.json().get("status", "").upper() == "STORNIERT"
        finally:
            if tariff_id:
                _purge_tariff(tariff_id)
            if tour_id:
                _purge_tour(tour_id)
