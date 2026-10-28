"""RLS-Domain logistics: Touren und alles, was an ihnen haengt, je Mandant; Wege mit Mandant aus dem Token.

Bis 28.10.2026 lieferte ``GET /logistik/tours`` ohne Kopf die Touren aller Mandanten; Detail, Live-Status, Tracking,
Optimierung und ePOD lasen gar nicht nach Mandant, Stopps und Ereignisse liessen sich an fremde Touren haengen, die
ePOD-Abrechnung las Stopps nur nach ID; die Spediteur-Rechnung meldete ``gebucht`` fuer einen Buchungsentwurf und eine
verworfene doppelte Nummer. Zwischen Touren und ihren Kindern gab es keinen einzigen Fremdschluessel.

Pruefhilfe und Rahmen: tests/rls_domain_support.py (valeo_probe, zurueckgerollt). Die Fachketten laufen als
Tabelleneigentuemer (ohne RLS): Sie pruefen den Code, nicht die Policies.
"""

from __future__ import annotations

import inspect
from uuid import uuid4

import pytest
import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy.orm import Session

import rls_domain_support as support
from app.api.v1.endpoints import logistics_freight as fracht
from app.api.v1.endpoints import logistics_tours as touren
from app.core.tenant import get_tenant_id
from app.core.tenant_context import tenant_scope
from rls_domain_support import A, B, SYSTEM

LOG = "domain_logistics"
TOURS, STOPS = f"{LOG}.tours", f"{LOG}.tour_stops"
ISOLATED = (TOURS, STOPS, f"{LOG}.tour_events", f"{LOG}.tour_disposition_checks", f"{LOG}.epod_settlements",
            f"{LOG}.freight_tariffs", f"{LOG}.carrier_invoices")
LINKS = (
    (STOPS, "tour_id", TOURS),
    (f"{LOG}.tour_events", "tour_id", TOURS),
    (f"{LOG}.tour_disposition_checks", "tour_id", TOURS),
    (f"{LOG}.epod_settlements", "tour_id", TOURS),
    (f"{LOG}.epod_settlements", "stop_id", STOPS),
    (f"{LOG}.carrier_invoices", "tour_id", TOURS),
)
PARENTS = (TOURS, STOPS)
CHILDREN = tuple(dict.fromkeys(child for child, _, _ in LINKS))


def _links_of(table: str):
    return [(column, parent) for child, column, parent in LINKS if child == table]


@pytest.fixture(scope="module")
def probe():
    with support.probe(ISOLATED) as conn:
        support.ensure_tenants(conn, A, B, SYSTEM)
        rows = {}
        for tenant in (A, B, SYSTEM):
            for table in tuple(dict.fromkeys(PARENTS + ISOLATED)):
                links = {column: rows[parent, tenant] for column, parent in _links_of(table) if (parent, tenant) in rows}
                full = support.seed_row(conn, table, tenant, **links)
                rows["full", table, tenant] = full
                rows[table, tenant] = str(full["id"])
        rows["spare", TOURS] = str(support.seed_row(conn, TOURS, B)["id"])
        rows["spare", STOPS] = str(support.seed_row(conn, STOPS, B, tour_id=rows["spare", TOURS])["id"])
        support.as_app(conn)
        yield conn, rows


@pytest.fixture
def db(probe):
    conn, rows = probe
    savepoint = conn.begin_nested()
    yield conn, rows
    if savepoint.is_active:
        savepoint.rollback()


def test_policy_formen(db):
    conn, _ = db
    for table in ISOLATED:
        assert support.shape(conn, table) == ("getrennt", ""), table


@pytest.mark.parametrize("table", ISOLATED)
def test_mandantengrenze_je_tabelle(db, table):
    conn, rows = db
    support.assert_tenant_isolation(conn, table, rows[table, A], rows[table, B], rows[table, SYSTEM])


def _other_references(conn, rows, child: str, column: str) -> dict:
    full = rows["full", child, A]
    columns = {c for _, cols, parent, _ in conn.execute(sa.text(support.FKS_SQL), {"t": child})
               for c in cols if parent != "domain_shared.tenants"}
    return {c: full[c] for c in columns - {column, "tenant_id"} if full.get(c) is not None}


@pytest.mark.parametrize("child,column,parent", LINKS, ids=[f"{c.split('.')[1]}.{col}" for c, col, _ in LINKS])
def test_kein_verweis_auf_fremden_eltern(db, child, column, parent):
    conn, rows = db
    foreign = rows["spare", parent]
    constraint = f"fk_{child.split('.')[1]}_{column}_tenant"[:63]
    with tenant_scope(A, "test"):
        andere = _other_references(conn, rows, child, column)
        if "stop_id" in andere:  # eine Abrechnung je Stopp: fuer den Tour-Fall ein frischer eigener Stopp
            andere["stop_id"] = support.insert_row(conn, STOPS, A, tour_id=rows[TOURS, A])
        message = support.rejected_insert_with(conn, child, A, "id", **{column: foreign}, **andere)
        assert constraint in message, message
        message = support.rejected(conn, f"UPDATE {child} SET {column} = :p WHERE id = :i",
                                   {"p": foreign, "i": rows[child, A]})
    assert constraint in message, message


def test_mandant_pflicht_und_vorgabe_aus_dem_kontext(db):
    conn, _ = db
    for table in ISOLATED:
        notnull, default = conn.execute(sa.text(
            "SELECT a.attnotnull, pg_get_expr(d.adbin, d.adrelid) FROM pg_attribute a LEFT JOIN pg_attrdef d "
            "ON d.adrelid = a.attrelid AND d.adnum = a.attnum WHERE a.attrelid = to_regclass(:t) AND a.attname = 'tenant_id'"),
            {"t": table}).one()
        assert (notnull, default) == (True, "rls_current_tenant()"), table


def test_tour_mit_verweisen_behaelt_ihren_mandanten(db):
    conn, rows = db
    for parent in PARENTS:
        message = support.as_owner_rejected(conn, f"UPDATE {parent} SET tenant_id = :b WHERE id = :i",
                                            {"b": B, "i": rows[parent, A]})
        assert "foreign key constraint" in message and "_tena" in message, (parent, message)


# --- Fachwege (als Eigentuemer, ohne RLS) ------------------------------------------------------------------------


@pytest.fixture
def fach(db):
    conn, rows = db
    conn.execute(sa.text("RESET ROLE"))
    session = Session(bind=conn, join_transaction_mode="create_savepoint")
    try:
        yield session, rows
    finally:
        session.close()


def _404(aufruf):
    with pytest.raises(HTTPException) as info:
        aufruf()
    assert info.value.status_code == 404, info.value.detail


def test_touren_wege_nur_im_eigenen_mandanten(fach):
    db, rows = fach

    def statistik(t):
        return touren.get_statistics(date_from=None, date_to=None, vehicle_id=None, tenant_id=t, db=db)["total_tours"]

    a_vorher, b_vorher = statistik(A), statistik(B)
    tour = touren.create_tour(touren.TourIn(stops=[touren.TourStopIn(address="Hof 1", lat=53.1, lng=7.2)]), tenant_id=A, db=db)
    tid = tour["id"]
    stopp = db.execute(sa.text("SELECT id FROM domain_logistics.tour_stops WHERE tour_id = :t"), {"t": tid}).scalar()
    assert tid in [t["id"] for t in touren.list_tours(date=None, vehicle_id=None, status=None, tenant_id=A, db=db)]
    assert tid not in [t["id"] for t in touren.list_tours(date=None, vehicle_id=None, status=None, tenant_id=B, db=db)]
    assert touren.get_tour(tid, include_delivery_hints=False, tenant_id=A, db=db)["id"] == tid
    _404(lambda: touren.get_tour(tid, include_delivery_hints=False, tenant_id=B, db=db))
    _404(lambda: touren.add_stop(tid, touren.TourStopIn(address="fremd"), tenant_id=B, db=db))
    _404(lambda: touren.add_event(tid, touren.TourEventIn(event_type="GPS", lat=1, lng=1), tenant_id=B, db=db))
    _404(lambda: touren.live_status(tid, tenant_id=B, db=db))
    _404(lambda: touren.public_tracking(tid, tenant_id=B, db=db))
    _404(lambda: touren.optimize_stops(tid, depot_lat=0, depot_lng=0, tenant_id=B, db=db))
    _404(lambda: touren.get_pod(tid, stopp, tenant_id=B, db=db))
    _404(lambda: touren.patch_stop(tid, stopp, touren.TourStopPatch(status="ANGEFAHREN"), tenant_id=B, db=db))
    _404(lambda: touren.save_pod(tid, stopp, touren.PodIn(signature_base64="x", recipient_name="x", delivered_at="2026-10-28"),
                                 tenant_id=B, db=db))
    _404(lambda: touren.cancel_stop(tid, stopp, touren.TourCancelIn(), tenant_id=B, db=db))
    _404(lambda: touren.cancel_tour(tid, touren.TourCancelIn(), tenant_id=B, db=db))
    assert (statistik(A), statistik(B)) == (a_vorher + 1, b_vorher)
    assert touren.cancel_tour(tid, touren.TourCancelIn(grund="Test"), tenant_id=A, db=db)["status"] == "STORNIERT"


def test_epod_abrechnung_nur_eigener_stopp(fach):
    db, rows = fach
    from app.services.logistics_epod_service import EpodError, settle_epod

    db.execute(sa.text("UPDATE domain_logistics.tour_stops SET status = 'GELIEFERT' WHERE id = :s"), {"s": rows[STOPS, B]})
    tour_b = rows["full", STOPS, B]["tour_id"]
    with pytest.raises(EpodError):
        settle_epod(db, tour_id=tour_b, stop_id=rows[STOPS, B], tenant_id=A)
    with pytest.raises(EpodError):  # Stopp gehoert nicht zu dieser Tour
        settle_epod(db, tour_id=rows[TOURS, A], stop_id=rows[STOPS, B], tenant_id=B)


def test_frachttarife_und_spediteur_rechnung(fach, monkeypatch):
    db, rows = fach
    tarif = fracht.create_tariff(fracht.FreightTariffIn(carrier_id="SPED-1", price_per_100kg=4.5), tenant_id=A, db=db)
    assert tarif["id"] in [t["id"] for t in fracht.list_tariffs(carrier_id=None, tenant_id=A, db=db)]
    assert tarif["id"] not in [t["id"] for t in fracht.list_tariffs(carrier_id=None, tenant_id=B, db=db)]
    _404(lambda: fracht.cancel_tariff(tarif["id"], fracht.FreightTariffCancelIn(grund="x"), tenant_id=B, db=db))

    rechnung = dict(tour_id=rows[TOURS, A], carrier_id="SPED-1", invoice_number=f"SR-{uuid4().hex[:6]}",
                    invoice_date="2026-10-28", net_amount_eur=100.0)
    _404(lambda: fracht.create_carrier_invoice(fracht.CarrierInvoiceIn(**rechnung), tenant_id=B, db=db))
    erste = fracht.create_carrier_invoice(fracht.CarrierInvoiceIn(**rechnung), tenant_id=A, db=db)
    assert erste["status"] in ("entwurf", "offen") and erste["status"] != "gebucht"
    gespeichert = db.execute(sa.text("SELECT status FROM domain_logistics.carrier_invoices WHERE id = :i"), {"i": erste["id"]}).scalar()
    assert gespeichert == erste["status"]
    with pytest.raises(HTTPException) as info:
        fracht.create_carrier_invoice(fracht.CarrierInvoiceIn(**rechnung), tenant_id=A, db=db)
    assert info.value.status_code == 409


def test_jeder_weg_nimmt_den_mandanten_aus_dem_token():
    funde = []
    for modul in (touren, fracht):
        for route in modul.router.routes:
            parameter = inspect.signature(route.endpoint).parameters
            if "x_tenant_id" in parameter:
                funde.append(f"{modul.__name__}:{route.path}")
            if "tenant_id" in parameter and getattr(parameter["tenant_id"].default, "dependency", None) is not get_tenant_id:
                funde.append(f"{modul.__name__}:{route.path}:tenant_id")
            if "tenant_id" not in parameter and "db" in parameter:
                funde.append(f"{modul.__name__}:{route.path}:ohne Mandant")
    assert funde == []
