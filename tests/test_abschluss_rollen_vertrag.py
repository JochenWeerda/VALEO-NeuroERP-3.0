"""Abschluss, Auswertung, Kostenrechnung: jede Rolle wird vor dem ersten Datenbankzugriff geprueft.

Bis zum 12.10.2026 pruefte keiner der 74 Wege fuer Abschluss-Checklisten, Abgrenzungen, Anlagen,
Budget, Liquiditaet, Finanzberichte, Nebenbuchabstimmung, Umsatzsteuer-Voranmeldung, DATEV-Ausgabe
und Kostenrechnung eine Rolle.

Die Regel ist dieselbe wie am Hauptbuch:

* lesen — Finanzrollen
* anlegen, aendern, buchen — Buchhaltung (``finance_write``)
* loeschen, genehmigen, UStVA einreichen, Anlagenabgang, Abschreibungslauf — Finanzleitung

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
    "closing_checklists": [
        ("GET", "/closing-checklists/templates", "read"),
        ("POST", "/closing-checklists/templates", "write"),
        ("POST", "/closing-checklists", "write"),
        ("GET", "/closing-checklists/{checklist_id}", "read"),
        ("POST", "/closing-checklists/{checklist_id}/items/{item_code}/complete", "write"),
        ("POST", "/closing-checklists/{checklist_id}/validate", "write"),
        ("GET", "/closing-checklists", "read"),
        ("GET", "/closing-checklists/cockpit/summary", "read"),
        ("POST", "/closing-checklists/{checklist_id}/approve", "admin"),
        ("DELETE", "/closing-checklists/{checklist_id}", "admin"),
    ],
    "accruals_provisions": [
        ("GET", "/accruals-provisions", "read"),
        ("POST", "/accruals-provisions", "write"),
        ("GET", "/accruals-provisions/{item_id}", "read"),
        ("PUT", "/accruals-provisions/{item_id}", "write"),
        ("DELETE", "/accruals-provisions/{item_id}", "admin"),
        ("POST", "/accruals-provisions/{item_id}/post", "write"),
    ],
    "asset_accounting": [
        ("GET", "/finance/asset-accounting/assets", "read"),
        ("POST", "/finance/asset-accounting/assets", "write"),
        ("GET", "/finance/asset-accounting/assets/{asset_id}", "read"),
        ("PATCH", "/finance/asset-accounting/assets/{asset_id}", "write"),
        ("POST", "/finance/asset-accounting/assets/{asset_id}/dispose", "admin"),
        ("POST", "/finance/asset-accounting/depreciation-run", "admin"),
        ("GET", "/finance/asset-accounting/asset-register", "read"),
        ("GET", "/finance/asset-accounting/depreciation-forecast", "read"),
    ],
    "budget_planning": [
        ("GET", "/finance/budgets", "read"),
        ("POST", "/finance/budgets", "write"),
        ("GET", "/finance/budgets/summary", "read"),
        ("GET", "/finance/budgets/{plan_id}", "read"),
        ("POST", "/finance/budgets/{plan_id}/approve", "admin"),
        ("GET", "/finance/budgets/{plan_id}/vs-actual", "read"),
        ("POST", "/finance/budgets/{plan_id}/lines", "write"),
        ("PATCH", "/finance/budgets/{plan_id}/lines/{line_id}", "write"),
    ],
    "liquidity_planning": [
        ("GET", "/finance/liquidity/forecast", "read"),
        ("GET", "/finance/liquidity/cash-position", "read"),
        ("POST", "/finance/liquidity/scenarios", "write"),
    ],
    "liquidity": [
        ("GET", "/finance/liquidity/overview", "read"),
    ],
    "financial_reports": [
        ("GET", "/financial-reports/balance-sheet", "read"),
        ("GET", "/financial-reports/profit-loss", "read"),
        ("GET", "/financial-reports/bwa", "read"),
        ("GET", "/financial-reports/drilldown", "read"),
        ("GET", "/financial-reports/export/{report_type}", "read"),
        ("GET", "/financial-reports/periodenvergleich", "read"),
        ("GET", "/financial-reports/beleg-drilldown/{journal_entry_id}", "read"),
    ],
    "subsidiary_ledger_reconciliation": [
        ("GET", "/subsidiary-ledger-reconciliation/ar", "read"),
        ("GET", "/subsidiary-ledger-reconciliation/ap", "read"),
        ("GET", "/subsidiary-ledger-reconciliation/bank", "read"),
        ("GET", "/subsidiary-ledger-reconciliation/{ledger_type}/details", "read"),
        ("GET", "/subsidiary-ledger-reconciliation/{ledger_type}/export", "read"),
        ("GET", "/subsidiary-ledger-reconciliation/summary", "read"),
    ],
    "vat_return_export": [
        ("GET", "/vat-return/vorberechnung", "read"),
        ("POST", "/vat-return/calculate", "write"),
        ("GET", "/vat-return/{return_id}", "read"),
        ("GET", "/vat-return/export/{return_id}", "read"),
        ("GET", "/vat-return/{return_id}/elster-xml", "read"),
        ("POST", "/vat-return/{return_id}/validate", "write"),
        ("GET", "/vat-return", "read"),
        ("POST", "/vat-return/{return_id}/approve", "admin"),
        ("POST", "/vat-return/{return_id}/submit", "admin"),
    ],
    "finance_datev": [
        ("GET", "/finance/datev-export", "read"),
        ("GET", "/finance/datev-journal", "read"),
    ],
    "kostenrechnung": [
        ("GET", "/kostenrechnung/kostenstellen", "read"),
        ("GET", "/kostenrechnung/kostenstellen/{kst_id}", "read"),
        ("POST", "/kostenrechnung/kostenstellen", "write"),
        ("PATCH", "/kostenrechnung/kostenstellen/{kst_id}", "write"),
        ("DELETE", "/kostenrechnung/kostenstellen/{kst_id}", "admin"),
        ("GET", "/kostenrechnung/kostenarten", "read"),
        ("POST", "/kostenrechnung/kostenarten", "write"),
        ("DELETE", "/kostenrechnung/kostenarten/{koa_id}", "admin"),
        ("GET", "/kostenrechnung/buchungen", "read"),
        ("POST", "/kostenrechnung/buchungen", "write"),
        ("DELETE", "/kostenrechnung/buchungen/{buchung_id}", "admin"),
        ("GET", "/kostenrechnung/report", "read"),
        ("POST", "/kostenrechnung/umlagen", "write"),
        ("GET", "/kostenrechnung/bab", "read"),
    ],
}
FAELLE = [(modul, methode, weg, zugang) for modul, wege in WEGE.items() for methode, weg, zugang in wege]

FINANZ_LESEN = {"FINANCE_LESEN", "FINANCE_BEARBEITEN", "FINANCE_ADMIN", "admin"}
ERLAUBT = {
    "read": FINANZ_LESEN,
    "write": {"FINANCE_BEARBEITEN", "FINANCE_ADMIN", "admin"},
    "admin": {"FINANCE_ADMIN", "admin"},
}
ROLLEN = [None, "user", "LAGER_ADMIN", "PERSONAL_ADMIN", "SALES_ADMIN", "CRM_ADMIN",
          "EINKAUF_LESEN", "EINKAUF_ADMIN", "FINANCE_LESEN", "FINANCE_BEARBEITEN", "FINANCE_ADMIN",
          "admin", "manager"]


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
    from app.core.tenant import get_tenant_id
    app.dependency_overrides[get_tenant_id] = lambda: 'haus-a'  # isolated role contract, not provider/tenant proof
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


def test_einkauf_und_verkauf_lesen_hier_nicht():
    """Abschluss und Auswertung sind Sache der Finanzrollen."""
    for rolle in ("EINKAUF_ADMIN", "SALES_ADMIN", "CRM_ADMIN"):
        assert all(rolle not in erlaubt for erlaubt in ERLAUBT.values())


@pytest.mark.parametrize("modul", list(WEGE))
def test_jeder_weg_hat_eine_zugangsklasse(modul):
    """Ein neuer Weg ohne Eintrag hier — und damit ohne geprueften Zugang — macht den Vertrag rot."""
    vorhanden = {(methode, route.path) for route in _router(modul).routes for methode in route.methods}
    assert vorhanden == {(m, w) for m, w, _ in WEGE[modul]}
