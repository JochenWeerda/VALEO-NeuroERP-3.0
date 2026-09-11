"""Rohware-Sammelabrechnung — echte HTTP-Vertraege (SPEC-P0-05).

Erfordert PostgreSQL (`require_db`). Lifecycle und Validierung mit harten Statuscodes.
"""
from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app, raise_server_exceptions=False)
HEADERS = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-Id": "00000000-0000-0000-0000-000000000001",
}
BASE = "/api/v1/agrar/sammelabrechnung"

pytestmark = pytest.mark.unit


def test_list_returns_200_list(require_db):
    resp = client.get(BASE, headers=HEADERS)
    assert resp.status_code == 200, resp.text
    assert isinstance(resp.json(), list)


def test_create_requires_min_two_acceptance_ids(require_db):
    resp = client.post(
        BASE,
        json={"bezeichnung": "T", "abrechnungsperiode": "2026-08", "harvest_acceptance_ids": ["a"]},
        headers=HEADERS,
    )
    assert resp.status_code == 422, resp.text


def test_create_calculate_book_and_conflict_on_delete(require_db):
    create = client.post(
        BASE,
        json={
            "bezeichnung": f"IT-{uuid.uuid4().hex[:6]}",
            "abrechnungsperiode": "2026-08",
            "harvest_acceptance_ids": [str(uuid.uuid4()), str(uuid.uuid4())],
        },
        headers=HEADERS,
    )
    assert create.status_code == 201, create.text
    sid = create.json()["id"]
    assert create.json()["status"] == "ENTWURF"

    calc = client.post(f"{BASE}/{sid}/berechnen", headers=HEADERS)
    assert calc.status_code == 200, calc.text
    assert calc.json()["status"] == "BERECHNET"

    book = client.post(f"{BASE}/{sid}/buchen", headers=HEADERS)
    assert book.status_code == 200, book.text
    assert book.json().get("gebucht") is True

    deleted = client.delete(f"{BASE}/{sid}", headers=HEADERS)
    assert deleted.status_code == 409, deleted.text


def test_delete_unknown_is_404(require_db):
    resp = client.delete(f"{BASE}/{uuid.uuid4()}", headers=HEADERS)
    assert resp.status_code == 404, resp.text


def test_book_without_calculate_is_409(require_db):
    create = client.post(
        BASE,
        json={
            "bezeichnung": f"DRAFT-{uuid.uuid4().hex[:6]}",
            "abrechnungsperiode": "2026-08",
            "harvest_acceptance_ids": [str(uuid.uuid4()), str(uuid.uuid4())],
        },
        headers=HEADERS,
    )
    assert create.status_code == 201, create.text
    sid = create.json()["id"]

    book = client.post(f"{BASE}/{sid}/buchen", headers=HEADERS)
    assert book.status_code == 409, book.text


def test_recalculate_after_book_is_409(require_db):
    create = client.post(
        BASE,
        json={
            "bezeichnung": f"BOOK-{uuid.uuid4().hex[:6]}",
            "abrechnungsperiode": "2026-08",
            "harvest_acceptance_ids": [str(uuid.uuid4()), str(uuid.uuid4())],
        },
        headers=HEADERS,
    )
    assert create.status_code == 201, create.text
    sid = create.json()["id"]
    assert client.post(f"{BASE}/{sid}/berechnen", headers=HEADERS).status_code == 200
    assert client.post(f"{BASE}/{sid}/buchen", headers=HEADERS).status_code == 200

    recalc = client.post(f"{BASE}/{sid}/berechnen", headers=HEADERS)
    assert recalc.status_code == 409, recalc.text
