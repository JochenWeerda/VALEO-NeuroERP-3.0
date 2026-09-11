"""Rohware-Sammelabrechnung — echte HTTP-Vertraege (SPEC-P0-05).

Erfordert PostgreSQL (`require_db`). Lifecycle, Persistenz und Validierung
mit harten Statuscodes — keine Schein-201 ohne DB-Zeile.
"""
from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.database import SessionLocal
from app.main import app

client = TestClient(app, raise_server_exceptions=False)
TENANT = "00000000-0000-0000-0000-000000000001"
HEADERS = {
    "Authorization": "Bearer dev-token",
    "X-Tenant-Id": TENANT,
}
BASE = "/api/v1/agrar/sammelabrechnung"

pytestmark = pytest.mark.unit


def _seed_harvest(*, menge_kg: float = 1000.0, preis_eur_t: float = 200.0) -> str:
    ha_id = str(uuid.uuid4())
    db = SessionLocal()
    try:
        db.execute(
            text(
                """
                INSERT INTO domain_agrar.harvest_acceptances
                    (id, tenant_id, lieferant_id, artikel_nr, menge_netto_kg,
                     qualitaet_feuchte, qualitaet_besatz, preis_eur_t)
                VALUES
                    (:id, :tid, :lief, :art, :menge, :feuchte, :besatz, :preis)
                """
            ),
            {
                "id": ha_id,
                "tid": TENANT,
                "lief": "L-1",
                "art": "WEIZEN",
                "menge": menge_kg,
                "feuchte": 14.0,
                "besatz": 1.0,
                "preis": preis_eur_t,
            },
        )
        db.commit()
    finally:
        db.close()
    return ha_id


def _create_payload(ha_ids: list[str] | None = None) -> dict:
    ids = ha_ids or [_seed_harvest(), _seed_harvest()]
    return {
        "bezeichnung": f"IT-{uuid.uuid4().hex[:6]}",
        "abrechnungsperiode": "2026-08",
        "harvest_acceptance_ids": ids,
    }


def _assert_persisted(sid: str, *, status: str | None = None) -> dict:
    listed = client.get(BASE, headers=HEADERS)
    assert listed.status_code == 200, listed.text
    rows = listed.json()
    match = next((r for r in rows if r.get("id") == sid), None)
    assert match is not None, f"Sammelabrechnung {sid} nicht in Liste — Persistenz fehlt"
    if status is not None:
        assert match["status"] == status
    return match


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


def test_create_persists_and_is_reloadable(require_db):
    create = client.post(BASE, json=_create_payload(), headers=HEADERS)
    assert create.status_code == 201, create.text
    body = create.json()
    sid = body["id"]
    assert body["status"] == "ENTWURF"
    persisted = _assert_persisted(sid, status="ENTWURF")
    assert persisted["bezeichnung"] == body["bezeichnung"]


def test_create_calculate_book_and_conflict_on_delete(require_db):
    ha1 = _seed_harvest(menge_kg=2000.0, preis_eur_t=250.0)
    ha2 = _seed_harvest(menge_kg=1000.0, preis_eur_t=200.0)
    create = client.post(BASE, json=_create_payload([ha1, ha2]), headers=HEADERS)
    assert create.status_code == 201, create.text
    sid = create.json()["id"]
    _assert_persisted(sid, status="ENTWURF")

    calc = client.post(f"{BASE}/{sid}/berechnen", headers=HEADERS)
    assert calc.status_code == 200, calc.text
    assert calc.json()["status"] == "BERECHNET"
    assert calc.json()["summe_menge_kg"] == pytest.approx(3000.0)
    assert calc.json()["summe_betrag_eur"] == pytest.approx(700.0)
    persisted_calc = _assert_persisted(sid, status="BERECHNET")
    assert persisted_calc["summe_betrag_eur"] == pytest.approx(700.0)

    book = client.post(f"{BASE}/{sid}/buchen", headers=HEADERS)
    assert book.status_code == 200, book.text
    assert book.json().get("gebucht") is True
    assert book.json().get("op_angelegt") is True
    _assert_persisted(sid, status="GEBUCHT")

    deleted = client.delete(f"{BASE}/{sid}", headers=HEADERS)
    assert deleted.status_code == 409, deleted.text


def test_berechnen_unknown_harvest_is_422(require_db):
    create = client.post(
        BASE,
        json=_create_payload([str(uuid.uuid4()), str(uuid.uuid4())]),
        headers=HEADERS,
    )
    assert create.status_code == 201, create.text
    sid = create.json()["id"]
    calc = client.post(f"{BASE}/{sid}/berechnen", headers=HEADERS)
    assert calc.status_code == 422, calc.text
    detail = calc.json().get("detail") or {}
    assert "harvest_acceptance_id" in detail or "Harvest" in str(detail)


def test_delete_unknown_is_404(require_db):
    resp = client.delete(f"{BASE}/{uuid.uuid4()}", headers=HEADERS)
    assert resp.status_code == 404, resp.text


def test_book_without_calculate_is_409(require_db):
    create = client.post(BASE, json=_create_payload(), headers=HEADERS)
    assert create.status_code == 201, create.text
    sid = create.json()["id"]
    book = client.post(f"{BASE}/{sid}/buchen", headers=HEADERS)
    assert book.status_code == 409, book.text


def test_recalculate_after_book_is_409(require_db):
    create = client.post(BASE, json=_create_payload(), headers=HEADERS)
    assert create.status_code == 201, create.text
    sid = create.json()["id"]
    assert client.post(f"{BASE}/{sid}/berechnen", headers=HEADERS).status_code == 200
    assert client.post(f"{BASE}/{sid}/buchen", headers=HEADERS).status_code == 200
    recalc = client.post(f"{BASE}/{sid}/berechnen", headers=HEADERS)
    assert recalc.status_code == 409, recalc.text


def test_delete_draft_after_persist(require_db):
    create = client.post(BASE, json=_create_payload(), headers=HEADERS)
    assert create.status_code == 201, create.text
    sid = create.json()["id"]
    _assert_persisted(sid, status="ENTWURF")
    deleted = client.delete(f"{BASE}/{sid}", headers=HEADERS)
    assert deleted.status_code == 204, deleted.text
    listed = client.get(BASE, headers=HEADERS)
    assert listed.status_code == 200, listed.text
    assert all(r.get("id") != sid for r in listed.json())
