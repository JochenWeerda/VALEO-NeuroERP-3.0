"""Offenes geschlossen: echter Mailversand, Bestellkommunikation am Beleg, Bankkonten im Mandanten.

Bis zum 08.10.2026:

* meldeten ``ProductionEmailService``, der Newsletter und die Bestellkommunikation
  Versanderfolg, ohne dass irgendwo eine E-Mail verschickt wurde;
* schrieb die Bestellkommunikation in den Dokumentspeicher und kannte nur
  Altbelege; "Im Portal veroeffentlichen" war ohne Gegenstueck im Portal;
* hatte ``domain_ops.ops_bankkonten`` keine ``tenant_id`` — ``/banken/konten``
  zeigte und aenderte die Bankkonten aller Mandanten; ``/konten/iban-validate``
  war unerreichbar und pruefte nur die Laenge;
* waren Bankkontonummern (``domain_erp.bank_accounts``) systemweit eindeutig.
"""

from __future__ import annotations

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

HAUS_A = f"os-a-{uuid.uuid4().hex[:6]}"
HAUS_B = f"os-b-{uuid.uuid4().hex[:6]}"
LIEFERANT = str(uuid.uuid4())
IBAN = "DE89370400440532013000"


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as v:
            vorhanden = v.execute(text(
                "SELECT 1 FROM information_schema.columns WHERE table_schema = 'domain_ops' "
                "AND table_name = 'ops_bankkonten' AND column_name = 'tenant_id'")).scalar()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    if not vorhanden:
        pytest.skip("Migration offenes_schliessen_20261008 nicht angewandt")
    with motor.begin() as v:
        for haus in (HAUS_A, HAUS_B):
            v.execute(text("INSERT INTO domain_shared.tenants (id, name) VALUES (:i, :n) ON CONFLICT (id) DO NOTHING"),
                      {"i": haus, "n": f"Pruefbetrieb {haus}"})
        v.execute(text("INSERT INTO domain_einkauf.lieferanten (id, tenant_id, lieferantennummer, firmenname, "
                       " email_bestellung) VALUES (:i, :h, :n, 'Saatgut Ost', 'bestellung@saatgut-ost.example')"),
                  {"i": LIEFERANT, "h": HAUS_A, "n": f"LF-{LIEFERANT[:6]}"})
    yield motor
    with motor.begin() as v:
        h = {"h": [HAUS_A, HAUS_B]}
        v.execute(text("DELETE FROM domain_einkauf.bestellung_kommunikation WHERE tenant_id = ANY(:h)"), h)
        v.execute(text("DELETE FROM domain_einkauf.bestellungen WHERE tenant_id = ANY(:h)"), h)
        v.execute(text("DELETE FROM domain_einkauf.lieferanten WHERE id = :i"), {"i": LIEFERANT})
        v.execute(text("DELETE FROM domain_ops.ops_bankkonten WHERE tenant_id = ANY(:h)"), h)
        v.execute(text("DELETE FROM public.outbox_events WHERE tenant_id = ANY(:h)"), h)
        v.execute(text("DELETE FROM domain_shared.tenants WHERE id = ANY(:h)"), h)


@pytest.fixture(scope="module")
def client(engine):
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


def kopf(haus: str = HAUS_A) -> dict[str, str]:
    return {"X-Tenant-ID": haus, "Authorization": "Bearer dev-token"}


def wert(engine, sql: str, **p):
    from sqlalchemy import text

    with engine.connect() as v:
        return v.execute(text(sql), p).scalar()


# ---------------------------------------------------------------------------
# SMTP: ein Ersatzserver an der smtplib-Grenze — der Dienst selbst laeuft echt.
# ---------------------------------------------------------------------------

class _Postfach:
    def __init__(self):
        self.nachrichten = []
        self.ablehnen = False


@pytest.fixture
def smtp(monkeypatch):
    import smtplib

    from app.core.config import settings

    postfach = _Postfach()

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

        def login(self, *_a):
            return None

        def send_message(self, nachricht):
            if postfach.ablehnen:
                raise smtplib.SMTPRecipientsRefused({nachricht["To"]: (550, b"nein")})
            postfach.nachrichten.append(nachricht)
            return {}

    monkeypatch.setattr(smtplib, "SMTP", Server)
    monkeypatch.setattr(settings, "EMAIL_SMTP_SERVER", "smtp.pruefstand.example")
    monkeypatch.setattr(settings, "EMAIL_SMTP_PORT", 587)
    monkeypatch.setattr(settings, "EMAIL_USERNAME", "einkauf@valeo.example")
    monkeypatch.setattr(settings, "EMAIL_PASSWORD", "geheim")
    return postfach


@pytest.fixture
def ohne_smtp(monkeypatch):
    from app.core.config import settings

    monkeypatch.setattr(settings, "EMAIL_SMTP_SERVER", None)


class TestMailversand:
    def test_ohne_einrichtung_wird_nichts_als_versendet_gemeldet(self, ohne_smtp):
        import asyncio

        from app.core.production_enhanced_services import ProductionEmailService
        from app.services.mail_versand import MailVersandNichtEingerichtet, sende_mail

        with pytest.raises(MailVersandNichtEingerichtet):
            sende_mail("a@b.example", "x", "y")
        assert asyncio.run(ProductionEmailService().send_email("a@b.example", "x", "y")) is False

    def test_mit_einrichtung_geht_die_nachricht_an_den_server(self, smtp):
        from app.services.mail_versand import sende_mail

        sende_mail("a@b.example", "Betreff", "Text")
        assert [n["To"] for n in smtp.nachrichten] == ["a@b.example"]

    def test_ablehnung_ist_ein_fehler(self, smtp):
        from app.services.mail_versand import MailVersandFehler, sende_mail

        smtp.ablehnen = True
        with pytest.raises(MailVersandFehler):
            sende_mail("a@b.example", "x", "y")


class TestNewsletter:
    WEG = "/api/v1/crm/kommunikation/newsletter"

    def test_ohne_einrichtung_503(self, client, ohne_smtp):
        antwort = client.post(self.WEG, headers=kopf(), json={"empfaenger": ["a@b.example"], "text": "Hallo"})
        assert antwort.status_code == 503

    def test_ohne_text_kein_versand(self, client, smtp):
        assert client.post(self.WEG, headers=kopf(), json={"empfaenger": ["a@b.example"]}).status_code == 422
        assert smtp.nachrichten == []

    def test_zaehlt_was_der_server_annahm(self, client, smtp):
        antwort = client.post(self.WEG, headers=kopf(), json={
            "empfaenger": ["a@b.example", "c@d.example", "kaputt"], "betreff": "Ernte", "text": "Termine"})
        assert antwort.status_code == 200, antwort.text
        daten = antwort.json()
        assert (daten["versendet"], daten["empfaenger_ungueltig"], daten["status"]) == (2, 1, "versendet")
        assert len(smtp.nachrichten) == 2


def bestellung(engine, status: str = "versendet") -> tuple[str, str]:
    from sqlalchemy import text

    kennung, nummer = str(uuid.uuid4()), f"EK-{uuid.uuid4().hex[:8]}"
    with engine.begin() as v:
        v.execute(text("INSERT INTO domain_einkauf.bestellungen (id, tenant_id, bestellnummer, lieferant_id, "
                       " bestelldatum, status) VALUES (:i, :h, :n, :l, CURRENT_DATE, :s)"),
                  {"i": kennung, "h": HAUS_A, "n": nummer, "l": LIEFERANT, "s": status})
    return kennung, nummer


def eintraege(engine, kennung: str) -> list[tuple]:
    from sqlalchemy import text

    with engine.connect() as v:
        return [tuple(z) for z in v.execute(text(
            "SELECT kanal, status, empfaenger FROM domain_einkauf.bestellung_kommunikation "
            "WHERE bestellung_id = :b ORDER BY erfasst_am"), {"b": kennung})]


class TestBestellkommunikation:
    def test_erfassen_landet_am_beleg_und_in_der_liste(self, engine, client):
        kennung, nummer = bestellung(engine)
        antwort = client.post(f"/api/v1/purchase-orders/{nummer}/communications", headers=kopf(),
                              json={"channel": "telefon", "subject": "Liefertermin", "message": "KW 43"})
        assert antwort.status_code == 201, antwort.text
        assert eintraege(engine, kennung) == [("telefon", "erfasst", None)]
        liste = client.get(f"/api/v1/purchase-orders/{kennung}/communications", headers=kopf()).json()
        assert [z["subject"] for z in liste] == ["Liefertermin"]

    def test_mail_ohne_einrichtung_wird_nicht_als_versendet_eingetragen(self, engine, client, ohne_smtp):
        kennung, nummer = bestellung(engine)
        antwort = client.post(f"/api/v1/purchase-orders/{nummer}/communications/email", headers=kopf(), json={})
        assert antwort.status_code == 503
        assert eintraege(engine, kennung) == []

    def test_mail_geht_an_den_lieferanten_und_wird_eingetragen(self, engine, client, smtp):
        kennung, nummer = bestellung(engine)
        antwort = client.post(f"/api/v1/purchase-orders/{nummer}/communications/email", headers=kopf(),
                              json={"message": "Bitte bestaetigen"})
        assert antwort.status_code == 201, antwort.text
        assert [n["To"] for n in smtp.nachrichten] == ["bestellung@saatgut-ost.example"]
        assert eintraege(engine, kennung) == [("email", "versendet", "bestellung@saatgut-ost.example")]

    def test_abgelehnte_mail_wird_nicht_eingetragen(self, engine, client, smtp):
        smtp.ablehnen = True
        kennung, nummer = bestellung(engine)
        antwort = client.post(f"/api/v1/purchase-orders/{nummer}/communications/email", headers=kopf(), json={})
        assert antwort.status_code == 502
        assert eintraege(engine, kennung) == []

    def test_portal_veroeffentlicht_und_das_portal_zeigt_es(self, engine, client):
        kennung, nummer = bestellung(engine)
        antwort = client.post(f"/api/v1/purchase-orders/{nummer}/communications/portal", headers=kopf(), json={})
        assert antwort.status_code == 201, antwort.text
        portal = client.get(f"/api/v1/supplier-portal/lieferanten/{LIEFERANT}/bestellungen", headers=kopf()).json()
        assert nummer in [z["bestellnummer"] for z in portal]
        fremd = client.get(f"/api/v1/supplier-portal/lieferanten/{LIEFERANT}/bestellungen", headers=kopf(HAUS_B)).json()
        assert fremd == []

    def test_ein_entwurf_wird_nicht_veroeffentlicht(self, engine, client):
        kennung, nummer = bestellung(engine, status="entwurf")
        antwort = client.post(f"/api/v1/purchase-orders/{nummer}/communications/portal", headers=kopf(), json={})
        assert antwort.status_code == 422
        assert eintraege(engine, kennung) == []

    def test_fremder_mandant_findet_die_bestellung_nicht(self, engine, client):
        kennung, nummer = bestellung(engine)
        antwort = client.post(f"/api/v1/purchase-orders/{nummer}/communications", headers=kopf(HAUS_B), json={})
        assert antwort.status_code == 404
        assert eintraege(engine, kennung) == []


class TestBankkonten:
    WEG = "/api/v1/banken/konten"

    def test_konten_gehoeren_dem_mandanten(self, client):
        angelegt = client.post(self.WEG, headers=kopf(), json={
            "iban": "DE89 3704 0044 0532 0130 00", "bic": "COBADEFFXXX", "bank_name": "Commerzbank", "kontoart": "giro"})
        assert angelegt.status_code == 201, angelegt.text
        kennung = angelegt.json()["id"]
        ids_b = [k["id"] for k in client.get(self.WEG, headers=kopf(HAUS_B)).json()["items"]]
        assert kennung not in ids_b
        assert client.get(f"{self.WEG}/{kennung}", headers=kopf(HAUS_B)).status_code == 404
        assert client.patch(f"{self.WEG}/{kennung}", headers=kopf(HAUS_B), json={"saldo": 1}).status_code == 404
        assert client.delete(f"{self.WEG}/{kennung}", headers=kopf(HAUS_B)).status_code == 404
        assert client.get("/api/v1/banken/salden", headers=kopf(HAUS_B)).json()["anzahl_konten"] == 0

    def test_dieselbe_iban_in_zwei_mandanten_aber_nicht_doppelt_im_eigenen(self, client):
        daten = {"iban": IBAN, "bic": "COBADEFFXXX", "bank_name": "Commerzbank", "kontoart": "giro"}
        assert client.post(self.WEG, headers=kopf(HAUS_B), json=daten).status_code == 201
        # Schreibweise mit Leerzeichen ist dieselbe IBAN.
        assert client.post(self.WEG, headers=kopf(HAUS_B), json={**daten, "iban": "DE89 3704 0044 0532 0130 00"}).status_code == 409

    def test_ungueltige_iban_wird_abgelehnt(self, client):
        antwort = client.post(self.WEG, headers=kopf(), json={
            "iban": "DE89370400440532013001", "bic": "X", "bank_name": "Y", "kontoart": "giro"})
        assert antwort.status_code == 422

    def test_iban_pruefung_ist_erreichbar_und_rechnet(self, client):
        gut = client.get(f"{self.WEG}/iban-validate?iban={IBAN}", headers=kopf())
        assert gut.status_code == 200, gut.text
        assert gut.json()["valid"] is True and gut.json()["bic"] is None
        assert client.get(f"{self.WEG}/iban-validate?iban=DE89370400440532013001", headers=kopf()).json()["valid"] is False


def test_bankkontonummer_je_mandant(engine):
    from sqlalchemy import text
    from sqlalchemy.exc import IntegrityError

    with engine.connect() as v:
        aussen = v.begin()
        nummer = f"K{uuid.uuid4().hex[:8]}"
        for haus in (HAUS_A, HAUS_B):
            v.execute(text("INSERT INTO domain_erp.bank_accounts (id, tenant_id, account_number, bank_name) "
                           "VALUES (:i, :h, :n, 'Bank')"), {"i": str(uuid.uuid4()), "h": haus, "n": nummer})
        punkt = v.begin_nested()
        with pytest.raises(IntegrityError):
            v.execute(text("INSERT INTO domain_erp.bank_accounts (id, tenant_id, account_number, bank_name) "
                           "VALUES (:i, :h, :n, 'Bank')"), {"i": str(uuid.uuid4()), "h": HAUS_A, "n": nummer})
        punkt.rollback()
        aussen.rollback()


class TestLieferantenportal:
    """Bis 08.10.2026 fragten Lieferungen, Kontrakte, Preisauskunft und Silobestand Spalten ab,
    die es nicht gibt; der Fehler wurde zu "leer" — das Portal zeigte nie etwas."""

    @pytest.fixture
    def landwirt(self, engine):
        from sqlalchemy import text

        k = {n: str(uuid.uuid4()) for n in ("kunde", "artikel", "ticket", "annahme", "kontrakt", "silo", "partie")}
        with engine.begin() as v:
            v.execute(text("INSERT INTO domain_crm.customers (id, customer_number, tenant_id) VALUES (:i, :n, :h)"),
                      {"i": k["kunde"], "n": f"LW-{k['kunde'][:6]}", "h": HAUS_A})
            v.execute(text("INSERT INTO domain_inventory.articles (id, article_number, name, tenant_id, is_active) "
                           "VALUES (:i, :n, 'Braugerste', :h, true)"), {"i": k["artikel"], "n": f"BG-{k['artikel'][:6]}", "h": HAUS_A})
            v.execute(text("INSERT INTO domain_inventory.weighing_tickets (id, ticket_number, tenant_id, gross_weight, "
                           " tare_weight, net_weight) VALUES (:i, :n, :h, 40000, 15000, 25000)"),
                      {"i": k["ticket"], "n": f"WS-{k['ticket'][:6]}", "h": HAUS_A})
            v.execute(text("INSERT INTO domain_inventory.harvest_acceptances (id, acceptance_number, tenant_id, delivery_date, "
                           " operator_id, customer_id, article_id, weighing_ticket_id, release_status) "
                           "VALUES (:i, :n, :h, CURRENT_DATE, 'waage', :c, :a, :w, 'freigegeben')"),
                      {"i": k["annahme"], "n": f"AN-{k['annahme'][:6]}", "h": HAUS_A, "c": k["kunde"], "a": k["artikel"], "w": k["ticket"]})
            v.execute(text("INSERT INTO domain_inventory.agrar_contracts (id, contract_number, contract_type, harvest_year, "
                           " partner_id, article_id, pricing_model, total_quantity_kg, remaining_quantity_kg, fixed_price, "
                           " status, tenant_id) VALUES (:i, :n, 'purchase', 2026, :c, :a, 'fixed', 100000, 75000, 215, 'active', :h)"),
                      {"i": k["kontrakt"], "n": f"KO-{k['kontrakt'][:6]}", "c": k["kunde"], "a": k["artikel"], "h": HAUS_A})
            v.execute(text("INSERT INTO domain_inventory.silos (id, silo_number, capacity_tons, article_id, tenant_id) "
                           "VALUES (:i, :n, 500, :a, :h)"), {"i": k["silo"], "n": f"S{k['silo'][:4]}", "a": k["artikel"], "h": HAUS_A})
            v.execute(text("INSERT INTO domain_inventory.silo_lots (id, silo_id, virtual_lot_number, quantity_tons, "
                           " source_partner_id, tenant_id) VALUES (:i, :s, :n, 25, :c, :h)"),
                      {"i": k["partie"], "s": k["silo"], "n": f"P-{k['partie'][:6]}", "c": k["kunde"], "h": HAUS_A})
        yield k
        with engine.begin() as v:
            for tabelle, schluessel in (("domain_inventory.silo_lots", "partie"), ("domain_inventory.silos", "silo"),
                                        ("domain_inventory.harvest_acceptances", "annahme"),
                                        ("domain_inventory.agrar_contracts", "kontrakt"),
                                        ("domain_inventory.weighing_tickets", "ticket"),
                                        ("domain_inventory.articles", "artikel"), ("domain_crm.customers", "kunde")):
                v.execute(text(f"DELETE FROM {tabelle} WHERE id = :i"), {"i": k[schluessel]})  # nosec B608

    def test_lieferungen_mit_menge_und_sorte(self, client, landwirt):
        antwort = client.get(f"/api/v1/supplier-portal/lieferanten/{landwirt['kunde']}/lieferungen", headers=kopf())
        assert antwort.status_code == 200, antwort.text
        assert [(z["sorte"], z["menge_t"]) for z in antwort.json()] == [("Braugerste", 25.0)]
        assert client.get(f"/api/v1/supplier-portal/lieferanten/{landwirt['kunde']}/lieferungen",
                          headers=kopf(HAUS_B)).json() == []

    def test_kontrakte_mit_erfuellungsstand(self, client, landwirt):
        zeilen = client.get(f"/api/v1/supplier-portal/lieferanten/{landwirt['kunde']}/kontrakte", headers=kopf()).json()
        assert [(z["sorte"], z["menge_soll_t"], z["menge_geliefert_t"], z["offene_menge_t"]) for z in zeilen] == [
            ("Braugerste", 100.0, 25.0, 75.0)]

    def test_preisauskunft_findet_den_kontraktpreis(self, client, landwirt):
        daten = client.get("/api/v1/supplier-portal/preisauskunft", headers=kopf(),
                           params={"sorte": "Braugerste", "qualitaet": "A", "stichtag": "2026-10-08"}).json()
        assert (daten["preis_eur_t"], daten["verfuegbar"]) == (215.0, True)

    def test_silobestand_des_lieferanten(self, client, landwirt):
        daten = client.get("/api/v1/supplier-portal/silo-bestaende", headers=kopf(),
                           params={"lieferant_id": landwirt["kunde"]}).json()
        zelle = next(z for z in daten["zellen"] if z["sorte"] == "Braugerste")
        assert (zelle["bestand_t"], zelle["kapazitaet_t"]) == (25.0, 500.0)
