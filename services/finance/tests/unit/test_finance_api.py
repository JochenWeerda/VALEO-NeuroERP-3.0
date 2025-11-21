"""Smoke tests for the finance FastAPI service."""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
PACKAGE_SRC = ROOT / "packages" / "finance-shared" / "src"
if str(PACKAGE_SRC) not in sys.path:
    sys.path.insert(0, str(PACKAGE_SRC))

os.environ["FINANCE_DATABASE_URL"] = "sqlite:///./test_finance.db"

from services.finance.app.core import config as core_config

core_config.get_settings.cache_clear()

import services.finance.app.core.database as database_module

database_module = importlib.reload(database_module)

from services.finance.app.core.database import Base, engine
from fastapi.testclient import TestClient

from services.finance.main import app


client = TestClient(app)


def reset_db() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def test_health_and_ready_endpoints():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


def test_chart_of_accounts_seed_and_list():
    reset_db()
    resp = client.get("/api/v1/chart-of-accounts")
    assert resp.status_code == 200
    data = resp.json()
    assert data["items"]
    assert data["items"][0]["account_number"]


def test_create_journal_entry_and_list():
    reset_db()
    payload = {
        "account_id": "temporary",
        "description": "Initial booking",
        "amount": 100.5,
        "currency": "EUR",
        "period": "2025-11",
        "userId": "tester",
    }

    # ensure accounts exist to grab actual id
    accounts = client.get("/api/v1/chart-of-accounts").json()["items"]
    payload["account_id"] = accounts[0]["id"]

    response = client.post("/api/v1/journal-entries", json=payload)
    assert response.status_code == 201
    body = response.json()
    assert body["entry"]["description"] == "Initial booking"
    assert body["audit_hash"]

    listing = client.get("/api/v1/journal-entries")
    assert listing.status_code == 200
    assert listing.json()["items"]

