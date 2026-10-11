"""Mahnwesen: jede Rolle wird vor dem ersten Datenbankzugriff geprueft.

Bis zum 11.10.2026 verlangten die elf Mahnwege eine Anmeldung, aber keine Rolle: Wer
angemeldet war — Lager, Personal, wer auch immer —, konnte einen Mahnlauf ausloesen und
Mahnungen an Kunden versenden. Zahlungslaeufe und Eingangsrechnungen pruefen seit dem
07.10.2026 ueber ``app/auth/finance_roles.py``; das Mahnwesen folgt demselben Muster.

Kein Datenbankzugriff: Die Grenze antwortet 418, sobald ein Weg die Datenbank verlangt.
"""

from __future__ import annotations

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.api.v1.endpoints import dunning, finance_dunning
from app.auth.deps import get_current_user
from app.core.database import get_db

PREFIX = "/api/v1/finance"

WEGE = [
    ("GET", "/mahnlauf/candidates", "read"),
    ("GET", "/mahnlauf/notices", "read"),
    ("POST", "/mahnlauf/run", "write"),
    ("GET", "/dunning/rules", "read"),
    ("POST", "/dunning/rules", "write"),
    ("POST", "/dunning/process", "write"),
    ("POST", "/dunning/run", "write"),
    ("POST", "/dunning", "write"),
    ("GET", "/dunning", "read"),
    ("PUT", "/dunning/mahnung/send", "write"),
    ("PUT", "/dunning/mahnung/paid", "write"),
]
ROLLEN = [None, "user", "LAGER_ADMIN", "PERSONAL_ADMIN", "SALES_BEARBEITEN",
          "FINANCE_LESEN", "FINANCE_BEARBEITEN", "FINANCE_ADMIN", "admin", "manager"]
ERLAUBT = {
    "read": {"FINANCE_LESEN", "FINANCE_BEARBEITEN", "FINANCE_ADMIN", "admin", "manager"},
    "write": {"FINANCE_BEARBEITEN", "FINANCE_ADMIN", "admin", "manager"},
}
# Rumpf, der die Eingabepruefung besteht — damit 418 die Datenbank meint und nicht 422 den Rumpf.
RUMPF = {
    "/dunning/rules": {"level": 1, "days_overdue": 14, "fee_amount": 5, "interest_rate": 5, "name": "Stufe 1"},
    "/dunning": {"customer_id": "K-1", "invoice_id": "R-1", "level": 1, "amount": 100},
}


@pytest.fixture
def grenze():
    app = FastAPI()
    app.include_router(finance_dunning.router, prefix="/api/v1")
    app.include_router(dunning.router, prefix=PREFIX)
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
    antwort = client.request(
        methode, PREFIX + weg, json=RUMPF.get(weg, {}), headers={"X-Tenant-Id": "haus-a"},
    )
    erlaubt = rolle in ERLAUBT[zugang]
    assert antwort.status_code == (418 if erlaubt else 403), antwort.text
    assert aufrufe == (["db"] if erlaubt else [])


@pytest.mark.parametrize("methode,weg,_zugang", WEGE)
def test_ohne_anmeldung_kein_weg(grenze, methode, weg, _zugang):
    _app, client, aufrufe = grenze
    antwort = client.request(methode, PREFIX + weg, json=RUMPF.get(weg, {}), headers={"X-Tenant-Id": "haus-a"})
    assert antwort.status_code in (401, 403), antwort.text
    assert aufrufe == []


def test_jeder_mahnweg_hat_eine_zugangsklasse():
    """Ein neuer Weg ohne Eintrag hier — und damit ohne geprueften Zugang — macht den Vertrag rot."""
    vorhanden = set()
    for vorsatz, router in (("", finance_dunning.router), ("", dunning.router)):
        for route in router.routes:
            pfad = route.path.replace("/finance", "", 1) if route.path.startswith("/finance") else route.path
            pfad = pfad.replace("{dunning_id}", "mahnung")
            for methode in route.methods:
                vorhanden.add((methode, vorsatz + pfad))
    assert vorhanden == {(m, w) for m, w, _ in WEGE}
