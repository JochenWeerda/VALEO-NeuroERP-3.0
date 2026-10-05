"""Die Kundenstufe der Preisfindung — und die Sperren, die der Bestand kennt.

Drei Dinge, die vorher fehlten:

1. **Der Kundenrabatt las die falsche Tabelle.**
   `get_customer_discount` las `domain_crm.customers.discount` und
   `.discount_percent` — zwei Spalten, die es nicht gibt. Die Methode fing den
   Fehler und lieferte `None`; sie sagte das im Docstring, also log sie nicht,
   aber die Stufe wirkte nie. Die Rabattinformation liegt vollständig im
   Partnerstamm und seinen Satelliten.
2. **`articles.rabattfaehig` wurde nie geprüft.** Ein nicht rabattfähiger
   Artikel bekam Rabatt — eine Preiszusage, die das Haus nicht geben wollte.
3. **`discount_allowed` an der Preisvereinbarung wurde nie geprüft.** Ist ein
   Preis vereinbart und weiterer Rabatt ausgeschlossen, darf keine spätere Stufe
   ihn senken.

Die beiden Satellitentabellen führen **kein** `tenant_id`; die Mandantengrenze
kommt aus dem Verbund mit `business_partners`. Eine zweite Mandantenspalte neben
der des Vaters wäre eine zweite Wahrheit.

Geprüft wird gegen die gemeinsame, vorhandene Prüfstand-Datenbank.
"""

from __future__ import annotations

import os
import uuid

import pytest

pytestmark = pytest.mark.integration

DB_URL = os.environ.get(
    "TEST_DATABASE_URL",
    os.environ.get(
        "DATABASE_URL",
        "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe",
    ),
)
os.environ.setdefault("DATABASE_URL", DB_URL)
os.environ.setdefault("API_DEV_TOKEN", "dev-token")

HAUS_A = f"kunde-a-{uuid.uuid4().hex[:6]}"
HAUS_B = f"kunde-b-{uuid.uuid4().hex[:6]}"

WEG = "/api/v1/pricing"
ARTIKEL = "domain_inventory.articles"
PARTNER = "domain_crm.business_partners"
KUNDEN = "domain_crm.customers"
VEREINBARUNGEN = "domain_crm.business_partner_price_agreements"
RABATTPOSTEN = "domain_crm.business_partner_discount_items"

ARTIKEL_A = str(uuid.uuid4())
ARTIKEL_GESPERRT = str(uuid.uuid4())
ARTIKELNR_A = f"ART-{uuid.uuid4().hex[:8]}"
ARTIKELNR_GESPERRT = f"ART-{uuid.uuid4().hex[:8]}"

PARTNER_A = str(uuid.uuid4())
PARTNER_B = str(uuid.uuid4())
KUNDE_A = str(uuid.uuid4())
KUNDE_B = str(uuid.uuid4())


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    return motor


@pytest.fixture(scope="module", autouse=True)
def bestand(engine):
    """Zwei Häuser, je ein Partner mit Kunde; ein Artikel 100 €, einer gesperrt."""
    from sqlalchemy import text

    with engine.begin() as v:
        for haus in (HAUS_A, HAUS_B):
            v.execute(
                text(
                    "INSERT INTO domain_shared.tenants (id, name) VALUES (:id, :name) "
                    "ON CONFLICT (id) DO NOTHING"
                ),
                {"id": haus, "name": f"Pruefkunde {haus}"},
            )
        for aid, anr, haus, rabattfaehig in (
            (ARTIKEL_A, ARTIKELNR_A, HAUS_A, True),
            (ARTIKEL_GESPERRT, ARTIKELNR_GESPERRT, HAUS_A, False),
        ):
            v.execute(
                text(
                    f"INSERT INTO {ARTIKEL} (id, tenant_id, article_number, name, "
                    " sales_price, warengruppe, is_active, rabattfaehig) "
                    "VALUES (:id, :tid, :nr, 'Pruefartikel', 100, 'GE', TRUE, :rf)"
                ),
                {"id": aid, "tid": haus, "nr": anr, "rf": rabattfaehig},
            )
        for pid, kid, haus, pauschal in (
            (PARTNER_A, KUNDE_A, HAUS_A, 4),
            (PARTNER_B, KUNDE_B, HAUS_B, 25),
        ):
            v.execute(
                text(
                    f"INSERT INTO {PARTNER} (partner_id, tenant_id, partner_number, "
                    " name_1, status, discount_percent, price_group) "
                    "VALUES (:pid, :tid, :nr, 'Pruefpartner', 'aktiv', :proz, 'G1')"
                ),
                {"pid": pid, "tid": haus, "nr": f"P-{pid[:8]}", "proz": pauschal},
            )
            v.execute(
                text(
                    f"INSERT INTO {KUNDEN} (id, tenant_id, customer_number, company_name, "
                    " business_partner_id, is_active) "
                    "VALUES (:kid, :tid, :nr, 'Pruefkunde', :pid, TRUE)"
                ),
                {"kid": kid, "tid": haus, "nr": f"K-{kid[:8]}", "pid": pid},
            )
    yield
    with engine.begin() as v:
        v.execute(
            text(f"DELETE FROM {VEREINBARUNGEN} WHERE partner_id = ANY(:p)"),
            {"p": [PARTNER_A, PARTNER_B]},
        )
        v.execute(
            text(f"DELETE FROM {RABATTPOSTEN} WHERE partner_id = ANY(:p)"),
            {"p": [PARTNER_A, PARTNER_B]},
        )
        for tabelle in (KUNDEN, PARTNER, ARTIKEL):
            v.execute(
                text(f"DELETE FROM {tabelle} WHERE tenant_id = ANY(:h)"),
                {"h": [HAUS_A, HAUS_B]},
            )
        v.execute(
            text("DELETE FROM domain_shared.tenants WHERE id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]}
        )


@pytest.fixture(autouse=True)
def leere_satelliten(engine):
    from sqlalchemy import text

    with engine.begin() as v:
        for tabelle in (VEREINBARUNGEN, RABATTPOSTEN):
            v.execute(
                text(f"DELETE FROM {tabelle} WHERE partner_id = ANY(:p)"),
                {"p": [PARTNER_A, PARTNER_B]},
            )
    yield


@pytest.fixture(scope="module")
def client(engine):
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


def kopf(haus: str) -> dict[str, str]:
    return {"X-Tenant-ID": haus, "Authorization": "Bearer dev-token"}


def zahl(wert) -> float:
    return float(wert)


def preis(client, haus: str, artikel: str = ARTIKEL_A, **felder):
    werte = {"article_id": artikel}
    werte.update({k: str(v) for k, v in felder.items()})
    return client.get(f"{WEG}/calculate", params=werte, headers=kopf(haus))


def vereinbarung(engine, partner: str, artikelnr: str, **felder) -> str:
    from sqlalchemy import text

    vid = str(uuid.uuid4())
    with engine.begin() as v:
        v.execute(
            text(
                f"INSERT INTO {VEREINBARUNGEN} (id, partner_id, article_number, "
                " price_net, discount_allowed, valid_from, valid_to) "
                "VALUES (:id, :pid, :nr, :preis, :rabatt_erlaubt, :von, :bis)"
            ),
            {
                "id": vid,
                "pid": partner,
                "nr": artikelnr,
                "preis": felder.get("price_net", 70),
                "rabatt_erlaubt": felder.get("discount_allowed", True),
                "von": felder.get("valid_from"),
                "bis": felder.get("valid_to"),
            },
        )
    return vid


def rabattposten(engine, partner: str, artikelnr: str, prozent, **felder) -> str:
    from sqlalchemy import text

    rid = str(uuid.uuid4())
    with engine.begin() as v:
        v.execute(
            text(
                f"INSERT INTO {RABATTPOSTEN} (id, partner_id, article_number, "
                " discount_percent, valid_from, valid_to) "
                "VALUES (:id, :pid, :nr, :proz, :von, :bis)"
            ),
            {
                "id": rid,
                "pid": partner,
                "nr": artikelnr,
                "proz": prozent,
                "von": felder.get("valid_from"),
                "bis": felder.get("valid_to"),
            },
        )
    return rid


# ── 1. Der pauschale Kundenrabatt wirkt überhaupt ───────────────────────────


class TestPauschalerKundenrabatt:
    def test_rabatt_kommt_aus_dem_partnerstamm(self, client):
        """Vorher las die Stufe `customers.discount` — eine Spalte, die es nicht gibt."""
        daten = preis(client, HAUS_A, customer_id=KUNDE_A).json()
        assert daten["source"] == "customer_discount"
        assert zahl(daten["discount"]) == pytest.approx(4.0)
        assert zahl(daten["net_price"]) == pytest.approx(96.0)

    def test_ohne_kunden_kein_kundenrabatt(self, client):
        assert preis(client, HAUS_A).json()["source"] == "base"

    def test_partnerkennung_wirkt_wie_die_kundenkennung(self, client):
        """Aufrufer geben je nach Weg das eine oder das andere."""
        daten = preis(client, HAUS_A, customer_id=PARTNER_A).json()
        assert daten["source"] == "customer_discount"
        assert zahl(daten["discount"]) == pytest.approx(4.0)

    def test_fremder_kunde_bringt_keinen_rabatt(self, client):
        """Haus B gewaehrt 25 % — das darf in Haus A nichts bewirken."""
        daten = preis(client, HAUS_A, customer_id=KUNDE_B).json()
        assert daten["source"] == "base"
        assert zahl(daten["discount"]) == pytest.approx(0.0)

    def test_pauschaler_rabatt_von_null_ist_kein_rabatt(self, engine, client):
        from sqlalchemy import text

        with engine.begin() as v:
            v.execute(
                text(f"UPDATE {PARTNER} SET discount_percent = 0 WHERE partner_id = :p"),
                {"p": PARTNER_A},
            )
        try:
            assert preis(client, HAUS_A, customer_id=KUNDE_A).json()["source"] == "base"
        finally:
            with engine.begin() as v:
                v.execute(
                    text(f"UPDATE {PARTNER} SET discount_percent = 4 WHERE partner_id = :p"),
                    {"p": PARTNER_A},
                )


# ── 2. Der artikelbezogene Kundenrabatt geht vor ────────────────────────────


class TestArtikelbezogenerRabatt:
    def test_artikelrabatt_schlaegt_den_pauschalen(self, engine, client):
        rabattposten(engine, PARTNER_A, ARTIKELNR_A, 12)
        daten = preis(client, HAUS_A, customer_id=KUNDE_A).json()
        assert daten["source"] == "customer_article_discount"
        assert zahl(daten["discount"]) == pytest.approx(12.0)

    def test_rabattposten_eines_fremden_artikels_wirkt_nicht(self, engine, client):
        rabattposten(engine, PARTNER_A, "ART-GIBT-ES-NICHT", 30)
        daten = preis(client, HAUS_A, customer_id=KUNDE_A).json()
        assert daten["source"] == "customer_discount"

    def test_abgelaufener_rabattposten_wirkt_nicht(self, engine, client):
        rabattposten(engine, PARTNER_A, ARTIKELNR_A, 30, valid_to="2020-01-01")
        assert preis(client, HAUS_A, customer_id=KUNDE_A).json()["source"] == "customer_discount"

    def test_rabattposten_des_fremden_partners_wirkt_nicht(self, engine, client):
        """Der Satellit fuehrt kein `tenant_id` — die Grenze kommt aus dem Verbund."""
        rabattposten(engine, PARTNER_B, ARTIKELNR_A, 40)
        daten = preis(client, HAUS_A, customer_id=KUNDE_A).json()
        assert zahl(daten["discount"]) == pytest.approx(4.0)


# ── 3. Die Preisvereinbarung ist eine Zusage ────────────────────────────────


class TestPreisvereinbarung:
    def test_vereinbarter_preis_ersetzt_den_listenpreis(self, engine, client):
        vereinbarung(engine, PARTNER_A, ARTIKELNR_A, price_net=70)
        daten = preis(client, HAUS_A, customer_id=KUNDE_A).json()
        assert daten["source"] == "customer_price"
        assert zahl(daten["list_price"]) == pytest.approx(70.0)
        assert zahl(daten["discount"]) == pytest.approx(0.0)
        assert zahl(daten["net_price"]) == pytest.approx(70.0)

    def test_artikelrabatt_gilt_auf_den_vereinbarten_preis(self, engine, client):
        vereinbarung(engine, PARTNER_A, ARTIKELNR_A, price_net=70)
        rabattposten(engine, PARTNER_A, ARTIKELNR_A, 10)
        daten = preis(client, HAUS_A, customer_id=KUNDE_A).json()
        assert daten["source"] == "customer_article_discount"
        assert zahl(daten["list_price"]) == pytest.approx(70.0)
        assert zahl(daten["net_price"]) == pytest.approx(63.0)

    def test_discount_allowed_false_schliesst_rabatt_aus(self, engine, client):
        """Ist ein Preis zugesagt und Rabatt ausgeschlossen, senkt ihn niemand mehr."""
        vereinbarung(engine, PARTNER_A, ARTIKELNR_A, price_net=70, discount_allowed=False)
        rabattposten(engine, PARTNER_A, ARTIKELNR_A, 10)
        daten = preis(client, HAUS_A, customer_id=KUNDE_A).json()
        assert zahl(daten["list_price"]) == pytest.approx(70.0)
        assert zahl(daten["discount"]) == pytest.approx(0.0)
        assert zahl(daten["net_price"]) == pytest.approx(70.0)
        assert daten["rabatt_gesperrt"] is True
        assert "discount_allowed" in daten["rabatt_sperrgrund"]

    def test_abgelaufene_vereinbarung_wirkt_nicht(self, engine, client):
        vereinbarung(engine, PARTNER_A, ARTIKELNR_A, price_net=70, valid_to="2020-01-01")
        daten = preis(client, HAUS_A, customer_id=KUNDE_A).json()
        assert zahl(daten["list_price"]) == pytest.approx(100.0)

    def test_vereinbarung_des_fremden_partners_wirkt_nicht(self, engine, client):
        vereinbarung(engine, PARTNER_B, ARTIKELNR_A, price_net=10)
        daten = preis(client, HAUS_A, customer_id=KUNDE_A).json()
        assert zahl(daten["list_price"]) == pytest.approx(100.0)


# ── 4. Die Rabattfähigkeit des Artikels ─────────────────────────────────────


class TestRabattfaehigkeit:
    def test_nicht_rabattfaehiger_artikel_bekommt_keinen_rabatt(self, client):
        """Der Artikelstamm sagt es, und die Kaskade hat es nie gelesen."""
        daten = preis(client, HAUS_A, artikel=ARTIKEL_GESPERRT, customer_id=KUNDE_A).json()
        assert zahl(daten["discount"]) == pytest.approx(0.0)
        assert zahl(daten["net_price"]) == pytest.approx(100.0)
        assert daten["rabatt_gesperrt"] is True
        assert "rabattfaehig" in daten["rabatt_sperrgrund"]

    def test_die_sperre_wird_benannt_und_nicht_verschwiegen(self, client):
        """Ein stiller Rabatt von null ist nicht unterscheidbar von "keiner gefunden"."""
        gesperrt = preis(client, HAUS_A, artikel=ARTIKEL_GESPERRT, customer_id=KUNDE_A).json()
        ohne = preis(client, HAUS_A).json()
        assert zahl(gesperrt["discount"]) == zahl(ohne["discount"]) == 0.0
        assert gesperrt["rabatt_gesperrt"] is True
        assert ohne["rabatt_gesperrt"] is False
        assert ohne["rabatt_sperrgrund"] is None

    def test_rabattfaehiger_artikel_bleibt_rabattierbar(self, client):
        daten = preis(client, HAUS_A, customer_id=KUNDE_A).json()
        assert daten["rabatt_gesperrt"] is False
        assert zahl(daten["discount"]) > 0


# ── 5. Die alte Quelle wird nicht mehr gelesen ──────────────────────────────


class TestAlteQuelle:
    def test_customers_discount_wird_nicht_mehr_gelesen(self):
        from pathlib import Path

        quelle = Path("app/services/business_partner_service.py").read_text(encoding="utf-8")
        anweisungen = [z for z in quelle.splitlines() if not z.lstrip().startswith("#")]
        verbunden = "\n".join(anweisungen)
        assert "SELECT discount, discount_percent FROM domain_crm.customers" not in verbunden

    def test_satelliten_werden_ueber_den_partner_eingegrenzt(self):
        """Keine zweite Mandantenspalte neben der des Vaters."""
        from pathlib import Path

        quelle = Path("app/services/business_partner_service.py").read_text(encoding="utf-8")
        for tabelle in (
            "business_partner_price_agreements",
            "business_partner_discount_items",
        ):
            # Die SQL-Stelle, nicht die erste Nennung im Kommentar.
            stelle = quelle.index(f"FROM domain_crm.{tabelle}")
            abschnitt = quelle[stelle:stelle + 700]
            assert "JOIN domain_crm.business_partners" in abschnitt, tabelle
            assert "p.tenant_id = :tid" in abschnitt, tabelle

    def test_stufen_decken_die_kundenstufe_ab(self):
        from app.services import preisfindung_service as dienst

        assert "customer_price" in dienst.STUFEN
        assert "customer_article_discount" in dienst.STUFEN
        assert dienst.STUFEN.index("customer_price") < dienst.STUFEN.index("staffelrabatt")
        assert dienst.STUFEN.index("customer_article_discount") < dienst.STUFEN.index(
            "customer_discount"
        )
