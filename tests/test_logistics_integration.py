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
