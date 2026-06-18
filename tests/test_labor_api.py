"""Labor API: /labor und /qualitaet Alias, Liste, Detail, Create."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

pytestmark = pytest.mark.usefixtures("require_db")

client = TestClient(app, raise_server_exceptions=False)


def test_qualitaet_labor_auftraege_list_ok():
    r = client.get("/api/v1/qualitaet/labor-auftraege")
    assert r.status_code == 200
    data = r.json()
    assert "items" in data
    assert isinstance(data["items"], list)


def test_labor_labor_auftraege_list_same_shape():
    r1 = client.get("/api/v1/labor/labor-auftraege")
    r2 = client.get("/api/v1/qualitaet/labor-auftraege")
    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r1.json()["total"] == r2.json()["total"]


def test_labor_auftrag_detail_and_chargen_id():
    lst = client.get("/api/v1/qualitaet/labor-auftraege").json()
    assert lst["items"]
    first_id = lst["items"][0]["id"]
    item = lst["items"][0]
    assert "chargenId" in item or "chargen_id" in item

    r = client.get(f"/api/v1/qualitaet/labor-auftraege/{first_id}")
    assert r.status_code == 200
    d = r.json()
    assert d["id"] == first_id
    assert "chargenId" in d


def test_labor_auftrag_create_201():
    r = client.post(
        "/api/v1/qualitaet/labor-auftraege",
        json={
            "chargenId": "TEST-CHARGE-001",
            "labor": "Test-Labor",
            "analysen": ["A", "B"],
            "prioritaet": "standard",
        },
    )
    assert r.status_code == 201
    body = r.json()
    assert body["id"]
    assert body["chargenId"] == "TEST-CHARGE-001"
    assert body["analysen"] == 2


def test_labor_auftrag_befund_creates_qs_followup():
    created = client.post(
        "/api/v1/qualitaet/labor-auftraege",
        json={
            "chargenId": "TEST-CHARGE-SPERRE-001",
            "labor": "Test-Labor",
            "analysen": ["Feuchte"],
            "prioritaet": "express",
        },
    )
    assert created.status_code == 201
    auftrag_id = created.json()["id"]

    r = client.post(
        f"/api/v1/qualitaet/labor-auftraege/{auftrag_id}/befund",
        json={
            "entscheidung": "sperren",
            "analysewerte": {"feuchte": 18.1},
            "grenzwerte": {"feuchte_max": 14.5},
            "bemerkung": "Grenzwert ueberschritten",
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert body["qs_entscheidung"] == "sperren"
    assert body["folgeaktion"] == "charge_sperren"
    assert body["status"] == "abgeschlossen"


def test_labor_auftrag_detail_404():
    r = client.get("/api/v1/qualitaet/labor-auftraege/does-not-exist-99999")
    assert r.status_code == 404
