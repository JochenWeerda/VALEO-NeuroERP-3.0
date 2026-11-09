"""Vertreterprovisionen als Studio-Liste mit Kommandowegen (09.11.2026).

Die handgebaute Seite ist abgeloest: Gruppe anlegen, Staffelzeile anlegen und Stilllegen laufen als Fachaktion
(Trockenlauf prueft, Ausfuehren schreibt mit Audit); die Staffelzeilen liest eine flache Liste.
"""
from __future__ import annotations

import os
import uuid

import pytest

pytestmark = pytest.mark.integration

DB_URL = os.environ.get("TEST_DATABASE_URL", os.environ.get(
    "DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe"))
os.environ.setdefault("DATABASE_URL", DB_URL)

_PFAD = "/api/v1/crm/vertreter/provisionen"


@pytest.fixture(scope="module")
def mandant():
    from sqlalchemy import create_engine, text

    try:
        engine = create_engine(DB_URL, connect_args={"connect_timeout": 5})
        engine.connect().close()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    tid = f"vp-{uuid.uuid4().hex[:8]}"
    with engine.begin() as v:
        v.execute(text("INSERT INTO domain_shared.tenants (id, name) VALUES (:id, :id) ON CONFLICT (id) DO NOTHING"),
                  {"id": tid})
    yield {"tid": tid, "engine": engine}
    with engine.begin() as v:
        v.execute(text("DELETE FROM domain_shared.vertreter_staffel_zeilen WHERE tenant_id = :t"), {"t": tid})
        v.execute(text("DELETE FROM domain_shared.vertreter_provisionsstaffeln WHERE tenant_id = :t"), {"t": tid})
        v.execute(text("DELETE FROM domain_shared.vertreter_provisionsgruppen WHERE tenant_id = :t"), {"t": tid})
        v.execute(text("DELETE FROM outbox_events WHERE tenant_id = :t"), {"t": tid})


@pytest.fixture()
def client(mandant):
    from fastapi.testclient import TestClient

    from app.auth.deps import get_current_user
    from app.main import app

    vorher = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = lambda: {"sub": "vertrieb-1", "roles": ["CRM_BEARBEITEN", "CRM_LESEN"]}
    yield TestClient(app, raise_server_exceptions=False)
    if vorher is None:
        app.dependency_overrides.pop(get_current_user, None)
    else:
        app.dependency_overrides[get_current_user] = vorher


def _kopf(mandant):
    return {"X-Tenant-Id": mandant["tid"], "Authorization": "Bearer dev-token"}


def test_gruppe_staffel_und_stilllegen(client, mandant):
    kopf = _kopf(mandant)
    ohne_satz = client.post(f"{_PFAD}/gruppen/actions/anlegen", headers=kopf, json={
        "gruppe_nr": "P1", "bezeichnung": "Fest", "richtung": "vk", "provisionstyp": "fix"}).json()
    assert ohne_satz["success"] is False and "Satz" in ohne_satz["error"]
    trocken = client.post(f"{_PFAD}/gruppen/actions/anlegen", headers=kopf, json={
        "_mode": "dryRun", "gruppe_nr": "S1", "bezeichnung": "Staffel", "provisionstyp": "staffel_optpreis"}).json()
    assert trocken["success"] is True
    assert client.get(f"{_PFAD}/gruppen", headers=kopf).json() == []  # Trockenlauf schreibt nichts
    angelegt = client.post(f"{_PFAD}/gruppen/actions/anlegen", headers=kopf, json={
        "gruppe_nr": "S1", "bezeichnung": "Staffel", "provisionstyp": "staffel_optpreis"}).json()
    assert angelegt["success"] is True, angelegt
    doppelt = client.post(f"{_PFAD}/gruppen/actions/anlegen", headers=kopf, json={
        "gruppe_nr": "S1", "bezeichnung": "Nochmal", "provisionstyp": "staffel_optpreis"}).json()
    assert doppelt["success"] is False and "schon" in doppelt["error"]
    [gruppe] = client.get(f"{_PFAD}/gruppen", headers=kopf).json()
    for ab, satz in ((0, 1.5), (10000, "2,5")):
        zeile = client.post(f"{_PFAD}/gruppen/{gruppe['id']}/actions/staffelzeile_anlegen", headers=kopf,
                            json={"vertreterklasse": "A", "ab_wert": ab, "provisionssatz": satz}).json()
        assert zeile["success"] is True, zeile
    zeilen = client.get(f"{_PFAD}/staffelzeilen", headers=kopf).json()
    assert [(z["zeile_nr"], float(z["ab_wert"]), float(z["provisionssatz"])) for z in zeilen] == [
        (1, 0.0, 1.5), (2, 10000.0, 2.5)]
    assert {z["gruppe_nr"] for z in zeilen} == {"S1"}
    ohne_grund = client.post(f"{_PFAD}/gruppen/{gruppe['id']}/actions/deaktivieren", headers=kopf, json={}).json()
    assert ohne_grund["success"] is False
    still = client.post(f"{_PFAD}/gruppen/{gruppe['id']}/actions/deaktivieren", headers=kopf,
                        json={"_auditReason": "Gruppe ersetzt"}).json()
    assert still["success"] is True, still
    assert client.get(f"{_PFAD}/gruppen", headers=kopf).json() == []
    assert client.get(f"{_PFAD}/staffelzeilen", headers=kopf).json() == []


def test_fremder_mandant_sieht_die_gruppe_nicht(client, mandant):
    fremd = {"X-Tenant-Id": f"vp-fremd-{uuid.uuid4().hex[:6]}", "Authorization": "Bearer dev-token"}
    eigene = client.post(f"{_PFAD}/gruppen/actions/anlegen", headers=_kopf(mandant), json={
        "gruppe_nr": "F1", "bezeichnung": "Fest", "provisionstyp": "fix", "provisionssatz": 3}).json()
    assert eigene["success"] is True
    [gruppe] = [g for g in client.get(f"{_PFAD}/gruppen", headers=_kopf(mandant)).json() if g["gruppe_nr"] == "F1"]
    fremdzugriff = client.post(f"{_PFAD}/gruppen/{gruppe['id']}/actions/deaktivieren", headers=fremd,
                               json={"_auditReason": "Versuch"}).json()
    assert fremdzugriff["success"] is False
