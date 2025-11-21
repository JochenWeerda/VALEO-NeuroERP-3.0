from __future__ import annotations

from datetime import date
from typing import AsyncGenerator

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app import main
from app.config import settings
from app.db.models import Base
from app.dependencies import get_db_session, get_event_bus

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def test_app(monkeypatch) -> AsyncGenerator[FastAPI, None]:
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)

    async def override_session() -> AsyncGenerator[AsyncSession, None]:
        async with SessionLocal() as session:
            yield session

    previous_bus_state = settings.EVENT_BUS_ENABLED
    monkeypatch.setattr(settings, "EVENT_BUS_ENABLED", False)

    app = main.app
    app.dependency_overrides[get_db_session] = override_session
    app.dependency_overrides[get_event_bus] = lambda: None

    try:
        yield app
    finally:
        app.dependency_overrides.clear()
        monkeypatch.setattr(settings, "EVENT_BUS_ENABLED", previous_bus_state)
        await engine.dispose()


@pytest.mark.asyncio
async def test_ingestion_and_metrics(test_app: FastAPI) -> None:
    async with AsyncClient(app=test_app, base_url="http://test") as client:
        payload = {
            "records": [
                {
                    "commodity_code": "12099190",
                    "country_of_origin": "DE",
                    "country_of_destination": "FR",
                    "net_mass_kg": 100.0,
                    "invoice_value_eur": 15000.0,
                    "nature_of_transaction": "11",
                    "transport_mode": "3",
                    "delivery_terms": "DAP",
                }
            ]
        }
        params = {
            "tenant_id": "tenant-a",
            "reference_period": date(2025, 9, 1).isoformat(),
        }
        response = await client.post("/api/v1/ingestion/batch", json=payload, params=params)
        response.raise_for_status()
        body = response.json()
        assert body["ingested_lines"] == 1
        assert body["validation_error_count"] == 0

        metrics_response = await client.get("/metrics")
        metrics_response.raise_for_status()
        text = metrics_response.text
        assert "infrastat_validation_success_total" in text
