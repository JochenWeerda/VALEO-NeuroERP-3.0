"""Gebinde-Mengeneinheit am Stamm, Artikelfaktoren, versionierte Belegabbilder - Landhandelsfaelle gegen die echte DB.

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
from app.core.gebinde_rechnung import FaktorFehlt
from app.services.gebinde_aufloesung import (
    BelegGebucht, abbild_der_position, abbild_versionen, berechne_position, schreibe_abbild,
)
from testgrenze import ersetze_mandant, ersetze_nutzer

pytestmark = pytest.mark.integration
D = Decimal
BASIS = "/artikel/mengeneinheiten/stamm"


def _mandant_anlegen() -> str:
    kennung = f"gb-{uuid.uuid4().hex[:6]}"
    with SessionLocal() as db:
        db.execute(text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:id, :id, true)"),
                   {"id": kennung})
        db.commit()
    return kennung


def _aufraeumen(kennung: str) -> None:
    with SessionLocal() as db:
        for sql in ("DELETE FROM domain_docflow.document_headers WHERE tenant_id = :t",
                    "DELETE FROM domain_shared.artikel_gebindefaktoren WHERE tenant_id = :t",
                    "DELETE FROM domain_shared.artikel_mengeneinheiten WHERE tenant_id = :t",
                    "DELETE FROM domain_inventory.articles WHERE tenant_id = :t"):
            db.execute(text(sql), {"t": kennung})
        db.commit()


@pytest.fixture
def mandant():
    kennung = _mandant_anlegen()
    try:
        yield kennung
    finally:
        _aufraeumen(kennung)


def _artikel(mandant: str, nummer: str) -> str:
    kennung = f"{mandant}-{nummer}"
    with SessionLocal() as db:
        db.execute(text("INSERT INTO domain_inventory.articles (id, tenant_id, article_number, name, unit) "
                        "VALUES (:id, :t, :nr, :nr, 'st')"), {"id": kennung, "t": mandant, "nr": nummer})
        db.commit()
    return kennung


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


def test_pflanzenschutz_gebindegroesse_je_artikel(client, mandant):
    fuenf_l, zehn_l, ohne_faktor = (_artikel(mandant, n) for n in ("PSM-5L", "PSM-10L", "PSM-OHNE"))
    _einheit(client, "kan", "Kanister", gebindetyp=1, faktorherkunft=3, ergebniseinheit="l")
    assert client.put(f"{BASIS}/kan/gebindefaktoren/3/{fuenf_l}", json={"faktor1": "5"}).status_code == 200
    assert client.put(f"{BASIS}/kan/gebindefaktoren/3/{zehn_l}", json={"faktor1": "10"}).status_code == 200

    fuenf = _rechne(client, "kan", 4, artikel_id=fuenf_l).json()
    zehn = _rechne(client, "kan", 4, artikel_id=zehn_l).json()
    ohne = _rechne(client, "kan", 4, artikel_id=ohne_faktor)

    assert (fuenf["ergebnis"], zehn["ergebnis"]) == ("20.000", "40.000")
    assert ohne.status_code == 422 and "Keine Gebindefaktoren" in ohne.json()["detail"]  # kein Ersatzwert 1


def test_saatmais_koernerzahl_je_einheit(client, mandant):
    mais50, mais80 = _artikel(mandant, "MAIS-50"), _artikel(mandant, "MAIS-80")
    _einheit(client, "ein", "Einheit Saatmais", gebindetyp=1, faktorherkunft=3, ergebniseinheit="st", rundung=0)
    client.put(f"{BASIS}/ein/gebindefaktoren/3/{mais50}", json={"faktor1": "50000"})
    client.put(f"{BASIS}/ein/gebindefaktoren/3/{mais80}", json={"faktor1": "80000"})

    assert _rechne(client, "ein", 3, artikel_id=mais50).json()["ergebnis"] == "150000"
    assert _rechne(client, "ein", 3, artikel_id=mais80).json()["ergebnis"] == "240000"


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


def test_faktorpflege_ausserhalb_des_suchpfads_abgewiesen(client, mandant):
    artikel = _artikel(mandant, "PSM-X")
    _einheit(client, "kan2", "Kanister fest", gebindetyp=1, faktorherkunft=1, faktor1="10", ergebniseinheit="l")

    am_artikel = client.put(f"{BASIS}/kan2/gebindefaktoren/3/{artikel}", json={"faktor1": "5"})

    assert am_artikel.status_code == 409  # a.eins: bei Herkunft Mengeneinheit im Artikel nicht aenderbar


@pytest.mark.parametrize("stufe", [2, 4])
def test_stufen_ohne_valeo_gegenstueck_nicht_pflegbar(client, stufe):
    _einheit(client, "kan6", "Kanister", gebindetyp=1, faktorherkunft=4, ergebniseinheit="l")

    antwort = client.put(f"{BASIS}/kan6/gebindefaktoren/{stufe}/irgendwas", json={"faktor1": "5"})

    assert antwort.status_code == 422 and "kein Gegenstueck" in antwort.json()["detail"]


def test_artikel_eines_fremden_mandanten_abgewiesen(client):
    fremd = _mandant_anlegen()
    try:
        fremder_artikel = _artikel(fremd, "PSM-FREMD")
        _einheit(client, "kan7", "Kanister", gebindetyp=1, faktorherkunft=3, ergebniseinheit="l")

        antwort = client.put(f"{BASIS}/kan7/gebindefaktoren/3/{fremder_artikel}", json={"faktor1": "5"})
        unbekannt = client.put(f"{BASIS}/kan7/gebindefaktoren/3/gibt-es-nicht", json={"faktor1": "5"})

        assert (antwort.status_code, unbekannt.status_code) == (404, 404)
    finally:
        _aufraeumen(fremd)


def test_herkunft_nicht_enger_stellen_solange_faktoren_darueber_liegen(client, mandant):
    artikel = _artikel(mandant, "PSM-A")
    _einheit(client, "kan3", "Kanister", gebindetyp=1, faktorherkunft=3, ergebniseinheit="l")
    client.put(f"{BASIS}/kan3/gebindefaktoren/3/{artikel}", json={"faktor1": "5"})

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


def _position(mandant: str, artikel: str) -> tuple[str, str]:
    kopf, position = str(uuid.uuid4()), str(uuid.uuid4())
    with SessionLocal() as db:
        db.execute(text("INSERT INTO domain_docflow.document_headers (id, tenant_id, doc_type, doc_number) "
                        "VALUES (:id, :t, 'sales_delivery', :nr)"), {"id": kopf, "t": mandant, "nr": f"LS-{kopf[:8]}"})
        db.execute(text("INSERT INTO domain_docflow.document_items (id, tenant_id, header_id, line_number, "
                        "article_number, quantity) VALUES (:id, :t, :k, 1, :a, 4)"),
                   {"id": position, "t": mandant, "k": kopf, "a": artikel})
        db.commit()
    return kopf, position


def test_entwurf_versioniert_gebuchter_beleg_unveraenderlich(client, mandant):
    artikel = _artikel(mandant, "PSM-5L")
    _einheit(client, "kan4", "Kanister", gebindetyp=1, faktorherkunft=3, ergebniseinheit="l")
    client.put(f"{BASIS}/kan4/gebindefaktoren/3/{artikel}", json={"faktor1": "5"})
    kopf, position = _position(mandant, artikel)

    with SessionLocal() as db:
        erste = schreibe_abbild(db, mandant, position, berechne_position(db, mandant, "kan4", D(4), artikel_id=artikel))
        wiederholt = schreibe_abbild(db, mandant, position,
                                     berechne_position(db, mandant, "kan4", D(4), artikel_id=artikel))
        # Verwiegung: im Entwurf aendert sich die Liefermenge -> neue Version, die alte bleibt erhalten
        zweite = schreibe_abbild(db, mandant, position, berechne_position(db, mandant, "kan4", D(5), artikel_id=artikel))
        db.execute(text("UPDATE domain_docflow.document_headers SET status = 'posted' WHERE id = :k"), {"k": kopf})
        db.commit()
    client.put(f"{BASIS}/kan4/gebindefaktoren/3/{artikel}", json={"faktor1": "6"})  # Stamm aendert sich spaeter

    with SessionLocal() as db:
        neu = berechne_position(db, mandant, "kan4", D(5), artikel_id=artikel)
        abbild = abbild_der_position(db, mandant, position)
        versionen = abbild_versionen(db, mandant, position)
        with pytest.raises(BelegGebucht):
            schreibe_abbild(db, mandant, position, neu)
        with pytest.raises(Exception, match="festgeschrieben"):
            db.execute(text("UPDATE domain_docflow.document_items SET gebinde_berechnung = '{}'::jsonb "
                            "WHERE id = :id"), {"id": position})
        db.rollback()
        with pytest.raises(Exception, match="unveraenderlich"):
            db.execute(text("UPDATE domain_docflow.document_item_gebinde_abbilder SET version = 9 "
                            "WHERE position_id = :id"), {"id": position})
        db.rollback()

    assert (erste, wiederholt, zweite) == (1, 1, 2)
    assert [v["abbild"]["ergebnis"] for v in versionen] == ["20.000", "25.000"]
    assert neu.ergebnis == "30.000"
    assert (abbild["ergebnis"], abbild["faktoren"], abbild["herkunft_verwendet"], abbild["version"]) == \
        ("25.000", ["5.000000"], 3, "gebinde-1")


def test_ohne_faktor_im_pfad_kein_abbild(client, mandant):
    artikel = _artikel(mandant, "PSM-Y")
    _einheit(client, "kan5", "Kanister", gebindetyp=1, faktorherkunft=2, ergebniseinheit="l")

    with SessionLocal() as db, pytest.raises(FaktorFehlt):
        berechne_position(db, mandant, "kan5", D(1), artikel_id=artikel)  # Stufe 3 liegt oberhalb von Herkunft 2
