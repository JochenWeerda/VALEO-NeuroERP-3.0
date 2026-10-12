"""Kontenplan: Der Mandant kommt aus dem Mandantenkontext, nicht aus der Anfrage.

Bis zum 12.10.2026 nahm ``chart_of_accounts.py`` den Mandanten aus dem Query-Parameter
``tenant_id`` (Liste, Pruefung, DATEV-Ausgabe) oder aus dem Rumpf (anlegen); lesen, aendern
und loeschen eines einzelnen Kontos filterten gar nicht. Wer lesen durfte, bekam mit
``?tenant_id=`` Kontenplan und DATEV-Buchungen eines anderen Mandanten.

Geprueft gegen die echte Datenbank — ein Mandantenfilter, der nur im Mock greift, greift nicht.
"""

from __future__ import annotations

import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api.v1.endpoints import chart_of_accounts
from app.auth.deps import get_current_user
from app.core.database import SessionLocal, get_db

HAUS_A = "kp-mandant-a"
HAUS_B = "kp-mandant-b"
PREFIX = "/api/v1/finance/chart-of-accounts"


def _kopf(mandant: str) -> dict[str, str]:
    return {"X-Tenant-ID": mandant}


def _konto(nummer: str, mandant_im_rumpf: str) -> dict:
    return {"tenant_id": mandant_im_rumpf, "account_number": nummer, "account_name": f"Konto {nummer}",
            "account_type": "asset", "category": "current_assets", "currency": "EUR"}


@pytest.fixture
def haus():
    """Zwei Mandanten, je ein eigenes Konto, dazu eines im gemeinsamen Rahmen."""
    lauf = uuid.uuid4().hex[:6]
    gemeinsam_id = f"kp-{lauf}-sys"
    with SessionLocal() as db:
        for mandant in (HAUS_A, HAUS_B, "system"):
            db.execute(text(
                "INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true) "
                "ON CONFLICT (id) DO NOTHING"), {"id": mandant})
        db.execute(text(
            "INSERT INTO domain_erp.chart_of_accounts "
            "(id, account_number, account_name, account_type, category, tenant_id, is_active) "
            "VALUES (:id, :nr, 'Gemeinsam', 'asset', 'current_assets', 'system', true)"),
            {"id": gemeinsam_id, "nr": f"S{lauf}"})
        db.commit()

    app = FastAPI()
    app.include_router(chart_of_accounts.router, prefix="/api/v1/finance")
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "5f0c2a9e", "name": "t.de-vries", "roles": ["FINANCE_ADMIN"]}
    with TestClient(app) as client:
        a = client.post(PREFIX + "/", json=_konto(f"A{lauf}", HAUS_A), headers=_kopf(HAUS_A))
        b = client.post(PREFIX + "/", json=_konto(f"B{lauf}", HAUS_B), headers=_kopf(HAUS_B))
        assert a.status_code == 200 and b.status_code == 200, (a.text, b.text)
        try:
            yield {"client": client, "app": app, "lauf": lauf, "a": a.json()["id"], "b": b.json()["id"],
                   "gemeinsam": gemeinsam_id}
        finally:
            with SessionLocal() as db:
                db.execute(text("DELETE FROM domain_erp.chart_of_accounts WHERE account_number LIKE :m"),
                           {"m": f"_{lauf}%"})
                db.commit()


def _nummern(antwort) -> set[str]:
    return {k["account_number"] for k in antwort.json()["items"]}


def test_liste_zeigt_eigene_und_gemeinsame_konten(haus):
    lauf = haus["lauf"]
    antwort = haus["client"].get(PREFIX + "/", params={"search": lauf, "limit": 200}, headers=_kopf(HAUS_A))
    assert antwort.status_code == 200, antwort.text
    assert _nummern(antwort) == {f"A{lauf}", f"S{lauf}"}


def test_query_parameter_waehlt_keinen_fremden_mandanten(haus):
    """Der alte Weg: ``?tenant_id=`` nannte den Mandanten, dessen Konten man sehen wollte."""
    lauf = haus["lauf"]
    antwort = haus["client"].get(
        PREFIX + "/", params={"search": lauf, "limit": 200, "tenant_id": HAUS_B}, headers=_kopf(HAUS_A))
    assert antwort.status_code == 200, antwort.text
    assert f"B{lauf}" not in _nummern(antwort)
    assert f"A{lauf}" in _nummern(antwort)


@pytest.mark.parametrize("methode,rumpf", [("GET", None), ("PUT", {"account_name": "gekapert"}), ("DELETE", None)])
def test_fremdes_konto_gibt_es_nicht(haus, methode, rumpf):
    antwort = haus["client"].request(methode, f"{PREFIX}/{haus['b']}", json=rumpf, headers=_kopf(HAUS_A))
    assert antwort.status_code == 404, antwort.text
    eigentuemer = haus["client"].get(f"{PREFIX}/{haus['b']}", headers=_kopf(HAUS_B))
    assert eigentuemer.status_code == 200, eigentuemer.text
    assert eigentuemer.json()["account_name"] == f"Konto B{haus['lauf']}"
    assert eigentuemer.json()["is_active"] is True


def test_eigenes_und_gemeinsames_konto_sind_lesbar(haus):
    for konto in (haus["a"], haus["gemeinsam"]):
        antwort = haus["client"].get(f"{PREFIX}/{konto}", headers=_kopf(HAUS_A))
        assert antwort.status_code == 200, antwort.text


def test_anlegen_folgt_der_anmeldung_nicht_dem_rumpf(haus):
    """Im Rumpf steht Haus B — das Konto gehoert trotzdem dem angemeldeten Haus A."""
    nummer = f"X{haus['lauf']}"
    antwort = haus["client"].post(PREFIX + "/", json=_konto(nummer, HAUS_B), headers=_kopf(HAUS_A))
    assert antwort.status_code == 200, antwort.text
    assert antwort.json()["tenant_id"] == HAUS_A
    bei_b = haus["client"].get(PREFIX + "/", params={"search": nummer}, headers=_kopf(HAUS_B))
    assert _nummern(bei_b) == set()


def test_aendern_wirkt_auch_ohne_namen_im_rumpf(haus):
    """Der Weg aenderte nur, wenn der Name im Rumpf stand — und meldete sonst Erfolg ohne Wirkung."""
    antwort = haus["client"].put(f"{PREFIX}/{haus['a']}", json={"category": "fixed_assets"}, headers=_kopf(HAUS_A))
    assert antwort.status_code == 200, antwort.text
    gelesen = haus["client"].get(f"{PREFIX}/{haus['a']}", headers=_kopf(HAUS_A))
    assert gelesen.json()["category"] == "fixed_assets"


class _Mitschnitt:
    """Nimmt die Parameter der DATEV-Abfrage auf und liefert keine Buchungen."""

    def __init__(self):
        self.parameter: list[dict] = []

    def execute(self, _sql, parameter=None):
        self.parameter.append(dict(parameter or {}))
        return self

    def fetchall(self):
        return []


def test_datev_ausgabe_nimmt_den_mandanten_der_anmeldung(haus):
    mitschnitt = _Mitschnitt()
    haus["app"].dependency_overrides[get_db] = lambda: mitschnitt
    try:
        haus["client"].post(
            PREFIX + "/datev-export", params={"von_datum": "2026-01-01", "tenant_id": HAUS_B}, headers=_kopf(HAUS_A))
    finally:
        haus["app"].dependency_overrides.pop(get_db, None)
    assert [p["tenant_id"] for p in mitschnitt.parameter] == [HAUS_A]


def test_kein_weg_nimmt_den_mandanten_aus_der_anfrage():
    """Ratsche: Kein Weg des Kontenplans hat einen Query-Parameter ``tenant_id``."""
    for route in chart_of_accounts.router.routes:
        assert "tenant_id" not in {p.name for p in route.dependant.query_params}, route.path
