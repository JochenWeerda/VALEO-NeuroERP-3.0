"""Folgeartikel nur zwischen Artikeln desselben Mandanten (Fremdschluessel, 24.11.2026) - gegen die echte DB."""
from __future__ import annotations

import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api.v1.endpoints import artikel_stamm_ext
from app.core.database import SessionLocal, get_db
from testgrenze import ersetze_mandant, ersetze_nutzer

pytestmark = pytest.mark.integration


def _mandant(*artikelnummern: str) -> str:
    kennung = f"fa-{uuid.uuid4().hex[:6]}"
    with SessionLocal() as db:
        db.execute(text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"),
                   {"id": kennung})
        for nr in artikelnummern:
            db.execute(text("INSERT INTO domain_inventory.articles (id, tenant_id, article_number, name, unit) "
                            "VALUES (:id, :t, :nr, :nr, 'st')"), {"id": f"{kennung}-{nr}", "t": kennung, "nr": nr})
        db.commit()
    return kennung


def _aufraeumen(*mandanten: str) -> None:
    with SessionLocal() as db:
        for t in mandanten:
            db.execute(text("DELETE FROM domain_shared.artikel_folgeartikel WHERE tenant_id = :t"), {"t": t})
            db.execute(text("DELETE FROM domain_inventory.articles WHERE tenant_id = :t"), {"t": t})
        db.commit()


@pytest.fixture
def welt():
    eigener, fremder = _mandant("W-001", "W-002"), _mandant("F-900")
    app = FastAPI()
    app.include_router(artikel_stamm_ext.router)

    def sitzung():
        with SessionLocal() as db:
            yield db

    app.dependency_overrides[get_db] = sitzung
    ersetze_mandant(app, eigener)
    app.dependency_overrides[artikel_stamm_ext.get_tenant_id] = lambda: eigener  # Router liest den Header-Mandanten
    ersetze_nutzer(app, "STAMMDATEN_BEARBEITEN", "admin")
    try:
        with TestClient(app) as c:
            yield c, eigener
    finally:
        _aufraeumen(eigener, fremder)


def _anlegen(c, von: str, nach: str):
    return c.post("/artikel/folgeartikel", json={"artikel_nr": von, "folge_artikel_nr": nach, "grund": "Test"})


def test_folgeartikel_zwischen_eigenen_artikeln(welt):
    c, _ = welt

    angelegt = _anlegen(c, "W-001", "W-002")

    assert angelegt.status_code == 201, angelegt.text
    assert c.get("/artikel/folgeartikel/W-001/aktuell").json()["folgeartikel"] == "W-002"


@pytest.mark.parametrize(("von", "nach"), [("W-001", "GIBT-ES-NICHT"), ("GIBT-ES-NICHT", "W-002"), ("W-001", "F-900")])
def test_unbekannter_oder_fremder_artikel_abgewiesen(welt, von, nach):
    c, _ = welt

    antwort = _anlegen(c, von, nach)

    assert antwort.status_code == 404, antwort.text


def test_umnummerierung_wandert_mit(welt):
    c, mandant = welt
    _anlegen(c, "W-001", "W-002")
    with SessionLocal() as db:
        db.execute(text("UPDATE domain_inventory.articles SET article_number = 'W-002-NEU' "
                        "WHERE tenant_id = :t AND article_number = 'W-002'"), {"t": mandant})
        db.commit()

    assert c.get("/artikel/folgeartikel/W-001/aktuell").json()["folgeartikel"] == "W-002-NEU"
