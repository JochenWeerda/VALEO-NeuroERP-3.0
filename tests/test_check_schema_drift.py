"""Die Vergleichslogik des Schema-Abgleichs — und ein Lauf gegen echtes Postgres.

Zweigeteilt, mit Absicht:

- **Reine Unit-Tests** fuer den Vergleich. Sie geben Katalogauszuege hinein und
  pruefen die Funde. Keine Datenbank, kein Ersatzobjekt: Die verglichenen Daten
  sind einfache Listen von Wortverzeichnissen, genau wie sie aus
  ``information_schema`` kommen.
- **Ein Lauf gegen echtes Postgres** (``needs_live_db``). Er legt zwei Schemata
  an, verbiegt eines und prueft, dass der Abgleich die Abweichung findet. Ein
  MagicMock wuerde hier nichts beweisen — die Frage ist, ob die Abfragen gegen
  die Kataloge das Richtige liefern.
"""

from __future__ import annotations

import os
import pathlib
import sys
import uuid

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))

from check_schema_drift import (  # noqa: E402
    lies_katalog,
    vergleiche,
    vergleiche_bedingungen,
    vergleiche_indizes,
    vergleiche_spalten,
    vergleiche_tabellen,
)


def _spalte(schema: str, tabelle: str, spalte: str, typ: str = "character varying",
            laenge: int = 255, skala: int = -1, nullbar: str = "YES") -> dict:
    return {
        "table_schema": schema, "table_name": tabelle, "column_name": spalte,
        "data_type": typ, "laenge": laenge, "skala": skala,
        "is_nullable": nullbar, "column_default": None,
    }


# ── Spalten ────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_eine_fehlende_spalte_wird_gemeldet() -> None:
    referenz = [_spalte("domain_crm", "customers", "company_name")]
    funde = vergleiche_spalten([], referenz)
    assert len(funde) == 1
    assert funde[0]["befund"] == "fehlt"
    assert funde[0]["wo"] == "domain_crm.customers.company_name"


@pytest.mark.unit
def test_eine_zusaetzliche_spalte_wird_gemeldet() -> None:
    """Der Fall vom 29.09.: sales_offers.customer_name gab es nur lokal."""
    ziel = [_spalte("domain_crm", "sales_offers", "customer_name")]
    funde = vergleiche_spalten(ziel, [])
    assert len(funde) == 1
    assert funde[0]["befund"] == "zusaetzlich"


@pytest.mark.unit
def test_gelockerte_nullbarkeit_wird_gemeldet() -> None:
    """Der andere Fall vom 29.09.: die gewachsene Datenbank hatte NOT NULL verloren."""
    ziel = [_spalte("domain_crm", "sales_orders", "description", nullbar="YES")]
    referenz = [_spalte("domain_crm", "sales_orders", "description", nullbar="NO")]
    funde = vergleiche_spalten(ziel, referenz)
    assert len(funde) == 1
    assert funde[0]["befund"] == "anders"
    assert funde[0]["unterschiede"] == {"nullbar": {"ziel": "YES", "referenz": "NO"}}


@pytest.mark.unit
def test_gleiche_spalten_ergeben_keinen_fund() -> None:
    eine = [_spalte("domain_crm", "customers", "company_name")]
    assert vergleiche_spalten(eine, list(eine)) == []


@pytest.mark.unit
def test_ein_anderer_vorgabewert_ist_kein_fund() -> None:
    """Vorgabewerte unterscheiden sich zwischen Staenden, ohne etwas zu bedeuten."""
    a = _spalte("domain_crm", "customers", "id")
    b = dict(a, column_default="nextval('kunden_seq'::regclass)")
    assert vergleiche_spalten([a], [b]) == []


@pytest.mark.unit
def test_laenge_und_typ_werden_verglichen() -> None:
    ziel = [_spalte("domain_crm", "customers", "plz", laenge=10)]
    referenz = [_spalte("domain_crm", "customers", "plz", laenge=5)]
    funde = vergleiche_spalten(ziel, referenz)
    assert funde[0]["unterschiede"] == {"laenge": {"ziel": 10, "referenz": 5}}


# ── Bedingungen ────────────────────────────────────────────────────────


def _bedingung(schema: str, tabelle: str, name: str, art: str, definition: str) -> dict:
    return {"schema": schema, "tabelle": tabelle, "name": name,
            "art": art, "definition": definition}


@pytest.mark.unit
def test_ein_fehlender_fremdschluessel_wird_gemeldet() -> None:
    """Der Fall, der die Testfixtures gruen aussehen liess."""
    referenz = [_bedingung(
        "domain_sales", "delivery_notes", "delivery_notes_customer_id_fkey", "f",
        "FOREIGN KEY (customer_id) REFERENCES domain_crm.customers(id)",
    )]
    funde = vergleiche_bedingungen([], referenz)
    assert len(funde) == 1
    assert funde[0]["art"] == "fremdschluessel"
    assert funde[0]["befund"] == "fehlt"
    assert funde[0]["wo"] == "domain_sales.delivery_notes"


@pytest.mark.unit
def test_eine_fehlende_pruefbedingung_wird_gemeldet() -> None:
    referenz = [_bedingung(
        "domain_sales", "delivery_notes", "ck_delivery_notes_status", "c",
        "CHECK (status IN ('draft', 'printed'))",
    )]
    funde = vergleiche_bedingungen([], referenz)
    assert funde[0]["art"] == "check"
    assert funde[0]["befund"] == "fehlt"


@pytest.mark.unit
def test_ein_anderer_bedingungsname_ist_kein_fund() -> None:
    """Verglichen wird die Aussage, nicht der automatisch erzeugte Name."""
    a = _bedingung("domain_crm", "customers", "customers_pkey", "p", "PRIMARY KEY (id)")
    b = _bedingung("domain_crm", "customers", "customers_pkey1", "p", "PRIMARY KEY (id)")
    assert vergleiche_bedingungen([a], [b]) == []


@pytest.mark.unit
def test_eine_andere_bedingungsaussage_ist_zwei_funde() -> None:
    """Eine geaenderte Bedingung fehlt in der einen und ist in der anderen zusaetzlich."""
    a = _bedingung("domain_sales", "delivery_notes", "ck", "c", "CHECK (status IN ('draft'))")
    b = _bedingung("domain_sales", "delivery_notes", "ck", "c",
                   "CHECK (status IN ('draft', 'posted'))")
    funde = vergleiche_bedingungen([a], [b])
    assert {f["befund"] for f in funde} == {"fehlt", "zusaetzlich"}


# ── Indizes ────────────────────────────────────────────────────────────


@pytest.mark.unit
def test_ein_anderer_indexname_ist_kein_fund() -> None:
    a = {"schema": "domain_crm", "tabelle": "customers", "name": "ix_a",
         "definition": "CREATE INDEX ix_a ON domain_crm.customers USING btree (tenant_id)"}
    b = dict(a, name="ix_b",
             definition="CREATE INDEX ix_b ON domain_crm.customers USING btree (tenant_id)")
    assert vergleiche_indizes([a], [b]) == []


@pytest.mark.unit
def test_ein_fehlender_index_wird_gemeldet() -> None:
    referenz = [{
        "schema": "domain_agrar", "tabelle": "feldbuch_massnahmen", "name": "ix_sd",
        "definition": "CREATE INDEX ix_sd ON domain_agrar.feldbuch_massnahmen "
                      "USING btree (schlag_id, datum)",
    }]
    funde = vergleiche_indizes([], referenz)
    assert len(funde) == 1
    assert funde[0]["befund"] == "fehlt"


# ── Tabellen und das Zusammenspiel ─────────────────────────────────────


@pytest.mark.unit
def test_eine_fehlende_tabelle_wird_gemeldet() -> None:
    referenz = [_spalte("domain_pos", "promotions", "id")]
    funde = vergleiche_tabellen([], referenz)
    assert funde == [{"art": "tabelle", "befund": "fehlt", "wo": "domain_pos.promotions"}]


@pytest.mark.unit
def test_eine_fehlende_tabelle_ertraenkt_die_liste_nicht() -> None:
    """Fehlt die Tabelle, sind ihre dreissig Spalten kein eigener Fund.

    Sonst waere eine fehlende Tabelle mit vielen Spalten lauter als alles
    andere, und die uebrigen Funde gingen darin unter.
    """
    referenz = {
        "spalten": [
            _spalte("domain_pos", "promotions", "id"),
            _spalte("domain_pos", "promotions", "name"),
            _spalte("domain_pos", "promotions", "rabatt"),
        ],
        "bedingungen": [_bedingung("domain_pos", "promotions", "pk", "p", "PRIMARY KEY (id)")],
        "indizes": [],
    }
    ziel = {"spalten": [], "bedingungen": [], "indizes": []}
    funde = vergleiche(ziel, referenz)
    assert len(funde) == 1
    assert funde[0]["art"] == "tabelle"


@pytest.mark.unit
def test_zwei_gleiche_staende_ergeben_keinen_fund() -> None:
    stand = {
        "spalten": [_spalte("domain_crm", "customers", "id", nullbar="NO")],
        "bedingungen": [_bedingung("domain_crm", "customers", "pk", "p", "PRIMARY KEY (id)")],
        "indizes": [],
    }
    import copy

    assert vergleiche(copy.deepcopy(stand), copy.deepcopy(stand)) == []


# ── Der Lauf gegen echtes Postgres ─────────────────────────────────────


@pytest.mark.integration
@pytest.mark.needs_live_db
def test_der_abgleich_findet_eine_echte_abweichung() -> None:
    """Gegen echtes Postgres, nicht gegen ein Ersatzobjekt.

    Zwei Schemata mit derselben Tabelle; in einem fehlt eine Spalte, ein
    Fremdschluessel und eine Pruefbedingung. Der Abgleich muss genau das
    finden — und zwar ueber die Katalogabfragen, nicht ueber eine Annahme
    darueber, was sie liefern.
    """
    from sqlalchemy import create_engine, text

    url = os.environ.get(
        "DATABASE_URL",
        "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_neuro_erp",
    )
    kennung = uuid.uuid4().hex[:8]
    voll, arm = f"probe_voll_{kennung}", f"probe_arm_{kennung}"

    try:
        engine = create_engine(url)
        with engine.connect() as c:
            c.execute(text("SELECT 1"))
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")

    with engine.begin() as v:
        v.execute(text(f"CREATE SCHEMA {voll}"))
        v.execute(text(f"CREATE SCHEMA {arm}"))
        v.execute(text(f"CREATE TABLE {voll}.eltern (id varchar(64) PRIMARY KEY)"))
        v.execute(text(f"CREATE TABLE {arm}.eltern (id varchar(64) PRIMARY KEY)"))
        v.execute(text(
            f"CREATE TABLE {voll}.beleg ("
            f"  id varchar(64) PRIMARY KEY,"
            f"  eltern_id varchar(64) REFERENCES {voll}.eltern(id),"
            f"  status varchar(20) NOT NULL CHECK (status IN ('offen', 'fertig')),"
            f"  bemerkung text"
            f")"
        ))
        # Derselbe Beleg, aber verbogen: ohne Fremdschluessel, ohne
        # Pruefbedingung, ohne bemerkung, und status ist nullbar.
        v.execute(text(
            f"CREATE TABLE {arm}.beleg ("
            f"  id varchar(64) PRIMARY KEY,"
            f"  eltern_id varchar(64),"
            f"  status varchar(20)"
            f")"
        ))

    try:
        referenz = lies_katalog(url, [voll])
        ziel = lies_katalog(url, [arm])
        # Die Schemanamen unterscheiden sich; fuer den Vergleich werden sie
        # gleichgesetzt, sonst waere jede Zeile ein Fund.
        for teil in ("spalten", "bedingungen", "indizes"):
            for zeile in ziel[teil]:
                schluessel = "table_schema" if teil == "spalten" else "schema"
                zeile[schluessel] = voll
        funde = vergleiche(ziel, referenz)

        arten = {(f["art"], f["befund"]) for f in funde}
        assert ("spalte", "fehlt") in arten, funde
        assert ("fremdschluessel", "fehlt") in arten, funde
        assert ("check", "fehlt") in arten, funde
        assert ("spalte", "anders") in arten, funde

        fehlende_spalten = {
            f["wo"] for f in funde if f["art"] == "spalte" and f["befund"] == "fehlt"
        }
        assert f"{voll}.beleg.bemerkung" in fehlende_spalten

        gelockert = [
            f for f in funde
            if f["art"] == "spalte" and f["befund"] == "anders"
            and f["wo"].endswith(".status")
        ]
        assert gelockert, funde
        assert gelockert[0]["unterschiede"]["nullbar"] == {"ziel": "YES", "referenz": "NO"}
    finally:
        with engine.begin() as v:
            v.execute(text(f"DROP SCHEMA IF EXISTS {voll} CASCADE"))
            v.execute(text(f"DROP SCHEMA IF EXISTS {arm} CASCADE"))
