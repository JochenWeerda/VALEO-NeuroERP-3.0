"""Steuerschluessel statt Prozentsatz: die eine Auswahl fuer Masken und der Artikel als Quelle der Position.

Auftrag vom 13.10.2026: „Offenes aendern auf einheitlich Steuerschluessel.“ Rund zehn Masken fragten einen
Prozentsatz ab oder setzten 19 ein. Angegeben wird jetzt der Steuerschluessel; der Satz ist sein Abbild.

Geprueft gegen die echte Datenbank.
"""

from __future__ import annotations

import importlib.util
import pathlib
import uuid
from decimal import Decimal
from types import SimpleNamespace

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api.v1.endpoints import articles, tax_keys
from app.core.database import SessionLocal
from app.finance.steuerschluessel import Steuerklaerung, richte_skr03_ein, satz_des_schluessels, schluessel_auswahl
from testgrenze import ersetze_mandant, ersetze_nutzer


@pytest.fixture
def haus(monkeypatch):
    mandant = f"sb-{uuid.uuid4().hex[:6]}"
    with SessionLocal() as db:
        db.execute(text(
            "INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"), {"id": mandant})
        # SKR03: 2 und 3 (Umsatzsteuer 7/19), 8 und 9 (Vorsteuer 7/19).
        richte_skr03_ein(db, mandant)
        for code, name, satz, ust, vst, aktiv, bis in (
            ("1", "Steuerfrei", 0, None, None, True, None),
            ("5", "Umsatzsteuer 19 % Dienstleistung", 19, "1776", None, True, None),
            ("6", "Umsatzsteuer 16 % (abgelaufen)", 16, "1776", None, True, "2020-12-31"),
            ("7", "Umsatzsteuer 5 % (inaktiv)", 5, "1771", None, False, None),
        ):
            db.execute(text(
                "INSERT INTO domain_erp.tax_keys (id, tenant_id, code, bezeichnung, steuersatz, gueltig_von, gueltig_bis, "
                " credit_account, debit_account, active) "
                "VALUES (:id, :t, :code, :name, :satz, DATE '2020-01-01', CAST(:bis AS date), :ust, :vst, :aktiv)"),
                {"id": f"{mandant}-sk{code}", "t": mandant, "code": code, "name": name, "satz": satz, "ust": ust,
                 "vst": vst, "aktiv": aktiv, "bis": bis})
        db.commit()
    # Die Datenqualitaetspruefung des Artikels ist hier nicht der Gegenstand.
    monkeypatch.setattr(articles, "evaluate_article_datensatz", lambda *_a, **_k: SimpleNamespace(bestanden=True))
    app = FastAPI()
    app.include_router(tax_keys.router)
    app.include_router(articles.router, prefix="/articles")
    ersetze_mandant(app, mandant)
    ersetze_nutzer(app, "admin")
    try:
        with TestClient(app, raise_server_exceptions=False) as client:
            yield {"mandant": mandant, "client": client}
    finally:
        with SessionLocal() as db:
            for sql in (
                "DELETE FROM domain_inventory.articles WHERE tenant_id = :t",
                "DELETE FROM domain_erp.tax_keys WHERE tenant_id = :t",
                "DELETE FROM domain_erp.chart_of_accounts WHERE tenant_id = :t",
                "DELETE FROM domain_shared.system_properties WHERE tenant_id = :t",
                "DELETE FROM domain_shared.tenants WHERE id = :t",
            ):
                db.execute(text(sql), {"t": mandant})
            db.commit()


# --- Die eine Auswahl ---------------------------------------------------------------------------

def test_auswahl_trennt_verkauf_und_einkauf_und_laesst_ungueltige_weg(haus):
    def codes(richtung: str) -> list[str]:
        antwort = haus["client"].get("/tax-keys/auswahl", params={"richtung": richtung})
        assert antwort.status_code == 200, antwort.text
        return [k["code"] for k in antwort.json()]

    # Steuerfrei (1) gilt fuer beide; abgelaufen (6) und inaktiv (7) fuer keine.
    assert codes("verkauf") == ["1", "2", "3", "5"]
    assert codes("einkauf") == ["1", "8", "9"]
    assert haus["client"].get("/tax-keys/auswahl", params={"richtung": "beides"}).status_code == 422
    drei = next(k for k in haus["client"].get("/tax-keys/auswahl", params={"richtung": "verkauf"}).json() if k["code"] == "3")
    assert (drei["bezeichnung"], Decimal(drei["steuersatz"])) == ("Umsatzsteuer 19 %", Decimal("19"))


def test_der_satz_kommt_aus_dem_schluessel_der_richtung(haus):
    with SessionLocal() as db:
        assert satz_des_schluessels(db, haus["mandant"], "3", "verkauf") == Decimal("19")
        assert satz_des_schluessels(db, haus["mandant"], " 8 ", "einkauf") == Decimal("7")
        for code, richtung, meldung in (
            ("9", "verkauf", "Steuerschlüssel 9 ist für Verkaufsbelege nicht bekannt oder nicht gültig"),
            ("3", "einkauf", "Steuerschlüssel 3 ist für Eingangsbelege"),
            ("6", "verkauf", "nicht bekannt oder nicht gültig"),
            ("", "verkauf", "Steuerschlüssel (leer)"),
        ):
            with pytest.raises(Steuerklaerung, match=meldung.replace("(", r"\(").replace(")", r"\)")):
                satz_des_schluessels(db, haus["mandant"], code, richtung)
        assert [w.code for w in schluessel_auswahl(db, "sb-gibt-es-nicht", "verkauf")] == []


# --- Artikelstamm -------------------------------------------------------------------------------

def _artikel(haus, **abweichend):
    return haus["client"].post("/articles/", json={
        "article_number": f"A-{uuid.uuid4().hex[:6]}", "name": "Weizen", "unit": "t", "category": "Getreide",
        "sales_price": 200, "tenant_id": haus["mandant"], **abweichend})


def test_artikel_traegt_schluessel_und_der_satz_ist_ihr_abbild(haus):
    antwort = _artikel(haus, steuerschluessel_verkauf="2", steuerschluessel_einkauf="8")
    assert antwort.status_code == 201, antwort.text
    artikel = antwort.json()
    assert (artikel["steuerschluessel_verkauf"], artikel["steuerschluessel_einkauf"]) == ("2", "8")
    assert Decimal(artikel["mehrwertsteuer_prozent"]) == Decimal("7")
    # Der Schluessel wechselt, der Satz folgt.
    geaendert = haus["client"].put(f"/articles/{artikel['id']}", json={"steuerschluessel_verkauf": "3"})
    assert geaendert.status_code == 200, geaendert.text
    assert Decimal(geaendert.json()["mehrwertsteuer_prozent"]) == Decimal("19")


def test_artikel_ohne_schluessel_bekommt_keinen_satz_unterstellt(haus):
    artikel = _artikel(haus).json()
    assert (artikel["steuerschluessel_verkauf"], artikel["steuerschluessel_einkauf"], artikel["mehrwertsteuer_prozent"]) == (
        None, None, None)


@pytest.mark.parametrize("abweichend,meldung", [
    ({"steuerschluessel_verkauf": "9"}, "Steuerschlüssel 9 ist für Verkaufsbelege nicht bekannt oder nicht gültig"),
    ({"steuerschluessel_einkauf": "3"}, "Steuerschlüssel 3 ist für Eingangsbelege nicht bekannt oder nicht gültig"),
    ({"steuerschluessel_verkauf": "6"}, "nicht bekannt oder nicht gültig"),
    ({"steuerschluessel_verkauf": "3", "mehrwertsteuer_prozent": 7}, "widerspricht dem Steuerschlüssel 3 (19 %)"),
])
def test_artikel_mit_unpassendem_schluessel_wird_abgelehnt(haus, abweichend, meldung):
    antwort = _artikel(haus, **abweichend)
    assert antwort.status_code == 422, antwort.text
    assert meldung in antwort.json()["detail"]


def test_ein_satz_gegen_den_hinterlegten_schluessel_wird_abgelehnt(haus):
    artikel = _artikel(haus, steuerschluessel_verkauf="3").json()
    antwort = haus["client"].put(f"/articles/{artikel['id']}", json={"mehrwertsteuer_prozent": 7})
    assert antwort.status_code == 422 and "widerspricht dem Steuerschlüssel 3" in antwort.json()["detail"]
    # Den Schluessel zuruecknehmen geht; dann steht der Satz fuer sich.
    assert haus["client"].put(f"/articles/{artikel['id']}", json={"steuerschluessel_verkauf": ""}).status_code == 200


# --- Bestand zuordnen ---------------------------------------------------------------------------

def test_bestand_wird_nur_eindeutig_zugeordnet(haus):
    pfad = pathlib.Path(__file__).resolve().parent.parent / "scripts/artikel_steuerschluessel_zuordnen.py"
    spec = importlib.util.spec_from_file_location("artikel_steuerschluessel_zuordnen", pfad)
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)

    with SessionLocal() as db:
        for nummer, satz in (("ALT-7", 7), ("ALT-19", 19), ("ALT-11", 11), ("ALT-OHNE", None)):
            db.execute(text(
                "INSERT INTO domain_inventory.articles (id, tenant_id, article_number, name, is_active, mehrwertsteuer_prozent) "
                "VALUES (:id, :t, :nr, :nr, true, :satz)"),
                {"id": f"{haus['mandant']}-{nummer}", "t": haus["mandant"], "nr": nummer, "satz": satz})
        db.commit()
        gesetzt, offen = modul.zuordnen(db, haus["mandant"])
        db.commit()
        stand = {z[0]: (z[1], z[2]) for z in db.execute(text(
            "SELECT article_number, steuerschluessel_verkauf, steuerschluessel_einkauf FROM domain_inventory.articles "
            "WHERE tenant_id = :t"), {"t": haus["mandant"]}).fetchall()}
    # 7 %: je Richtung genau ein Schluessel. 19 %: im Verkauf zwei (3 und 5) — offen; im Einkauf einer.
    assert stand == {"ALT-7": ("2", "8"), "ALT-19": (None, "9"), "ALT-11": (None, None), "ALT-OHNE": (None, None)}
    assert (gesetzt["steuerschluessel_verkauf"], gesetzt["steuerschluessel_einkauf"]) == (1, 2)
    assert any("ALT-19: verkauf" in z and "mehrere Schluessel (3, 5)" in z for z in offen)
    assert sum("ALT-11" in z and "kein Schluessel" in z for z in offen) == 2
    assert not [z for z in offen if "ALT-OHNE" in z]
