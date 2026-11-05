"""Labor API: /labor und /qualitaet Alias, Liste, Detail, Create, Befund.

Seit Batch 8 (03.11.2026) ohne Seed und im Mandanten: Der Test legt seine Charge selbst an (ein Auftrag braucht eine
Charge des Mandanten) und liest nur, was er angelegt hat.
"""

from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.main import app

pytestmark = pytest.mark.usefixtures("require_db")

client = TestClient(app, raise_server_exceptions=False)
MANDANT = "test-tenant"
KOPF = {"X-Tenant-ID": MANDANT}


@pytest.fixture
def charge() -> str:
    from app.core.database import SessionLocal

    nummer = f"TEST-CHARGE-{uuid4().hex[:8]}"
    with SessionLocal() as db:
        db.execute(text("INSERT INTO domain_ops.ops_chargen (id, tenant_id, chargen_id, artikel, artikel_id, menge, lagerort, eingang) "
                        "VALUES (:i, :t, :c, 'Weizen', 'A-1', 250, 'Silo 1', now())"),
                   {"i": str(uuid4()), "t": MANDANT, "c": nummer})
        db.commit()
    return nummer


def _anlegen(charge: str, prioritaet: str = "standard") -> dict:
    r = client.post("/api/v1/qualitaet/labor-auftraege", headers=KOPF,
                    json={"chargenId": charge, "labor": "Test-Labor", "analysen": ["A", "B"], "prioritaet": prioritaet})
    assert r.status_code == 201, r.text
    return r.json()


def test_qualitaet_labor_auftraege_list_ok():
    r = client.get("/api/v1/qualitaet/labor-auftraege", headers=KOPF)
    assert r.status_code == 200
    data = r.json()
    assert isinstance(data["items"], list)


def test_labor_labor_auftraege_list_same_shape():
    r1 = client.get("/api/v1/labor/labor-auftraege", headers=KOPF)
    r2 = client.get("/api/v1/qualitaet/labor-auftraege", headers=KOPF)
    assert r1.status_code == r2.status_code == 200
    assert r1.json()["total"] == r2.json()["total"]


def test_labor_auftrag_create_detail_and_chargen_id(charge):
    body = _anlegen(charge)
    assert (body["chargenId"], body["analysen"]) == (charge, 2)
    r = client.get(f"/api/v1/qualitaet/labor-auftraege/{body['id']}", headers=KOPF)
    assert r.status_code == 200
    assert r.json()["chargenId"] == charge


def test_labor_auftrag_zu_unbekannter_charge_404():
    r = client.post("/api/v1/qualitaet/labor-auftraege", headers=KOPF,
                    json={"chargenId": f"GIBT-ES-NICHT-{uuid4().hex[:6]}", "labor": "Test-Labor", "analysen": ["A"]})
    assert r.status_code == 404


def test_labor_auftrag_befund_creates_qs_followup_und_speichert(charge):
    auftrag_id = _anlegen(charge, "express")["id"]
    r = client.post(
        f"/api/v1/qualitaet/labor-auftraege/{auftrag_id}/befund", headers=KOPF,
        json={"entscheidung": "sperren", "analysewerte": {"feuchte": 18.1}, "grenzwerte": {"feuchte_max": 14.5},
              "bemerkung": "Grenzwert ueberschritten"},
    )
    assert r.status_code == 200
    body = r.json()
    assert (body["qs_entscheidung"], body["folgeaktion"], body["status"]) == ("sperren", "charge_sperren", "abgeschlossen")
    gelesen = client.get(f"/api/v1/qualitaet/labor-auftraege/{auftrag_id}", headers=KOPF).json()
    assert gelesen["analysewerte"] == {"feuchte": 18.1}
    assert gelesen["bemerkung"] == "Grenzwert ueberschritten"


def test_labor_auftrag_detail_404():
    r = client.get("/api/v1/qualitaet/labor-auftraege/does-not-exist-99999", headers=KOPF)
    assert r.status_code == 404
