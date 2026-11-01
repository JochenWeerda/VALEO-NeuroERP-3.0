"""DMS-Webhook schreibt tenant_id nur aus verifiziertem Claim — nie aus Payload."""

from __future__ import annotations

import uuid
from contextlib import contextmanager

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.database import SessionLocal
from app.core.tenant import get_tenant_id
from app.routers import dms_webhook_router as webhook_mod
from app.routers.dms_webhook_router import router
from testgrenze import ersetze_mandant, ersetze_nutzer

pytestmark = [pytest.mark.integration, pytest.mark.needs_live_db]


class _FakeResponse:
    def __init__(self, payload=None, body: str = ""):
        self._payload = payload
        self.text = body

    def raise_for_status(self) -> None:
        return None

    def json(self):
        return self._payload


class _FakeClient:
    def get(self, path: str):
        if path.endswith("/versions/"):
            return _FakeResponse({"results": [{"id": 1}]})
        if path.endswith("/ocr_content/"):
            return _FakeResponse(body="Rechnung RE-WH-1 Lieferant Nordkorn")
        raise AssertionError(f"unerwarteter DMS-Pfad: {path}")


@contextmanager
def _fake_get_client():
    yield _FakeClient()


@pytest.fixture
def webhook_client(require_db, monkeypatch):
    mandant = f"dms-wh-{uuid.uuid4().hex[:8]}"
    monkeypatch.setattr(webhook_mod, "is_configured", lambda: True)
    monkeypatch.setattr(webhook_mod, "get_client", _fake_get_client)
    app = FastAPI()
    app.include_router(router)
    ersetze_nutzer(app, "SALES_ADMIN")
    ersetze_mandant(app, mandant)
    return TestClient(app, raise_server_exceptions=False), mandant


def test_webhook_persists_verified_tenant(webhook_client):
    http, mandant = webhook_client
    document_id = 880_000 + (uuid.uuid4().int % 10_000)
    item_id = f"INBOX-{document_id}"
    try:
        response = http.post(
            "/api/dms/webhook",
            json={"event": "document.ocr.finished", "document_id": document_id},
        )
        assert response.status_code == 200, response.text
        assert response.json()["ok"] is True

        with SessionLocal() as db:
            row = db.execute(
                text(
                    """
                    SELECT tenant_id, status
                    FROM domain_shared.dms_inbox
                    WHERE id = :id
                    """
                ),
                {"id": item_id},
            ).mappings().one()
        assert row["tenant_id"] == mandant
        assert row["status"] == "pending"
    finally:
        with SessionLocal() as db:
            db.execute(text("DELETE FROM domain_shared.dms_inbox WHERE id = :id"), {"id": item_id})
            db.commit()


def test_webhook_without_verified_tenant_is_403(require_db):
    app = FastAPI()
    app.include_router(router)
    ersetze_nutzer(app, "SALES_ADMIN")
    # get_tenant_id nicht ersetzen → tenant_verified fehlt → 403

    def _deny_tenant():
        from fastapi import HTTPException

        raise HTTPException(status_code=403, detail="Verified tenant context required")

    app.dependency_overrides[get_tenant_id] = _deny_tenant
    http = TestClient(app, raise_server_exceptions=False)
    response = http.post(
        "/api/dms/webhook",
        json={"event": "document.created", "document_id": 1},
    )
    assert response.status_code == 403
    assert "tenant" in response.json()["detail"].lower()


def test_webhook_rejects_blank_tenant_with_400(require_db, monkeypatch):
    monkeypatch.setattr(webhook_mod, "is_configured", lambda: True)
    app = FastAPI()
    app.include_router(router)
    ersetze_nutzer(app, "SALES_ADMIN")
    app.dependency_overrides[get_tenant_id] = lambda: "   "
    http = TestClient(app, raise_server_exceptions=False)
    response = http.post(
        "/api/dms/webhook",
        json={"event": "document.created", "document_id": 2},
    )
    assert response.status_code == 400
    assert "tenant" in response.json()["detail"].lower()
