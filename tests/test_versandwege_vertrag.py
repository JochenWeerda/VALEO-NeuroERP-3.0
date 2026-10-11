"""Versandwege: Bestellung, Preisanfrage, Anfrage und Mahnung gehen wirklich hinaus.

Bis zum 08.10.2026 meldeten vier Wege Erfolg, ohne dass etwas versendet wurde:
die Bestellung ("DEV-MODE simuliert", Fax/EDI als ``manuell``), die Preisanfrage
(``suppliers_notified`` ohne Mail), die Anfrage der Maske (``sent: true`` ohne
Speichern) und die Mahnung (``sent`` ohne Versand).

Die Vertraege laufen gegen ``valeo_probe``. SMTP wird an ``smtplib`` ersetzt;
Postfachwahl, Freigaben, Statuswechsel und Mandantentrennung laufen echt.
"""

from __future__ import annotations

import base64
import os
import uuid

import pytest

pytestmark = pytest.mark.integration

DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    os.environ.get("DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe"),
)
os.environ.setdefault("DATABASE_URL", DB_URL)
os.environ.setdefault("API_DEV_TOKEN", "dev-token")

HAUS_A = f"vw-a-{uuid.uuid4().hex[:6]}"
HAUS_B = f"vw-b-{uuid.uuid4().hex[:6]}"
SCHLUESSEL = base64.b64encode(b"k" * 32).decode()
MIT_ADRESSE = str(uuid.uuid4())
OHNE_ADRESSE = str(uuid.uuid4())
FREMDER = str(uuid.uuid4())
KUNDE = f"K-{uuid.uuid4().hex[:8]}"
KUNDE_STUMM = f"K-{uuid.uuid4().hex[:8]}"

EINKAUF = {"sub": "einkaeuferin", "roles": ["EINKAUF_BEARBEITEN"]}
FIBU = {"sub": "buchhalter", "roles": ["FINANCE_ADMIN"]}
LAGER = {"sub": "lagerist", "roles": ["LAGER_BEARBEITEN"]}


@pytest.fixture(autouse=True)
def schluessel(monkeypatch):
    monkeypatch.setenv("VALEO_SECRET_KEY", SCHLUESSEL)


def _aufraeumen(v) -> None:
    from sqlalchemy import text

    h = {"h": [HAUS_A, HAUS_B]}
    for anweisung in (
        "DELETE FROM domain_shared.mailkonten WHERE tenant_id = ANY(:h) AND zugang_von IS NOT NULL",
        "DELETE FROM domain_shared.mailkonten WHERE tenant_id = ANY(:h)",
        "DELETE FROM domain_einkauf.bestellung_kommunikation WHERE tenant_id = ANY(:h)",
        "DELETE FROM domain_einkauf.bestellungen WHERE tenant_id = ANY(:h)",
        "DELETE FROM domain_einkauf.rfq_requests WHERE tenant_id = ANY(:h)",
        "DELETE FROM einkauf_anfragen_positionen WHERE anfrage_id IN "
        "(SELECT id FROM einkauf_anfragen WHERE tenant_id = ANY(:h))",
        "DELETE FROM einkauf_anfragen WHERE tenant_id = ANY(:h)",
        "DELETE FROM domain_erp.dunning_notices WHERE tenant_id = ANY(:h)",
    ):
        v.execute(text(anweisung), h)


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as v:
            v.execute(text("SELECT versand_art FROM domain_erp.dunning_notices LIMIT 0"))
            v.execute(text("SELECT tenant_id FROM einkauf_anfragen LIMIT 0"))
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank/Migration nicht bereit: {fehler}")
    with motor.begin() as v:
        for haus in (HAUS_A, HAUS_B):
            v.execute(text("INSERT INTO domain_shared.tenants (id, name) VALUES (:i, :n) ON CONFLICT (id) DO NOTHING"),
                      {"i": haus, "n": f"Pruefbetrieb {haus}"})
        for kennung, haus, name, adresse in (
            (MIT_ADRESSE, HAUS_A, "Duengerhandel", "auftrag@duenger.example"),
            (OHNE_ADRESSE, HAUS_A, "Saatzucht ohne Mail", None),
            (FREMDER, HAUS_B, "Fremder Lieferant", "fremd@anderswo.example"),
        ):
            v.execute(text("INSERT INTO domain_einkauf.lieferanten (id, tenant_id, lieferantennummer, firmenname, "
                           " email_bestellung) VALUES (:i, :h, :n, :f, :e)"),
                      {"i": kennung, "h": haus, "n": f"LF-{kennung[:6]}", "f": name, "e": adresse})
        for nummer, adresse in ((KUNDE, "hof@landwirt.example"), (KUNDE_STUMM, None)):
            v.execute(text("INSERT INTO domain_crm.customers (id, tenant_id, customer_number, email) "
                           "VALUES (:i, :h, :n, :e)"),
                      {"i": str(uuid.uuid4()), "h": HAUS_A, "n": nummer, "e": adresse})
    yield motor
    with motor.begin() as v:
        _aufraeumen(v)
        v.execute(text("DELETE FROM domain_crm.customers WHERE customer_number = ANY(:k)"),
                  {"k": [KUNDE, KUNDE_STUMM]})
        v.execute(text("DELETE FROM domain_einkauf.lieferanten WHERE id = ANY(CAST(:i AS uuid[]))"),
                  {"i": [MIT_ADRESSE, OHNE_ADRESSE, FREMDER]})
        v.execute(text("DELETE FROM public.outbox_events WHERE tenant_id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})
        v.execute(text("DELETE FROM domain_shared.tenants WHERE id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]})


@pytest.fixture(autouse=True)
def leer(engine):
    with engine.begin() as v:
        _aufraeumen(v)
    yield


@pytest.fixture
def db(engine):
    from app.core.database import SessionLocal

    with SessionLocal() as sitzung:
        yield sitzung


@pytest.fixture
def smtp(monkeypatch):
    """Ersatz an der ``smtplib``-Grenze; ``ablehnen`` laesst den Server einzelne Empfaenger abweisen."""
    import smtplib

    from app.core.config import settings

    class Postausgang:
        gesendet: list[dict] = []
        ablehnen: set[str] = set()

    Postausgang.gesendet, Postausgang.ablehnen = [], set()

    class Server:
        def __init__(self, host, port, timeout=None):
            self.host = host

        def __enter__(self):
            return self

        def __exit__(self, *_a):
            return False

        def ehlo(self):
            return None

        def has_extn(self, name):
            return name == "starttls"

        def starttls(self):
            return None

        def login(self, benutzer, passwort):
            return None

        def send_message(self, nachricht):
            if nachricht["To"] in Postausgang.ablehnen:
                raise smtplib.SMTPRecipientsRefused({nachricht["To"]: (550, b"Postfach unbekannt")})
            Postausgang.gesendet.append({
                "from": nachricht["From"], "to": nachricht["To"], "betreff": nachricht["Subject"],
                "anhaenge": [(teil.get_filename(), teil.get_content_type()) for teil in nachricht.iter_attachments()],
            })
            return {}

    monkeypatch.setattr(smtplib, "SMTP", Server)
    monkeypatch.setattr(settings, "EMAIL_SMTP_SERVER", None)  # kein Plattformkonto
    return Postausgang


def postfach(db, kennung: str, **daten):
    from app.services import mailkonto_service as konto

    grund = {"kennung": kennung, "anbieter": "ionos", "absender_email": f"{kennung}@genossenschaft.example",
             "passwort": "geheim-123", "verwendungen": [kennung]}
    return konto.speichern(db, HAUS_A, {**grund, **daten}, von="chefin")


@pytest.fixture
def client(engine):
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


def kopf(haus: str = HAUS_A) -> dict[str, str]:
    return {"X-Tenant-ID": haus, "Authorization": "Bearer dev-token"}


@pytest.fixture
def als(client):
    from app.auth.deps import get_current_user
    from app.main import app

    def setzen(nutzer):
        app.dependency_overrides[get_current_user] = lambda: nutzer

    yield setzen
    app.dependency_overrides.pop(get_current_user, None)


def wert(engine, sql: str, **parameter):
    from sqlalchemy import text

    with engine.connect() as v:
        return v.execute(text(sql), parameter).first()


# ── Anhang ────────────────────────────────────────────────────────────────────
class TestAnhang:
    def test_pdf_haengt_an_der_nachricht(self, db, smtp):
        from app.services.mail_versand import sende_mail

        postfach(db, "einkauf")
        sende_mail("auftrag@duenger.example", "Bestellung EK-1", "siehe Anhang", db=db, tenant_id=HAUS_A,
                   verwendung="einkauf", nutzer=EINKAUF,
                   anhaenge=[("Bestellung_EK-1.pdf", b"%PDF-1.4 probe", "application/pdf")])
        assert smtp.gesendet[0]["anhaenge"] == [("Bestellung_EK-1.pdf", "application/pdf")]


# ── Bestellung ────────────────────────────────────────────────────────────────
@pytest.fixture
def bestellung(engine):
    from sqlalchemy import text

    kennung, nummer = str(uuid.uuid4()), f"EK-{uuid.uuid4().hex[:8]}"
    with engine.begin() as v:
        v.execute(text("INSERT INTO domain_einkauf.bestellungen (id, tenant_id, bestellnummer, lieferant_id, "
                       " bestelldatum, status) VALUES (:i, :h, :n, :l, CURRENT_DATE, 'entwurf')"),
                  {"i": kennung, "h": HAUS_A, "n": nummer, "l": MIT_ADRESSE})
    return kennung


class TestBestellung:
    WEG = "/api/v1/einkauf/bestellungen/{}/versenden"

    def stand(self, engine, kennung):
        status = wert(engine, "SELECT status FROM domain_einkauf.bestellungen WHERE id = CAST(:i AS uuid)", i=kennung)[0]
        eintraege = wert(engine, "SELECT count(*) FROM domain_einkauf.bestellung_kommunikation "
                                 "WHERE bestellung_id = :i", i=kennung)[0]
        return status, eintraege

    def test_ohne_postfach_bleibt_sie_entwurf(self, engine, client, als, smtp, bestellung):
        als(EINKAUF)
        antwort = client.post(self.WEG.format(bestellung), headers=kopf(), params={"versand_art": "email"})
        assert antwort.status_code == 503, antwort.text
        assert antwort.json()["error"] == "VERSAND_NICHT_MOEGLICH"
        assert smtp.gesendet == []
        assert self.stand(engine, bestellung) == ("entwurf", 0)

    def test_mit_postfach_geht_sie_raus_und_steht_in_der_kommunikation(self, engine, client, als, db, smtp, bestellung):
        postfach(db, "einkauf", absender_name="Einkauf")
        als(EINKAUF)
        antwort = client.post(self.WEG.format(bestellung), headers=kopf(), params={"versand_art": "email"})
        assert antwort.status_code == 200, antwort.text
        assert antwort.json()["versand"]["status"] == "gesendet"
        assert [(m["from"], m["to"]) for m in smtp.gesendet] == [
            ("Einkauf <einkauf@genossenschaft.example>", "auftrag@duenger.example")]
        assert self.stand(engine, bestellung) == ("versandt", 1)
        eintrag = wert(engine, "SELECT kanal, empfaenger, status, versendet_am IS NOT NULL, erfasst_von "
                               "FROM domain_einkauf.bestellung_kommunikation WHERE bestellung_id = :i", i=bestellung)
        assert tuple(eintrag) == ("email", "auftrag@duenger.example", "versendet", True, "einkaeuferin")

    def test_server_lehnt_ab_502(self, engine, client, als, db, smtp, bestellung):
        postfach(db, "einkauf")
        smtp.ablehnen.add("auftrag@duenger.example")
        als(EINKAUF)
        antwort = client.post(self.WEG.format(bestellung), headers=kopf(), params={"versand_art": "email"})
        assert antwort.status_code == 502, antwort.text
        assert self.stand(engine, bestellung) == ("entwurf", 0)

    @pytest.mark.parametrize("art", ["fax", "edi"])
    def test_fax_und_edi_ohne_einrichtung_sind_kein_versand(self, engine, client, als, bestellung, art, monkeypatch):
        from sqlalchemy import text

        from modules.einkauf.services import versand_service

        monkeypatch.setattr(versand_service, "_TWILIO_SID", "")
        with engine.begin() as v:
            v.execute(text("UPDATE domain_einkauf.lieferanten SET fax_bestellung = '+49 491 1234', "
                           "edi_kennung = '4012345000009', edi_format = 'EDIFACT' WHERE id = CAST(:i AS uuid)"),
                      {"i": MIT_ADRESSE})
        als(EINKAUF)
        antwort = client.post(self.WEG.format(bestellung), headers=kopf(), params={"versand_art": art})
        assert antwort.status_code == 503, antwort.text
        assert self.stand(engine, bestellung) == ("entwurf", 0)

    def test_post_ist_bewusst_gewaehlt(self, engine, client, als, smtp, bestellung):
        als(EINKAUF)
        antwort = client.post(self.WEG.format(bestellung), headers=kopf(), params={"versand_art": "post"})
        assert antwort.status_code == 200, antwort.text
        assert antwort.json()["versand"]["status"] == "manuell"
        assert smtp.gesendet == []
        assert self.stand(engine, bestellung) == ("versandt", 1)
        assert wert(engine, "SELECT status, versendet_am FROM domain_einkauf.bestellung_kommunikation "
                            "WHERE bestellung_id = :i", i=bestellung) == ("erfasst", None)


# ── Preisanfrage (RFQ) ────────────────────────────────────────────────────────
@pytest.fixture
def rfq(engine):
    from sqlalchemy import text

    with engine.begin() as v:
        return v.execute(text("INSERT INTO domain_einkauf.rfq_requests (article_id, quantity, notes, tenant_id) "
                              "VALUES ('WEIZEN-A', 100, 'frei Hof', :h) RETURNING id, status"), {"h": HAUS_A}).first()


class TestPreisanfrage:
    WEG = "/api/v1/einkauf/rfq/{}/send"

    def status(self, engine, kennung):
        return wert(engine, "SELECT status FROM domain_einkauf.rfq_requests WHERE id = :i", i=kennung)[0]

    def test_ohne_lieferanten_422(self, engine, client, als, db, smtp, rfq):
        postfach(db, "einkauf")
        als(EINKAUF)
        antwort = client.post(self.WEG.format(rfq[0]), headers=kopf(), json={})
        assert antwort.status_code == 422, antwort.text
        assert self.status(engine, rfq[0]) == rfq[1]

    def test_einer_erreicht_einer_ohne_adresse(self, engine, client, als, db, smtp, rfq):
        postfach(db, "einkauf")
        als(EINKAUF)
        antwort = client.post(self.WEG.format(rfq[0]), headers=kopf(),
                              json={"supplier_ids": [MIT_ADRESSE, OHNE_ADRESSE]})
        assert antwort.status_code == 200, antwort.text
        daten = antwort.json()
        assert (daten["status"], daten["suppliers_notified"]) == ("VERSENDET", [MIT_ADRESSE])
        assert [(v["supplier_id"], v["status"]) for v in daten["versand"]] == [
            (MIT_ADRESSE, "gesendet"), (OHNE_ADRESSE, "fehler")]
        assert [(m["to"], m["betreff"]) for m in smtp.gesendet] == [
            ("auftrag@duenger.example", f"Preisanfrage Nr. {rfq[0]}: WEIZEN-A")]
        assert self.status(engine, rfq[0]) == "VERSENDET"

    def test_keiner_erreicht_502_und_status_bleibt(self, engine, client, als, db, smtp, rfq):
        postfach(db, "einkauf")
        als(EINKAUF)
        antwort = client.post(self.WEG.format(rfq[0]), headers=kopf(), json={"supplier_ids": [OHNE_ADRESSE]})
        assert antwort.status_code == 502, antwort.text
        assert "Saatzucht ohne Mail" in antwort.json()["detail"]
        assert self.status(engine, rfq[0]) == rfq[1]

    def test_ohne_postfach_503(self, engine, client, als, smtp, rfq):
        als(EINKAUF)
        antwort = client.post(self.WEG.format(rfq[0]), headers=kopf(), json={"supplier_ids": [MIT_ADRESSE]})
        assert antwort.status_code == 503, antwort.text
        assert self.status(engine, rfq[0]) == rfq[1]

    def test_lieferant_eines_anderen_mandanten_ist_unbekannt(self, engine, client, als, db, smtp, rfq):
        postfach(db, "einkauf")
        als(EINKAUF)
        antwort = client.post(self.WEG.format(rfq[0]), headers=kopf(), json={"supplier_ids": [FREMDER]})
        assert antwort.status_code == 422, antwort.text
        assert smtp.gesendet == []


# ── Anfrage (BANF) ────────────────────────────────────────────────────────────
@pytest.fixture
def anfrage(engine):
    from sqlalchemy import text

    kennung, nummer = str(uuid.uuid4()), f"ANF-{uuid.uuid4().hex[:8]}"
    with engine.begin() as v:
        v.execute(text("INSERT INTO einkauf_anfragen (id, tenant_id, anfrage_nummer, anforderer, artikel, menge, "
                       " einheit, status) VALUES (:i, :h, :n, 'Lager Nord', 'Kalkammonsalpeter', 24, 't', 'FREIGEGEBEN')"),
                  {"i": kennung, "h": HAUS_A, "n": nummer})
    return kennung, nummer


class TestAnfrage:
    WEG = "/api/v1/einkauf/anfragen/{}/send"

    def status(self, engine, kennung):
        return wert(engine, "SELECT status FROM einkauf_anfragen WHERE id = :i", i=kennung)[0]

    def test_mail_an_den_lieferanten_dann_angebotsphase(self, engine, client, als, db, smtp, anfrage):
        postfach(db, "einkauf")
        als(EINKAUF)
        antwort = client.post(self.WEG.format(anfrage[0]), headers=kopf(),
                              json={"supplierIds": [MIT_ADRESSE], "method": "email"})
        assert antwort.status_code == 200, antwort.text
        daten = antwort.json()
        assert (daten["status"], daten["sent"], daten["count"]) == ("ANGEBOTSPHASE", True, 1)
        assert [(m["to"], m["betreff"]) for m in smtp.gesendet] == [
            ("auftrag@duenger.example", f"Anfrage {anfrage[1]}")]
        assert self.status(engine, anfrage[0]) == "ANGEBOTSPHASE"

    def test_ohne_postfach_wird_nichts_behauptet(self, engine, client, als, smtp, anfrage):
        als(EINKAUF)
        antwort = client.post(self.WEG.format(anfrage[0]), headers=kopf(),
                              json={"supplierIds": [MIT_ADRESSE], "method": "email"})
        assert antwort.status_code == 503, antwort.text
        assert self.status(engine, anfrage[0]) == "FREIGEGEBEN"

    def test_portal_gibt_es_nicht(self, engine, client, als, db, smtp, anfrage):
        postfach(db, "einkauf")
        als(EINKAUF)
        antwort = client.post(self.WEG.format(anfrage[0]), headers=kopf(),
                              json={"supplierIds": [MIT_ADRESSE], "method": "portal"})
        assert antwort.status_code == 422, antwort.text
        assert (smtp.gesendet, self.status(engine, anfrage[0])) == ([], "FREIGEGEBEN")

    def test_anderer_mandant_sieht_und_sendet_sie_nicht(self, engine, client, als, db, smtp, anfrage):
        from app.core.exceptions import EntityNotFoundError
        from app.services.einkauf_compat_service import EinkaufCompatService

        postfach(db, "einkauf")
        als(EINKAUF)
        antwort = client.post(self.WEG.format(anfrage[0]), headers=kopf(HAUS_B),
                              json={"supplierIds": [FREMDER], "method": "email"})
        assert antwort.status_code == 404, antwort.text
        assert smtp.gesendet == []
        assert EinkaufCompatService(db, HAUS_A).get_anfrage(anfrage[0])["id"] == anfrage[0]
        with pytest.raises(EntityNotFoundError):
            EinkaufCompatService(db, HAUS_B).get_anfrage(anfrage[0])


# ── Mahnung ───────────────────────────────────────────────────────────────────
def mahnung(engine, debitor: str = KUNDE, status: str = "created") -> str:
    from sqlalchemy import text

    kennung = str(uuid.uuid4())
    with engine.begin() as v:
        v.execute(text("INSERT INTO domain_erp.dunning_notices (id, tenant_id, debtor_id, dunning_level, dunning_date, "
                       " open_amount, dunning_fee, interest, total_amount, payment_deadline, status) "
                       "VALUES (:i, :h, :d, 1, CURRENT_DATE, 1250, 5, 3.70, 1258.70, CURRENT_DATE + 10, :s)"),
                  {"i": kennung, "h": HAUS_A, "d": debitor, "s": status})
    return kennung


class TestMahnung:
    WEG = "/api/v1/finance/dunning/{}/send"

    @pytest.fixture(autouse=True)
    def archiv(self, monkeypatch):
        """Archivierte Inhalte lassen sich nicht loeschen (``guard_archived_content``) und blieben
        im geteilten Pruefstand liegen. Der Eintrag wird deshalb festgehalten statt geschrieben."""
        from app.api.v1.endpoints import dunning as modul

        eintraege: list[str] = []
        monkeypatch.setattr(modul, "register_artifact",
                            lambda _db, _haus, nummer, *_a, **k: eintraege.append(k["content"].decode()) or "art-1")
        return eintraege

    def stand(self, engine, kennung):
        return tuple(wert(engine, "SELECT status, versand_art, empfaenger FROM domain_erp.dunning_notices "
                                  "WHERE id = :i", i=kennung))

    def test_per_mail_ueber_das_fibu_postfach(self, engine, client, als, db, smtp, archiv):
        postfach(db, "fibu", rollen=["FINANCE_ADMIN"], absender_name="Buchhaltung")
        kennung = mahnung(engine)
        als(FIBU)
        antwort = client.put(self.WEG.format(kennung), headers=kopf())
        assert antwort.status_code == 200, antwort.text
        assert antwort.json()["status"] == "sent"
        assert [(m["from"], m["to"]) for m in smtp.gesendet] == [
            ("Buchhaltung <fibu@genossenschaft.example>", "hof@landwirt.example")]
        assert self.stand(engine, kennung) == ("sent", "email", "hof@landwirt.example")
        assert len(archiv) == 1 and archiv[0].endswith("|email")

    def test_die_liste_nennt_kennung_und_versandweg(self, engine, client, als, db, smtp):
        """Ohne Kennung liess sich aus der Liste "Erzeugte Mahnungen" nichts versenden."""
        postfach(db, "fibu")
        offen, raus = mahnung(engine), mahnung(engine)
        als(FIBU)
        assert client.put(self.WEG.format(raus), headers=kopf()).status_code == 200
        liste = client.get("/api/v1/finance/mahnlauf/notices", headers=kopf()).json()["items"]
        nach_kennung = {m["id"]: (m["status"], m["versand_art"], m["empfaenger"]) for m in liste}
        assert nach_kennung == {offen: ("created", None, None), raus: ("sent", "email", "hof@landwirt.example")}

    def test_ohne_adresse_422_und_unversendet(self, engine, client, als, db, smtp, archiv):
        postfach(db, "fibu")
        kennung = mahnung(engine, KUNDE_STUMM)
        als(FIBU)
        antwort = client.put(self.WEG.format(kennung), headers=kopf())
        assert antwort.status_code == 422, antwort.text
        assert "Post" in antwort.json()["detail"]
        assert self.stand(engine, kennung) == ("created", None, None)
        assert archiv == []

    def test_post_wird_festgehalten_ohne_mail(self, engine, client, als, smtp):
        kennung = mahnung(engine, KUNDE_STUMM)
        als(FIBU)
        antwort = client.put(self.WEG.format(kennung), headers=kopf(), params={"versand_art": "post"})
        assert antwort.status_code == 200, antwort.text
        assert smtp.gesendet == []
        assert self.stand(engine, kennung) == ("sent", "post", None)

    def test_ohne_postfach_503(self, engine, client, als, smtp):
        kennung = mahnung(engine)
        als(FIBU)
        assert client.put(self.WEG.format(kennung), headers=kopf()).status_code == 503
        assert self.stand(engine, kennung) == ("created", None, None)

    def test_ohne_freigabe_403(self, engine, client, als, db, smtp):
        postfach(db, "fibu", rollen=["FINANCE_ADMIN"])
        kennung = mahnung(engine)
        als(LAGER)
        assert client.put(self.WEG.format(kennung), headers=kopf()).status_code == 403
        assert (smtp.gesendet, self.stand(engine, kennung)) == ([], ("created", None, None))

    def test_server_lehnt_ab_502(self, engine, client, als, db, smtp):
        postfach(db, "fibu")
        smtp.ablehnen.add("hof@landwirt.example")
        kennung = mahnung(engine)
        als(FIBU)
        assert client.put(self.WEG.format(kennung), headers=kopf()).status_code == 502
        assert self.stand(engine, kennung) == ("created", None, None)

    def test_bezahlte_mahnung_409(self, engine, client, als, db, smtp):
        postfach(db, "fibu")
        kennung = mahnung(engine, status="paid")
        als(FIBU)
        assert client.put(self.WEG.format(kennung), headers=kopf()).status_code == 409
        assert smtp.gesendet == []

    def test_anderer_mandant_404(self, engine, client, als, smtp):
        kennung = mahnung(engine)
        als(FIBU)
        assert client.put(self.WEG.format(kennung), headers=kopf(HAUS_B),
                          params={"versand_art": "post"}).status_code == 404
        assert self.stand(engine, kennung) == ("created", None, None)

    def test_unbekannter_versandweg_422(self, engine, client, als):
        kennung = mahnung(engine)
        als(FIBU)
        assert client.put(self.WEG.format(kennung), headers=kopf(), params={"versand_art": "fax"}).status_code == 422


class TestSchema:
    def test_anfragenummer_ist_je_mandant_eindeutig(self, engine, anfrage):
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        zeile = ("INSERT INTO einkauf_anfragen (id, tenant_id, anfrage_nummer, anforderer) "
                 "VALUES (:i, :h, :n, 'Lager Sued')")
        with engine.begin() as v:  # derselbe Nummernkreis in einem anderen Haus
            v.execute(text(zeile), {"i": str(uuid.uuid4()), "h": HAUS_B, "n": anfrage[1]})
        with pytest.raises(IntegrityError), engine.begin() as v:
            v.execute(text(zeile), {"i": str(uuid.uuid4()), "h": HAUS_A, "n": anfrage[1]})

    def test_versandweg_der_mahnung_ist_geprueft(self, engine):
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        kennung = mahnung(engine)
        with pytest.raises(IntegrityError), engine.begin() as v:
            v.execute(text("UPDATE domain_erp.dunning_notices SET versand_art = 'fax' WHERE id = :i"), {"i": kennung})
