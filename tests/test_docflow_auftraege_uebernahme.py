"""Verkaufsauftraege gehen nach DocFlow; domain_crm.sales_orders wird Sicht (BELEG-052, 09.11.2026).

Auf dem Pruefstand: alte Auftraege anlegen, die Migration in einer Transaktion ausfuehren, die zurueckgerollt wird.
Geprueft wird, was fachlich zaehlt - derselbe Beleg (ID, Nummer, Kunde), seine Kopfangaben als Bausteine, Positionen
mit Summen ohne angenommene Steuer, der Stand, die Ursprungsdaten und die Sicht fuer die bisherigen Leser.
"""
from __future__ import annotations

import importlib.util
import os
import uuid
from pathlib import Path

import pytest
import sqlalchemy as sa
from alembic.migration import MigrationContext
from alembic.operations import Operations

pytestmark = pytest.mark.integration

WURZEL = Path(__file__).resolve().parents[1]
DB_URL = os.environ.get("TEST_DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_probe")


def _modul(name: str):
    spec = importlib.util.spec_from_file_location(name, WURZEL / f"alembic/versions/{name}.py")
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    return modul


def _migriere(verbindung, name: str) -> None:
    with Operations.context(MigrationContext.configure(verbindung)):
        _modul(name).upgrade()


@pytest.fixture
def stand():
    from testgrenze import pruefstand_erlaubt

    try:
        engine = sa.create_engine(DB_URL, connect_args={"connect_timeout": 5, "application_name": "agent:claude"})
        verbindung = engine.connect()
    except Exception as fehler:  # noqa: BLE001
        pytest.skip(f"Datenbank nicht erreichbar: {fehler}")
    assert pruefstand_erlaubt(engine.url)
    aussen = verbindung.begin()
    art = verbindung.execute(sa.text(
        "SELECT c.relkind FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace "
        "WHERE n.nspname = 'domain_crm' AND c.relname = 'sales_orders'")).scalar()
    if art == "v":
        # Frischer Pruefstand nach ``upgrade head``: erst der Rueckweg (in dieser Transaktion), dann wird geprueft.
        with Operations.context(MigrationContext.configure(verbindung)):
            _modul("docflow_auftraege_uebernahme_20261109").downgrade()
    elif art != "r":
        aussen.rollback()
        verbindung.close()
        pytest.skip("domain_crm.sales_orders fehlt im Pruefstand")
    if not verbindung.execute(sa.text(
            "SELECT 1 FROM information_schema.columns WHERE table_schema = 'domain_docflow' "
            "AND table_name = 'document_headers' AND column_name = 'bausteine'")).scalar():
        _migriere(verbindung, "docflow_kopfbausteine_20261109")
    mandant, kunde = f"au-{uuid.uuid4().hex[:8]}", str(uuid.uuid4())
    verbindung.execute(sa.text("INSERT INTO domain_shared.tenants (id, name, is_active) VALUES (:t, :t, true)"),
                       {"t": mandant})
    verbindung.execute(sa.text("INSERT INTO domain_crm.customers (id, tenant_id, customer_number, company_name) "
                               "VALUES (:id, :t, 'K-AU', 'Hof Uebernahme')"), {"id": kunde, "t": mandant})
    try:
        yield {"db": verbindung, "mandant": mandant, "kunde": kunde}
    finally:
        aussen.rollback()
        verbindung.close()


def _alt(s, nummer: str, status: str, **kopf) -> str:
    kennung = str(uuid.uuid4())
    werte = {"subject": "", "description": "", "notes": None, "contact_person": None, "delivery_date": None,
             "delivery_address": None, "shipping_method": None, "payment_terms": None, **kopf}
    s["db"].execute(sa.text(
        "INSERT INTO domain_crm.sales_orders (id, tenant_id, customer_id, order_number, status, currency, total_amount, "
        "subject, description, notes, contact_person, delivery_date, delivery_address, shipping_method, payment_terms, "
        "created_at, version) VALUES (:id, :t, :k, :nr, :st, 'EUR', 999, :subject, :description, :notes, "
        ":contact_person, :delivery_date, :delivery_address, :shipping_method, :payment_terms, "
        "'2026-10-01T09:00:00+02:00', 3)"),
        {"id": kennung, "t": s["mandant"], "k": s["kunde"], "nr": nummer, "st": status, **werte})
    return kennung


def _position(s, auftrag: str, nr: int, menge: float, preis: float, rabatt: float = 0) -> None:
    s["db"].execute(sa.text(
        "INSERT INTO domain_crm.sales_order_items (id, tenant_id, order_id, line_number, article_number, description, "
        "quantity, unit, unit_price, discount_percent, line_total) "
        "VALUES (:id, :t, :o, :nr, 'WEIZEN', 'Weizen A', :m, 'dt', :p, :r, 1)"),
        {"id": str(uuid.uuid4()), "t": s["mandant"], "o": auftrag, "nr": nr, "m": menge, "p": preis, "r": rabatt})


def _kopf(s, beleg: str) -> dict:
    return dict(s["db"].execute(sa.text(
        "SELECT * FROM domain_docflow.document_headers WHERE id = :id"), {"id": beleg}).mappings().one())


def test_auftrag_wird_derselbe_docflow_beleg_mit_bausteinen_und_summen(stand):
    auftrag = _alt(stand, "AU-ALT-1", "bestaetigt", subject="Weizen Ernte 2026", notes="Rampe 2",
                   contact_person="Frau Meyer", delivery_date="2026-12-01T00:00:00+01:00",
                   delivery_address="Hof 3, Leer", payment_terms="14 Tage 2 %")
    _position(stand, auftrag, 1, 10, 21.5)
    _position(stand, auftrag, 2, 4, 30, rabatt=10)
    _migriere(stand["db"], "docflow_auftraege_uebernahme_20261109")

    kopf = _kopf(stand, auftrag)
    assert (kopf["doc_type"], kopf["doc_number"], kopf["status"]) == ("sales_order", "AU-ALT-1", "open")
    assert (kopf["customer_id"], kopf["source_system"], kopf["source_ref"]) == (
        stand["kunde"], "domain_crm.sales_orders", auftrag)
    assert kopf["bausteine"] == {
        "texte": {"betreff": "Weizen Ernte 2026", "notiz": "Rampe 2"},
        "kontakt": {"ansprechpartner": "Frau Meyer"},
        "lieferung": {"liefertermin": "2026-12-01", "lieferadresse": "Hof 3, Leer"},
        "zahlung": {"zahlungsbedingung": "14 Tage 2 %"},
    }
    # 10 x 21,50 + 4 x 30 x 0,9: aus den Positionen gerechnet, nicht aus dem alten Kopfbetrag; keine Steuer angenommen.
    assert (float(kopf["total_net"]), float(kopf["total_tax"]), float(kopf["total_gross"])) == (323.0, 0.0, 323.0)
    positionen = stand["db"].execute(sa.text(
        "SELECT line_number, quantity, unit, tax_code, tax_rate, line_total_net FROM domain_docflow.document_items "
        "WHERE header_id = :h ORDER BY line_number"), {"h": auftrag}).all()
    assert [(p[0], float(p[1]), p[2], p[3], float(p[4]), float(p[5])) for p in positionen] == [
        (1, 10.0, "dt", None, 0.0, 215.0), (2, 4.0, "dt", None, 0.0, 108.0)]
    historie = stand["db"].execute(sa.text(
        "SELECT to_status, command FROM domain_docflow.document_status_history WHERE header_id = :h"),
        {"h": auftrag}).all()
    assert [tuple(h) for h in historie] == [("open", "migration:auftraege_20261109")]


def test_stand_wird_zugeordnet_nicht_geraten(stand):
    entwurf = _alt(stand, "AU-ALT-2", "ENTWURF")
    geliefert = _alt(stand, "AU-ALT-3", "geliefert")
    storniert = _alt(stand, "AU-ALT-4", "cancelled")
    _migriere(stand["db"], "docflow_auftraege_uebernahme_20261109")
    assert [_kopf(stand, b)["status"] for b in (entwurf, geliefert, storniert)] == ["draft", "completed", "cancelled"]


def test_unbekannter_stand_haelt_die_migration_an(stand):
    _alt(stand, "AU-ALT-5", "irgendwas")
    with pytest.raises(RuntimeError, match="Unbekannter Auftragsstand"):
        _migriere(stand["db"], "docflow_auftraege_uebernahme_20261109")


def test_sicht_liefert_den_lesern_die_alten_spalten_und_ursprung_bleibt(stand):
    auftrag = _alt(stand, "AU-ALT-6", "open", subject="Gerste", delivery_date="2026-11-20T00:00:00+01:00")
    _position(stand, auftrag, 1, 2, 50)
    _migriere(stand["db"], "docflow_auftraege_uebernahme_20261109")

    zeile = dict(stand["db"].execute(sa.text(
        "SELECT order_number, customer_name, subject, status, total_amount, delivery_date::date AS termin, deleted_at "
        "FROM domain_crm.sales_orders WHERE id = :id"), {"id": auftrag}).mappings().one())
    assert zeile == {"order_number": "AU-ALT-6", "customer_name": "Hof Uebernahme", "subject": "Gerste",
                     "status": "open", "total_amount": 100, "termin": __import__("datetime").date(2026, 11, 20),
                     "deleted_at": None}
    assert stand["db"].execute(sa.text(
        "SELECT count(*) FROM domain_crm.sales_order_items WHERE order_id = :id"), {"id": auftrag}).scalar() == 1
    # Ursprungsdaten unveraendert erhalten
    alt = stand["db"].execute(sa.text(
        "SELECT total_amount, version FROM domain_crm.sales_orders_vor_docflow WHERE id = :id"), {"id": auftrag}).one()
    assert (float(alt[0]), alt[1]) == (999.0, 3)
    # Die Sicht prueft mit den Rechten des Lesers: es gilt die Mandantentrennung von DocFlow.
    for sicht in ("domain_crm.sales_orders", "domain_crm.sales_order_items"):
        optionen = stand["db"].execute(sa.text("SELECT reloptions FROM pg_class WHERE oid = CAST(:s AS regclass)"),
                                       {"s": sicht}).scalar()
        assert "security_invoker=true" in (optionen or []), sicht
    # Schreiben geht nur noch ueber DocFlow
    with pytest.raises(sa.exc.DBAPIError):
        with stand["db"].begin_nested():
            stand["db"].execute(sa.text("UPDATE domain_crm.sales_orders SET status = 'geliefert' WHERE id = :id"),
                                {"id": auftrag})
