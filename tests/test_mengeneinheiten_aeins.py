"""Mengeneinheiten nach a.eins (Grundmengeneinheit) - gegen die echte Datenbank (Nutzerauftrag 24.11.2026)."""
from __future__ import annotations

import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api.v1.endpoints import artikel_mengeneinheiten
from app.core.database import SessionLocal, get_db
from app.services.mengeneinheiten_grund import GRUNDEINHEITEN
from testgrenze import ersetze_mandant, ersetze_nutzer

pytestmark = pytest.mark.integration


@pytest.fixture
def mandant():
    kennung = f"me-{uuid.uuid4().hex[:6]}"
    with SessionLocal() as db:
        db.execute(text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"),
                   {"id": kennung})
        db.commit()
    try:
        yield kennung
    finally:
        with SessionLocal() as db:
            db.execute(text("DELETE FROM domain_shared.artikel_mengeneinheiten WHERE tenant_id = :t"), {"t": kennung})
            db.commit()


@pytest.fixture
def client(mandant):
    app = FastAPI()
    app.include_router(artikel_mengeneinheiten.router)

    def sitzung():
        with SessionLocal() as db:
            yield db

    app.dependency_overrides[get_db] = sitzung
    ersetze_mandant(app, mandant)
    ersetze_nutzer(app, "STAMMDATEN_BEARBEITEN", "admin")
    with TestClient(app) as c:
        yield c


def test_grundeinheiten_werden_mit_un_code_eingerichtet_und_nicht_doppelt(client):
    erste = client.post("/artikel/mengeneinheiten/stamm/grundeinheiten")
    zweite = client.post("/artikel/mengeneinheiten/stamm/grundeinheiten")

    assert erste.status_code == 201, erste.text
    assert sorted(erste.json()) == sorted(g.kuerzel for g in GRUNDEINHEITEN)
    assert zweite.json() == []
    dt = client.get("/artikel/mengeneinheiten/stamm/dt").json()
    assert (dt["un_code"], dt["basis_einheit"], float(dt["umrechnungsfaktor"]), dt["dezimalstellen"]) == \
        ("DTN", "kg", 100.0, 2)
    sack = client.get("/artikel/mengeneinheiten/stamm/sack").json()
    assert sack["umrechnungsfaktor"] is None  # Zaehleinheit: Faktor haengt am Artikel


def test_felder_der_grundmengeneinheit_mit_preisbezug(client):
    angelegt = client.post("/artikel/mengeneinheiten/stamm", json={
        "einheit_kuerzel": "kg100", "bezeichnung": "Kilogramm, Preis je 100 kg", "nummer": 42, "langtext": "Kilogramm",
        "dezimalstellen": 2, "preisbezug_einheit": "kg", "preisbezug_menge": 100, "un_code": "KGM",
        "datanorm_kurz": "KG", "statistikkennzeichen": "M"})

    assert angelegt.status_code == 201, angelegt.text
    body = angelegt.json()
    assert (body["nummer"], float(body["preisbezug_menge"]), body["un_code"]) == (42, 100.0, "KGM")


def test_eingaben_werden_geprueft(client):
    zu_lange_nummer = client.post("/artikel/mengeneinheiten/stamm", json={
        "einheit_kuerzel": "x1", "bezeichnung": "x", "nummer": 10000})
    falscher_code = client.post("/artikel/mengeneinheiten/stamm", json={
        "einheit_kuerzel": "x2", "bezeichnung": "x", "un_code": "kg"})
    rundung = client.post("/artikel/mengeneinheiten/stamm", json={
        "einheit_kuerzel": "x3", "bezeichnung": "x", "dezimalstellen": 5})

    assert (zu_lange_nummer.status_code, falscher_code.status_code, rundung.status_code) == (422, 422, 422)


def test_rundung_einer_aktiven_einheit_nur_nach_oben(client):
    client.post("/artikel/mengeneinheiten/stamm/grundeinheiten")
    basis = {"bezeichnung": "Dezitonne (100 kg)", "basis_einheit": "kg", "umrechnungsfaktor": 100, "un_code": "DTN"}

    hoeher = client.put("/artikel/mengeneinheiten/stamm/dt", json={"einheit_kuerzel": "dt", "dezimalstellen": 3, **basis})
    tiefer = client.put("/artikel/mengeneinheiten/stamm/dt", json={"einheit_kuerzel": "dt", "dezimalstellen": 1, **basis})

    assert hoeher.status_code == 200, hoeher.text
    assert tiefer.status_code == 409
    assert client.get("/artikel/mengeneinheiten/stamm/dt").json()["dezimalstellen"] == 3


def test_e_rechnung_nimmt_den_un_code_aus_dem_stamm(client, mandant):
    from app.services.beleg_erechnung import einheit_code

    client.post("/artikel/mengeneinheiten/stamm", json={"einheit_kuerzel": "BB1", "bezeichnung": "Big Bag 1 t",
                                                         "un_code": "XBG"})
    with SessionLocal() as db:
        assert einheit_code("BB1", db, mandant) == "XBG"   # aus dem Stamm
        assert einheit_code("dt", db, mandant) == "DTN"    # Rueckfall Grundeinheiten-Tabelle
        with pytest.raises(Exception, match="UN/ECE"):
            einheit_code("Kiste", db, mandant)
