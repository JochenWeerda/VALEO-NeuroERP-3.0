"""Hauptbuch: jede Rolle wird vor dem ersten Datenbankzugriff geprueft.

Bis zum 11.10.2026 pruefte keiner der 54 Wege fuer Buchungen, Konten, Kontenplan, Perioden,
Geschaeftsjahre, Buchungsvorlagen, periodische Buchungen und Buchungsimport eine Rolle: Wer
angemeldet war, konnte buchen, stornieren, Konten loeschen und Perioden oeffnen.

Die Regel ist dieselbe wie an den uebrigen Finanzwegen:

* lesen — Finanzrollen; den Kontenplan liest auch der Einkauf, der Rechnungseingang kontiert damit
* anlegen, aendern, buchen, stornieren — Buchhaltung (``finance_write``)
* Konten anlegen, aendern, deaktivieren — Kontenpflege (``KONTENPLAN_PFLEGE``, delegierbar) und
  Finanzleitung: Kontenplanpflege ist Stammdatenpflege, kein Tagesgeschaeft
* loeschen, Periode sperren und oeffnen, Geschaeftsjahr anlegen, Massenimport — Finanzleitung

Kein Datenbankzugriff: Die Grenze antwortet 418, sobald ein Weg die Datenbank verlangt.
"""

from __future__ import annotations

import importlib
import re

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.auth.deps import get_current_user
from app.core.database import get_db

WEGE = {
    "journal_entries": [
        ("GET", "/new", "read"),
        ("POST", "/", "write"),
        ("GET", "/", "read"),
        ("GET", "/{entry_id}", "read"),
        ("PUT", "/{entry_id}", "write"),
        ("POST", "/{entry_id}/post", "write"),
        ("POST", "/{entry_id}/reverse", "write"),
        ("DELETE", "/{entry_id}", "admin"),
    ],
    "accounts": [
        ("POST", "/", "pflege"),
        ("GET", "/", "read"),
        ("GET", "/hierarchy", "read"),
        ("GET", "/{account_id}", "read"),
        ("GET", "/number/{account_number}", "read"),
        ("PUT", "/{account_id}", "pflege"),
        ("DELETE", "/{account_id}", "pflege"),
        ("GET", "/{account_id}/balance", "read"),
    ],
    "chart_of_accounts": [
        ("GET", "/chart-of-accounts/", "kontenplan"),
        ("GET", "/chart-of-accounts/{account_id}", "kontenplan"),
        ("POST", "/chart-of-accounts/", "pflege"),
        ("PUT", "/chart-of-accounts/{account_id}", "pflege"),
        ("DELETE", "/chart-of-accounts/{account_id}", "pflege"),
        ("POST", "/chart-of-accounts/validate", "read"),
        ("POST", "/chart-of-accounts/datev-export", "read"),
    ],
    "accounting_periods": [
        ("POST", "/", "admin"),
        ("GET", "/", "read"),
        ("GET", "/{period_id}", "read"),
        ("PUT", "/{period_id}", "admin"),
        ("GET", "/check/{tenant_id}/{period}", "read"),
        ("GET", "/check/{period}", "read"),
    ],
    "finance_period": [
        ("GET", "/finance/perioden", "read"),
        ("GET", "/finance/perioden/{period}/readiness", "read"),
        ("POST", "/finance/perioden/{period}/close", "admin"),
        ("POST", "/finance/perioden/{period}/reopen", "admin"),
    ],
    "bulk_journal_import": [
        ("POST", "/bulk-journal-import/csv", "admin"),
        ("GET", "/bulk-journal-import/template", "read"),
    ],
    "booking_templates": [
        ("GET", "/booking-templates", "read"),
        ("GET", "/booking-templates/{template_id}", "read"),
        ("POST", "/booking-templates", "write"),
        ("POST", "/booking-templates/{template_id}/apply", "write"),
        ("PUT", "/booking-templates/{template_id}", "write"),
        ("DELETE", "/booking-templates/{template_id}", "admin"),
    ],
    "periodische_buchungen": [
        ("GET", "/fibu/periodische-buchungen", "read"),
        ("GET", "/fibu/periodische-buchungen/faellig", "read"),
        ("POST", "/fibu/periodische-buchungen", "write"),
        ("PATCH", "/fibu/periodische-buchungen/{buchung_id}/sperren", "write"),
        ("DELETE", "/fibu/periodische-buchungen/{buchung_id}", "admin"),
    ],
    "fibu_geschaeftsjahre": [
        ("GET", "/fibu/geschaeftsjahre", "read"),
        ("POST", "/fibu/geschaeftsjahre", "admin"),
        ("GET", "/fibu/geschaeftsjahre/{jahr_nr}/perioden", "read"),
        ("PATCH", "/fibu/geschaeftsjahre/{jahr_nr}/perioden/{periode_nr}/sperren", "admin"),
        ("GET", "/fibu/geschaeftsjahre/periodisch", "read"),
        ("POST", "/fibu/geschaeftsjahre/periodisch", "write"),
        ("POST", "/fibu/geschaeftsjahre/periodisch/{buchung_id}/ausfuehren", "write"),
        ("DELETE", "/fibu/geschaeftsjahre/periodisch/{buchung_id}", "admin"),
    ],
}
FAELLE = [(modul, methode, weg, zugang) for modul, wege in WEGE.items() for methode, weg, zugang in wege]

FINANZ_LESEN = {"FINANCE_LESEN", "FINANCE_BEARBEITEN", "FINANCE_ADMIN", "admin", "manager"}
ERLAUBT = {
    "read": FINANZ_LESEN,
    "kontenplan": FINANZ_LESEN | {"EINKAUF_LESEN", "EINKAUF_BEARBEITEN", "EINKAUF_ADMIN", "KONTENPLAN_PFLEGE"},
    "pflege": {"KONTENPLAN_PFLEGE", "FINANCE_ADMIN", "admin"},
    "write": {"FINANCE_BEARBEITEN", "FINANCE_ADMIN", "admin", "manager"},
    "admin": {"FINANCE_ADMIN", "admin"},
}
ROLLEN = [None, "user", "LAGER_ADMIN", "PERSONAL_ADMIN", "SALES_ADMIN", "CRM_ADMIN",
          "EINKAUF_LESEN", "EINKAUF_ADMIN", "FINANCE_LESEN", "FINANCE_BEARBEITEN", "FINANCE_ADMIN",
          "admin", "manager", "KONTENPLAN_PFLEGE"]


def _router(modul: str):
    return importlib.import_module(f"app.api.v1.endpoints.{modul}").router


@pytest.fixture(scope="module")
def grenze():
    app = FastAPI()
    for modul in WEGE:
        app.include_router(_router(modul), prefix=f"/{modul}")
    aufrufe: list[str] = []

    def datenbank():
        aufrufe.append("db")
        raise HTTPException(418, "autorisierte Datenbankgrenze")

    app.dependency_overrides[get_db] = datenbank
    with TestClient(app) as client:
        yield app, client, aufrufe
    app.dependency_overrides.clear()


def _ruf(client, modul, methode, weg):
    return client.request(methode, f"/{modul}" + re.sub(r"\{[^}]+\}", "1", weg), json={},
                          headers={"X-Tenant-ID": "haus-a"})


@pytest.mark.parametrize("modul,methode,weg,zugang", FAELLE)
@pytest.mark.parametrize("rolle", ROLLEN)
def test_rolle_vor_der_datenbank(grenze, modul, methode, weg, zugang, rolle):
    app, client, aufrufe = grenze
    aufrufe.clear()
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "5f0c2a9e", "name": "t.de-vries", "roles": [] if rolle is None else [rolle]}
    try:
        antwort = _ruf(client, modul, methode, weg)
    finally:
        app.dependency_overrides.pop(get_current_user, None)
    if rolle in ERLAUBT[zugang]:
        # Hinter der Rolle darf alles kommen (Datenbankgrenze 418, Eingabefehler 422, Vorlage 200) —
        # nur keine Ablehnung.
        assert antwort.status_code not in (401, 403), antwort.text
    else:
        assert antwort.status_code == 403, antwort.text
        assert aufrufe == []


@pytest.mark.parametrize("modul,methode,weg,_zugang", FAELLE)
def test_ohne_anmeldung_kein_weg(grenze, modul, methode, weg, _zugang):
    _app, client, aufrufe = grenze
    aufrufe.clear()
    antwort = _ruf(client, modul, methode, weg)
    assert antwort.status_code in (401, 403), antwort.text
    assert aufrufe == []


def test_einkauf_liest_nur_den_kontenplan():
    """Die Leserolle des Einkaufs am Kontenplan ist keine Hintertuer zu Salden und Buchungen."""
    for rolle in ("EINKAUF_LESEN", "EINKAUF_BEARBEITEN", "EINKAUF_ADMIN"):
        assert rolle in ERLAUBT["kontenplan"]
        assert rolle not in ERLAUBT["read"] | ERLAUBT["write"] | ERLAUBT["admin"]


@pytest.mark.parametrize("modul", list(WEGE))
def test_jeder_weg_hat_eine_zugangsklasse(modul):
    """Ein neuer Weg ohne Eintrag hier — und damit ohne geprueften Zugang — macht den Vertrag rot."""
    vorhanden = {(methode, route.path) for route in _router(modul).routes for methode in route.methods}
    assert vorhanden == {(m, w) for m, w, _ in WEGE[modul]}
