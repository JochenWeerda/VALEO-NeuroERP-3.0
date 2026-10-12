"""31 Bank-/Finanzaktionswege: echte Rollen-Dependencies vor verweigerter DB.

Identitaet ersetzt, keine DB-/Tenant-/Providerabnahme; Kreditlimits breit,
Bankkonto-Optionen auch Einkauf, administrative Aktionen getrennt.
"""

from __future__ import annotations

import importlib
import re

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from app.auth.deps import get_current_user
from app.core.database import get_db

WEGE = {'bank_accounts': [('GET', '/bank-accounts/new', 'read'),
                   ('GET', '/bank-accounts', 'read'),
                   ('GET', '/bank-accounts/ledger-options', 'kontenplan'),
                   ('GET', '/bank-accounts/{account_id}', 'read'),
                   ('POST', '/bank-accounts', 'write'),
                   ('PUT', '/bank-accounts/{account_id}', 'write'),
                   ('DELETE', '/bank-accounts/{account_id}', 'admin')],
 'bank_reconciliation': [('GET', '/bank-reconciliation/{statement_id}/balance-comparison', 'read'),
                         ('GET', '/bank-reconciliation/{statement_id}/differences', 'read'),
                         ('POST', '/bank-reconciliation/{statement_id}/reconcile', 'read'),
                         ('GET', '/bank-reconciliation/{statement_id}/summary', 'read')],
 'finance_actions': [('POST', '/bank-reconciliation/run', 'read'),
                     ('POST', '/journal-entries/post', 'write'),
                     ('POST', '/cash/close-day', 'admin'),
                     ('POST', '/direct-debit/run', 'admin'),
                     ('POST', '/closing/calculate', 'read'),
                     ('POST', '/closing/lock', 'admin'),
                     ('POST', '/closing/run', 'admin'),
                     ('POST', '/closing/approve', 'admin'),
                     ('GET', '/credit-limits', 'broad'),
                     ('GET', '/collaterals', 'read'),
                     ('GET', '/payment-suggestions', 'read'),
                     ('POST', '/buchungsuebergabe-export', 'read'),
                     ('GET', '/close-readiness', 'read'),
                     ('POST', '/sepa/mandate', 'write'),
                     ('POST', '/sepa/mandate/{mandat_id}/widerruf', 'write'),
                     ('POST', '/sepa/batches', 'admin'),
                     ('POST', '/ratenzahlung/plaene', 'write'),
                     ('POST', '/ratenzahlung/raten/{rate_id}/buchen', 'write'),
                     ('POST', '/mahnstufe/{rechnungsnr}/eskalieren', 'write'),
                     ('GET', '/mahnstufe/{rechnungsnr}/trail', 'read')]}
FAELLE = [(modul, methode, weg, zugang) for modul, wege in WEGE.items() for methode, weg, zugang in wege]

FINANZ_LESEN = {"FINANCE_LESEN", "FINANCE_BEARBEITEN", "FINANCE_ADMIN", "admin", "manager"}
ERLAUBT = {
    "read": FINANZ_LESEN,
    "kontenplan": FINANZ_LESEN | {"EINKAUF_LESEN", "EINKAUF_BEARBEITEN", "EINKAUF_ADMIN"},
    "write": {"FINANCE_BEARBEITEN", "FINANCE_ADMIN", "admin", "manager"},
    "admin": {"FINANCE_ADMIN", "admin"},
}
ERLAUBT['broad'] = FINANZ_LESEN | {d + '_' + r for d in ['SALES','CRM','EINKAUF'] for r in ['LESEN','BEARBEITEN','ADMIN']}
ROLLEN = [None, 'user', 'LAGER_ADMIN', 'PERSONAL_ADMIN', 'SALES_LESEN', 'SALES_BEARBEITEN', 'SALES_ADMIN', 'CRM_LESEN', 'CRM_BEARBEITEN', 'CRM_ADMIN', 'EINKAUF_LESEN', 'EINKAUF_BEARBEITEN', 'EINKAUF_ADMIN', 'FINANCE_LESEN', 'FINANCE_BEARBEITEN', 'FINANCE_ADMIN', 'admin', 'manager']


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
        assert antwort.status_code in (200, 418), antwort.text
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
