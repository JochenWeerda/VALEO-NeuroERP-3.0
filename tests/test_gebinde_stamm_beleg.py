"""Gebinde-Mengeneinheit am Stamm, Stufenfaktoren, Belegabbild - Landhandelsfaelle gegen die echte Datenbank.

Schnitt 2b-1 (24.11.2026). Faelle: Duenger als Sack, Big Bag und lose Ware; Pflanzenschutzmittel mit
artikelabhaengigen Gebindegroessen; Saatmais mit unterschiedlicher Koernerzahl je Einheit; Futtermittel auf der
Palette; Diesel in Litern mit Preisbezug 100 l. Alle Werte sind Testwerte, keine Stammdaten.
"""
from __future__ import annotations

import uuid
from decimal import Decimal

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.api.v1.endpoints import artikel_mengeneinheiten
from app.core.database import SessionLocal, get_db
from app.core.gebinde_rechnung import FaktorFehlt, GebindeNichtRechenbar
from app.services.gebinde_aufloesung import abbild_der_position, berechne_position, halte_fest
from testgrenze import ersetze_mandant, ersetze_nutzer

pytestmark = pytest.mark.integration
D = Decimal
BASIS = "/artikel/mengeneinheiten/stamm"


@pytest.fixture
def mandant():
    kennung = f"gb-{uuid.uuid4().hex[:6]}"
    with SessionLocal() as db:
        db.execute(text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"),
                   {"id": kennung})
        db.commit()
    try:
        yield kennung
    finally:
        with SessionLocal() as db:
            for sql in ("DELETE FROM domain_docflow.document_items WHERE tenant_id = :t",
                        "DELETE FROM domain_docflow.document_headers WHERE tenant_id = :t",
                        "DELETE FROM domain_shared.artikel_gebindefaktoren WHERE tenant_id = :t",
                        "DELETE FROM domain_shared.artikel_mengeneinheiten WHERE tenant_id = :t"):
                db.execute(text(sql), {"t": kennung})
            db.commit()


@pytest.fixture
def client(mandant):
    app = FastAPI()
    app.include_router(artikel_mengeneinheiten.router)

    def sitzung():
        with SessionLocal() as db:
            yield db

    app.dependency_overrides[get_db] = sitzung
    ersetze_mandant(app, mandant)
    ersetze_nutzer(app, "STAMMDATEN_BEARBEITEN", "admin")
    with TestClient(app) as c:
        assert c.post(f"{BASIS}/grundeinheiten").status_code == 201
        yield c


def _einheit(c, kz: str, bez: str, **gebinde):
    angelegt = c.post(BASIS, json={"einheit_kuerzel": kz, "bezeichnung": bez, "dezimalstellen": gebinde.pop("rundung", 3)})
    assert angelegt.status_code == 201, angelegt.text
    antwort = c.put(f"{BASIS}/{kz}/gebinde", json=gebinde)
    assert antwort.status_code == 200, antwort.text
    return antwort.json()


def _rechne(c, kz: str, anzahl, **bezug):
    return c.get(f"{BASIS}/{kz}/gebinde/berechnen", params={"anzahl": str(anzahl), **bezug})


def test_duenger_sack_bigbag_und_lose_ware(client):
    _einheit(client, "sack50", "Sack 50 kg", gebindetyp=1, faktorherkunft=1, faktor1="50", ergebniseinheit="kg")
    _einheit(client, "bb600", "Big Bag 600 kg", gebindetyp=1, faktorherkunft=1, faktor1="600", ergebniseinheit="kg")

    sack = _rechne(client, "sack50", 10).json()
    bigbag = _rechne(client, "bb600", "2.5").json()
    lose = _rechne(client, "kg", "1234.5").json()  # Grundeinheit, kein Gebinde

    assert (sack["ergebnis"], sack["ergebniseinheit"], sack["herkunft_verwendet"]) == ("500.000", "kg", 1)
    assert bigbag["ergebnis"] == "1500.000"
    assert (lose["gebindetyp"], lose["ergebnis"], lose["herkunft_verwendet"]) == (0, "1234.500", None)


def test_pflanzenschutz_gebindegroesse_je_artikel(client):
    _einheit(client, "kan", "Kanister", gebindetyp=1, faktorherkunft=3, ergebniseinheit="l")
    assert client.put(f"{BASIS}/kan/gebindefaktoren/3/PSM-5L", json={"faktor1": "5"}).status_code == 200
    assert client.put(f"{BASIS}/kan/gebindefaktoren/3/PSM-10L", json={"faktor1": "10"}).status_code == 200

    fuenf = _rechne(client, "kan", 4, artikel_id="PSM-5L").json()
    zehn = _rechne(client, "kan", 4, artikel_id="PSM-10L").json()
    ohne = _rechne(client, "kan", 4, artikel_id="PSM-UNGEPFLEGT")

    assert (fuenf["ergebnis"], zehn["ergebnis"]) == ("20.000", "40.000")
    assert ohne.status_code == 422 and "Keine Gebindefaktoren" in ohne.json()["detail"]  # kein Ersatzwert 1


def test_saatmais_koernerzahl_je_einheit(client):
    _einheit(client, "ein", "Einheit Saatmais", gebindetyp=1, faktorherkunft=3, ergebniseinheit="st", rundung=0)
    client.put(f"{BASIS}/ein/gebindefaktoren/3/MAIS-50", json={"faktor1": "50000"})
    client.put(f"{BASIS}/ein/gebindefaktoren/3/MAIS-80", json={"faktor1": "80000"})

    assert _rechne(client, "ein", 3, artikel_id="MAIS-50").json()["ergebnis"] == "150000"
    assert _rechne(client, "ein", 3, artikel_id="MAIS-80").json()["ergebnis"] == "240000"


def test_futtermittel_palette_zweistufig(client):
    _einheit(client, "palft", "Palette 40 Sack a 25 kg", gebindetyp=2, faktorherkunft=1, faktor1="40", faktor2="25",
             ergebniseinheit="kg")

    assert _rechne(client, "palft", 3).json()["ergebnis"] == "3000.000"


def test_diesel_liter_mit_preisbezug_100(client):
    angelegt = client.post(BASIS, json={"einheit_kuerzel": "l100", "bezeichnung": "Liter, Preis je 100 l",
                                        "dezimalstellen": 2, "preisbezug_einheit": "l", "preisbezug_menge": 100,
                                        "un_code": "LTR"})
    assert angelegt.status_code == 201, angelegt.text

    diesel = _rechne(client, "l100", "2345.67").json()

    assert (diesel["gebindetyp"], diesel["ergebnis"]) == (0, "2345.67")  # Mengenfuehrung in Litern, keine Umrechnung
    assert float(client.get(f"{BASIS}/l100").json()["preisbezug_menge"]) == 100.0


def test_faktorpflege_ausserhalb_des_suchpfads_abgewiesen(client):
    _einheit(client, "kan2", "Kanister fest", gebindetyp=1, faktorherkunft=1, faktor1="10", ergebniseinheit="l")

    am_artikel = client.put(f"{BASIS}/kan2/gebindefaktoren/3/PSM-X", json={"faktor1": "5"})

    assert am_artikel.status_code == 409  # a.eins: bei Herkunft Mengeneinheit im Artikel nicht aenderbar


def test_herkunft_nicht_enger_stellen_solange_faktoren_darueber_liegen(client):
    _einheit(client, "kan3", "Kanister", gebindetyp=1, faktorherkunft=3, ergebniseinheit="l")
    client.put(f"{BASIS}/kan3/gebindefaktoren/3/PSM-A", json={"faktor1": "5"})

    enger = client.put(f"{BASIS}/kan3/gebinde", json={"gebindetyp": 1, "faktorherkunft": 1, "faktor1": "10"})

    assert enger.status_code == 409


@pytest.mark.parametrize(("einstellung", "grund"), [
    ({"gebindetyp": 6, "faktorherkunft": 1, "faktor1": "5"}, "deaktiv"),
    ({"gebindetyp": 1}, "Faktorherkunft"),
    ({"gebindetyp": 1, "faktorherkunft": 1}, "braucht 1 Faktor"),
    ({"gebindetyp": 1, "faktorherkunft": 1, "faktor1": "0"}, "positiv"),
    ({"gebindetyp": 0, "faktor1": "5"}, "Ohne Gebinde"),
])
def test_ungueltige_gebindeeinstellung(client, einstellung, grund):
    client.post(BASIS, json={"einheit_kuerzel": "x9", "bezeichnung": "x"})

    antwort = client.put(f"{BASIS}/x9/gebinde", json=einstellung)

    assert antwort.status_code == 422 and grund in antwort.json()["detail"], antwort.text


def test_lvs_relevanz_ist_eigene_eigenschaft(client):
    stand = _einheit(client, "palx", "Palette", gebindetyp=1, faktorherkunft=1, faktor1="40", lvs_relevanz=2,
                     lvs_default_lokalitaet="WE-ZONE")
    falsch = client.put(f"{BASIS}/palx/gebinde", json={"gebindetyp": 1, "faktorherkunft": 1, "faktor1": "40",
                                                         "lvs_relevanz": 3})

    assert (stand["lvs_relevanz"], stand["lvs_default_lokalitaet"], stand["faktorherkunft"]) == (2, "WE-ZONE", 1)
    assert falsch.status_code == 422


def _position(mandant: str) -> str:
    kopf, position = str(uuid.uuid4()), str(uuid.uuid4())
    with SessionLocal() as db:
        db.execute(text("INSERT INTO domain_docflow.document_headers (id, tenant_id, doc_type, doc_number) "
                        "VALUES (:id, :t, 'sales_delivery', :nr)"), {"id": kopf, "t": mandant, "nr": f"LS-{kopf[:8]}"})
        db.execute(text("INSERT INTO domain_docflow.document_items (id, tenant_id, header_id, line_number, "
                        "article_number, quantity) VALUES (:id, :t, :k, 1, 'PSM-5L', 4)"),
                   {"id": position, "t": mandant, "k": kopf})
        db.commit()
    return position


def test_abbild_schuetzt_den_beleg_vor_spaeteren_stammaenderungen(client, mandant):
    _einheit(client, "kan4", "Kanister", gebindetyp=1, faktorherkunft=3, ergebniseinheit="l")
    client.put(f"{BASIS}/kan4/gebindefaktoren/3/PSM-5L", json={"faktor1": "5"})
    position = _position(mandant)

    with SessionLocal() as db:
        zum_beleg = berechne_position(db, mandant, "kan4", D(4), artikel_id="PSM-5L")
        halte_fest(db, mandant, position, zum_beleg)
        halte_fest(db, mandant, position, zum_beleg)  # Wiederholung mit gleichem Abbild: idempotent
        db.commit()
    client.put(f"{BASIS}/kan4/gebindefaktoren/3/PSM-5L", json={"faktor1": "6"})  # Stamm aendert sich spaeter

    with SessionLocal() as db:
        neu = berechne_position(db, mandant, "kan4", D(4), artikel_id="PSM-5L")
        abbild = abbild_der_position(db, mandant, position)
        with pytest.raises(GebindeNichtRechenbar, match="festgeschrieben"):
            halte_fest(db, mandant, position, neu)
        with pytest.raises(Exception, match="festgeschrieben"):
            db.execute(text("UPDATE domain_docflow.document_items SET gebinde_berechnung = '{}'::jsonb "
                            "WHERE id = :id"), {"id": position})
        db.rollback()

    assert neu.ergebnis == "24.000"
    assert (abbild["ergebnis"], abbild["faktoren"], abbild["herkunft_verwendet"], abbild["version"]) == \
        ("20.000", ["5.000000"], 3, "gebinde-1")


def test_ohne_faktor_im_pfad_kein_abbild(client, mandant):
    _einheit(client, "kan5", "Kanister", gebindetyp=1, faktorherkunft=2, ergebniseinheit="l")
    client.put(f"{BASIS}/kan5/gebinde", json={"gebindetyp": 1, "faktorherkunft": 2})

    with SessionLocal() as db, pytest.raises(FaktorFehlt):
        berechne_position(db, mandant, "kan5", D(1), artikel_id="egal", artikelstamm_id="FAM-1")
