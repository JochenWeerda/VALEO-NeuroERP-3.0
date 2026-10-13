"""Zahlungsverkehr, Schnittstellen, Finanzstammdaten: die Rolle wird vor der Datenbank geprueft.

Bis zum 12.10.2026 pruefte keiner der 137 Wege in 22 Dateien eine Rolle.

* Zahlungsverkehr und Schnittstellen: lesen Finanzrollen, schreiben Buchhaltung; Lastschrift ausgeben,
  Rechnungsstapel freigeben und ausfuehren, Importlauf buchen, Lohn- und Fremdsystemlaeufe,
  Schnittstellenkonfiguration und jedes Loeschen — Finanzleitung.
* Stammdaten: Das Lesen bleibt fuer jeden Angemeldeten (31 Wege, Zugangsklasse ``offen``) — Verkauf,
  Einkauf und CRM lesen Zahlungsbedingungen und Steuerschluessel. Schreiben Buchhaltung, loeschen Leitung.

Kein Datenbankzugriff: Die Grenze antwortet 418, sobald ein Weg die Datenbank verlangt. Die offenen
Lesewege haengen wie alle Wege am Bearer-Token des Hauptrouters; den prueft dieser Vertrag nicht.
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
    "auto_matching": [
        ("GET", "/auto-matching/rules", "read"),
        ("POST", "/auto-matching/rules", "write"),
        ("GET", "/auto-matching/rules/{rule_id}", "read"),
        ("PUT", "/auto-matching/rules/{rule_id}", "write"),
        ("DELETE", "/auto-matching/rules/{rule_id}", "admin"),
        ("POST", "/auto-matching/match", "write"),
        ("POST", "/auto-matching/match/{line_id}/apply", "write"),
        ("GET", "/auto-matching/statistics", "read"),
    ],
    "direct_debits": [
        ("GET", "/direct-debits", "read"),
        ("GET", "/direct-debits/new", "read"),
        ("POST", "/direct-debits", "write"),
        ("GET", "/direct-debits/{run_id}", "read"),
        ("POST", "/direct-debits/{run_id}/export", "admin"),
        ("DELETE", "/direct-debits/{run_id}", "admin"),
    ],
    "op_skonto_auszifferung": [
        ("POST", "/fibu/op-auszifferung/berechnen", "write"),
        ("GET", "/fibu/op-auszifferung", "read"),
        ("POST", "/fibu/op-auszifferung", "write"),
        ("POST", "/fibu/op-auszifferung/{auszifferung_id}/stornieren", "write"),
    ],
    "fibu_zahlungsmeldungen": [
        ("GET", "/fibu/zahlungsmeldungen", "read"),
        ("POST", "/fibu/zahlungsmeldungen", "write"),
        ("POST", "/fibu/zahlungsmeldungen/{meldung_id}/verarbeiten", "write"),
        ("POST", "/fibu/zahlungsmeldungen/{meldung_id}/abweisen", "write"),
        ("GET", "/fibu/zahlungsmeldungen/offen/zusammenfassung", "read"),
    ],
    "finance_clearing": [
        ("GET", "/finance/zahlungseingang/clearings", "read"),
        ("POST", "/finance/zahlungseingang", "write"),
    ],
    "finance_op": [
        ("GET", "/finance/offene-posten", "read"),
    ],
    "finance_followup": [
        ("GET", "/finance/followup/mahnwesen/preview", "read"),
        ("POST", "/finance/followup/mahnwesen/export", "write"),
        ("GET", "/finance/followup/mahnwesen/export/{export_id}/download", "read"),
        ("GET", "/finance/followup/lastschriften/{run_id}/preview", "read"),
        ("POST", "/finance/followup/lastschriften/{run_id}/export", "admin"),
        ("GET", "/finance/followup/lastschriften/{run_id}/export/{export_id}/download", "read"),
        ("GET", "/finance/followup/kasse/preview", "read"),
        ("POST", "/finance/followup/kasse/export", "write"),
        ("GET", "/finance/followup/kasse/export/{export_id}/download", "read"),
    ],
    "billing_batch": [
        ("POST", "/billing-batches", "write"),
        ("GET", "/billing-batches", "read"),
        ("GET", "/billing-batches/summary", "read"),
        ("GET", "/billing-batches/lines", "read"),
        ("POST", "/billing-batches/{batch_id}/validate", "write"),
        ("POST", "/billing-batches/{batch_id}/release", "admin"),
        ("POST", "/billing-batches/{batch_id}/execute", "admin"),
        ("POST", "/billing-batches/lines/{line_id}/retry", "write"),
    ],
    "fibu_connectors": [
        ("GET", "/connectors/profiles", "read"),
        ("POST", "/connectors/profiles", "admin"),
        ("GET", "/connectors/profiles/{profile_id}", "read"),
        ("PUT", "/connectors/profiles/{profile_id}", "admin"),
        ("DELETE", "/connectors/profiles/{profile_id}", "admin"),
        ("POST", "/connectors/{connector_type}/imports", "write"),
        ("GET", "/connectors/imports/{run_id}", "read"),
        ("GET", "/connectors/imports/{run_id}/items", "read"),
        ("POST", "/connectors/imports/{run_id}/validate", "write"),
        ("POST", "/connectors/imports/{run_id}/post", "admin"),
        ("POST", "/connectors/imports/{run_id}/cancel", "write"),
        ("POST", "/connectors/imports/{run_id}/reverse", "admin"),
    ],
    "lohn_connector": [
        ("GET", "/lohn-connector/runs", "read"),
        ("GET", "/lohn-connector/runs/{run_id}", "read"),
        ("POST", "/lohn-connector/runs", "admin"),
        ("POST", "/lohn-connector/runs/trigger", "admin"),
        ("DELETE", "/lohn-connector/runs/{run_id}", "admin"),
    ],
    "quadriga_connector": [
        ("GET", "/quadriga-connector/config", "read"),
        ("PUT", "/quadriga-connector/config", "admin"),
        ("POST", "/quadriga-connector/sync", "admin"),
        ("GET", "/quadriga-connector/config/list", "read"),
    ],
    "asset_ledger_connector": [
        ("GET", "/asset-ledger-connector/config", "read"),
        ("PUT", "/asset-ledger-connector/config", "admin"),
        ("POST", "/asset-ledger-connector/sync", "admin"),
        ("GET", "/asset-ledger-connector/config/list", "read"),
    ],
    "finance_stammdaten": [
        ("GET", "/finance/debitoren", "offen"),
        ("GET", "/finance/debitoren/{debitor_id}", "offen"),
        ("PATCH", "/finance/debtors/{debitor_id}", "write"),
        ("PATCH", "/finance/debitoren/{debitor_id}", "write"),
        ("GET", "/finance/creditors", "offen"),
        ("GET", "/finance/kreditoren", "offen"),
        ("POST", "/finance/creditors", "write"),
        ("GET", "/finance/creditors/{kreditor_id}", "offen"),
        ("GET", "/finance/kreditoren/{kreditor_id}", "offen"),
        ("PATCH", "/finance/creditors/{kreditor_id}", "write"),
        ("PUT", "/finance/creditors/{kreditor_id}", "write"),
        ("DELETE", "/finance/creditors/{kreditor_id}", "admin"),
    ],
    "fibu_stammdaten": [
        ("GET", "/fibu/stammdaten/zahlungsformulare", "offen"),
        ("POST", "/fibu/stammdaten/zahlungsformulare", "write"),
        ("DELETE", "/fibu/stammdaten/zahlungsformulare/{formular_nr}", "admin"),
        ("GET", "/fibu/stammdaten/zinsgruppen", "offen"),
        ("POST", "/fibu/stammdaten/zinsgruppen", "write"),
        ("DELETE", "/fibu/stammdaten/zinsgruppen/{gruppe_nr}", "admin"),
        ("GET", "/fibu/stammdaten/leergutarten", "offen"),
        ("POST", "/fibu/stammdaten/leergutarten", "write"),
        ("DELETE", "/fibu/stammdaten/leergutarten/{art_nr}", "admin"),
    ],
    "tax_keys": [
        ("GET", "/tax-keys", "offen"),
        ("GET", "/tax-keys/{tax_key_id}", "offen"),
        ("POST", "/tax-keys", "write"),
        ("PUT", "/tax-keys/{tax_key_id}", "write"),
        ("DELETE", "/tax-keys/{tax_key_id}", "admin"),
        ("GET", "/tax-keys/code/{code}", "offen"),
        ("POST", "/tax-keys/actions/speichern", "write"),
        ("GET", "/tax-keys/kontenvorschlaege", "offen"),
    ],
    "exchange_rates": [
        ("GET", "/exchange-rates", "offen"),
        ("GET", "/exchange-rates/{rate_id}", "offen"),
        ("POST", "/exchange-rates", "write"),
        ("PUT", "/exchange-rates/{rate_id}", "write"),
        ("POST", "/exchange-rates/convert", "write"),
        ("GET", "/exchange-rates/latest/{from_currency}/{to_currency}", "offen"),
    ],
    "zahlungsbedingungen": [
        ("GET", "/fibu/zahlungsbedingungen", "offen"),
        ("GET", "/fibu/zahlungsbedingungen/{zabd_nr}", "offen"),
        ("POST", "/fibu/zahlungsbedingungen", "write"),
        ("PUT", "/fibu/zahlungsbedingungen/{zabd_nr}", "write"),
        ("DELETE", "/fibu/zahlungsbedingungen/{zabd_nr}", "admin"),
    ],
    "forderungsgruppen": [
        ("GET", "/fibu/forderungsgruppen", "offen"),
        ("GET", "/fibu/forderungsgruppen/{gruppe_nr}", "offen"),
        ("POST", "/fibu/forderungsgruppen", "write"),
        ("PUT", "/fibu/forderungsgruppen/{gruppe_nr}", "write"),
        ("DELETE", "/fibu/forderungsgruppen/{gruppe_nr}", "admin"),
    ],
    "erloeskennziffern": [
        ("GET", "/fibu/erloeskennziffern", "offen"),
        ("POST", "/fibu/erloeskennziffern", "write"),
        ("PUT", "/fibu/erloeskennziffern/{ekz_nr}", "write"),
        ("DELETE", "/fibu/erloeskennziffern/{ekz_nr}", "admin"),
        ("GET", "/fibu/erloeskennziffern/zuordnungen", "offen"),
        ("POST", "/fibu/erloeskennziffern/zuordnungen", "write"),
        ("GET", "/fibu/erloeskennziffern/lookup", "offen"),
    ],
    "debtors": [
        ("POST", "/debtors/", "write"),
        ("GET", "/debtors/", "offen"),
        ("GET", "/debtors/{debtor_id}", "offen"),
        ("PUT", "/debtors/{debtor_id}", "write"),
        ("GET", "/debtors/{debtor_id}/balance", "offen"),
        ("DELETE", "/debtors/{debtor_id}", "admin"),
    ],
    "creditors": [
        ("POST", "/creditors/", "write"),
        ("GET", "/creditors/", "offen"),
        ("GET", "/creditors/{creditor_id}", "offen"),
        ("PUT", "/creditors/{creditor_id}", "write"),
        ("GET", "/creditors/{creditor_id}/balance", "offen"),
        ("DELETE", "/creditors/{creditor_id}", "admin"),
    ],
}
FAELLE = [(modul, methode, weg, zugang) for modul, wege in WEGE.items() for methode, weg, zugang in wege]

FINANZ_LESEN = {"FINANCE_LESEN", "FINANCE_BEARBEITEN", "FINANCE_ADMIN", "admin", "manager"}
ROLLEN = [None, "user", "LAGER_ADMIN", "PERSONAL_ADMIN", "SALES_ADMIN", "CRM_ADMIN", "EINKAUF_ADMIN",
          "KONTENPLAN_PFLEGE", "FINANCE_LESEN", "FINANCE_BEARBEITEN", "FINANCE_ADMIN", "admin", "manager"]
ERLAUBT = {
    "offen": set(ROLLEN),
    "read": FINANZ_LESEN,
    "write": {"FINANCE_BEARBEITEN", "FINANCE_ADMIN", "admin", "manager"},
    "admin": {"FINANCE_ADMIN", "admin"},
}


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
        assert antwort.status_code not in (401, 403), antwort.text
    else:
        assert antwort.status_code == 403, antwort.text
        assert aufrufe == []


@pytest.mark.parametrize("modul,methode,weg,zugang", [f for f in FAELLE if f[3] != "offen"])
def test_ohne_anmeldung_kein_geschuetzter_weg(grenze, modul, methode, weg, zugang):
    _app, client, aufrufe = grenze
    aufrufe.clear()
    antwort = _ruf(client, modul, methode, weg)
    assert antwort.status_code in (401, 403), antwort.text
    assert aufrufe == []


def test_offen_ist_nur_das_lesen_von_stammdaten():
    """Kein schreibender Weg und kein Weg des Zahlungsverkehrs ist offen."""
    stammdaten = {"finance_stammdaten", "fibu_stammdaten", "tax_keys", "exchange_rates",
                  "zahlungsbedingungen", "forderungsgruppen", "erloeskennziffern", "debtors", "creditors"}
    for modul, methode, weg, zugang in FAELLE:
        if zugang == "offen":
            assert modul in stammdaten and methode == "GET", (modul, methode, weg)


@pytest.mark.parametrize("modul", list(WEGE))
def test_jeder_weg_hat_eine_zugangsklasse(modul):
    """Ein neuer Weg ohne Eintrag hier — und damit ohne geprueften Zugang — macht den Vertrag rot."""
    vorhanden = {(methode, route.path) for route in _router(modul).routes for methode in route.methods}
    assert vorhanden == {(m, w) for m, w, _ in WEGE[modul]}
