"""Die uebrigen Finanzwege: die Rolle wird vor der Datenbank geprueft.

Bis zum 12.10.2026 pruefte keiner dieser 47 Wege eine Rolle. Drei Gruppen:

* Kontoauszugsimport, Zahlungsabgleich, Finanz-Lesemodelle — lesen Finanzrollen, schreiben Buchhaltung,
  Projektionen neu aufbauen Finanzleitung.
* Belege mehrerer Bereiche (Ausgangsrechnung, Eingangsrechnung, Belegkontrolle) — lesen wie die offenen
  Posten (Finanz, Verkauf, Vertrieb, Einkauf), bearbeiten die Sachbearbeitung von Finanz, Verkauf und
  Einkauf, loeschen Finanzleitung.
* Umgehungswege: ``mask_frontend_bridges`` gab Lastschriften frei, fuehrte sie aus und schloss Perioden,
  ``compat`` importierte Debitoren — an den Rollen der eigentlichen Wege vorbei.

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
from app.core.tenant import get_tenant_id

WEGE = {
    "payment_matching": [
        ("POST", "/import/csv", "write"),
        ("GET", "/unmatched", "read"),
        ("GET", "/open-items/{customer_id}", "read"),
        ("POST", "/match/{payment_id}", "write"),
        ("POST", "/auto-match", "write"),
        ("GET", "/match-suggestions/{payment_id}", "read"),
    ],
    "bank_statement_import": [
        ("POST", "/bank-statements/import", "write"),
        ("GET", "/bank-statements/{statement_id}/lines", "read"),
    ],
    "finance_read_models": [
        ("GET", "/finance/read-models/ap-invoice-cockpit", "read"),
        ("GET", "/finance/read-models/payment-run-cockpit", "read"),
        ("GET", "/finance/read-models/process-observation", "read"),
        ("GET", "/finance/read-models/cash-closings", "read"),
        ("GET", "/finance/read-models/cash-closings/analysis", "read"),
        ("GET", "/finance/read-models/cash-closings/reporting", "read"),
        ("POST", "/finance/read-models/_rebuild", "admin"),
        ("GET", "/finance/read-models/_status", "read"),
        ("GET", "/finance/read-models/cash-closings/{closing_id}", "read"),
    ],
    "finance_invoices": [
        ("POST", "/finance/invoices", "beleg_write"),
        ("GET", "/finance/invoices/{invoice_number}", "beleg_read"),
        ("PUT", "/finance/invoices/{invoice_number}", "beleg_write"),
        ("GET", "/finance/invoices", "beleg_read"),
        ("DELETE", "/finance/invoices/{invoice_number}", "admin"),
        ("POST", "/finance/invoices/{invoice_number}/storno", "beleg_write"),
    ],
    "document_control": [
        ("POST", "/document-control/exceptions", "beleg_write"),
        ("GET", "/document-control/exceptions", "beleg_read"),
        ("GET", "/document-control/summary", "beleg_read"),
        ("POST", "/document-control/project", "beleg_write"),
        ("POST", "/document-control/exceptions/{case_id}/assign", "beleg_write"),
        ("POST", "/document-control/exceptions/{case_id}/transition", "beleg_write"),
        ("POST", "/document-control/exceptions/{entity_id}/actions/{action_key}", "beleg_write"),
    ],
    "mask_frontend_bridges": [
        ("GET", "/einkauf/rechnungen", "beleg_read"),
        ("POST", "/einkauf/rechnungen", "beleg_write"),
        ("GET", "/einkauf/rechnungen/{rechnung_id}", "beleg_read"),
        ("PATCH", "/einkauf/rechnungen/{rechnung_id}", "beleg_write"),
        ("DELETE", "/einkauf/rechnungen/{rechnung_id}", "admin"),
        ("POST", "/finance/direct-debits/{run_id}/approve", "admin"),
        ("POST", "/finance/direct-debits/{run_id}/execute", "admin"),
        ("GET", "/finance/export/datev", "read"),
        ("GET", "/finance/fixed-assets", "read"),
        ("POST", "/finance/fixed-assets", "write"),
        ("GET", "/finance/fixed-assets/detail", "read"),
        ("GET", "/finance/fixed-assets/{asset_id}/depreciation", "read"),
        ("GET", "/finance/stats", "read"),
        ("GET", "/finance/followup/fibu/cockpit", "read"),
        ("POST", "/finance/periods/{period_id}/close", "admin"),
    ],
    "compat": [
        ("POST", "/finance/import/debitoren", "admin"),
    ],
}
FAELLE = [(modul, methode, weg, zugang) for modul, wege in WEGE.items() for methode, weg, zugang in wege]

FINANZ_LESEN = {"FINANCE_LESEN", "FINANCE_BEARBEITEN", "FINANCE_ADMIN", "admin", "manager"}
ERLAUBT = {
    "read": FINANZ_LESEN,
    "write": {"FINANCE_BEARBEITEN", "FINANCE_ADMIN", "admin", "manager"},
    "admin": {"FINANCE_ADMIN", "admin"},
    "beleg_read": FINANZ_LESEN | {
        "SALES_LESEN", "SALES_BEARBEITEN", "SALES_ADMIN", "CRM_LESEN", "CRM_BEARBEITEN", "CRM_ADMIN",
        "EINKAUF_LESEN", "EINKAUF_BEARBEITEN", "EINKAUF_ADMIN"},
    "beleg_write": {"FINANCE_BEARBEITEN", "FINANCE_ADMIN", "SALES_BEARBEITEN", "SALES_ADMIN",
                    "EINKAUF_BEARBEITEN", "EINKAUF_ADMIN", "admin", "manager"},
}
ROLLEN = [None, "user", "LAGER_ADMIN", "PERSONAL_ADMIN", "CRM_ADMIN", "SALES_LESEN", "SALES_BEARBEITEN",
          "EINKAUF_LESEN", "EINKAUF_ADMIN", "FINANCE_LESEN", "FINANCE_BEARBEITEN", "FINANCE_ADMIN", "admin", "manager"]
# Sammeldateien: Dort stehen auch Wege anderer Bereiche; der Vertrag gilt ihren Finanzwegen.
FINANZPFADE = {"mask_frontend_bridges": ("/finance/", "/einkauf/rechnungen"), "compat": ("/finance/import/",)}
# Abrechnungs- und Positions-Lesemodell liegen im Finanzrouter, gehoeren aber Agrar und Kontrakt: Eine
# Finanzrolle haette deren Leser ausgesperrt. Ihre Rolle ist dort zu klaeren, nicht hier.
AUSGENOMMEN = {"finance_read_models": {"/finance/read-models/settlement-cockpit",
                                       "/finance/read-models/position-exposure"}}


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
    # Der Mandant ist hier nicht Gegenstand: Er kommt sonst aus dem geprueften Token (Identitaetsgrenze).
    app.dependency_overrides[get_tenant_id] = lambda: "haus-a"
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


def test_umgehungswege_liegen_bei_der_leitung():
    """Was der eigentliche Weg nur der Finanzleitung erlaubt, erlaubt auch die Bruecke niemandem sonst."""
    bruecke = {(m, w): z for m, w, z in WEGE["mask_frontend_bridges"]}
    for weg in ("/finance/direct-debits/{run_id}/approve", "/finance/direct-debits/{run_id}/execute",
                "/finance/periods/{period_id}/close"):
        assert bruecke[("POST", weg)] == "admin", weg
    assert dict(((m, w), z) for m, w, z in WEGE["compat"])[("POST", "/finance/import/debitoren")] == "admin"


def test_belegbearbeitung_loescht_nicht():
    for modul, methode, _weg, zugang in FAELLE:
        if methode == "DELETE":
            assert zugang == "admin", (modul, _weg)


@pytest.mark.parametrize("modul", list(WEGE))
def test_jeder_finanzweg_hat_eine_zugangsklasse(modul):
    """Ein neuer Finanzweg ohne Eintrag hier — und damit ohne geprueften Zugang — macht den Vertrag rot."""
    praefixe = FINANZPFADE.get(modul)
    vorhanden = {
        (methode, route.path) for route in _router(modul).routes for methode in route.methods
        if (praefixe is None or route.path.startswith(praefixe))
        and route.path not in AUSGENOMMEN.get(modul, set())
    }
    assert vorhanden == {(m, w) for m, w, _ in WEGE[modul]}
