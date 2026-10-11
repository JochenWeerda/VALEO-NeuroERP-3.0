"""Offene Posten: jede Rolle wird vor dem ersten Datenbankzugriff geprueft.

Bis zum 11.10.2026 pruefte keiner der elf Wege unter ``/finance/open-items`` eine Rolle:
Wer angemeldet war, konnte Posten anlegen, ausgleichen, loeschen und mahnen.

Lesen duerfen neben den Finanzrollen auch Verkauf, Vertrieb und Einkauf — wer einen Auftrag
annimmt oder bestellt, muss sehen, was offen ist. Aendern, ausgleichen und mahnen ist Sache
der Buchhaltung, loeschen der Finanzleitung.

Kein Datenbankzugriff: Die Grenze antwortet 418, sobald ein Weg die Datenbank verlangt.
"""

from __future__ import annotations

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.api.v1.endpoints import open_items
from app.auth.deps import get_current_user
from app.core.database import get_db

PREFIX = "/api/v1/finance/open-items"

WEGE = [
    ("GET", "", "read"),
    ("GET", "/posten", "read"),
    ("GET", "/posten/settlements", "read"),
    ("POST", "", "write"),
    ("PUT", "/posten", "write"),
    ("PATCH", "/posten", "write"),
    ("POST", "/batch-settle", "write"),
    ("POST", "/posten/settle", "write"),
    ("POST", "/posten/reverse-settlement", "write"),
    ("POST", "/posten/actions/mahnen", "write"),
    ("DELETE", "/posten", "admin"),
]
FINANZ_LESEN = {"FINANCE_LESEN", "FINANCE_BEARBEITEN", "FINANCE_ADMIN", "admin", "manager"}
ERLAUBT = {
    "read": FINANZ_LESEN | {
        "SALES_LESEN", "SALES_BEARBEITEN", "SALES_ADMIN", "CRM_LESEN", "CRM_BEARBEITEN", "CRM_ADMIN",
        "EINKAUF_LESEN", "EINKAUF_BEARBEITEN", "EINKAUF_ADMIN",
    },
    "write": {"FINANCE_BEARBEITEN", "FINANCE_ADMIN", "admin", "manager"},
    "admin": {"FINANCE_ADMIN", "admin"},
}
ROLLEN = [None, "user", "LAGER_ADMIN", "PERSONAL_ADMIN", "QUALITAET_ADMIN", "HARVEST_ADMIN",
          "SALES_LESEN", "SALES_ADMIN", "CRM_BEARBEITEN", "EINKAUF_BEARBEITEN",
          "FINANCE_LESEN", "FINANCE_BEARBEITEN", "FINANCE_ADMIN", "admin", "manager"]


@pytest.fixture
def grenze():
    app = FastAPI()
    app.include_router(open_items.router, prefix="/api/v1/finance")
    aufrufe: list[str] = []

    def datenbank():
        aufrufe.append("db")
        raise HTTPException(418, "autorisierte Datenbankgrenze")

    app.dependency_overrides[get_db] = datenbank
    with TestClient(app) as client:
        yield app, client, aufrufe


@pytest.mark.parametrize("methode,weg,zugang", WEGE)
@pytest.mark.parametrize("rolle", ROLLEN)
def test_rolle_vor_der_datenbank(grenze, methode, weg, zugang, rolle):
    app, client, aufrufe = grenze
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "5f0c2a9e", "name": "t.de-vries", "roles": [] if rolle is None else [rolle]}
    antwort = client.request(methode, PREFIX + weg, json={}, headers={"X-Tenant-Id": "haus-a"})
    erlaubt = rolle in ERLAUBT[zugang]
    assert antwort.status_code == (418 if erlaubt else 403), antwort.text
    assert aufrufe == (["db"] if erlaubt else [])


@pytest.mark.parametrize("methode,weg,_zugang", WEGE)
def test_ohne_anmeldung_kein_weg(grenze, methode, weg, _zugang):
    _app, client, aufrufe = grenze
    antwort = client.request(methode, PREFIX + weg, json={}, headers={"X-Tenant-Id": "haus-a"})
    assert antwort.status_code in (401, 403), antwort.text
    assert aufrufe == []


def test_verkauf_liest_und_aendert_nichts():
    """Die Leserolle des Verkaufs ist keine Hintertuer zum Ausgleichen."""
    for rolle in ("SALES_ADMIN", "CRM_ADMIN", "EINKAUF_ADMIN"):
        assert rolle in ERLAUBT["read"]
        assert rolle not in ERLAUBT["write"] | ERLAUBT["admin"]


def test_jeder_weg_hat_eine_zugangsklasse():
    """Ein neuer Weg ohne Eintrag hier — und damit ohne geprueften Zugang — macht den Vertrag rot."""
    vorhanden = {
        (methode, route.path.removeprefix("/open-items").replace("{op_id}", "posten").replace("{entity_id}", "posten"))
        for route in open_items.router.routes for methode in route.methods
    }
    assert vorhanden == {(m, w) for m, w, _ in WEGE}
