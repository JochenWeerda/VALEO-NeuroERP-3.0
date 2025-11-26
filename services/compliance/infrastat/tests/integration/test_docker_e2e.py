from __future__ import annotations

import asyncio
from datetime import date
from pathlib import Path

import pytest
from httpx import AsyncClient

from app.config import settings

COMPOSE_FILE = Path(__file__).resolve().parents[3] / "docker-compose.integration.yml"


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.skipif(not COMPOSE_FILE.exists(), reason="Integration docker compose not available")
async def test_infrastat_end_to_end(integration_environment) -> None:
    async with AsyncClient(base_url="http://localhost:5205") as client:
        payload = {
            "records": [
                {
                    "commodity_code": "12099190",
                    "country_of_origin": "DE",
                    "country_of_destination": "FR",
                    "net_mass_kg": 100.0,
                    "invoice_value_eur": 15000.0,
                }
            ]
        }
        params = {
            "tenant_id": "tenant-integration",
            "reference_period": date.today().replace(day=1).isoformat(),
        }
        response = await client.post("/api/v1/ingestion/batch", json=payload, params=params)
        response.raise_for_status()

        batches = await client.get("/api/v1/batches", params={"tenant_id": "tenant-integration"})
        batches.raise_for_status()
        assert batches.json()

        metrics = await client.get("/metrics")
        metrics.raise_for_status()
        assert "infrastat_validation_success_total" in metrics.text
