from fastapi.testclient import TestClient

from main import app


client = TestClient(app, raise_server_exceptions=False)
AUTH_HEADERS = {"Authorization": "Bearer dev-token"}


def test_futter_stamm_endpoints_are_reachable():
    einzel = client.get("/api/v1/futter/einzelfuttermittel/EF-001", headers=AUTH_HEADERS)
    misch = client.get("/api/v1/futter/mischfuttermittel/MF-001", headers=AUTH_HEADERS)
    rezept = client.get("/api/v1/futter/rezepte/REZ-001", headers=AUTH_HEADERS)

    assert einzel.status_code == 200, einzel.text
    assert misch.status_code == 200, misch.text
    assert rezept.status_code == 200, rezept.text
    assert einzel.json()["id"] == "EF-001"
    assert misch.json()["id"] == "MF-001"
    assert rezept.json()["id"] == "REZ-001"


def test_schaeden_and_etiketten_endpoints_work():
    versicherungen = client.get("/api/v1/schaeden/versicherungen", headers=AUTH_HEADERS)
    drucker = client.get("/api/v1/etiketten/drucker", headers=AUTH_HEADERS)
    meldung = client.post(
        "/api/v1/schaeden/meldungen",
        json={
            "art": "hagel",
            "datum": "2026-04-07",
            "beschreibung": "Hagelschaden im Feldblock 7",
            "schadenhoehe": 1200,
        },
        headers=AUTH_HEADERS,
    )
    druckauftrag = client.post(
        "/api/v1/etiketten/druckauftrag",
        json={
            "chargen_id": "CH-001",
            "anzahl_etiketten": 2,
            "drucker_id": "DR-001",
        },
        headers=AUTH_HEADERS,
    )

    assert versicherungen.status_code == 200, versicherungen.text
    assert drucker.status_code == 200, drucker.text
    assert meldung.status_code == 201, meldung.text
    assert druckauftrag.status_code == 201, druckauftrag.text
    assert isinstance(versicherungen.json(), list)
    assert isinstance(drucker.json(), list)
    assert meldung.json()["meldungsnummer"].startswith("SM-")
    assert druckauftrag.json()["auftrags_nr"].startswith("ETK-")


def test_strecke_produktion_kasse_and_ustva_endpoints_work():
    strecke = client.get("/api/v1/strecke/streckengeschaefte", headers=AUTH_HEADERS)
    verfuegbarkeit = client.get("/api/v1/produktion/mischfutter/verfuegbarkeit", headers=AUTH_HEADERS)
    rezepte = client.get("/api/v1/produktion/mischfutter/rezepte", headers=AUTH_HEADERS)
    auftrag = client.post(
        "/api/v1/produktion/mischfutter/auftrag",
        json={"rezeptur": "R-001", "menge": 12.5},
        headers=AUTH_HEADERS,
    )
    kasse = client.get("/api/v1/kasse/tagesabschluss/aktuell", headers=AUTH_HEADERS)
    ustva = client.get("/api/v1/finance/vat-return/vorberechnung?zeitraum=2026-03", headers=AUTH_HEADERS)

    assert strecke.status_code == 200, strecke.text
    assert verfuegbarkeit.status_code == 200, verfuegbarkeit.text
    assert rezepte.status_code == 200, rezepte.text
    assert auftrag.status_code == 201, auftrag.text
    assert kasse.status_code == 200, kasse.text
    assert ustva.status_code == 200, ustva.text
    assert isinstance(strecke.json(), list)
    assert isinstance(verfuegbarkeit.json(), list)
    assert isinstance(rezepte.json(), list)
    assert "chargen_id" in auftrag.json()
    assert "umsatz_gesamt" in kasse.json()
    assert "zahllast" in ustva.json()
