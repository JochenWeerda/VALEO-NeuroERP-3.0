"""Kasse: Erfolg nur, wenn signiert und gespeichert ist.

Bis 27.10.2026 antwortete ``POST /pos/checkout`` mit ``completed``, ohne etwas zu speichern; die
Offline-Warteschlange des Terminals loeschte den Bon daraufhin lokal. ``POST /pos/retoure`` nahm den
Mandanten aus dem Rumpf (Rueckfall Standardmandant) und meldete Erfolg, auch wenn die Buchung scheiterte.

Geprueft auf dem Pruefstand ``valeo_probe`` mit eigenen, zurueckgerollten Zeilen; der Fiskalisierungsdienst
laeuft mit dem ausdruecklich erlaubten Simulationsprovider.
"""
from __future__ import annotations

import asyncio
import inspect
import os
from decimal import Decimal
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi import HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session

from app.api.v1.endpoints import pos_retoure as kasse
from app.services.fiscalization.contracts import FiscalLine, StartTransactionCommand
from app.services.fiscalization.providers import FiscalProviderError, FiskalyProvider

pytestmark = pytest.mark.integration


@pytest.fixture
def pruefstand():
    url = os.environ.get("TEST_DATABASE_URL")
    if not url:
        pytest.skip("TEST_DATABASE_URL (valeo_probe) erforderlich")
    assert make_url(url).database == "valeo_probe" or os.environ.get("GITHUB_ACTIONS") == "true"
    engine = create_engine(url)
    with engine.connect() as connection:
        transaction = connection.begin()
        ids = {k: f"pos-{k}-{uuid4().hex[:10]}" for k in ("a", "b", "lager", "art7", "art19", "ohne", "fremd")}

        def sql(statement, **params):
            return connection.execute(text(statement), {**ids, **params})

        for t in ("a", "b"):
            sql("INSERT INTO domain_shared.tenants(id, name) VALUES (:t, 'Kassenpruefung')", t=ids[t])
        sql("INSERT INTO domain_inventory.warehouses(id, warehouse_code, name, tenant_id) VALUES (:lager, 'POS-T', 'Kasse', :a)")
        for code, satz in (("2", 7), ("3", 19)):
            sql("""INSERT INTO domain_erp.tax_keys(id, tenant_id, code, bezeichnung, steuersatz, gueltig_von)
                   VALUES (:id, :a, :code, 'Kassenpruefung', :satz, DATE '2020-01-01')""",
                id=str(uuid4()), code=code, satz=satz)
        for key, code in (("art7", "2"), ("art19", "3"), ("ohne", None)):
            sql("""INSERT INTO domain_inventory.articles(id, article_number, name, tenant_id, steuerschluessel_verkauf, current_stock)
                   VALUES (:id, :id, 'Kassenartikel', :a, :code, 5)""", id=ids[key], code=code)
        sql("""INSERT INTO domain_inventory.articles(id, article_number, name, tenant_id, steuerschluessel_verkauf)
               VALUES (:fremd, :fremd, 'Fremdartikel', :b, '2')""")
        sql("""INSERT INTO domain_docflow.pos_fiscal_provider_configs
               (tenant_id, provider, dsfinvk_provider, cash_register_id, client_id, simulation_allowed)
               VALUES (:a, 'simulation', 'simulation', 'KASSE-1', 'CLIENT-1', true)""")
        session = Session(bind=connection, join_transaction_mode="create_savepoint")
        try:
            yield session, sql, ids
        finally:
            session.close()
            transaction.rollback()
    engine.dispose()


def _checkout(session, tenant, **daten):
    body = {"offline_id": f"offline-{uuid4()}", "cart": [], "zahlungen": [], "gesamt": "0"} | daten
    return asyncio.run(kasse.pos_checkout(kasse.CheckoutRequest(**body), tenant_id=tenant, db=session))


def _retoure(session, tenant, **daten):
    body = {"vorgang_id": str(uuid4()), "kassierer": "Anzeige", "zahlungsrueckerstattung": "bar"} | daten
    return asyncio.run(kasse.create_retoure(kasse.RetourRequest(**body), tenant_id=tenant, db=session))


def _fehler(aufruf) -> HTTPException:
    with pytest.raises(HTTPException) as info:
        aufruf()
    return info.value


def _fiskal(sql, tenant, tx):
    return sql("SELECT gross_total, state, payment_breakdown FROM domain_docflow.pos_fiscal_transactions "
               "WHERE tenant_id = :t AND transaction_id = :tx", t=tenant, tx=tx).fetchall()


def test_offline_bon_wird_signiert_gespeichert_und_nur_einmal(pruefstand):
    session, sql, ids = pruefstand
    offline_id = f"offline-{uuid4()}"
    daten = dict(offline_id=offline_id, gesamt="38.00",
                 cart=[{"artikelnr": ids["art19"], "bezeichnung": "Futter", "preis": "10", "menge": 2, "rabatt_pct": 10,
                        "vat_rate": 19},
                       {"artikelnr": ids["art7"], "bezeichnung": "Saatgut", "preis": "20", "menge": 1}],
                 zahlungen=[{"art": "bar", "betrag": "30"}, {"art": "ec", "betrag": "8"}])
    erstes = _checkout(session, ids["a"], **daten)
    assert erstes.status == "completed" and erstes.simuliert and erstes.signatur_zaehler is not None
    zeilen = _fiskal(sql, ids["a"], offline_id)
    assert len(zeilen) == 1
    brutto, zustand, zahlarten = zeilen[0]
    assert (Decimal(brutto), zustand) == (Decimal("38.00"), "FINISHED")
    assert {k: Decimal(v) for k, v in zahlarten.items()} == {"BAR": Decimal("30"), "KARTE": Decimal("8")}

    zweites = _checkout(session, ids["a"], **daten)
    assert zweites.signatur_zaehler == erstes.signatur_zaehler
    assert len(_fiskal(sql, ids["a"], offline_id)) == 1


@pytest.mark.parametrize("aenderung, status", [
    ({"gesamt": "20.00"}, 422),                                                  # Rabatt nicht beruecksichtigt
    ({"zahlungen": [{"art": "bar", "betrag": "10"}]}, 422),                      # Zahlung deckt nicht
    ({"zahlungen": [{"art": "scheck", "betrag": "18"}]}, 422),                   # unbekannte Zahlart
    ({"cart": [{"artikelnr": "x", "bezeichnung": "x", "preis": "18", "menge": 1, "vat_rate": "7.8"}]}, 422),
])
def test_unstimmiger_bon_bleibt_in_der_warteschlange(pruefstand, aenderung, status):
    session, sql, ids = pruefstand
    daten = dict(gesamt="18.00", cart=[{"artikelnr": ids["art19"], "bezeichnung": "Futter", "preis": "10", "menge": 2,
                                        "rabatt_pct": 10, "vat_rate": 19}],
                 zahlungen=[{"art": "bar", "betrag": "18"}]) | aenderung
    offline_id = f"offline-{uuid4()}"
    assert _fehler(lambda: _checkout(session, ids["a"], offline_id=offline_id, **daten)).status_code == status
    assert _fiskal(sql, ids["a"], offline_id) == []


@pytest.mark.parametrize("artikel", ["ohne", "fremd", "unbekannt"])
def test_steuersatz_nie_angenommen(pruefstand, artikel):
    """Ohne Satz vom Terminal kommt er aus dem Steuerschluessel des eigenen Artikels — sonst 422, keine 19 %."""
    session, sql, ids = pruefstand
    nummer = ids.get(artikel, "gibt-es-nicht")
    fehler = _fehler(lambda: _checkout(session, ids["a"], gesamt="5", zahlungen=[{"art": "bar", "betrag": "5"}],
                                       cart=[{"artikelnr": nummer, "bezeichnung": "x", "preis": "5", "menge": 1}]))
    assert fehler.status_code == 422


def test_ohne_kasse_des_mandanten_kein_erfolg(pruefstand):
    """Mandant b hat keine Fiskalisierung — die Kasse von a gilt nicht fuer ihn."""
    session, sql, ids = pruefstand
    offline_id = f"offline-{uuid4()}"
    fehler = _fehler(lambda: _checkout(session, ids["b"], offline_id=offline_id, gesamt="5",
                                       zahlungen=[{"art": "bar", "betrag": "5"}],
                                       cart=[{"bezeichnung": "x", "preis": "5", "menge": 1, "vat_rate": 19}]))
    assert fehler.status_code == 503
    assert _fiskal(sql, ids["b"], offline_id) == [] and _fiskal(sql, ids["a"], offline_id) == []


def test_wiederholung_mit_anderen_betraegen_wird_abgewiesen(pruefstand):
    session, sql, ids = pruefstand
    offline_id = f"offline-{uuid4()}"
    zeile = {"bezeichnung": "x", "preis": "5", "menge": 1, "vat_rate": 19}
    _checkout(session, ids["a"], offline_id=offline_id, gesamt="5", zahlungen=[{"art": "bar", "betrag": "5"}], cart=[zeile])
    fehler = _fehler(lambda: _checkout(session, ids["a"], offline_id=offline_id, gesamt="10",
                                       zahlungen=[{"art": "bar", "betrag": "10"}], cart=[zeile | {"menge": 2}]))
    assert fehler.status_code == 409


def _bewegungen(sql, tenant, vorgang):
    return sql("SELECT article_id, quantity, warehouse_id FROM domain_inventory.inventory_stock_movements "
               "WHERE tenant_id = :t AND source_document_type = 'pos_retoure' AND source_document_id = :v",
               t=tenant, v=vorgang).fetchall()


def test_retoure_signiert_negativ_bucht_bestand_und_nur_einmal(pruefstand):
    session, sql, ids = pruefstand
    vorgang = str(uuid4())
    daten = dict(vorgang_id=vorgang, gesamt="25.00",
                 positionen=[{"artikelnr": ids["art7"], "bezeichnung": "Saatgut", "einzelpreis": "12.5", "menge": 2}])
    antwort = _retoure(session, ids["a"], **daten)
    assert antwort.status == "completed" and antwort.retoure_id == vorgang
    [(brutto, zustand, zahlarten)] = _fiskal(sql, ids["a"], vorgang)
    assert (Decimal(brutto), zustand) == (Decimal("-25.00"), "FINISHED")
    assert {k: Decimal(v) for k, v in zahlarten.items()} == {"BAR": Decimal("-25.00")}
    assert _bewegungen(sql, ids["a"], vorgang) == [(ids["art7"], Decimal("2.00"), ids["lager"])]

    _retoure(session, ids["a"], **daten)
    assert len(_bewegungen(sql, ids["a"], vorgang)) == 1
    assert len(_fiskal(sql, ids["a"], vorgang)) == 1


@pytest.mark.parametrize("tenant, artikel, status", [
    ("a", "unbekannt", 422),   # unbekannter Artikel: frueher 0 Zeilen und trotzdem "erfolgreich gebucht"
    ("a", "ohne", 422),        # ohne Steuerschluessel nicht signierbar
    ("a", "fremd", 422),       # Artikel eines anderen Mandanten
    ("b", "fremd", 422),       # Mandant b hat kein Lager
])
def test_retoure_ohne_grundlage_bucht_nichts(pruefstand, tenant, artikel, status):
    session, sql, ids = pruefstand
    vorgang = str(uuid4())
    nummer = ids.get(artikel, "gibt-es-nicht")
    fehler = _fehler(lambda: _retoure(session, ids[tenant], vorgang_id=vorgang, gesamt="5",
                                      positionen=[{"artikelnr": nummer, "bezeichnung": "x", "einzelpreis": "5", "menge": 1}]))
    assert fehler.status_code == status
    assert _fiskal(sql, ids[tenant], vorgang) == [] and _bewegungen(sql, ids[tenant], vorgang) == []


def test_retoure_summe_muss_stimmen(pruefstand):
    session, sql, ids = pruefstand
    fehler = _fehler(lambda: _retoure(session, ids["a"], gesamt="99",
                                      positionen=[{"artikelnr": ids["art7"], "bezeichnung": "x", "einzelpreis": "5", "menge": 1}]))
    assert fehler.status_code == 422


def test_mandant_kommt_aus_dem_token_nicht_aus_dem_rumpf():
    from app.core.tenant import get_tenant_id

    for weg in (kasse.create_retoure, kasse.pos_checkout):
        assert inspect.signature(weg).parameters["tenant_id"].default.dependency is get_tenant_id
    assert "tenant_id" not in kasse.RetourRequest.model_fields
    assert "tenant_id" not in kasse.CheckoutRequest.model_fields
    quelle = Path(kasse.__file__).read_text(encoding="utf-8")
    assert "DEFAULT_TENANT" not in quelle and "except Exception" not in quelle


def test_fiskaly_signiert_unbekannten_satz_nicht_als_normalsatz():
    befehl = StartTransactionCommand(terminal_id="t", cash_register_id="k", client_id="c", transaction_id="x",
                                     lines=[FiscalLine(text="x", gross_amount=Decimal("1"), vat_rate=Decimal("7.8"))])
    with pytest.raises(FiscalProviderError):
        FiskalyProvider._receipt_payload(befehl, "FINISHED")
    befehl.lines[0].vat_rate = Decimal("7")
    assert FiskalyProvider._receipt_payload(befehl, "FINISHED")
