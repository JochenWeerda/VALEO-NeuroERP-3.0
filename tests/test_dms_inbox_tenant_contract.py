"""DMS inbox HTTP and PostgreSQL isolation on the existing shared probe."""

from __future__ import annotations

import uuid
import os

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api.v1.endpoints.dms_inbox import router as v1_router
from app.core.database import SessionLocal, engine
from app.documents.dms_inbox_model import inbox_id_for_document
from app.routers import dms_webhook_router as webhook
from helpers.dms_inbox import insert_inbox
from testgrenze import ersetze_bearer, pruefstand_erlaubt

TENANT_A = "00000000-0000-0000-0000-000000000001"
TENANT_B = "00000000-0000-0000-0000-000000000002"


@pytest.fixture
def pg_probe():
    """Use only the declared shared probe (also works without the huge app conftest)."""
    declared = os.environ.get("TEST_DATABASE_URL")
    assert declared and pruefstand_erlaubt(engine.url)
    from sqlalchemy.engine import make_url

    assert make_url(declared).database == engine.url.database
    with SessionLocal() as db:
        db.execute(text("SELECT 1"))


def _client(*roles: str) -> TestClient:
    app = FastAPI()
    app.include_router(webhook.router)
    app.include_router(v1_router, prefix="/api/v1/dms")
    ersetze_bearer(app, *roles)
    return TestClient(app, raise_server_exceptions=False)


def _get_status(item_id: str) -> str | None:
    with SessionLocal() as db:
        return db.execute(
            text("SELECT status FROM domain_shared.dms_inbox WHERE id = :id"), {"id": item_id}
        ).scalar_one_or_none()


def _cleanup(*item_ids: str) -> None:
    with SessionLocal() as db:
        for item_id in item_ids:
            db.execute(text("DELETE FROM domain_shared.dms_inbox WHERE id = :id"), {"id": item_id})
        db.commit()


def test_both_inbox_routes_filter_tenant_and_stop_fake_booking(pg_probe):
    own = f"DMSQA-{uuid.uuid4().hex}"
    foreign = f"DMSQA-{uuid.uuid4().hex}"
    with SessionLocal() as db:
        insert_inbox(db, item_id=own, tenant_id=TENANT_A, number="RE-OWN")
        insert_inbox(db, item_id=foreign, tenant_id=TENANT_B, number="RE-FOREIGN")
        db.commit()
    try:
        http = _client("FINANCE_BEARBEITEN")
        reader = _client("FINANCE_LESEN")
        for base in ("/api/dms", "/api/v1/dms"):
            assert reader.get(f"{base}/inbox", headers={"X-Tenant-ID": TENANT_A}).status_code == 200
            own_list = http.get(f"{base}/inbox", headers={"X-Tenant-ID": TENANT_A})
            assert own_list.status_code == 200, own_list.text
            ids = {item["id"] for item in own_list.json()["items"]}
            assert own in ids and foreign not in ids

            foreign_create = http.post(f"{base}/inbox/{foreign}/create", json={}, headers={"X-Tenant-ID": TENANT_A})
            foreign_delete = http.delete(f"{base}/inbox/{foreign}", headers={"X-Tenant-ID": TENANT_A})
            assert foreign_create.status_code == 404, foreign_create.text
            assert foreign_delete.status_code == 404, foreign_delete.text

            own_create = http.post(f"{base}/inbox/{own}/create", json={"invoice_number": "FAKE"}, headers={"X-Tenant-ID": TENANT_A})
            assert own_create.status_code == 409, own_create.text
            detail = own_create.json()["detail"]
            assert detail["code"] == "booking_not_from_inbox"
            assert detail["open_mask"] == "/einkauf/rechnung-eingang-erfassung"
            assert _get_status(own) == "pending"
            assert _get_status(foreign) == "pending"

        own_detail = http.get(f"/api/dms/inbox/{own}", headers={"X-Tenant-ID": TENANT_A})
        foreign_detail = http.get(f"/api/dms/inbox/{foreign}", headers={"X-Tenant-ID": TENANT_A})
        assert own_detail.status_code == 200
        assert foreign_detail.status_code == 404

        deleted = http.delete(f"/api/v1/dms/inbox/{own}", headers={"X-Tenant-ID": TENANT_A})
        assert deleted.status_code == 204, deleted.text
        assert _get_status(own) is None
        assert _get_status(foreign) == "pending"
    finally:
        _cleanup(own, foreign)


def test_read_roles_do_not_gain_mutation_and_unprivileged_cannot_read():
    reader = _client("FINANCE_LESEN")
    no_role = _client("user")
    for base in ("/api/dms", "/api/v1/dms"):
        assert no_role.get(f"{base}/inbox", headers={"X-Tenant-ID": TENANT_A}).status_code == 403
        assert reader.post(f"{base}/inbox/any/create", json={}, headers={"X-Tenant-ID": TENANT_A}).status_code == 403
        assert reader.delete(f"{base}/inbox/any", headers={"X-Tenant-ID": TENANT_A}).status_code == 403
    assert reader.post("/api/dms/webhook", json={"event": "document.created", "document_id": 1},
                       headers={"X-Tenant-ID": TENANT_A}).status_code == 403


class _MayanResponse:
    def __init__(self, *, body=None, content=""):
        self.body = body
        self.text = content

    def raise_for_status(self):
        return None

    def json(self):
        return self.body


class _MayanClient:
    def __init__(self, paths):
        self.paths = paths

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return None

    def get(self, path):
        self.paths.append(path)
        if path.endswith("/versions/"):
            return _MayanResponse(body={"results": [{"id": 7}]})
        if path.endswith("/ocr_content/"):
            return _MayanResponse(content=(
                "Eingangsrechnung Nr. RE-123\nLieferant: Test Handel GmbH\n"
                "MwSt 19% Zahlungsziel 14 Tage\n"
                "Pos Art-Nr Bezeichnung Menge ME Preis\n1 AB12 Korn 2 kg 3,00\n"
            ))
        raise AssertionError(f"Unexpected DMS path: {path}")


def test_webhook_binding_upsert_retry_and_same_document_other_tenant(pg_probe, monkeypatch):
    document_id = 800000000 + (uuid.uuid4().int % 100000000)
    own_id = inbox_id_for_document(TENANT_A, document_id)
    other_id = inbox_id_for_document(TENANT_B, document_id)
    paths = []
    monkeypatch.setattr(webhook, "is_configured", lambda: True)
    monkeypatch.setattr(webhook, "get_client", lambda: _MayanClient(paths))
    monkeypatch.setenv("EINKAUF_OCR_ENGINE", "stub")
    http = _client("FINANCE_BEARBEITEN")
    request = {"event": "document.created", "document_id": document_id}
    try:
        monkeypatch.delenv("DMS_TENANT_ID", raising=False)
        missing = http.post("/api/dms/webhook", json=request, headers={"X-Tenant-ID": TENANT_A})
        assert missing.status_code == 503 and paths == []

        monkeypatch.setenv("DMS_TENANT_ID", TENANT_A)
        foreign = http.post("/api/dms/webhook", json=request, headers={"X-Tenant-ID": TENANT_B})
        assert foreign.status_code == 404 and paths == []

        first = http.post("/api/dms/webhook", json=request, headers={"X-Tenant-ID": TENANT_A})
        assert first.status_code == 200, first.text
        assert _get_status(own_id) == "pending"
        with SessionLocal() as db:
            row = db.execute(text("SELECT parsed_fields FROM domain_shared.dms_inbox WHERE id=:id"), {"id": own_id}).scalar_one()
            assert row.get("positionen"), row
            db.execute(text("UPDATE domain_shared.dms_inbox SET status='processed' WHERE id=:id"), {"id": own_id})
            db.commit()

        retry = http.post("/api/dms/webhook", json={**request, "event": "document.ocr.finished"},
                          headers={"X-Tenant-ID": TENANT_A})
        assert retry.status_code == 200, retry.text
        assert _get_status(own_id) == "processed"

        monkeypatch.setenv("DMS_TENANT_ID", TENANT_B)
        second_tenant = http.post("/api/dms/webhook", json=request, headers={"X-Tenant-ID": TENANT_B})
        assert second_tenant.status_code == 200, second_tenant.text
        assert own_id != other_id and _get_status(other_id) == "pending"
        assert _get_status(own_id) == "processed"
    finally:
        _cleanup(own_id, other_id)


def test_webhook_rejects_cross_tenant_identity_conflict_without_replacing_row(pg_probe, monkeypatch):
    document_id = 900000000 + (uuid.uuid4().int % 100000000)
    conflicted_id = inbox_id_for_document(TENANT_A, document_id)
    with SessionLocal() as db:
        insert_inbox(db, item_id=conflicted_id, tenant_id=TENANT_B, number="RE-FOREIGN")
        db.execute(text("UPDATE domain_shared.dms_inbox SET dms_document_id=:document_id WHERE id=:id"),
                   {"document_id": document_id, "id": conflicted_id})
        db.commit()
    paths = []
    monkeypatch.setenv("DMS_TENANT_ID", TENANT_A)
    monkeypatch.setenv("EINKAUF_OCR_ENGINE", "stub")
    monkeypatch.setattr(webhook, "is_configured", lambda: True)
    monkeypatch.setattr(webhook, "get_client", lambda: _MayanClient(paths))
    try:
        http = _client("FINANCE_BEARBEITEN")
        response = http.post("/api/dms/webhook", json={"event": "document.created", "document_id": document_id},
                             headers={"X-Tenant-ID": TENANT_A})
        assert response.status_code == 409, response.text
        with SessionLocal() as db:
            row = db.execute(text("SELECT tenant_id, status, parsed_fields FROM domain_shared.dms_inbox WHERE id=:id"),
                             {"id": conflicted_id}).one()
            assert row.tenant_id == TENANT_B
            assert row.status == "pending"
            assert row.parsed_fields["invoice_number"] == "RE-FOREIGN"
    finally:
        _cleanup(conflicted_id)
