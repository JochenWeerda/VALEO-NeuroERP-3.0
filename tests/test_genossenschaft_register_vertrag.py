"""Mitgliederregister einer eG — die Liste, der Bestand und das Kapital.

Vier Dinge, die vorher fehlten:

1. **Die Tabellen.** `domain_shared.genossenschaft_mitglieder` und
   `genossenschaft_anteilsbewegungen` existierten in keiner Datenbank. Der
   Endpunkt fing den Lesefehler: Die Mitgliederliste war leer, die
   Kapitalübersicht meldete 0 Mitglieder und **0,00 €**. Für eine eG ist beides
   nie wahr — § 30 GenG verpflichtet zur Mitgliederliste, und das
   Geschäftsguthaben ist eine Bilanzposition (§ 337 HGB).
2. **Der Mandant.** Keine Abfrage trug ihn, obwohl `get_tenant_id` hing.
3. **Eine Wahrheit über den Bestand.** Die Spalte `genossenschaftsanteile`
   wurde neben dem Bewegungsjournal fortgeschrieben. Jetzt ist der Bestand die
   Summe der Bewegungen — es gibt keine zweite Zahl mehr, die abweichen kann.
4. **Eine verbindliche Hauptbuchbuchung.** Sie stand in
   `except Exception: pass  # GL-Buchung nicht kritisch`.

Geprüft wird gegen die gemeinsame, vorhandene Prüfstand-Datenbank.
"""

from __future__ import annotations

import os
import uuid
from datetime import date
from unittest.mock import MagicMock

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

HAUS_A = f"geno-a-{uuid.uuid4().hex[:6]}"
HAUS_B = f"geno-b-{uuid.uuid4().hex[:6]}"
#: Ein Haus ohne Kontenrahmen — hier muss die Hauptbuchbuchung scheitern.
HAUS_OHNE_KONTEN = f"geno-x-{uuid.uuid4().hex[:6]}"

WEG = "/api/v1/genossenschaft"
MITGLIEDER = "domain_shared.genossenschaft_mitglieder"
BEWEGUNGEN = "domain_shared.genossenschaft_anteilsbewegungen"

KONTEN = ("1200", "0900", "1600")


@pytest.fixture(scope="module")
def engine():
    from sqlalchemy import create_engine, text

    try:
        motor = create_engine(DB_URL)
        with motor.connect() as conn:
            vorhanden = conn.execute(
                text(
                    "SELECT table_name FROM information_schema.tables "
                    "WHERE table_schema='domain_shared' "
                    "AND table_name='genossenschaft_anteilsbewegungen'"
                )
            ).scalar()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    if not vorhanden:
        pytest.skip("Migration genossenschaft_mitgliederregister_20261005 nicht angewandt")
    return motor


@pytest.fixture(scope="module", autouse=True)
def haeuser(engine):
    """Eigene Mandanten mit Kontenrahmen — und einer ohne."""
    from sqlalchemy import text

    with engine.begin() as v:
        for haus in (HAUS_A, HAUS_B, HAUS_OHNE_KONTEN):
            v.execute(
                text(
                    "INSERT INTO domain_shared.tenants (id, name) VALUES (:id, :name) "
                    "ON CONFLICT (id) DO NOTHING"
                ),
                {"id": haus, "name": f"Pruefgenossenschaft {haus} eG"},
            )
        for haus in (HAUS_A, HAUS_B):
            for nummer in KONTEN:
                v.execute(
                    text(
                        "INSERT INTO domain_erp.chart_of_accounts "
                        "(id, tenant_id, account_number, account_name, account_type, "
                        " is_active, is_summary) "
                        "VALUES (:id, :tid, :nr, :name, 'EQUITY', TRUE, FALSE)"
                    ),
                    {
                        "id": str(uuid.uuid4()),
                        "tid": haus,
                        "nr": nummer,
                        "name": f"Pruefkonto {nummer}",
                    },
                )
    yield
    _aufraeumen(engine)


def _aufraeumen(engine) -> None:
    from sqlalchemy import text

    haeuser = (HAUS_A, HAUS_B, HAUS_OHNE_KONTEN)
    with engine.begin() as v:
        v.execute(
            text(
                "DELETE FROM domain_erp.journal_entry_lines WHERE journal_entry_id IN "
                "(SELECT id FROM domain_erp.journal_entries WHERE tenant_id = ANY(:h))"
            ),
            {"h": list(haeuser)},
        )
        v.execute(
            text("DELETE FROM domain_erp.journal_entries WHERE tenant_id = ANY(:h)"),
            {"h": list(haeuser)},
        )
        v.execute(
            text(f"DELETE FROM {BEWEGUNGEN} WHERE tenant_id = ANY(:h)"), {"h": list(haeuser)}
        )
        v.execute(
            text(f"DELETE FROM {MITGLIEDER} WHERE tenant_id = ANY(:h)"), {"h": list(haeuser)}
        )
        v.execute(
            text("DELETE FROM domain_erp.chart_of_accounts WHERE tenant_id = ANY(:h)"),
            {"h": list(haeuser)},
        )
        v.execute(
            text("DELETE FROM domain_shared.tenants WHERE id = ANY(:h)"), {"h": list(haeuser)}
        )


@pytest.fixture(scope="module")
def client(engine):
    from fastapi.testclient import TestClient

    from app.main import app

    return TestClient(app, raise_server_exceptions=False)


def kopf(haus: str) -> dict[str, str]:
    return {"X-Tenant-Id": haus, "Authorization": "Bearer dev-token"}


def mitglied_anlegen(client, haus: str, anteile: int = 0, **felder) -> dict:
    nutzlast = {
        "name": felder.pop("name", f"Mitglied {uuid.uuid4().hex[:5]}"),
        "adresse": "Dorfstrasse 1, 26789 Musterdorf",
        "eintrittsdatum": "2026-01-15",
        "anteilswert_eur": felder.pop("anteilswert_eur", 100.0),
        "genossenschaftsanteile": anteile,
        "iban": "DE02120300000000202051",
        "bank_name": "Pruefbank",
    }
    nutzlast.update(felder)
    antwort = client.post(f"{WEG}/mitglieder", json=nutzlast, headers=kopf(haus))
    assert antwort.status_code == 201, antwort.text
    return antwort.json()


def bewegen(client, haus: str, mitglied_id: str, typ: str, anzahl: int, **felder):
    nutzlast = {
        "bewegungstyp": typ,
        "anzahl_anteile": anzahl,
        "wert_eur": felder.pop("wert_eur", anzahl * 100.0),
        "datum": felder.pop("datum", "2026-02-01"),
    }
    nutzlast.update(felder)
    return client.post(
        f"{WEG}/mitglieder/{mitglied_id}/anteilsbewegung", json=nutzlast, headers=kopf(haus)
    )


# ── 1. Das Schema einer frischen Installation ───────────────────────────────


class TestSchema:
    def test_beide_tabellen_sind_angelegt(self, engine):
        """Der ganze Weg hing an zwei Tabellen, die keine Migration anlegte."""
        from sqlalchemy import text

        with engine.connect() as c:
            for tabelle in ("genossenschaft_mitglieder", "genossenschaft_anteilsbewegungen"):
                assert c.execute(
                    text(
                        "SELECT 1 FROM information_schema.tables "
                        "WHERE table_schema='domain_shared' AND table_name=:t"
                    ),
                    {"t": tabelle},
                ).scalar() == 1, tabelle

    def test_bestand_ist_keine_spalte(self, engine):
        """Zwei Wahrheiten uber denselben Bestand koennen auseinanderlaufen."""
        from sqlalchemy import text

        with engine.connect() as c:
            spalten = {
                r[0]
                for r in c.execute(
                    text(
                        "SELECT column_name FROM information_schema.columns "
                        "WHERE table_schema='domain_shared' "
                        "AND table_name='genossenschaft_mitglieder'"
                    )
                ).all()
            }
        assert "genossenschaftsanteile" not in spalten
        assert {"tenant_id", "austrittsdatum"} <= spalten

    def test_mitgliedsnummer_ist_je_mandant_eindeutig(self, engine):
        """Eine Doppelnummer macht die Liste nach § 30 GenG unbrauchbar."""
        from sqlalchemy import text

        with engine.connect() as c:
            definition = c.execute(
                text(
                    "SELECT indexdef FROM pg_indexes WHERE schemaname='domain_shared' "
                    "AND indexname='ux_geno_mitglied_nr'"
                )
            ).scalar()
        assert definition and "UNIQUE" in definition
        assert "tenant_id" in definition and "mitglieds_nr" in definition

    def test_kontonummer_ist_je_mandant_eindeutig(self, engine):
        """``001_initial_schema`` machte sie systemweit eindeutig.

        Damit konnte genau **eine** Genossenschaft im System das Konto 1200
        besitzen — jede zweite konnte ihren Kontenrahmen nicht anlegen, und die
        Hauptbuchbuchung einer Anteilszeichnung haette fuer sie nie gelingen
        koennen. Dass es je Mandant gemeint war, stand im Code daneben:
        ``_bookable_account`` sucht mit ``tenant_id``.
        """
        from sqlalchemy import text

        with engine.connect() as c:
            bedingungen = {
                r[0]: r[1]
                for r in c.execute(
                    text(
                        "SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint "
                        "WHERE conrelid = 'domain_erp.chart_of_accounts'::regclass "
                        "AND contype = 'u'"
                    )
                ).all()
            }
        assert "chart_of_accounts_account_number_key" not in bedingungen
        assert "uq_coa_mandant_kontonummer" in bedingungen
        assert "tenant_id" in bedingungen["uq_coa_mandant_kontonummer"]

    def test_zwei_haeuser_duerfen_dasselbe_konto_fuehren(self, engine):
        """Zwei Genossenschaften, zwei Kontenrahmen, dieselbe Nummer."""
        from sqlalchemy import text

        with engine.connect() as c:
            je_nummer = c.execute(
                text(
                    "SELECT account_number, COUNT(DISTINCT tenant_id) FROM "
                    "domain_erp.chart_of_accounts WHERE account_number = ANY(:n) "
                    "GROUP BY account_number"
                ),
                {"n": list(KONTEN)},
            ).all()
        assert je_nummer, "Die Pruefkonten fehlen"
        assert all(anzahl >= 2 for _, anzahl in je_nummer), je_nummer

    @pytest.mark.parametrize(
        "bedingung",
        [
            "ck_geno_mitglied_status",
            "ck_geno_austritt_datiert",
            "ck_geno_austritt_nach_eintritt",
            "ck_geno_bewegungstyp",
            "ck_geno_anzahl_positiv",
            "ck_geno_wert_positiv",
            "ck_geno_uebertragung_gegenseite",
            "ck_geno_uebertragung_nicht_an_sich",
        ],
    )
    def test_pruefbedingung_vorhanden(self, engine, bedingung):
        from sqlalchemy import text

        with engine.connect() as c:
            assert c.execute(
                text("SELECT 1 FROM pg_constraint WHERE conname = :n"), {"n": bedingung}
            ).scalar() == 1


class TestDatenbankgrenzen:
    def test_null_anteile_werden_von_der_datenbank_abgewiesen(self, engine, client):
        """Die Richtung steckt im Typ; eine Anzahl ist immer positiv."""
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        mitglied = mitglied_anlegen(client, HAUS_A)
        with pytest.raises(IntegrityError):
            with engine.begin() as v:
                v.execute(
                    text(
                        f"INSERT INTO {BEWEGUNGEN} (id, tenant_id, mitglieds_id, bewegungstyp, "
                        "anzahl_anteile, wert_eur, datum) "
                        "VALUES (:id, :tid, :mid, 'ZEICHNUNG', 0, 10, '2026-02-01')"
                    ),
                    {"id": str(uuid.uuid4()), "tid": HAUS_A, "mid": mitglied["id"]},
                )

    def test_uebertragung_ohne_gegenseite_wird_abgewiesen(self, engine, client):
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        mitglied = mitglied_anlegen(client, HAUS_A)
        with pytest.raises(IntegrityError):
            with engine.begin() as v:
                v.execute(
                    text(
                        f"INSERT INTO {BEWEGUNGEN} (id, tenant_id, mitglieds_id, bewegungstyp, "
                        "anzahl_anteile, wert_eur, datum) "
                        "VALUES (:id, :tid, :mid, 'UEBERTRAGUNG_AB', 1, 10, '2026-02-01')"
                    ),
                    {"id": str(uuid.uuid4()), "tid": HAUS_A, "mid": mitglied["id"]},
                )

    def test_austritt_ohne_datum_wird_abgewiesen(self, engine, client):
        """§ 30 Abs. 2 GenG nennt den Austritt als Inhalt der Liste."""
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        mitglied = mitglied_anlegen(client, HAUS_A)
        with pytest.raises(IntegrityError):
            with engine.begin() as v:
                v.execute(
                    text(f"UPDATE {MITGLIEDER} SET status = 'AUSGETRETEN' WHERE id = :id"),
                    {"id": mitglied["id"]},
                )

    def test_mitglied_mit_bewegungen_ist_nicht_loeschbar(self, engine, client):
        """Die Bewegungen sind der Nachweis des Geschaeftsguthabens."""
        from sqlalchemy import text
        from sqlalchemy.exc import IntegrityError

        mitglied = mitglied_anlegen(client, HAUS_A, anteile=3)
        with pytest.raises(IntegrityError):
            with engine.begin() as v:
                v.execute(
                    text(f"DELETE FROM {MITGLIEDER} WHERE id = :id"), {"id": mitglied["id"]}
                )


# ── 2. Der Mandant ──────────────────────────────────────────────────────────


class TestMandantentrennung:
    def test_liste_zeigt_nur_eigene_mitglieder(self, client):
        meines = mitglied_anlegen(client, HAUS_A, name="Nur fuer Haus A")
        fremdes = mitglied_anlegen(client, HAUS_B, name="Nur fuer Haus B")

        antwort = client.get(f"{WEG}/mitglieder", headers=kopf(HAUS_A))
        assert antwort.status_code == 200
        ids = {z["id"] for z in antwort.json()}
        assert meines["id"] in ids
        assert fremdes["id"] not in ids
        assert all(z["tenant_id"] == HAUS_A for z in antwort.json())

    def test_fremdes_mitglied_ist_nicht_lesbar(self, client):
        fremdes = mitglied_anlegen(client, HAUS_B)
        antwort = client.get(f"{WEG}/mitglieder/{fremdes['id']}", headers=kopf(HAUS_A))
        assert antwort.status_code == 404

    def test_auf_fremdes_mitglied_wird_nicht_gebucht(self, client):
        fremdes = mitglied_anlegen(client, HAUS_B)
        antwort = bewegen(client, HAUS_A, fremdes["id"], "ZEICHNUNG", 1)
        assert antwort.status_code == 404

    def test_gleiche_mitgliedsnummer_in_zwei_haeusern_ist_erlaubt(self, client):
        nummer = f"M-SHARED-{uuid.uuid4().hex[:5]}"
        mitglied_anlegen(client, HAUS_A, mitglieds_nr=nummer)
        mitglied_anlegen(client, HAUS_B, mitglieds_nr=nummer)

    def test_gleiche_mitgliedsnummer_im_selben_haus_wird_abgewiesen(self, client):
        nummer = f"M-DOPPEL-{uuid.uuid4().hex[:5]}"
        mitglied_anlegen(client, HAUS_A, mitglieds_nr=nummer)
        antwort = client.post(
            f"{WEG}/mitglieder",
            json={
                "name": "Zweiter mit derselben Nummer",
                "adresse": "Dorfstrasse 2",
                "eintrittsdatum": "2026-01-16",
                "mitglieds_nr": nummer,
                "iban": "DE02120300000000202051",
                "bank_name": "Pruefbank",
            },
            headers=kopf(HAUS_A),
        )
        assert antwort.status_code == 409


# ── 3. Ein Fehler ist keine leere Liste und kein Kapital von 0,00 EUR ───────


class TestFehlerIstKeinLeererZustand:
    def test_unlesbare_liste_ist_ein_503(self):
        from app.api.v1.endpoints import genossenschaft as geno

        db = MagicMock()
        db.execute.side_effect = Exception('relation "genossenschaft_mitglieder" does not exist')
        with pytest.raises(Exception) as fehler:
            geno.list_mitglieder(status=None, limit=200, offset=0, db=db, tenant_id=HAUS_A)
        assert getattr(fehler.value, "status_code", None) == 503
        db.rollback.assert_called_once()

    def test_unlesbare_kapitaluebersicht_ist_ein_503(self):
        """0,00 EUR ist eine Bilanzaussage und darf nicht aus einem Fehler entstehen."""
        from app.api.v1.endpoints import genossenschaft as geno

        db = MagicMock()
        db.execute.side_effect = Exception("relation does not exist")
        with pytest.raises(Exception) as fehler:
            geno.kapitaluebersicht(db=db, tenant_id=HAUS_A)
        assert getattr(fehler.value, "status_code", None) == 503
        detail = str(fehler.value.detail)
        assert "migration_hint" in detail

    def test_unbekannter_stand_wird_abgewiesen(self, client):
        antwort = client.get(f"{WEG}/mitglieder", params={"status": "EHEMALIG"}, headers=kopf(HAUS_A))
        assert antwort.status_code == 422
        assert "AKTIV" in antwort.text


# ── 4. Eine Wahrheit uber den Bestand ───────────────────────────────────────


class TestAbgeleiteterBestand:
    def test_erstzeichnung_wird_als_bewegung_gebucht(self, client):
        """Auch der erste Anteil braucht einen Beleg."""
        mitglied = mitglied_anlegen(client, HAUS_A, anteile=5)
        akte = client.get(f"{WEG}/mitglieder/{mitglied['id']}", headers=kopf(HAUS_A)).json()
        assert akte["genossenschaftsanteile"] == 5
        assert akte["geschaeftsguthaben_eur"] == 500.0
        typen = [b["bewegungstyp"] for b in akte["anteilsbewegungen"]]
        assert typen == ["ZEICHNUNG"]

    def test_mitglied_ohne_anteile_hat_bestand_null(self, client):
        mitglied = mitglied_anlegen(client, HAUS_A, anteile=0)
        akte = client.get(f"{WEG}/mitglieder/{mitglied['id']}", headers=kopf(HAUS_A)).json()
        assert akte["genossenschaftsanteile"] == 0
        assert akte["anteilsbewegungen"] == []

    def test_bestand_ist_die_summe_der_bewegungen(self, engine, client):
        from sqlalchemy import text

        mitglied = mitglied_anlegen(client, HAUS_A, anteile=10)
        assert bewegen(client, HAUS_A, mitglied["id"], "ERHOEHUNG", 4).status_code == 201
        assert bewegen(client, HAUS_A, mitglied["id"], "TEILRUECKZAHLUNG", 6).status_code == 201

        akte = client.get(f"{WEG}/mitglieder/{mitglied['id']}", headers=kopf(HAUS_A)).json()
        with engine.connect() as c:
            gerechnet = c.execute(
                text(
                    "SELECT SUM(CASE WHEN bewegungstyp IN "
                    "('ZEICHNUNG','ERHOEHUNG','UEBERTRAGUNG_AN') "
                    "THEN anzahl_anteile ELSE -anzahl_anteile END) "
                    f"FROM {BEWEGUNGEN} WHERE mitglieds_id = :id"
                ),
                {"id": mitglied["id"]},
            ).scalar()
        assert akte["genossenschaftsanteile"] == 8 == int(gerechnet)

    def test_antwort_nennt_den_bestand_nach_der_buchung(self, client):
        mitglied = mitglied_anlegen(client, HAUS_A, anteile=2)
        antwort = bewegen(client, HAUS_A, mitglied["id"], "ERHOEHUNG", 3)
        assert antwort.json()["bestand_anteile"] == 5

    def test_patch_auf_den_bestand_wird_abgewiesen(self, client):
        """Eine Anteilsaenderung ohne Bewegung ist eine unbelegte Aenderung."""
        mitglied = mitglied_anlegen(client, HAUS_A, anteile=2)
        antwort = client.patch(
            f"{WEG}/mitglieder/{mitglied['id']}",
            json={"genossenschaftsanteile": 99},
            headers=kopf(HAUS_A),
        )
        assert antwort.status_code == 422
        akte = client.get(f"{WEG}/mitglieder/{mitglied['id']}", headers=kopf(HAUS_A)).json()
        assert akte["genossenschaftsanteile"] == 2


class TestVokabular:
    def test_transfer_wird_nicht_mehr_angenommen(self, client):
        """``TRANSFER`` bekam ein Vorzeichen ``+1`` und schuf Anteile aus nichts."""
        mitglied = mitglied_anlegen(client, HAUS_A, anteile=5)
        antwort = bewegen(client, HAUS_A, mitglied["id"], "TRANSFER", 2)
        assert antwort.status_code == 422

    @pytest.mark.parametrize("anzahl", [0, -3])
    def test_anzahl_muss_positiv_sein(self, client, anzahl):
        mitglied = mitglied_anlegen(client, HAUS_A, anteile=5)
        antwort = bewegen(client, HAUS_A, mitglied["id"], "ERHOEHUNG", anzahl)
        assert antwort.status_code == 422

    def test_vorzeichen_und_sql_stammen_aus_derselben_menge(self):
        """Eine Richtung, eine Quelle: ``ZUGANG``."""
        from app.services import genossenschaft_service as dienst

        assert set(dienst.VORZEICHEN) == set(dienst.BEWEGUNGSTYPEN)
        for typ in dienst.ZUGANG:
            assert dienst.VORZEICHEN[typ] == 1
            assert f"'{typ}'" in dienst.BESTANDSAUSDRUCK
        for typ in dienst.ABGANG:
            assert dienst.VORZEICHEN[typ] == -1
            assert f"'{typ}'" not in dienst.BESTANDSAUSDRUCK


class TestKeinNegativerBestand:
    def test_abgang_ueber_den_bestand_wird_abgewiesen(self, client):
        mitglied = mitglied_anlegen(client, HAUS_A, anteile=3)
        antwort = bewegen(client, HAUS_A, mitglied["id"], "TEILRUECKZAHLUNG", 4)
        assert antwort.status_code == 409
        assert "unterschreiten" in antwort.text
        akte = client.get(f"{WEG}/mitglieder/{mitglied['id']}", headers=kopf(HAUS_A)).json()
        assert akte["genossenschaftsanteile"] == 3

    def test_vollrueckzahlung_muss_den_ganzen_bestand_treffen(self, client):
        mitglied = mitglied_anlegen(client, HAUS_A, anteile=7)
        antwort = bewegen(client, HAUS_A, mitglied["id"], "VOLLRUECKZAHLUNG", 5)
        assert antwort.status_code == 409
        assert "TEILRUECKZAHLUNG" in antwort.text

    def test_vollrueckzahlung_auf_null(self, client):
        mitglied = mitglied_anlegen(client, HAUS_A, anteile=7)
        antwort = bewegen(client, HAUS_A, mitglied["id"], "VOLLRUECKZAHLUNG", 7)
        assert antwort.status_code == 201
        assert antwort.json()["bestand_anteile"] == 0


class TestUebertragung:
    def test_ohne_gegenseite_wird_abgewiesen(self, client):
        mitglied = mitglied_anlegen(client, HAUS_A, anteile=5)
        antwort = bewegen(client, HAUS_A, mitglied["id"], "UEBERTRAGUNG_AB", 2)
        assert antwort.status_code == 422
        assert "zwei Seiten" in antwort.text

    def test_an_sich_selbst_wird_abgewiesen(self, client):
        mitglied = mitglied_anlegen(client, HAUS_A, anteile=5)
        antwort = bewegen(
            client, HAUS_A, mitglied["id"], "UEBERTRAGUNG_AB", 2,
            gegen_mitglieds_id=mitglied["id"],
        )
        assert antwort.status_code == 422

    def test_gegenseite_bei_einem_typ_ohne_gegenseite_wird_abgewiesen(self, client):
        geber = mitglied_anlegen(client, HAUS_A, anteile=5)
        nehmer = mitglied_anlegen(client, HAUS_A)
        antwort = bewegen(
            client, HAUS_A, geber["id"], "ZEICHNUNG", 1, gegen_mitglieds_id=nehmer["id"]
        )
        assert antwort.status_code == 422

    def test_beide_seiten_werden_geschrieben_und_die_summe_bleibt(self, client):
        geber = mitglied_anlegen(client, HAUS_A, anteile=6)
        nehmer = mitglied_anlegen(client, HAUS_A, anteile=1)
        antwort = bewegen(
            client, HAUS_A, geber["id"], "UEBERTRAGUNG_AB", 4,
            gegen_mitglieds_id=nehmer["id"],
        )
        assert antwort.status_code == 201, antwort.text
        assert antwort.json()["gegenbewegung_id"]

        akte_geber = client.get(f"{WEG}/mitglieder/{geber['id']}", headers=kopf(HAUS_A)).json()
        akte_nehmer = client.get(f"{WEG}/mitglieder/{nehmer['id']}", headers=kopf(HAUS_A)).json()
        assert akte_geber["genossenschaftsanteile"] == 2
        assert akte_nehmer["genossenschaftsanteile"] == 5
        assert akte_geber["genossenschaftsanteile"] + akte_nehmer["genossenschaftsanteile"] == 7

    def test_uebertragung_bucht_nicht_ins_hauptbuch(self, client):
        """Anteile wechseln das Mitglied; die Bilanzposition bleibt gleich."""
        geber = mitglied_anlegen(client, HAUS_A, anteile=3)
        nehmer = mitglied_anlegen(client, HAUS_A)
        antwort = bewegen(
            client, HAUS_A, geber["id"], "UEBERTRAGUNG_AB", 3,
            gegen_mitglieds_id=nehmer["id"],
        )
        assert antwort.status_code == 201
        assert antwort.json()["journal_entry_id"] is None

    def test_uebertragung_ueber_den_bestand_schreibt_keine_seite(self, engine, client):
        geber = mitglied_anlegen(client, HAUS_A, anteile=2)
        nehmer = mitglied_anlegen(client, HAUS_A)
        antwort = bewegen(
            client, HAUS_A, geber["id"], "UEBERTRAGUNG_AB", 5,
            gegen_mitglieds_id=nehmer["id"],
        )
        assert antwort.status_code == 409
        akte_nehmer = client.get(f"{WEG}/mitglieder/{nehmer['id']}", headers=kopf(HAUS_A)).json()
        assert akte_nehmer["genossenschaftsanteile"] == 0
        assert akte_nehmer["anteilsbewegungen"] == []


# ── 5. Die Hauptbuchbuchung ist verbindlich ─────────────────────────────────


class TestHauptbuchbuchung:
    def test_zeichnung_erzeugt_eine_buchung_mit_belegbezug(self, engine, client):
        from sqlalchemy import text

        mitglied = mitglied_anlegen(client, HAUS_A, anteile=4)
        akte = client.get(f"{WEG}/mitglieder/{mitglied['id']}", headers=kopf(HAUS_A)).json()
        bewegung = akte["anteilsbewegungen"][0]
        assert bewegung["journal_entry_id"]
        with engine.connect() as c:
            referenz = c.execute(
                text("SELECT reference FROM domain_erp.journal_entries WHERE id = :id"),
                {"id": bewegung["journal_entry_id"]},
            ).scalar()
        assert referenz == bewegung["id"]

    def test_ohne_kontenrahmen_entsteht_keine_bewegung(self, engine, client):
        """Vorher: ``except Exception: pass  # GL-Buchung nicht kritisch``."""
        from sqlalchemy import text

        antwort = client.post(
            f"{WEG}/mitglieder",
            json={
                "name": "Haus ohne Kontenrahmen",
                "adresse": "Dorfstrasse 3",
                "eintrittsdatum": "2026-01-15",
                "genossenschaftsanteile": 5,
                "iban": "DE02120300000000202051",
                "bank_name": "Pruefbank",
            },
            headers=kopf(HAUS_OHNE_KONTEN),
        )
        assert antwort.status_code == 409, antwort.text
        assert "Hauptbuchbuchung" in antwort.text
        with engine.connect() as c:
            assert c.execute(
                text(f"SELECT COUNT(*) FROM {MITGLIEDER} WHERE tenant_id = :t"),
                {"t": HAUS_OHNE_KONTEN},
            ).scalar() == 0
            assert c.execute(
                text(f"SELECT COUNT(*) FROM {BEWEGUNGEN} WHERE tenant_id = :t"),
                {"t": HAUS_OHNE_KONTEN},
            ).scalar() == 0

    def test_belegnummern_kollidieren_nicht(self, engine, client):
        """``uuid7`` ist zeitgeordnet: Die vorderen Stellen sind der Zeitstempel.

        Eine Belegnummer aus ``bewegung_id[:8]`` war fuer alle Bewegungen
        derselben Minute dieselbe — und ``journal_entries.entry_number`` ist
        systemweit eindeutig, also scheiterte jede zweite Buchung.
        """
        from sqlalchemy import text

        for _ in range(4):
            mitglied_anlegen(client, HAUS_A, anteile=1)
        with engine.connect() as c:
            zeilen = c.execute(
                text(
                    "SELECT entry_number FROM domain_erp.journal_entries "
                    "WHERE tenant_id = :t AND entry_number LIKE 'GENO-%'"
                ),
                {"t": HAUS_A},
            ).scalars().all()
        assert len(zeilen) >= 4
        assert len(set(zeilen)) == len(zeilen)

    def test_mitglied_ohne_anteile_braucht_kein_hauptbuch(self, client):
        """Ohne Zeichnung gibt es nichts zu buchen — der Beitritt gelingt."""
        antwort = client.post(
            f"{WEG}/mitglieder",
            json={
                "name": "Beitritt ohne Zeichnung",
                "adresse": "Dorfstrasse 4",
                "eintrittsdatum": "2026-01-15",
                "iban": "DE02120300000000202051",
                "bank_name": "Pruefbank",
            },
            headers=kopf(HAUS_OHNE_KONTEN),
        )
        assert antwort.status_code == 201, antwort.text

    def test_kein_verzweigen_nach_testdoubles(self):
        """Produktionscode darf nicht wissen, dass er getestet wird."""
        from pathlib import Path

        quelle = Path("app/api/v1/endpoints/genossenschaft.py").read_text(encoding="utf-8")
        assert "unittest.mock" not in quelle
        assert "_is_test_double_session" not in quelle
        # Kein stilles Verschlucken: keine Zeile, die nur ``pass`` ist.
        assert not [z for z in quelle.splitlines() if z.strip() == "pass"]


# ── 6. Austritt und Auseinandersetzung (§ 73 GenG) ──────────────────────────


class TestAustritt:
    def test_austritt_ohne_datum_wird_abgewiesen(self, client):
        mitglied = mitglied_anlegen(client, HAUS_A)
        antwort = client.patch(
            f"{WEG}/mitglieder/{mitglied['id']}",
            json={"status": "AUSGETRETEN"},
            headers=kopf(HAUS_A),
        )
        assert antwort.status_code == 422
        assert "Austrittsdatum" in antwort.text

    def test_austritt_mit_restbestand_wird_abgewiesen(self, client):
        mitglied = mitglied_anlegen(client, HAUS_A, anteile=4)
        antwort = client.patch(
            f"{WEG}/mitglieder/{mitglied['id']}",
            json={"status": "AUSGETRETEN", "austrittsdatum": "2026-06-30"},
            headers=kopf(HAUS_A),
        )
        assert antwort.status_code == 409
        assert "73" in antwort.text

    def test_austritt_nach_vollrueckzahlung(self, client):
        mitglied = mitglied_anlegen(client, HAUS_A, anteile=4)
        assert bewegen(client, HAUS_A, mitglied["id"], "VOLLRUECKZAHLUNG", 4).status_code == 201
        antwort = client.patch(
            f"{WEG}/mitglieder/{mitglied['id']}",
            json={"status": "AUSGETRETEN", "austrittsdatum": "2026-06-30"},
            headers=kopf(HAUS_A),
        )
        assert antwort.status_code == 200, antwort.text
        akte = client.get(f"{WEG}/mitglieder/{mitglied['id']}", headers=kopf(HAUS_A)).json()
        assert akte["status"] == "AUSGETRETEN"
        assert akte["austrittsdatum"] == "2026-06-30"

    def test_eintritt_als_ausgetreten_wird_abgewiesen(self, client):
        antwort = client.post(
            f"{WEG}/mitglieder",
            json={
                "name": "Direkt ausgetreten",
                "adresse": "Dorfstrasse 5",
                "eintrittsdatum": "2026-01-15",
                "status": "AUSGETRETEN",
                "iban": "DE02120300000000202051",
                "bank_name": "Pruefbank",
            },
            headers=kopf(HAUS_A),
        )
        assert antwort.status_code == 422


# ── 7. Mitgliedsnummer und Kapital ─────────────────────────────────────────


class TestMitgliedsnummer:
    def test_nummern_laufen_hoch_und_zaehlen_nicht_zeilen(self, client):
        """Gezaehlt wird die hoechste Nummer: Ein Austritt gibt sie nicht frei."""
        erste = mitglied_anlegen(client, HAUS_B)["mitglieds_nr"]
        zweite = mitglied_anlegen(client, HAUS_B)["mitglieds_nr"]
        assert erste.startswith("M-") and zweite.startswith("M-")
        assert int(erste.rsplit("-", 1)[1]) + 1 == int(zweite.rsplit("-", 1)[1])

    def test_lesefehler_vergibt_nicht_die_nummer_eins(self):
        """Vorher: ``except: seq = 1`` — eine Nummer, die es schon gibt."""
        from app.services import genossenschaft_service as dienst

        db = MagicMock()
        db.execute.side_effect = Exception("not readable")
        with pytest.raises(Exception) as fehler:
            dienst.naechste_mitglieds_nr(db, HAUS_A)
        assert "not readable" in str(fehler.value)


class TestKapitaluebersicht:
    def test_summen_folgen_den_bewegungen(self, client):
        from sqlalchemy import text

        mitglied = mitglied_anlegen(client, HAUS_B, anteile=10, anteilswert_eur=50.0)
        vorher = client.get(f"{WEG}/kapitaluebersicht", headers=kopf(HAUS_B)).json()
        assert bewegen(client, HAUS_B, mitglied["id"], "ERHOEHUNG", 2, wert_eur=100.0).status_code == 201
        nachher = client.get(f"{WEG}/kapitaluebersicht", headers=kopf(HAUS_B)).json()
        assert nachher["total_anteile"] == vorher["total_anteile"] + 2
        assert nachher["total_kapital_eur"] == pytest.approx(vorher["total_kapital_eur"] + 100.0)

    def test_offene_auseinandersetzung_wird_benannt(self, client):
        """Ein Austritt mit Restbestand ist ueber den Weg nicht moeglich — also 0."""
        stand = client.get(f"{WEG}/kapitaluebersicht", headers=kopf(HAUS_B)).json()
        assert stand["offene_auseinandersetzung_anteile"] == 0

    def test_kapital_ist_mandantengebunden(self, client):
        a = client.get(f"{WEG}/kapitaluebersicht", headers=kopf(HAUS_A)).json()
        b = client.get(f"{WEG}/kapitaluebersicht", headers=kopf(HAUS_B)).json()
        summe_a = client.get(
            f"{WEG}/mitglieder", params={"limit": 1000}, headers=kopf(HAUS_A)
        ).json()
        assert a["total_mitglieder"] == len(summe_a)
        assert a["total_mitglieder"] != b["total_mitglieder"] or a["total_anteile"] != b["total_anteile"]


class TestAntwortmodelle:
    def test_offenes_modell_haengt_an_keinem_weg_mehr(self):
        """Ein Modell mit ``extra="allow"`` an jedem Weg beschreibt nichts."""
        from app.api.v1.endpoints import genossenschaft as geno
        from app.api.v1.schemas.genossenschaft_schemas import GenossenschaftOut

        modelle = {
            getattr(route, "response_model", None) for route in geno.router.routes
        }
        assert GenossenschaftOut not in modelle
        assert None not in modelle

    def test_liste_ist_begrenzt(self, client):
        antwort = client.get(f"{WEG}/mitglieder", params={"limit": 2}, headers=kopf(HAUS_A))
        assert antwort.status_code == 200
        assert len(antwort.json()) <= 2
        assert client.get(
            f"{WEG}/mitglieder", params={"limit": 5000}, headers=kopf(HAUS_A)
        ).status_code == 422
