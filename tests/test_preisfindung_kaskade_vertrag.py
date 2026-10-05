"""Die Preiskaskade — jede Stufe wirkt, jeder Fehlschlag wird gemeldet.

`/pricing/calculate` ist **der** Preisfindungsweg (Lieferscheinerfassung,
`lib/api/konditionen.ts`). Bis zum 05.10.2026 hatte er fünf Stufen, von denen
**drei nie funktionierten**:

* Der Kontraktrabatt las `domain_contracts.contracts.discount_percent` — eine
  Spalte, die es nicht gibt (die Tabelle ist ein Vertragsregister mit `title`
  und `notice_period_days`, kein Handelskontrakt).
* Der Rollenrabatt las `domain_pricing.discount_rules` — eine Tabelle, die es
  nicht gibt.
* Die gepflegten Mengenstaffeln (20 Zeilen in der Entwicklungsdatenbank) wurden
  **gar nicht** gelesen.

Jeder Fehlschlag lief in `except Exception: db.rollback()`, und heraus kam der
volle Listenpreis mit `source: "base"` — ein plausibler, falscher Preis. Und der
Mandant kam aus einem Query-Parameter mit Vorgabewert.

Geprüft wird gegen die gemeinsame, vorhandene Prüfstand-Datenbank.
"""

from __future__ import annotations

import json
import os
import uuid
from decimal import Decimal

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

HAUS_A = f"preis-a-{uuid.uuid4().hex[:6]}"
HAUS_B = f"preis-b-{uuid.uuid4().hex[:6]}"

WEG = "/api/v1/pricing"
ARTIKEL = "domain_inventory.articles"
STAFFELN = "domain_pricing.staffelrabatte"
REGELN = "domain_pricing.discount_rules"
KONTRAKTE = "domain_ops.kon_contract"
ZEILEN = "domain_ops.kon_contract_line"

ARTIKEL_A = str(uuid.uuid4())
ARTIKEL_B = str(uuid.uuid4())
KONTRAKT = str(uuid.uuid4())


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as conn:
            vorhanden = conn.execute(
                text(
                    "SELECT 1 FROM information_schema.tables "
                    "WHERE table_schema='domain_pricing' AND table_name='discount_rules'"
                )
            ).scalar()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    if not vorhanden:
        pytest.skip("Migration preisfindung_rabattregeln_20261005 nicht angewandt")
    return motor


@pytest.fixture(scope="module", autouse=True)
def bestand(engine):
    """Zwei Häuser, je ein Artikel zu 100,00 €, ein Kontrakt, eine Staffel."""
    from sqlalchemy import text

    with engine.begin() as v:
        for haus in (HAUS_A, HAUS_B):
            v.execute(
                text(
                    "INSERT INTO domain_shared.tenants (id, name) VALUES (:id, :name) "
                    "ON CONFLICT (id) DO NOTHING"
                ),
                {"id": haus, "name": f"Pruefpreis {haus}"},
            )
        for aid, haus, preis in ((ARTIKEL_A, HAUS_A, 100), (ARTIKEL_B, HAUS_B, 200)):
            v.execute(
                text(
                    f"INSERT INTO {ARTIKEL} (id, tenant_id, article_number, name, "
                    " sales_price, warengruppe, is_active) "
                    "VALUES (:id, :tid, :nr, 'Pruefartikel', :preis, 'GE', TRUE)"
                ),
                {"id": aid, "tid": haus, "nr": f"ART-{aid[:8]}", "preis": preis},
            )
        # Kontrakt des Hauses A mit Position auf Artikel A: 90,00 € und 10 % Rabatt.
        v.execute(
            text(
                f"INSERT INTO {KONTRAKTE} (contract_id, tenant_id, contract_no, "
                " contract_type, party_id, contract_date, quantity_type, "
                " total_quantity, unit, allow_overdelivery, status) "
                "VALUES (:id, :tid, 'K-PREIS', 'VERKAUF', 'P-1', '2026-01-01', 'FEST', "
                "        100, 't', FALSE, 'AKTIV')"
            ),
            {"id": KONTRAKT, "tid": HAUS_A},
        )
        v.execute(
            text(
                f"INSERT INTO {ZEILEN} (line_id, contract_id, tenant_id, position_no, "
                " article_id, qty_contract, unit_price, discount_pct, is_bio, is_matif) "
                "VALUES (:lid, :cid, :tid, 1, :aid, 100, 90, 10, FALSE, FALSE)"
            ),
            {"lid": str(uuid.uuid4()), "cid": KONTRAKT, "tid": HAUS_A, "aid": ARTIKEL_A},
        )
    yield
    with engine.begin() as v:
        for tabelle in (STAFFELN, REGELN, ZEILEN, KONTRAKTE, ARTIKEL):
            v.execute(
                text(f"DELETE FROM {tabelle} WHERE tenant_id = ANY(:h)"),
                {"h": [HAUS_A, HAUS_B]},
            )
        v.execute(
            text("DELETE FROM domain_shared.tenants WHERE id = ANY(:h)"), {"h": [HAUS_A, HAUS_B]}
        )


@pytest.fixture(scope="module")
def client(engine):
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture(autouse=True)
def leere_regeln(engine):
    """Jeder Test beginnt ohne Staffeln und Rabattregeln."""
    from sqlalchemy import text

    with engine.begin() as v:
        for tabelle in (STAFFELN, REGELN):
            v.execute(
                text(f"DELETE FROM {tabelle} WHERE tenant_id = ANY(:h)"),
                {"h": [HAUS_A, HAUS_B]},
            )
    yield


def kopf(haus: str) -> dict[str, str]:
    return {"X-Tenant-ID": haus, "Authorization": "Bearer dev-token"}


def zahl(wert) -> float:
    """FastAPI liefert `Decimal` als Zeichenkette aus — fuer Geld ist das richtig."""
    return float(wert)


def preis(client, haus: str, artikel: str = ARTIKEL_A, **felder):
    werte = {"article_id": artikel}
    werte.update({k: str(v) for k, v in felder.items()})
    return client.get(f"{WEG}/calculate", params=werte, headers=kopf(haus))


def staffel_anlegen(engine, haus: str, stufen: list[dict], **felder) -> str:
    from sqlalchemy import text

    sid = str(uuid.uuid4())
    with engine.begin() as v:
        v.execute(
            text(
                f"INSERT INTO {STAFFELN} (id, tenant_id, artikel_id, artikelgruppe, "
                " kunden_id, gueltig_von, gueltig_bis, stufen, bezeichnung, status) "
                "VALUES (:id, :tid, :aid, :gruppe, :kid, :von, :bis, "
                "        CAST(:stufen AS jsonb), 'Pruefstaffel', :status)"
            ),
            {
                "id": sid,
                "tid": haus,
                "aid": felder.get("artikel_id", ARTIKEL_A),
                "gruppe": felder.get("artikelgruppe"),
                "kid": felder.get("kunden_id"),
                "von": felder.get("gueltig_von"),
                "bis": felder.get("gueltig_bis"),
                "stufen": json.dumps(stufen),
                "status": felder.get("status", "aktiv"),
            },
        )
    return sid


def regel_anlegen(engine, haus: str, rolle: str, prozent, **felder) -> str:
    from sqlalchemy import text

    rid = str(uuid.uuid4())
    with engine.begin() as v:
        v.execute(
            text(
                f"INSERT INTO {REGELN} (id, tenant_id, role, discount_percent, "
                " is_active, valid_from, valid_until) "
                "VALUES (:id, :tid, :rolle, :proz, :aktiv, :von, :bis)"
            ),
            {
                "id": rid,
                "tid": haus,
                "rolle": rolle,
                "proz": prozent,
                "aktiv": felder.get("is_active", True),
                "von": felder.get("valid_from"),
                "bis": felder.get("valid_until"),
            },
        )
    return rid


# ── 1. Der Mandant kommt aus dem Kopf ───────────────────────────────────────


class TestMandant:
    def test_kopf_bestimmt_den_mandanten(self, client):
        antwort = preis(client, HAUS_A)
        assert antwort.status_code == 200, antwort.text
        assert zahl(antwort.json()["list_price"]) == pytest.approx(100.0)

    def test_fremder_artikel_ist_nicht_bepreisbar(self, client):
        """Vorher liess sich der Mandant per Query-Parameter waehlen."""
        assert preis(client, HAUS_A, artikel=ARTIKEL_B).status_code == 404
        assert preis(client, HAUS_B, artikel=ARTIKEL_B).status_code == 200

    def test_query_parameter_waehlt_keinen_mandanten_mehr(self, client):
        """Ein mitgegebenes `tenant_id` darf den Kopf nicht aushebeln."""
        antwort = client.get(
            f"{WEG}/calculate",
            params={"article_id": ARTIKEL_B, "tenant_id": HAUS_B},
            headers=kopf(HAUS_A),
        )
        assert antwort.status_code == 404

    def test_staffelliste_ist_mandantengebunden(self, engine, client):
        staffel_anlegen(engine, HAUS_B, [{"ab_menge": "1", "rabatt_prozent": "5"}],
                        artikel_id=ARTIKEL_B)
        antwort = client.get(f"{WEG}/staffelrabatte", headers=kopf(HAUS_A))
        assert antwort.status_code == 200
        assert antwort.json() == []


# ── 2. Die Mengenstaffel wirkt ──────────────────────────────────────────────


class TestMengenstaffel:
    def test_staffel_greift_ab_der_menge(self, engine, client):
        """20 gepflegte Staffelzeilen waren wirkungslos — die Kaskade las sie nicht."""
        staffel_anlegen(engine, HAUS_A, [
            {"ab_menge": "10", "rabatt_prozent": "3"},
            {"ab_menge": "25", "rabatt_prozent": "5"},
        ])
        klein = preis(client, HAUS_A, quantity=5).json()
        assert klein["source"] == "base"
        assert zahl(klein["discount"]) == pytest.approx(0.0)

        mittel = preis(client, HAUS_A, quantity=10).json()
        assert mittel["source"] == "staffelrabatt"
        assert zahl(mittel["discount"]) == pytest.approx(3.0)
        assert zahl(mittel["staffel_ab_menge"]) == pytest.approx(10.0)
        assert zahl(mittel["net_price"]) == pytest.approx(97.0)

        gross = preis(client, HAUS_A, quantity=30).json()
        assert zahl(gross["discount"]) == pytest.approx(5.0)
        assert zahl(gross["net_price"]) == pytest.approx(95.0)

    def test_festpreis_ersetzt_den_listenpreis(self, engine, client):
        staffel_anlegen(engine, HAUS_A, [{"ab_menge": "50", "festpreis": "80"}])
        daten = preis(client, HAUS_A, quantity=60).json()
        assert daten["source"] == "staffelrabatt"
        assert zahl(daten["list_price"]) == pytest.approx(80.0)
        assert zahl(daten["discount"]) == pytest.approx(0.0)
        assert zahl(daten["net_price"]) == pytest.approx(80.0)

    def test_nullstufe_verdraengt_nichts(self, engine, client):
        """`ab_menge: 1, rabatt: 0` ist keine Wirkung und darf nichts verdecken."""
        staffel_anlegen(engine, HAUS_A, [
            {"ab_menge": "1", "rabatt_prozent": "0"},
            {"ab_menge": "10", "rabatt_prozent": "3"},
        ])
        klein = preis(client, HAUS_A, quantity=2).json()
        assert klein["source"] == "base"
        assert klein["staffelrabatt_id"] is None

    def test_abgelaufene_staffel_wirkt_nicht(self, engine, client):
        staffel_anlegen(engine, HAUS_A, [{"ab_menge": "1", "rabatt_prozent": "9"}],
                        gueltig_bis="2020-01-01")
        assert preis(client, HAUS_A, quantity=5).json()["source"] == "base"

    def test_inaktive_staffel_wirkt_nicht(self, engine, client):
        staffel_anlegen(engine, HAUS_A, [{"ab_menge": "1", "rabatt_prozent": "9"}],
                        status="inaktiv")
        assert preis(client, HAUS_A, quantity=5).json()["source"] == "base"

    def test_gruppenstaffel_greift_ueber_die_warengruppe(self, engine, client):
        staffel_anlegen(engine, HAUS_A, [{"ab_menge": "1", "rabatt_prozent": "4"}],
                        artikel_id=None, artikelgruppe="GE")
        daten = preis(client, HAUS_A, quantity=1).json()
        assert daten["source"] == "staffelrabatt"
        assert zahl(daten["discount"]) == pytest.approx(4.0)

    def test_kundenstaffel_geht_der_allgemeinen_vor(self, engine, client):
        kunde = str(uuid.uuid4())
        staffel_anlegen(engine, HAUS_A, [{"ab_menge": "1", "rabatt_prozent": "2"}])
        staffel_anlegen(engine, HAUS_A, [{"ab_menge": "1", "rabatt_prozent": "7"}],
                        kunden_id=kunde)
        daten = preis(client, HAUS_A, quantity=1, customer_id=kunde).json()
        assert zahl(daten["discount"]) == pytest.approx(7.0)

    def test_fremde_kundenstaffel_greift_nicht(self, engine, client):
        staffel_anlegen(engine, HAUS_A, [{"ab_menge": "1", "rabatt_prozent": "7"}],
                        kunden_id=str(uuid.uuid4()))
        assert preis(client, HAUS_A, quantity=1, customer_id=str(uuid.uuid4())).json()[
            "source"
        ] == "base"


# ── 3. Der Kontrakt ─────────────────────────────────────────────────────────


class TestKontraktpreis:
    def test_kontraktzeile_bestimmt_preis_und_rabatt(self, client):
        """Vorher las diese Stufe zwei Spalten, die es nicht gibt."""
        daten = preis(client, HAUS_A, contract_id=KONTRAKT).json()
        assert daten["source"] == "contract"
        assert zahl(daten["list_price"]) == pytest.approx(90.0)
        assert zahl(daten["discount"]) == pytest.approx(10.0)
        assert zahl(daten["net_price"]) == pytest.approx(81.0)
        assert daten["contract_id"] == KONTRAKT

    def test_kontrakt_geht_der_staffel_vor(self, engine, client):
        """Eine Zusage geht der allgemeinen Mengenregel vor."""
        staffel_anlegen(engine, HAUS_A, [{"ab_menge": "1", "rabatt_prozent": "50"}])
        daten = preis(client, HAUS_A, quantity=100, contract_id=KONTRAKT).json()
        assert daten["source"] == "contract"
        assert zahl(daten["discount"]) == pytest.approx(10.0)

    def test_kontrakt_ohne_position_fuer_den_artikel_wirkt_nicht(self, client):
        daten = preis(client, HAUS_B, artikel=ARTIKEL_B, contract_id=KONTRAKT).json()
        assert daten["source"] == "base"

    def test_vertragsregister_wird_nicht_mehr_gelesen(self):
        """`domain_contracts.contracts` ist ein Vertragsregister, kein Handelskontrakt."""
        from pathlib import Path

        for pfad in (
            "app/api/v1/endpoints/pricing.py",
            "app/services/preisfindung_service.py",
        ):
            quelle = Path(pfad).read_text(encoding="utf-8")
            assert "FROM domain_contracts.contracts" not in quelle, pfad


# ── 4. Der Rollenrabatt ─────────────────────────────────────────────────────


class TestRollenrabatt:
    def test_rollenrabatt_greift(self, engine, client):
        regel_anlegen(engine, HAUS_A, "MITARBEITER", 15)
        daten = preis(client, HAUS_A, user_role="MITARBEITER").json()
        assert daten["source"] == "employee_discount"
        assert zahl(daten["discount"]) == pytest.approx(15.0)
        assert zahl(daten["net_price"]) == pytest.approx(85.0)

    def test_fremde_rolle_greift_nicht(self, engine, client):
        regel_anlegen(engine, HAUS_A, "MITARBEITER", 15)
        assert preis(client, HAUS_A, user_role="GAST").json()["source"] == "base"

    def test_inaktive_regel_greift_nicht(self, engine, client):
        regel_anlegen(engine, HAUS_A, "MITARBEITER", 15, is_active=False)
        assert preis(client, HAUS_A, user_role="MITARBEITER").json()["source"] == "base"

    def test_abgelaufene_regel_greift_nicht(self, engine, client):
        regel_anlegen(engine, HAUS_A, "MITARBEITER", 15, valid_until="2020-01-01")
        assert preis(client, HAUS_A, user_role="MITARBEITER").json()["source"] == "base"

    def test_regel_eines_anderen_hauses_greift_nicht(self, engine, client):
        regel_anlegen(engine, HAUS_B, "MITARBEITER", 40)
        assert preis(client, HAUS_A, user_role="MITARBEITER").json()["source"] == "base"

    @pytest.mark.parametrize("prozent", [-1, 101])
    def test_rabatt_ausserhalb_null_bis_hundert_wird_abgewiesen(self, engine, prozent):
        """Ueber hundert Prozent waere der Preis negativ."""
        from sqlalchemy.exc import IntegrityError

        with pytest.raises(IntegrityError):
            regel_anlegen(engine, HAUS_A, f"R-{uuid.uuid4().hex[:5]}", prozent)

    def test_zwei_aktive_regeln_je_rolle_sind_unmoeglich(self, engine):
        """Sonst entschiede `LIMIT 1` ohne Sortierung den Preis."""
        from sqlalchemy.exc import IntegrityError

        regel_anlegen(engine, HAUS_A, "DOPPEL", 5)
        with pytest.raises(IntegrityError):
            regel_anlegen(engine, HAUS_A, "DOPPEL", 7)


# ── 5. Ein Fehlschlag ist kein Listenpreis ──────────────────────────────────


class TestFehlerIstKeinPreis:
    def test_unlesbare_stufe_ist_ein_503_mit_stufenangabe(self):
        """Vorher: `except: db.rollback()` und der volle Listenpreis."""
        from unittest.mock import MagicMock

        from app.services import preisfindung_service as dienst

        db = MagicMock()
        fehler = dienst.stufe_nicht_lesbar(
            db, Exception("relation does not exist"), "staffelrabatt", HAUS_A
        )
        assert fehler.status_code == 503
        assert fehler.detail["stufe"] == "staffelrabatt"
        assert "kein Preis" in fehler.detail["error"]
        db.rollback.assert_called_once()

    def test_kein_verschlucktes_rollback_in_der_kaskade(self):
        from pathlib import Path

        quelle = Path("app/api/v1/endpoints/pricing.py").read_text(encoding="utf-8")
        kaskade = quelle[quelle.index("async def calculate_price"):quelle.index("async def find_price")]
        # Nur echter Code zaehlt; der Docstring darf den alten Weg zitieren.
        anweisungen = [
            z for z in kaskade.splitlines()
            if not z.lstrip().startswith(("#", "``", '"""'))
        ]
        assert not [z for z in anweisungen if "db.rollback()" in z]
        assert "stufe_nicht_lesbar" in kaskade

    def test_rabatt_ueber_hundert_prozent_wird_abgewiesen(self):
        from decimal import Decimal as D

        from fastapi import HTTPException

        from app.services import preisfindung_service as dienst

        dienst.pruefe_rabatt(D("100"), "price_list")
        with pytest.raises(HTTPException) as fehler:
            dienst.pruefe_rabatt(D("120"), "price_list")
        assert fehler.value.status_code == 409

    def test_stufenreihenfolge_hat_eine_quelle(self):
        from app.services import preisfindung_service as dienst

        assert dienst.STUFEN == (
            "contract",
            "customer_price",
            "staffelrabatt",
            "customer_article_discount",
            "customer_discount",
            "employee_discount",
        )
        assert set(dienst.QUELLEN) == {"base", "price_list", *dienst.STUFEN}

    def test_unbekannter_artikel_ist_ein_404(self, client):
        assert preis(client, HAUS_A, artikel=str(uuid.uuid4())).status_code == 404
