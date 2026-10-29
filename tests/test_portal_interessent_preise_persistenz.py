"""Portal-Interessenten und Preisspiegel liegen in der Datenbank, mandantengenau und mit Rollen (20.10.2026).

Vorher: Interessenten (Personendaten) nur im Arbeitsspeicher, Preisspiegel mit erfundenen Getreidekursen aus einer
Saat-Liste, Mandant aus dem frei setzbaren Kopf und keine Rolle — jede angemeldete Person, auch ein Portalkunde, konnte
alle Interessenten lesen und umstufen und Kurse fuer alle Kunden setzen. Ein ersetzter Preis galt am selben Tag weiter
als aktuell (beide wurden angezeigt).

Geprueft gegen eine frische Pruefstand-Datenbank (``TEST_DATABASE_URL``/``DATABASE_URL``).
"""
from __future__ import annotations

import os
import uuid
from datetime import date

import pytest

pytestmark = pytest.mark.integration

DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    os.environ.get("DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe"),
)

HAUS_A = f"portal-a-{uuid.uuid4().hex[:6]}"
HAUS_B = f"portal-b-{uuid.uuid4().hex[:6]}"


@pytest.fixture(scope="module")
def sitzung():
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import sessionmaker

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as conn:
            conn.execute(text("SELECT 1 FROM domain_shared.portal_interessenten LIMIT 0"))
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar oder nicht migriert: {fehler}")
    fabrik = sessionmaker(bind=motor)
    yield fabrik
    with motor.begin() as v:
        for tabelle in ("domain_shared.portal_interessenten", "domain_shared.portal_preise"):
            v.execute(text(f"DELETE FROM {tabelle} WHERE tenant_id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})  # nosec B608


@pytest.fixture()
def db(sitzung):
    s = sitzung()
    yield s
    s.close()


def _interessenten(db, haus=HAUS_A):
    from app.services.portal_interessent_service import PortalInteressentService

    return PortalInteressentService(db, haus)


def _preise(db, haus=HAUS_A):
    from app.services.portal_preisspiegel_service import PortalPreisspiegel

    return PortalPreisspiegel(db, haus)


# ─── Interessenten ───────────────────────────────────────────────────────────

def test_registrieren_speichert_und_normalisiert(db):
    i = _interessenten(db).registrieren("Hans", "Müller", "Hans@Example.de", hauptkulturen=["Raps"])
    neu = _interessenten(db).get(i.interessent_id)
    assert (neu["status"], neu["email"], neu["vollname"], neu["hauptkulturen"]) == (
        "interessent", "hans@example.de", "Hans Müller", ["Raps"])


@pytest.mark.parametrize(("vorname", "email"), [("", "a@b.de"), ("Hans", "keine-email")])
def test_pflichtfelder_und_email_werden_geprueft(db, vorname, email):
    with pytest.raises(ValueError):
        _interessenten(db).registrieren(vorname, "Müller", email)


def test_doppelregistrierung_haelt_die_datenbank(db):
    _interessenten(db).registrieren("Klaus", "Klein", "kk@example.de")
    with pytest.raises(ValueError, match="bereits registriert"):
        _interessenten(db).registrieren("Klaus", "Klein", "KK@example.de")
    # Im anderen Mandanten ist dieselbe E-Mail frei.
    _interessenten(db, HAUS_B).registrieren("Klaus", "Klein", "kk@example.de")


def test_statusmaschine_bis_zum_kunden(db):
    from app.services.portal_interessent_service import InteressentStatus, UngueltigerUebergangFehler

    svc = _interessenten(db)
    i = svc.registrieren("Peter", "Bauer", "pb@hof.de")
    with pytest.raises(UngueltigerUebergangFehler):
        svc.status_wechsel(i.interessent_id, InteressentStatus.KUNDE, kunden_nr="K-1")
    q = svc.status_wechsel(i.interessent_id, InteressentStatus.QUALIFIZIERT, zugewiesen_an="AD-7")
    assert q.qualifiziert_am is not None and q.zugewiesen_an == "AD-7"
    with pytest.raises(ValueError):
        svc.status_wechsel(i.interessent_id, InteressentStatus.KUNDE)
    k = svc.status_wechsel(i.interessent_id, InteressentStatus.KUNDE, kunden_nr="K-9999")
    assert (k.status, k.kunden_nr, k.zugewiesen_an) == (InteressentStatus.KUNDE, "K-9999", "AD-7")
    assert k.konvertiert_am is not None


def test_mandanten_sind_getrennt(db):
    from app.services.portal_interessent_service import InteressentNichtGefundenFehler

    i = _interessenten(db).registrieren("Eva", "Groß", "eva@farm.de")
    with pytest.raises(InteressentNichtGefundenFehler):
        _interessenten(db, HAUS_B).get(i.interessent_id)
    assert all(x["email"] != "eva@farm.de" for x in _interessenten(db, HAUS_B).list_interessenten())


# ─── Preisspiegel ────────────────────────────────────────────────────────────

def _setze(db, preis, haus=HAUS_A, artikel="WEI-001", **mehr):
    from app.services.portal_preisspiegel_service import PreisVariante

    return _preise(db, haus).preis_setzen(
        artikel_id=artikel, artikel_name="Brotweizen", frucht_gruppe="Getreide",
        variante=mehr.pop("variante", PreisVariante.ALTWARE_FREI_LAGER), preis_eur_dt=preis,
        basis_qualitaet="EU 2 / 14% Feuchte", ernte_jahr=2026, gepflegt_von="innendienst-1", **mehr,
    )


def test_ohne_pflege_gibt_es_keine_preise(db):
    leer = f"portal-leer-{uuid.uuid4().hex[:6]}"
    assert _preise(db, leer).preise_alle() == []
    assert _preise(db, leer).preisspiegel_fuer_kunde(["WEI-001"])["preisspiegel"] == []


def test_neuer_preis_loest_den_alten_ab_und_traegt_den_pflegenden(db):
    _setze(db, 21.0, artikel="ABL-1")
    neu = _setze(db, 22.3, artikel="ABL-1", aufschlag_eur_dt=0.5)
    aktuell = [p for p in _preise(db).preise_alle(artikel_ids=["ABL-1"])]
    assert [p["preis_eur_dt"] for p in aktuell] == [22.3]
    assert neu["gepflegt_von"] == "innendienst-1" and neu["gesamtpreis_eur_dt"] == 22.8


def test_preisspiegel_gruppiert_varianten_je_artikel(db):
    from app.services.portal_preisspiegel_service import PreisVariante

    _setze(db, 19.9, artikel="GRP-1", variante=PreisVariante.NEUE_ERNTE_AB_HOF)
    _setze(db, 20.8, artikel="GRP-1", variante=PreisVariante.NEUE_ERNTE_FREI_LAGER)
    spiegel = _preise(db).preisspiegel_fuer_kunde(["GRP-1"])
    (artikel,) = spiegel["preisspiegel"]
    assert set(artikel["varianten"]) == {"neue_ernte_ab_hof", "neue_ernte_frei_lager"}
    assert spiegel["stand"] == date.today().isoformat()
    assert _preise(db, HAUS_B).preisspiegel_fuer_kunde(["GRP-1"])["preisspiegel"] == []
    ohne_auswahl = _preise(db).preisspiegel_fuer_kunde(None)["preisspiegel"]
    assert "GRP-1" in {a["artikel_id"] for a in ohne_auswahl}


@pytest.mark.parametrize("preis", [0.0, -1.0])
def test_preis_muss_positiv_sein(db, preis):
    with pytest.raises(ValueError):
        _setze(db, preis, artikel="NEG-1")


# ─── Wege: Mandant aus dem Token, Rollen ─────────────────────────────────────

@pytest.fixture()
def wege(sitzung):
    """Mini-App mit den beiden Routern; Bearer-Pruefung ersetzt, Rollen je Test."""
    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    from app.api.v1.endpoints import portal_interessent, portal_preisspiegel
    from app.core.database import get_db
    from testgrenze import ersetze_mandant, ersetze_nutzer

    app = FastAPI()
    app.include_router(portal_interessent.router, prefix="/api/v1")
    app.include_router(portal_preisspiegel.router, prefix="/api/v1")

    def _db():
        s = sitzung()
        try:
            yield s
        finally:
            s.close()

    app.dependency_overrides[get_db] = _db
    ersetze_mandant(app, HAUS_A)

    def mit_rollen(*rollen: str) -> TestClient:
        ersetze_nutzer(app, *rollen)
        return TestClient(app)

    return mit_rollen


def test_portalkunde_darf_registrieren_aber_nicht_lesen_umstufen_oder_preise_setzen(wege):
    client = wege("PORTAL_KUNDE")
    angelegt = client.post("/api/v1/portal/interessenten", json={
        "vorname": "Jan", "nachname": "Janssen", "email": f"jan-{uuid.uuid4().hex[:4]}@hof.de"})
    assert angelegt.status_code == 201, angelegt.text
    assert angelegt.json()["tenant_id"] == HAUS_A
    nr = angelegt.json()["interessent_id"]
    assert client.get("/api/v1/portal/interessenten").status_code == 403
    assert client.get(f"/api/v1/portal/interessenten/{nr}").status_code == 403
    assert client.post(f"/api/v1/portal/interessenten/{nr}/status",
                       json={"neuer_status": "qualifiziert"}).status_code == 403
    assert client.post("/api/v1/portal/preisspiegel", json={
        "artikel_id": "X", "artikel_name": "X", "frucht_gruppe": "Getreide", "variante": "altware_ab_hof",
        "preis_eur_dt": 1.0, "basis_qualitaet": "EU 2", "ernte_jahr": 2026}).status_code == 403
    assert client.get("/api/v1/portal/preisspiegel/kunde").status_code == 200


def test_innendienst_stuft_um_und_kurspflege_traegt_den_token_nutzer(wege):
    crm = wege("SALES_BEARBEITEN")
    nr = crm.post("/api/v1/portal/interessenten", json={
        "vorname": "Ina", "nachname": "Ites", "email": f"ina-{uuid.uuid4().hex[:4]}@hof.de"}).json()["interessent_id"]
    assert crm.get("/api/v1/portal/interessenten").status_code == 200
    umgestuft = crm.post(f"/api/v1/portal/interessenten/{nr}/status", json={"neuer_status": "qualifiziert"})
    assert umgestuft.status_code == 200 and umgestuft.json()["status"] == "qualifiziert"
    assert crm.post(f"/api/v1/portal/interessenten/{nr}/status",
                    json={"neuer_status": "erfunden"}).status_code == 422

    handel = wege("KONTRAKT_BEARBEITEN")
    gesetzt = handel.post("/api/v1/portal/preisspiegel", json={
        "artikel_id": "API-1", "artikel_name": "Raps", "frucht_gruppe": "Ölsaaten", "variante": "altware_ab_hof",
        "preis_eur_dt": 45.0, "basis_qualitaet": "00 / 9%", "ernte_jahr": 2026})
    assert gesetzt.status_code == 201, gesetzt.text
    assert gesetzt.json()["gepflegt_von"] == "5f0c2a9e"
