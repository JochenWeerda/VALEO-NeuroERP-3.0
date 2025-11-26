"""Finance GoBD smoke tests."""

from __future__ import annotations

import os
from pathlib import Path
import time
from typing import Iterator

import pytest
from fastapi.testclient import TestClient

os.environ["FINANCE_DATABASE_URL"] = "sqlite:///./gobd_test.db"

from services.finance.app.core.database import Base, engine, SessionLocal  # noqa: E402
from services.finance.app.domains.finance import service as finance_domain_service  # noqa: E402
from services.finance.main import app  # noqa: E402

client = TestClient(app)
_DB_FILE = Path("gobd_test.db")


@pytest.fixture(autouse=True)
def reset_finance_db() -> Iterator[None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    finance_domain_service._audit_registry.clear()  # type: ignore[attr-defined]
    yield
    # Ensure all sessions are closed and engine disposed before deleting sqlite file on Windows
    try:
        SessionLocal.remove()  # type: ignore[attr-defined]
    except Exception:
        pass
    try:
        engine.dispose()
    except Exception:
        pass
    if _DB_FILE.exists():
        for _ in range(10):
            try:
                _DB_FILE.unlink()
                break
            except PermissionError:
                time.sleep(0.1)


def _ensure_account_id() -> str:
    resp = client.get("/api/v1/chart-of-accounts")
    resp.raise_for_status()
    return resp.json()["items"][0]["id"]


def test_journal_entry_contains_required_fields() -> None:
    account_id = _ensure_account_id()
    payload = {
        "account_id": account_id,
        "description": "Test GoBD entry",
        "amount": 123.45,
        "currency": "EUR",
        "period": "2025-11",
        "document_id": "DOC-1000",
        "userId": "auditor",
    }
    resp = client.post("/api/v1/journal-entries", json=payload)
    assert resp.status_code == 201
    body = resp.json()
    entry = body["entry"]
    assert entry["description"] == "Test GoBD entry"
    assert entry["document_id"] == "DOC-1000"
    assert entry["period"] == "2025-11"
    assert "posted_at" in entry
    assert body["audit_hash"]


def test_audit_trail_is_hash_chained() -> None:
    account_id = _ensure_account_id()
    payload = {
        "account_id": account_id,
        "description": "First entry",
        "amount": 10,
        "currency": "EUR",
        "period": "2025-10",
        "document_id": "DOC-1",
        "userId": "auditor",
    }
    resp = client.post("/api/v1/journal-entries", json=payload)
    first_hash = resp.json()["audit_hash"]

    payload["description"] = "Second entry"
    payload["document_id"] = "DOC-2"
    resp = client.post("/api/v1/journal-entries", json=payload)
    second_hash = resp.json()["audit_hash"]

    assert first_hash != second_hash
    audit_trail = finance_domain_service._audit_registry["default"]  # type: ignore[index]
    audit_trail.verify_chain()


def test_invalid_period_is_rejected() -> None:
    account_id = _ensure_account_id()
    payload = {
        "account_id": account_id,
        "description": "Bad period",
        "amount": 10,
        "currency": "EUR",
        "period": "2025/10",
        "userId": "auditor",
    }
    resp = client.post("/api/v1/journal-entries", json=payload)
    assert resp.status_code == 422

