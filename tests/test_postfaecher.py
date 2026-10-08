"""Postfaecher je Mandant: eigener Maildienst, Freigaben, verschluesselte Zugaenge.

Bis zum 08.10.2026 gab es fuer ausgehende E-Mails nur das Plattformkonto aus den
Umgebungsvariablen; das IMAP-Passwort des CRM-Connectors lag im Klartext in
``tenants.settings``, und dessen Admin-Wege prueften keine Rolle.

Die Vertraege laufen gegen ``valeo_probe``. SMTP und Google werden an ihren
Grenzen (``smtplib``, ``httpx``) ersetzt; Postfachwahl, Freigaben, Verschluesselung
und XOAUTH2 laufen echt.
"""

from __future__ import annotations

import base64
import json
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

HAUS_A = f"pf-a-{uuid.uuid4().hex[:6]}"
HAUS_B = f"pf-b-{uuid.uuid4().hex[:6]}"
SCHLUESSEL = base64.b64encode(b"k" * 32).decode()
LIEFERANT = str(uuid.uuid4())


@pytest.fixture(autouse=True)
def schluessel(monkeypatch):
    monkeypatch.setenv("VALEO_SECRET_KEY", SCHLUESSEL)


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as v:
            v.execute(text("SELECT 1 FROM domain_shared.mailkonten LIMIT 0"))
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank/Migration nicht bereit: {fehler}")
    with motor.begin() as v:
        for haus in (HAUS_A, HAUS_B):
            v.execute(text("INSERT INTO domain_shared.tenants (id, name) VALUES (:i, :n) ON CONFLICT (id) DO NOTHING"),
                      {"i": haus, "n": f"Pruefbetrieb {haus}"})
        v.execute(text("INSERT INTO domain_einkauf.lieferanten (id, tenant_id, lieferantennummer, firmenname, "
                       " email_bestellung) VALUES (:i, :h, :n, 'Duengerhandel', 'auftrag@duenger.example')"),
                  {"i": LIEFERANT, "h": HAUS_A, "n": f"LF-{LIEFERANT[:6]}"})
    yield motor
    with motor.begin() as v:
        h = {"h": [HAUS_A, HAUS_B]}
        v.execute(text("DELETE FROM domain_shared.mailkonten WHERE tenant_id = ANY(:h) AND zugang_von IS NOT NULL"), h)
        v.execute(text("DELETE FROM domain_shared.mailkonten WHERE tenant_id = ANY(:h)"), h)
        v.execute(text("DELETE FROM domain_einkauf.bestellung_kommunikation WHERE tenant_id = ANY(:h)"), h)
        v.execute(text("DELETE FROM domain_einkauf.bestellungen WHERE tenant_id = ANY(:h)"), h)
        v.execute(text("DELETE FROM domain_einkauf.lieferanten WHERE id = :i"), {"i": LIEFERANT})
        v.execute(text("DELETE FROM public.outbox_events WHERE tenant_id = ANY(:h)"), h)
        v.execute(text("DELETE FROM domain_shared.tenants WHERE id = ANY(:h)"), h)


@pytest.fixture(autouse=True)
def leer(engine):
    from sqlalchemy import text

    with engine.begin() as v:
        h = {"h": [HAUS_A, HAUS_B]}
        v.execute(text("DELETE FROM domain_shared.mailkonten WHERE tenant_id = ANY(:h) AND zugang_von IS NOT NULL"), h)
        v.execute(text("DELETE FROM domain_shared.mailkonten WHERE tenant_id = ANY(:h)"), h)
    yield


@pytest.fixture
def db(engine):
    from app.core.database import SessionLocal

    with SessionLocal() as sitzung:
        yield sitzung


# ── Ersatzserver ──────────────────────────────────────────────────────────────
class _Postausgang:
    def __init__(self):
        self.gesendet: list[dict] = []
        self.anmeldungen: list[tuple] = []


@pytest.fixture
def smtp(monkeypatch):
    import smtplib

    from app.core.config import settings

    ausgang = _Postausgang()

    class Server:
        def __init__(self, host, port, timeout=None):
            self.host, self.port = host, port

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
            ausgang.anmeldungen.append(("login", self.host, benutzer, passwort))

        def auth(self, verfahren, objekt):
            ausgang.anmeldungen.append((verfahren, self.host, objekt()))

        def send_message(self, nachricht):
            ausgang.gesendet.append({"host": self.host, "from": nachricht["From"], "to": nachricht["To"]})
            return {}

    monkeypatch.setattr(smtplib, "SMTP", Server)
    monkeypatch.setattr(settings, "EMAIL_SMTP_SERVER", None)  # kein Plattformkonto
    return ausgang


ADMIN = {"sub": "chefin", "roles": ["admin"]}
FIBU = {"sub": "buchhalter", "roles": ["FINANCE_ADMIN"]}
LAGER = {"sub": "lagerist", "roles": ["LAGER_BEARBEITEN"]}


def anlegen(db, haus=HAUS_A, **daten):
    from app.services import mailkonto_service as konto

    grund = {"anbieter": "ionos", "absender_email": f"{daten.get('kennung', 'info')}@genossenschaft.example",
             "passwort": "geheim-123"}
    return konto.speichern(db, haus, {**grund, **daten}, von="chefin")


# ── Verschluesselung ──────────────────────────────────────────────────────────
class TestGeheimnis:
    def test_an_mandant_und_zweck_gebunden(self):
        from app.core import geheimnis

        chiffrat = geheimnis.verschluesseln("pw", tenant_id=HAUS_A, zweck="mailkonto")
        assert chiffrat.startswith("v1:") and "pw" not in chiffrat
        assert geheimnis.entschluesseln(chiffrat, tenant_id=HAUS_A, zweck="mailkonto") == "pw"
        with pytest.raises(geheimnis.GeheimnisUngueltig):
            geheimnis.entschluesseln(chiffrat, tenant_id=HAUS_B, zweck="mailkonto")
        with pytest.raises(geheimnis.GeheimnisUngueltig):
            geheimnis.entschluesseln(chiffrat, tenant_id=HAUS_A, zweck="imap")

    def test_ohne_schluessel_wird_nichts_gespeichert(self, db, monkeypatch):
        from app.core.geheimnis import GeheimnisNichtEingerichtet

        monkeypatch.delenv("VALEO_SECRET_KEY")
        with pytest.raises(GeheimnisNichtEingerichtet):
            anlegen(db, kennung="info")


# ── Einrichten ────────────────────────────────────────────────────────────────
class TestEinrichten:
    def test_ionos_vorlage_und_verschluesseltes_passwort(self, engine, db):
        from sqlalchemy import text

        pf = anlegen(db, kennung="info")
        assert (pf["smtp_host"], pf["smtp_port"], pf["sicherheit"]) == ("smtp.ionos.de", 587, "starttls")
        assert pf["benutzer"] == "info@genossenschaft.example"
        assert pf["hat_geheimnis"] is True and "passwort" not in pf
        with engine.connect() as v:
            gespeichert = v.execute(text("SELECT geheimnis FROM domain_shared.mailkonten WHERE id = :i"),
                                    {"i": pf["id"]}).scalar()
        assert gespeichert.startswith("v1:") and "geheim-123" not in gespeichert

    def test_die_datenbank_verbietet_klartext(self, engine, db):
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        pf = anlegen(db, kennung="info")
        with pytest.raises(IntegrityError), engine.begin() as v:
            v.execute(text("UPDATE domain_shared.mailkonten SET geheimnis = 'klartext' WHERE id = :i"), {"i": pf["id"]})

    def test_leeres_passwort_laesst_das_bisherige_stehen(self, db, smtp):
        from app.services import mailkonto_service as konto

        pf = anlegen(db, kennung="info")
        konto.speichern(db, HAUS_A, {"kennung": "info", "anbieter": "ionos", "absender_email": pf["absender_email"],
                                     "absender_name": "Raiffeisen Info"}, postfach_id=pf["id"])
        z = konto.smtp_zugang(db, HAUS_A, postfach_id=pf["id"], nutzer=ADMIN)
        assert z.passwort == "geheim-123"

    def test_kennung_je_mandant_eindeutig(self, db):
        from app.services.mailkonto_service import MailkontoFehler

        anlegen(db, kennung="dispo")
        anlegen(db, haus=HAUS_B, kennung="dispo")
        with pytest.raises(MailkontoFehler, match="schon vergeben"):
            anlegen(db, kennung="dispo")

    def test_nur_ein_standard(self, db):
        from app.services import mailkonto_service as konto

        a = anlegen(db, kennung="zentrale", ist_standard=True)
        b = anlegen(db, kennung="info", ist_standard=True)
        standard = {p["kennung"]: p["ist_standard"] for p in konto.liste(db, HAUS_A)}
        assert standard == {"zentrale": False, "info": True}
        assert a["id"] != b["id"]

    def test_alias_braucht_ein_echtes_postfach(self, db):
        from app.services.mailkonto_service import MailkontoFehler

        haupt = anlegen(db, kennung="zentrale")
        alias = anlegen(db, kennung="info", anbieter="alias", zugang_von=haupt["id"], passwort=None)
        with pytest.raises(MailkontoFehler, match="Alias"):
            anlegen(db, kennung="presse", anbieter="alias", zugang_von=alias["id"], passwort=None)
        with pytest.raises(MailkontoFehler, match="Aliase info"):
            from app.services import mailkonto_service as konto

            konto.entfernen(db, HAUS_A, haupt["id"])


# ── Zugriff und Wahl ──────────────────────────────────────────────────────────
class TestZugriff:
    def test_rollen_freigabe(self, db):
        from app.services import mailkonto_service as konto

        anlegen(db, kennung="fibu", rollen=["FINANCE_ADMIN"], verwendungen=["fibu"])
        assert konto.postfach_waehlen(db, HAUS_A, verwendung="fibu", nutzer=FIBU)["kennung"] == "fibu"
        with pytest.raises(konto.KeinZugriff):
            konto.postfach_waehlen(db, HAUS_A, verwendung="fibu", nutzer=LAGER)
        assert konto.postfach_waehlen(db, HAUS_A, verwendung="fibu", nutzer=ADMIN)["kennung"] == "fibu"

    def test_persoenliches_postfach_nur_fuer_den_inhaber(self, db):
        from app.services import mailkonto_service as konto

        pf = anlegen(db, kennung="m.meier", persoenlich_fuer="lagerist")
        assert konto.postfach_waehlen(db, HAUS_A, postfach_id=pf["id"], nutzer=LAGER)["id"] == pf["id"]
        with pytest.raises(konto.KeinZugriff):
            konto.postfach_waehlen(db, HAUS_A, postfach_id=pf["id"], nutzer=FIBU)

    def test_verwendung_vor_standard(self, db):
        from app.services import mailkonto_service as konto

        anlegen(db, kennung="zentrale", ist_standard=True)
        anlegen(db, kennung="einkauf", verwendungen=["einkauf"])
        assert konto.postfach_waehlen(db, HAUS_A, verwendung="einkauf", nutzer=LAGER)["kennung"] == "einkauf"
        assert konto.postfach_waehlen(db, HAUS_A, verwendung="dispo", nutzer=LAGER)["kennung"] == "zentrale"

    def test_absenderwahl_zeigt_nur_freigegebene(self, db):
        from app.services import mailkonto_service as konto

        anlegen(db, kennung="info")
        anlegen(db, kennung="fibu", rollen=["FINANCE_ADMIN"])
        assert [p["kennung"] for p in konto.verfuegbar(db, HAUS_A, LAGER)] == ["fibu", "info"][1:]
        assert sorted(p["kennung"] for p in konto.verfuegbar(db, HAUS_A, FIBU)) == ["fibu", "info"]

    def test_fremder_mandant_sieht_nichts(self, db):
        from app.services import mailkonto_service as konto

        pf = anlegen(db, kennung="info")
        assert konto.liste(db, HAUS_B) == []
        with pytest.raises(konto.MailkontoFehler):
            konto.postfach_waehlen(db, HAUS_B, postfach_id=pf["id"], nutzer=ADMIN)


# ── Versand ───────────────────────────────────────────────────────────────────
class TestVersand:
    def test_ionos_postfach_meldet_sich_an_und_sendet_als_es_selbst(self, db, smtp):
        from app.services.mail_versand import sende_mail

        anlegen(db, kennung="dispo", verwendungen=["dispo"], absender_name="Disposition")
        sende_mail("fahrer@spedition.example", "Tour 12", "Abfahrt 6 Uhr", db=db, tenant_id=HAUS_A,
                   verwendung="dispo", nutzer=LAGER)
        assert smtp.anmeldungen == [("login", "smtp.ionos.de", "dispo@genossenschaft.example", "geheim-123")]
        assert smtp.gesendet[0]["from"] == "Disposition <dispo@genossenschaft.example>"

    def test_alias_nutzt_die_anmeldung_und_den_eigenen_absender(self, db, smtp):
        from app.services.mail_versand import sende_mail

        haupt = anlegen(db, kennung="zentrale")
        anlegen(db, kennung="info", anbieter="alias", zugang_von=haupt["id"], passwort=None, verwendungen=["newsletter"])
        sende_mail("kunde@example.org", "Info", "x", db=db, tenant_id=HAUS_A, verwendung="newsletter", nutzer=LAGER)
        assert smtp.anmeldungen[0][2:] == ("zentrale@genossenschaft.example", "geheim-123")
        assert smtp.gesendet[0]["from"] == "info@genossenschaft.example"

    def test_ohne_freigabe_wird_nicht_gesendet(self, db, smtp):
        from app.services.mail_versand import MailVersandVerweigert, sende_mail

        anlegen(db, kennung="fibu", rollen=["FINANCE_ADMIN"], verwendungen=["fibu"])
        with pytest.raises(MailVersandVerweigert):
            sende_mail("x@y.example", "Mahnung", "x", db=db, tenant_id=HAUS_A, verwendung="fibu", nutzer=LAGER)
        assert smtp.gesendet == []

    def test_testmail_setzt_den_pruefstatus(self, db, smtp):
        from app.services import mailkonto_service as konto

        pf = anlegen(db, kennung="info")
        ergebnis = konto.pruefen(db, HAUS_A, pf["id"], None, nutzer=ADMIN)
        assert (ergebnis["status"], ergebnis["testmail_an"]) == ("geprueft", "info@genossenschaft.example")


# ── Google ────────────────────────────────────────────────────────────────────
@pytest.fixture
def google(monkeypatch):
    import httpx

    monkeypatch.setenv("GOOGLE_OAUTH_CLIENT_ID", "client-123")
    monkeypatch.setenv("GOOGLE_OAUTH_CLIENT_SECRET", "secret-456")
    monkeypatch.setenv("GOOGLE_OAUTH_REDIRECT_URI", "https://erp.example/admin/postfaecher/anmeldung-rueckruf")
    monkeypatch.setenv("MICROSOFT_OAUTH_CLIENT_ID", "ms-client")
    monkeypatch.setenv("MICROSOFT_OAUTH_CLIENT_SECRET", "ms-secret")
    monkeypatch.setenv("MICROSOFT_OAUTH_REDIRECT_URI", "https://erp.example/admin/postfaecher/anmeldung-rueckruf")
    anfragen: list[dict] = []
    nutzlast = base64.urlsafe_b64encode(json.dumps({"email": "zentrale@gmail.example"}).encode()).decode().rstrip("=")

    class Antwort:
        def __init__(self, daten):
            self.status_code, self._daten, self.text = 200, daten, json.dumps(daten)

        def json(self):
            return self._daten

    def post(url, data=None, timeout=None, json=None, headers=None):
        anfragen.append({"url": url, "data": data, "json": json, "headers": headers})
        if "graph.microsoft.com" in url:
            antwort = Antwort({})
            antwort.status_code = 202
            return antwort
        if data["grant_type"] == "authorization_code":
            return Antwort({"refresh_token": "refresh-xyz", "access_token": "a1", "id_token": f"h.{nutzlast}.s"})
        return Antwort({"access_token": "frisch-789"})

    monkeypatch.setattr(httpx, "post", post)
    return anfragen


class TestGoogle:
    def test_anmeldung_bis_zum_versand(self, engine, db, smtp, google):
        from urllib.parse import parse_qs, urlparse

        from sqlalchemy import text

        from app.services import mailkonto_service as konto
        from app.services.mail_versand import sende_mail

        pf = anlegen(db, kennung="zentrale", anbieter="google", anmeldung="oauth2", passwort=None,
                     absender_email="zentrale@gmail.example", ist_standard=True)
        url = konto.anmeldung_starten(db, HAUS_A, pf["id"])["url"]
        parameter = parse_qs(urlparse(url).query)
        assert parameter["client_id"] == ["client-123"] and parameter["access_type"] == ["offline"]
        konto.google_anmeldung_abschliessen(db, HAUS_A, "code-1", parameter["state"][0], von="chefin")
        with engine.connect() as v:
            gespeichert = v.execute(text("SELECT geheimnis FROM domain_shared.mailkonten WHERE id = :i"),
                                    {"i": pf["id"]}).scalar()
        assert gespeichert.startswith("v1:") and "refresh-xyz" not in gespeichert

        sende_mail("kunde@example.org", "Hallo", "x", db=db, tenant_id=HAUS_A, nutzer=LAGER)
        verfahren, host, anmeldung = smtp.anmeldungen[0]
        assert (verfahren, host) == ("XOAUTH2", "smtp.gmail.com")
        assert anmeldung == "user=zentrale@gmail.example\x01auth=Bearer frisch-789\x01\x01"

    def test_state_eines_anderen_mandanten_wird_abgelehnt(self, db, google):
        from urllib.parse import parse_qs, urlparse

        from app.services import mailkonto_service as konto

        pf = anlegen(db, kennung="zentrale", anbieter="google", anmeldung="oauth2", passwort=None,
                     absender_email="zentrale@gmail.example")
        state = parse_qs(urlparse(konto.google_anmeldung_starten(db, HAUS_A, pf["id"])["url"]).query)["state"][0]
        with pytest.raises(konto.MailkontoFehler, match="anderen Mandanten"):
            konto.google_anmeldung_abschliessen(db, HAUS_B, "code-1", state)
        with pytest.raises(konto.MailkontoFehler, match="Signatur"):
            konto.google_anmeldung_abschliessen(db, HAUS_A, "code-1", state[:-2] + "00")


class TestMicrosoft:
    def test_nur_mit_anmeldung_ueber_microsoft(self, engine, db):
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        from app.services.mailkonto_service import MailkontoFehler

        with pytest.raises(MailkontoFehler, match="Microsoft 365 nur"):
            anlegen(db, kennung="zentrale", anbieter="microsoft", anmeldung="passwort")
        pf = anlegen(db, kennung="zentrale", anbieter="microsoft", passwort=None,
                     absender_email="zentrale@haus.onmicrosoft.example")
        assert pf["anmeldung"] == "oauth2"
        with pytest.raises(IntegrityError), engine.begin() as v:
            v.execute(text("UPDATE domain_shared.mailkonten SET anmeldung = 'passwort' WHERE id = :i"), {"i": pf["id"]})

    def test_anmeldung_bis_zum_versand_ueber_graph(self, engine, db, google, monkeypatch):
        from urllib.parse import parse_qs, urlparse

        from sqlalchemy import text

        from app.services import mailkonto_service as konto
        from app.services.mail_versand import sende_mail

        monkeypatch.setenv("MICROSOFT_OAUTH_TENANT", "contoso-id")
        pf = anlegen(db, kennung="zentrale", anbieter="microsoft", passwort=None,
                     absender_email="zentrale@gmail.example", ist_standard=True, absender_name="Zentrale")
        url = konto.anmeldung_starten(db, HAUS_A, pf["id"])["url"]
        assert url.startswith("https://login.microsoftonline.com/contoso-id/oauth2/v2.0/authorize?")
        parameter = parse_qs(urlparse(url).query)
        assert "Mail.Send" in parameter["scope"][0] and "offline_access" in parameter["scope"][0]
        konto.anmeldung_abschliessen(db, HAUS_A, "code-ms", parameter["state"][0], von="chefin")
        with engine.connect() as v:
            gespeichert = v.execute(text("SELECT geheimnis FROM domain_shared.mailkonten WHERE id = :i"),
                                    {"i": pf["id"]}).scalar()
        assert gespeichert.startswith("v1:") and "refresh-xyz" not in gespeichert
        assert google[0]["url"] == "https://login.microsoftonline.com/contoso-id/oauth2/v2.0/token"

        sende_mail("kunde@example.org", "Hallo", "Text", db=db, tenant_id=HAUS_A, nutzer=LAGER)
        graph = google[-1]
        assert graph["url"] == "https://graph.microsoft.com/v1.0/me/sendMail"
        assert graph["headers"] == {"Authorization": "Bearer frisch-789"}
        assert graph["json"]["saveToSentItems"] is True
        assert graph["json"]["message"]["toRecipients"] == [{"emailAddress": {"address": "kunde@example.org"}}]
        assert "from" not in graph["json"]["message"]  # angemeldet als die Absenderadresse

    def test_alias_sendet_ueber_graph_mit_eigenem_absender(self, db, google):
        from urllib.parse import parse_qs, urlparse

        from app.services import mailkonto_service as konto
        from app.services.mail_versand import sende_mail

        haupt = anlegen(db, kennung="zentrale", anbieter="microsoft", passwort=None,
                        absender_email="zentrale@gmail.example")
        state = parse_qs(urlparse(konto.anmeldung_starten(db, HAUS_A, haupt["id"])["url"]).query)["state"][0]
        konto.anmeldung_abschliessen(db, HAUS_A, "code-ms", state)
        anlegen(db, kennung="fibu", anbieter="alias", zugang_von=haupt["id"], passwort=None,
                absender_email="fibu@haus.example", absender_name="Buchhaltung", verwendungen=["fibu"])
        sende_mail("kunde@example.org", "Mahnung", "x", db=db, tenant_id=HAUS_A, verwendung="fibu", nutzer=LAGER)
        assert google[-1]["json"]["message"]["from"] == {
            "emailAddress": {"address": "fibu@haus.example", "name": "Buchhaltung"}}

    def test_graph_ablehnung_ist_kein_erfolg(self, db, google, monkeypatch):
        import httpx
        from urllib.parse import parse_qs, urlparse

        from app.services import mailkonto_service as konto
        from app.services.mail_versand import MailVersandFehler, sende_mail

        pf = anlegen(db, kennung="zentrale", anbieter="microsoft", passwort=None,
                     absender_email="zentrale@gmail.example", ist_standard=True)
        state = parse_qs(urlparse(konto.anmeldung_starten(db, HAUS_A, pf["id"])["url"]).query)["state"][0]
        konto.anmeldung_abschliessen(db, HAUS_A, "code-ms", state)
        echt = httpx.post

        class Abgelehnt:
            status_code = 403
            text = "ErrorSendAsDenied"

        def ablehnen(url, **kw):
            return Abgelehnt() if "graph.microsoft.com" in url else echt(url, **kw)

        monkeypatch.setattr(httpx, "post", ablehnen)
        with pytest.raises(MailVersandFehler, match="ErrorSendAsDenied"):
            sende_mail("kunde@example.org", "x", "y", db=db, tenant_id=HAUS_A, nutzer=LAGER)

    def test_state_traegt_den_anbieter(self, db, google):
        from urllib.parse import parse_qs, urlparse

        from app.services import mailkonto_service as konto

        g = anlegen(db, kennung="gmail", anbieter="google", anmeldung="oauth2", passwort=None,
                    absender_email="g@gmail.example")
        m = anlegen(db, kennung="m365", anbieter="microsoft", passwort=None, absender_email="m@haus.example")
        state_g = parse_qs(urlparse(konto.anmeldung_starten(db, HAUS_A, g["id"])["url"]).query)["state"][0]
        assert konto._state_pruefen(state_g, HAUS_A) == (g["id"], "google")
        state_m = parse_qs(urlparse(konto.anmeldung_starten(db, HAUS_A, m["id"])["url"]).query)["state"][0]
        assert konto._state_pruefen(state_m, HAUS_A) == (m["id"], "microsoft")


# ── HTTP ──────────────────────────────────────────────────────────────────────
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


class TestHttp:
    def test_verwaltung_nur_fuer_admin(self, client, als):
        daten = {"kennung": "info", "anbieter": "ionos", "absender_email": "info@g.example", "passwort": "x"}
        als(LAGER)
        assert client.post("/api/v1/admin/postfaecher", headers=kopf(), json=daten).status_code == 403
        assert client.get("/api/v1/admin/postfaecher", headers=kopf()).status_code == 403
        als(ADMIN)
        angelegt = client.post("/api/v1/admin/postfaecher", headers=kopf(), json=daten)
        assert angelegt.status_code == 201, angelegt.text
        assert "passwort" not in angelegt.json() and angelegt.json()["hat_geheimnis"] is True
        assert [p["kennung"] for p in client.get("/api/v1/admin/postfaecher", headers=kopf()).json()] == ["info"]
        assert client.get("/api/v1/admin/postfaecher", headers=kopf(HAUS_B)).json() == []

    def test_absenderwahl_fuer_jeden_nutzer(self, client, als, db):
        anlegen(db, kennung="info")
        anlegen(db, kennung="fibu", rollen=["FINANCE_ADMIN"])
        als(LAGER)
        antwort = client.get("/api/v1/admin/postfaecher/verfuegbar", headers=kopf())
        assert [p["kennung"] for p in antwort.json()] == ["info"]

    def test_bestellmail_geht_ueber_das_einkaufspostfach(self, engine, client, als, db, smtp):
        from sqlalchemy import text

        anlegen(db, kennung="zentrale", ist_standard=True)
        anlegen(db, kennung="einkauf", verwendungen=["einkauf"], absender_name="Einkauf")
        nummer = f"EK-{uuid.uuid4().hex[:8]}"
        with engine.begin() as v:
            v.execute(text("INSERT INTO domain_einkauf.bestellungen (id, tenant_id, bestellnummer, lieferant_id, "
                           " bestelldatum, status) VALUES (:i, :h, :n, :l, CURRENT_DATE, 'versendet')"),
                      {"i": str(uuid.uuid4()), "h": HAUS_A, "n": nummer, "l": LIEFERANT})
        als(LAGER)
        antwort = client.post(f"/api/v1/purchase-orders/{nummer}/communications/email", headers=kopf(), json={})
        assert antwort.status_code == 201, antwort.text
        assert smtp.gesendet == [{"host": "smtp.ionos.de", "from": "Einkauf <einkauf@genossenschaft.example>",
                                  "to": "auftrag@duenger.example"}]

    def test_ohne_schluessel_503(self, client, als, monkeypatch):
        monkeypatch.delenv("VALEO_SECRET_KEY")
        als(ADMIN)
        antwort = client.post("/api/v1/admin/postfaecher", headers=kopf(), json={
            "kennung": "info", "anbieter": "ionos", "absender_email": "info@g.example", "passwort": "x"})
        assert antwort.status_code == 503


# ── CRM-Connector ─────────────────────────────────────────────────────────────
class TestImapConnector:
    def test_passwort_liegt_verschluesselt_und_wird_gelesen(self, engine, db):
        from sqlalchemy import text

        from app.services.connector_config import load_imap_config, save_connectors

        save_connectors(db, HAUS_A, imap={"enabled": True, "host": "imap.ionos.de", "user": "crm@g.example",
                                          "password": "imap-geheim"})
        with engine.connect() as v:
            roh = v.execute(text("SELECT settings FROM domain_shared.tenants WHERE id = :i"), {"i": HAUS_A}).scalar()
        roh = roh if isinstance(roh, dict) else json.loads(roh)
        assert roh["connectors"]["imap"]["password"].startswith("v1:")
        assert load_imap_config(db, HAUS_A).password == "imap-geheim"

    def test_altwert_im_klartext_wird_gelesen_und_beim_speichern_verschluesselt(self, engine, db):
        from sqlalchemy import text

        from app.services.connector_config import load_imap_config, save_connectors

        with engine.begin() as v:
            v.execute(text("UPDATE domain_shared.tenants SET settings = CAST(:s AS json) WHERE id = :i"),
                      {"s": json.dumps({"connectors": {"imap": {"host": "h", "user": "u", "password": "alt"}}}),
                       "i": HAUS_B})
        assert load_imap_config(db, HAUS_B).password == "alt"
        save_connectors(db, HAUS_B, imap={"enabled": True})
        assert load_imap_config(db, HAUS_B).password == "alt"
        with engine.connect() as v:
            roh = v.execute(text("SELECT settings FROM domain_shared.tenants WHERE id = :i"), {"i": HAUS_B}).scalar()
        roh = roh if isinstance(roh, dict) else json.loads(roh)
        assert roh["connectors"]["imap"]["password"].startswith("v1:")

    def test_connector_einstellungen_nur_fuer_admin(self, client, als):
        als(LAGER)
        assert client.put("/api/v1/admin-suite/capture-connectors", headers=kopf(),
                          json={"imap": {"host": "boese.example"}}).status_code == 403


# ── Maske ─────────────────────────────────────────────────────────────────────
class TestMaske:
    """Die Einrichtung laeuft ueber die Screen Definition, nicht ueber eine Handmaske."""

    def test_registriert_bereit_und_ohne_governance_fehler(self):
        from app.api.v1.endpoints.mask_screen_definition import _check_readiness
        from app.core.screen_definitions import _AGENT_SYNONYMS, _SCREEN_LIST_ROUTE, get_screen_definition
        from app.core.screen_governance import governance_errors, ux_lint

        sd = get_screen_definition("admin/postfaecher")
        assert sd["adapter"]["temporary"] is False
        assert "admin/postfaecher" in _AGENT_SYNONYMS and "admin/postfaecher" in _SCREEN_LIST_ROUTE
        assert governance_errors(sd) == []
        assert [f for f in ux_lint(sd) if f["severity"] == "error"] == []
        bereit = _check_readiness(sd)
        assert bereit["generatorReady"] is True and bereit["advisoryScore"] == 1.0

    def test_passwort_ist_verdeckt_und_sensibel(self):
        from app.core.screen_definitions import get_screen_definition

        sd = get_screen_definition("admin/postfaecher")
        felder = {f["key"]: f for f in sd["fields"]}
        assert felder["passwort"]["type"] == "password"
        assert "passwort" in sd["agentContract"]["sensitiveFields"]
        assert all(not k.endswith("_id") for k in felder)

    def test_anbieter_und_verwendungen_sind_die_des_dienstes(self):
        from app.core.screen_definitions import get_screen_definition
        from app.services.mailkonto_service import VERWENDUNGEN, VORLAGEN

        felder = {f["key"]: f for f in get_screen_definition("admin/postfaecher")["fields"]}
        assert {o["value"] for o in felder["anbieter"]["options"]} == set(VORLAGEN)
        assert felder["verwendungen"]["type"] == "multiselect"
        assert [o["value"] for o in felder["verwendungen"]["options"]] == list(VERWENDUNGEN)
        assert felder["rollen"]["type"] == "multiselect"  # Optionen: Rollen des Hauses, von der Seite geladen

    def test_jede_aktion_hat_einen_befehl(self):
        from app.core.screen_definitions import get_screen_definition

        sd = get_screen_definition("admin/postfaecher")
        aktionen = [*sd["actions"], *sd["tables"][0]["rowActions"]]
        assert all(a.get("command", "").startswith("admin.postfach") for a in aktionen)

    def test_der_ts_spiegel_entspricht_dem_backend(self):
        import json
        import re
        from pathlib import Path

        from app.core.screen_definitions_capture import build_admin_postfaecher_screen_definition

        quelle = Path("packages/frontend-web/src/masks/capture-screens.ts").read_text(encoding="utf-8")
        treffer = re.search(r"export const adminPostfaecherScreen = (\{.*?\n\}) satisfies ScreenDefinition", quelle, re.S)
        sd = build_admin_postfaecher_screen_definition()
        for schluessel in ("agentContract", "performance"):
            sd.pop(schluessel)
        assert json.loads(treffer.group(1)) == sd
