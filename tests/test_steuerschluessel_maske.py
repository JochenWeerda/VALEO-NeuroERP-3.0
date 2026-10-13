"""Maske „Steuerschluessel“: der Kommando-Weg hinter der ScreenDefinition ``finance/steuerschluessel``.

Bis zum 13.10.2026 war die Maske handgebaut. Sie setzte beim Anlegen den Satz 19 und die Konten 1400/1776
als Vorgabe, kannte weder Erloeskonto noch Paragraf 24 UStG, konnte nichts aendern und zeigte keinen
Fehler, wenn das Speichern scheiterte. Die Liste dahinter lag bis zu einer Stunde im Cache, ohne nach
einer Aenderung geleert zu werden, und meldete einen Ladefehler als leeren Bestand.

Geprueft gegen die echte Datenbank.
"""

from __future__ import annotations

import asyncio
import uuid
from decimal import Decimal

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api.v1.endpoints import tax_keys
from app.core.database import SessionLocal
from app.core.exceptions import register_domain_exception_handlers
from app.finance.steuerschluessel import richte_skr03_ein
from testgrenze import ersetze_mandant, ersetze_nutzer

WEG = "/tax-keys/actions/speichern"


@pytest.fixture
def haus():
    mandant = f"sk-{uuid.uuid4().hex[:6]}"
    with SessionLocal() as db:
        db.execute(text(
            "INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"), {"id": mandant})
        # SKR03: Schluessel 2, 3, 8, 9 und die Konten 1571, 1576, 1771, 1776, 8300, 8400.
        richte_skr03_ein(db, mandant)
        db.commit()
    app = FastAPI()
    register_domain_exception_handlers(app)
    app.include_router(tax_keys.router)
    ersetze_mandant(app, mandant)
    ersetze_nutzer(app, "FINANCE_BEARBEITEN")
    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            yield {"mandant": mandant, "client": client, "app": app}
    finally:
        with SessionLocal() as db:
            for sql in (
                "DELETE FROM domain_erp.tax_keys WHERE tenant_id = :t",
                "DELETE FROM domain_erp.chart_of_accounts WHERE tenant_id = :t",
                "DELETE FROM domain_shared.system_properties WHERE tenant_id = :t",
                "DELETE FROM domain_shared.tenants WHERE id = :t",
            ):
                db.execute(text(sql), {"t": mandant})
            db.commit()


def _eingabe(**abweichend) -> dict:
    return {
        "code": "5", "bezeichnung": "Umsatzsteuer 19 % (Dienstleistung)", "steuersatz": "19",
        "credit_account": "1776", "revenue_account": "8400", "gueltig_von": "2021-01-01",
        "_mode": "execute", "_idempotencyKey": uuid.uuid4().hex,
        **abweichend,
    }


def _zeilen(mandant: str, code: str) -> list[tuple]:
    with SessionLocal() as db:
        return [tuple(z) for z in db.execute(text(
            "SELECT steuersatz, credit_account, debit_account, revenue_account, par_24_ustg, active "
            "FROM domain_erp.tax_keys WHERE tenant_id = :t AND code = :c"), {"t": mandant, "c": code}).fetchall()]


def _liste(haus) -> dict[str, dict]:
    antwort = haus["client"].get("/tax-keys", params={"active_only": False})
    assert antwort.status_code == 200, antwort.text
    return {z["code"]: z for z in antwort.json()}


# --- Anlegen und Aendern ------------------------------------------------------------------------

def test_legt_einen_schluessel_mit_erloeskonto_und_paragraf_24_an(haus):
    antwort = haus["client"].post(WEG, json=_eingabe(code="24", bezeichnung="Durchschnittssatz 7,8 %", steuersatz="7,8",
                                                    credit_account="1771", revenue_account="8300", par_24_ustg=True))
    ergebnis = antwort.json()
    assert antwort.status_code == 200 and ergebnis["success"], antwort.text
    assert "Steuerschlüssel 24 angelegt" in ergebnis["summary"] and "7,8 %" in ergebnis["summary"]
    assert ergebnis["auditEntryId"]
    assert _zeilen(haus["mandant"], "24") == [(Decimal("7.80"), "1771", None, "8300", True, True)]


def test_die_liste_zeigt_den_neuen_schluessel_sofort(haus):
    """Die Liste liegt im Cache; nach dem Speichern muss er geleert sein."""
    assert "5" not in _liste(haus)
    assert haus["client"].post(WEG, json=_eingabe()).json()["success"]
    assert _liste(haus)["5"]["revenue_account"] == "8400"


def test_die_liste_laesst_sich_zweimal_hintereinander_lesen(haus):
    """Der zweite gleiche Aufruf kommt aus dem Cache. Bis zum 13.10.2026 lag dort die Textdarstellung der
    Antwort, und der Aufruf endete mit 500 — bis der Eintrag nach einer Stunde ablief."""
    erste = haus["client"].get("/tax-keys", params={"active_only": True})
    zweite = haus["client"].get("/tax-keys", params={"active_only": True})
    assert (erste.status_code, zweite.status_code) == (200, 200), zweite.text
    assert zweite.json() == erste.json() and {k["code"] for k in zweite.json()} == {"2", "3", "8", "9"}


def test_aendert_den_vorhandenen_schluessel_und_nennt_die_aenderung(haus):
    assert haus["client"].post(WEG, json=_eingabe()).json()["success"]
    ergebnis = haus["client"].post(WEG, json=_eingabe(steuersatz="16", revenue_account="8300")).json()
    assert ergebnis["success"], ergebnis
    assert "Steuersatz 19 → 16" in ergebnis["summary"] and "Erlöskonto 8400 → 8300" in ergebnis["summary"]
    assert _zeilen(haus["mandant"], "5") == [(Decimal("16.00"), "1776", None, "8300", False, True)]


def test_nimmt_das_erloeskonto_zurueck_und_setzt_inaktiv(haus):
    assert haus["client"].post(WEG, json=_eingabe()).json()["success"]
    ergebnis = haus["client"].post(WEG, json=_eingabe(revenue_account="", active=False)).json()
    assert ergebnis["success"], ergebnis
    assert _zeilen(haus["mandant"], "5") == [(Decimal("19.00"), "1776", None, None, False, False)]


def test_gleiche_eingabe_aendert_nichts(haus):
    assert haus["client"].post(WEG, json=_eingabe()).json()["success"]
    assert haus["client"].post(WEG, json=_eingabe()).json()["summary"] == "Steuerschlüssel 5 unverändert."


def test_trockenlauf_schreibt_nichts(haus):
    ergebnis = haus["client"].post(WEG, json=_eingabe(_mode="dryRun")).json()
    assert ergebnis["success"] and ergebnis["mode"] == "dryRun", ergebnis
    assert _zeilen(haus["mandant"], "5") == []


# --- Keine stillschweigende Annahme --------------------------------------------------------------

@pytest.mark.parametrize("abweichend,feld,meldung", [
    ({"steuersatz": ""}, "steuersatz", "es gibt keinen Vorgabewert"),
    ({"steuersatz": None}, "steuersatz", "es gibt keinen Vorgabewert"),
    ({"steuersatz": "neunzehn"}, "steuersatz", "keine Zahl"),
    ({"steuersatz": "119"}, "steuersatz", "zwischen 0 und 100"),
    ({"code": "USt"}, "code", "ein oder zwei Ziffern"),
    ({"bezeichnung": " "}, "bezeichnung", "Bezeichnung angeben"),
    ({"gueltig_von": ""}, "gueltig_von", "Gültig von angeben"),
    ({"gueltig_bis": "2020-12-31"}, "gueltig_bis", "liegt vor"),
    ({"reverse_charge": True}, "steuersatz", "Reverse Charge verlangt den Steuersatz 0"),
    ({"credit_account": "1777"}, "credit_account", "Umsatzsteuerkonto 1777 steht nicht im Kontenplan"),
    ({"revenue_account": "8999"}, "revenue_account", "Erlöskonto 8999 steht nicht im Kontenplan"),
    ({"debit_account": "1599"}, "debit_account", "Vorsteuerkonto 1599 steht nicht im Kontenplan"),
])
def test_unklare_eingabe_wird_abgelehnt_und_nicht_gespeichert(haus, abweichend, feld, meldung):
    ergebnis = haus["client"].post(WEG, json=_eingabe(**abweichend)).json()
    assert ergebnis["success"] is False, ergebnis
    assert any(f["field"] == feld and meldung in f["message"] for f in ergebnis["validationErrors"]), ergebnis
    assert _zeilen(haus["mandant"], "5") == [] and _zeilen(haus["mandant"], "USt") == []


def test_ein_abgelehnter_wechsel_laesst_den_bestand_stehen(haus):
    assert haus["client"].post(WEG, json=_eingabe()).json()["success"]
    assert haus["client"].post(WEG, json=_eingabe(steuersatz="16", revenue_account="8999")).json()["success"] is False
    assert _zeilen(haus["mandant"], "5") == [(Decimal("19.00"), "1776", None, "8400", False, True)]


# --- Verwendung: dieselbe Regel wie die Buchung ---------------------------------------------------

def test_die_liste_sagt_wofuer_ein_schluessel_bucht(haus):
    for eingabe in (
        _eingabe(code="24", steuersatz="7,8", credit_account="1771", revenue_account=""),
        _eingabe(code="94", steuersatz="0", credit_account="", reverse_charge=True),
        _eingabe(code="7", credit_account="1776", debit_account="1576"),
    ):
        assert haus["client"].post(WEG, json=eingabe).json()["success"]
    liste = _liste(haus)
    assert liste["3"]["verwendung"] == "Verkauf"
    assert liste["9"]["verwendung"] == "Einkauf"
    assert liste["7"]["verwendung"] == "Verkauf, Einkauf"
    assert liste["24"]["verwendung"] == "Bucht nicht automatisch: Für Steuerschlüssel 24 ist kein Erlöskonto hinterlegt."
    assert "Reverse Charge" in liste["94"]["verwendung"]
    # Ohne UStVA-Kennzahl steht dort nichts — bis zum 13.10.2026 der Text „None“.
    assert liste["24"]["ustva_position"] is None


# --- Konten aus dem Kontenplan -------------------------------------------------------------------

def _vorschlaege(haus, satz: str | None) -> dict[str, list[dict]]:
    antwort = haus["client"].get("/tax-keys/kontenvorschlaege", params={"steuersatz": satz} if satz else None)
    assert antwort.status_code == 200, antwort.text
    return antwort.json()


def test_schlaegt_je_feld_konten_der_passenden_art_vor_und_reiht_nach_satz(haus):
    v = _vorschlaege(haus, "7")
    assert (v["credit_account"][0], v["debit_account"][0], v["revenue_account"][0]) == (
        {"account_number": "1771", "account_name": "Umsatzsteuer 7 %", "grund": "passt zum Satz 7 %"},
        {"account_number": "1571", "account_name": "Abziehbare Vorsteuer 7 %", "grund": "passt zum Satz 7 %"},
        {"account_number": "8300", "account_name": "Erlöse 7 % USt", "grund": "passt zum Satz 7 %"},
    )
    v = _vorschlaege(haus, "19,0")
    assert [k[0]["account_number"] for k in (v["credit_account"], v["debit_account"], v["revenue_account"])] == [
        "1776", "1576", "8400"]
    # Das andere Steuerkonto bleibt waehlbar, steht aber dahinter.
    nach_nr = {k["account_number"]: k for k in v["credit_account"]}
    assert nach_nr["1771"]["grund"] == "nach Bezeichnung"
    # Nur Konten der passenden Art: kein Forderungs- und kein Erloeskonto als Umsatzsteuerkonto.
    assert not {"1400", "1576", "8400"} & set(nach_nr)
    assert "1776" not in {k["account_number"] for k in v["revenue_account"]}


def test_sieben_prozent_trifft_nicht_siebzehn(haus):
    with SessionLocal() as db:
        db.execute(text(
            "INSERT INTO domain_erp.chart_of_accounts (id, tenant_id, account_number, account_name, account_type, "
            " category, is_active) VALUES (:id, :t, '1777', 'Umsatzsteuer 17 %', 'liability', 'tax', true)"),
            {"id": f"{haus['mandant']}-1777", "t": haus["mandant"]})
        db.commit()
    nach_nr = {k["account_number"]: k["grund"] for k in _vorschlaege(haus, "7")["credit_account"]}
    assert (nach_nr["1771"], nach_nr["1777"]) == ("passt zum Satz 7 %", "nach Bezeichnung")


def test_ohne_satz_und_bei_null_wird_kein_steuerkonto_zum_satz_gereiht(haus):
    for satz in (None, "0", "neunzehn"):
        v = _vorschlaege(haus, satz)
        assert {k["grund"] for k in v["credit_account"] if k["account_number"] in ("1771", "1776")} == {"nach Bezeichnung"}


def test_gesperrte_konten_werden_nicht_vorgeschlagen_und_nicht_angenommen(haus):
    with SessionLocal() as db:
        db.execute(text(
            "UPDATE domain_erp.chart_of_accounts SET posting_blocked = true WHERE tenant_id = :t AND account_number = '8300'"),
            {"t": haus["mandant"]})
        db.commit()
    assert "8300" not in {k["account_number"] for k in _vorschlaege(haus, "7")["revenue_account"]}
    ergebnis = haus["client"].post(WEG, json=_eingabe(revenue_account="8300")).json()
    assert ergebnis["success"] is False
    assert "Erlöskonto 8300 steht nicht im Kontenplan oder ist gesperrt" in ergebnis["validationErrors"][0]["message"]


@pytest.mark.parametrize("abweichend,meldung", [
    # 1400 war bis zum 13.10.2026 die Vorgabe der Maske fuer das „Konto Soll“.
    ({"credit_account": "1400"}, "Umsatzsteuerkonto 1400 (Forderungen aus Lieferungen und Leistungen) ist kein Verbindlichkeitskonto"),
    ({"debit_account": "1776"}, "Vorsteuerkonto 1776 (Umsatzsteuer 19 %) ist kein Aktivkonto"),
    ({"revenue_account": "1776"}, "Erlöskonto 1776 (Umsatzsteuer 19 %) ist kein Erlöskonto"),
])
def test_ein_konto_der_falschen_art_wird_abgelehnt(haus, abweichend, meldung):
    ergebnis = haus["client"].post(WEG, json=_eingabe(**abweichend)).json()
    assert ergebnis["success"] is False, ergebnis
    assert meldung in ergebnis["validationErrors"][0]["message"], ergebnis
    assert _zeilen(haus["mandant"], "5") == []


def test_aufwandskonto_fuer_eingangsbelege_wird_vorgeschlagen_gespeichert_und_geprueft(haus):
    """Das Gegenstueck zum Erloeskonto: Aus ihm bucht die Eingangsrechnung den Nettobetrag."""
    v = _vorschlaege(haus, "19")["expense_account"]
    assert v[0] == {"account_number": "3400", "account_name": "Wareneingang 19 % Vorsteuer", "grund": "passt zum Satz 19 %"}
    assert "1576" not in {k["account_number"] for k in v}
    assert haus["client"].post(WEG, json=_eingabe(
        code="6", credit_account="", revenue_account="", debit_account="1576", expense_account="3400")).json()["success"]
    assert _liste(haus)["6"]["expense_account"] == "3400"
    # Die SKR03-Grundausstattung traegt es fuer die Vorsteuerschluessel schon.
    assert (_liste(haus)["8"]["expense_account"], _liste(haus)["9"]["expense_account"]) == ("3300", "3400")
    abgelehnt = haus["client"].post(WEG, json=_eingabe(code="6", expense_account="1576")).json()
    assert abgelehnt["success"] is False
    assert "Aufwandskonto 1576 (Abziehbare Vorsteuer 19 %) ist kein Aufwandskonto" in abgelehnt["validationErrors"][0]["message"]


# --- Zugang und Ladefehler ----------------------------------------------------------------------

def test_lesen_reicht_nicht_zum_speichern(haus):
    ersetze_nutzer(haus["app"], "FINANCE_LESEN")
    assert haus["client"].post(WEG, json=_eingabe()).status_code == 403
    assert _zeilen(haus["mandant"], "5") == []


def test_ein_ladefehler_ist_kein_leerer_bestand():
    class Kaputt:
        zurueckgerollt = False

        def execute(self, *_a, **_k):
            raise RuntimeError("Verbindung weg")

        def rollback(self):
            self.zurueckgerollt = True

    db = Kaputt()
    with pytest.raises(HTTPException) as fehler:
        asyncio.run(tax_keys.list_tax_keys(tenant_id="sk-kaputt", active_only=True, country=None, db=db))
    assert fehler.value.status_code == 500 and db.zurueckgerollt


# --- ScreenDefinition, Aktionskarte --------------------------------------------------------------

def test_maske_ist_eine_screen_definition_ohne_vorgabewert():
    from app.api.v1.endpoints.mask_screen_definition import _check_readiness
    from app.core.screen_definitions import _AGENT_SYNONYMS, _SCREEN_LIST_ROUTE, get_screen_definition
    from app.core.screen_governance import governance_errors, ux_lint

    sd = get_screen_definition("finance/steuerschluessel")
    assert sd["adapter"]["temporary"] is False
    assert "finance/steuerschluessel" in _AGENT_SYNONYMS and "finance/steuerschluessel" in _SCREEN_LIST_ROUTE
    assert governance_errors(sd) == []
    assert [f for f in ux_lint(sd) if f["severity"] == "error"] == []
    bereit = _check_readiness(sd)
    assert bereit["generatorReady"] is True and bereit["advisoryScore"] == 1.0

    felder = {f["key"]: f for f in sd["fields"]}
    # Erloeskonto und Paragraf 24 fehlten der handgebauten Maske.
    assert {"revenue_account", "par_24_ustg", "credit_account", "debit_account"} <= set(felder)
    assert not [k for k, f in felder.items() if "default" in f or "defaultValue" in f]
    # Konten sind eine Auswahl aus dem Kontenplan, kein Freitext.
    for konto in ("credit_account", "debit_account", "revenue_account"):
        assert (felder[konto]["type"], felder[konto]["dataSourceKey"]) == ("select", "konten")
    # Jedes Feld der Maske kennt der Kommando-Weg.
    assert set(felder) <= {"code", *tax_keys._SPALTEN}
    speichern = next(a for a in sd["actions"] if a["key"] == "speichern")
    assert speichern["commandEndpoint"] == "/api/v1/finance/tax-keys/actions/speichern"


def test_ein_agent_setzt_keinen_steuerschluessel_in_kraft():
    import pathlib

    import yaml

    from app.core.screen_definitions import get_screen_definition

    speichern = next(a for a in get_screen_definition("finance/steuerschluessel")["actions"] if a["key"] == "speichern")
    assert speichern["forbiddenForAgents"] is True and speichern["humanApprovalRequired"] is True
    wurzel = pathlib.Path(__file__).resolve().parent.parent
    karte = yaml.safe_load((wurzel / "config/mcp_mask_action_map.yaml").read_text(encoding="utf-8"))
    eintrag = next(m for m in karte["mappings"] if m["mask_action_id"] == "mask:finance/steuerschluessel:speichern")
    assert eintrag["mcp_tool_id"] is None and eintrag["coverage"] == "open_high"
    werkzeuge = yaml.safe_load((wurzel / "config/mcp_erp_tools.yaml").read_text(encoding="utf-8"))["tools"]
    assert not [w["tool_id"] for w in werkzeuge if "steuerschluessel" in w["tool_id"] or "tax_key" in w["tool_id"]]

