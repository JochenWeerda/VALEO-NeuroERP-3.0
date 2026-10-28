"""RLS-Domain ops Teil 2: die zehn domain_ops-Tabellen ohne Mandantenspalte, die live leer sind.

Dokumente und Versionen, Fahrzeug-Bussgelder/-Schaeden/-Statushistorie/-Touren, Rahmenvertraege, Waagen, Wiegungen und
Strecken-Frachttarife hatten bis 28.10.2026 **keinen** Mandanten; ihre Wege lasen und schrieben mandantenuebergreifend,
Urheber kamen aus dem Rumpf (``hochgeladenVon``, ``erstellt_von``, ``benutzer``), Rahmenvertragsnummern waren
systemweit eindeutig, und jede partiepflichtige Wiegung scheiterte, weil Pruefangaben als Spalten in das Modell gingen.

Pruefhilfe und Rahmen: tests/rls_domain_support.py (valeo_probe, zurueckgerollt). Die Fachketten laufen als
Tabelleneigentuemer (ohne RLS): Sie pruefen den Code, nicht die Policies.
"""

from __future__ import annotations

import asyncio
import inspect
from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import uuid4

import pytest
import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy.orm import Session

import rls_domain_support as support
from app.api.v1.endpoints import compat, dokumente, fuhrpark, strecke_speditionen, vertraege, waage
from app.api.v1.schemas.fuhrpark import SchadenPayload
from app.core.tenant_context import tenant_scope
from app.domains.operations.repository import DokumentRepository, WaageRepository
from rls_domain_support import A, B, SYSTEM

OPS = "domain_ops"
DOKUMENTE, WAAGEN, FAHRZEUGE = f"{OPS}.ops_dokumente", f"{OPS}.ops_waagen", f"{OPS}.ops_fahrzeuge"
ISOLATED = (
    DOKUMENTE, f"{OPS}.ops_dokument_versionen", f"{OPS}.ops_fahrzeug_bussgeld", f"{OPS}.ops_fahrzeug_schaeden",
    f"{OPS}.ops_fahrzeug_status_historie", f"{OPS}.ops_fahrzeug_touren", f"{OPS}.ops_rahmenvertraege", WAAGEN,
    f"{OPS}.ops_wiegungen", f"{OPS}.strecke_speditionen_frachttarife",
)
LINKS = (
    (f"{OPS}.ops_dokument_versionen", "dokument_id", DOKUMENTE),
    (f"{OPS}.ops_fahrzeug_bussgeld", "fahrzeug_id", FAHRZEUGE),
    (f"{OPS}.ops_fahrzeug_schaeden", "fahrzeug_id", FAHRZEUGE),
    (f"{OPS}.ops_fahrzeug_status_historie", "fahrzeug_id", FAHRZEUGE),
    (f"{OPS}.ops_fahrzeug_touren", "fahrzeug_id", FAHRZEUGE),
    (f"{OPS}.ops_wiegungen", "waage_id", WAAGEN),
)
PARENTS = (DOKUMENTE, WAAGEN, FAHRZEUGE)


@pytest.fixture(scope="module")
def probe():
    with support.probe(ISOLATED + (FAHRZEUGE,)) as conn:
        support.ensure_tenants(conn, A, B, SYSTEM)
        rows = {}
        for tenant in (A, B, SYSTEM):
            for table in tuple(dict.fromkeys(PARENTS + ISOLATED)):
                links = {column: rows[parent, tenant] for child, column, parent in LINKS
                         if child == table and (parent, tenant) in rows}
                rows[table, tenant] = str(support.seed_row(conn, table, tenant, **links)["id"])
        for parent in PARENTS:
            rows["spare", parent] = support.insert_row(conn, parent, B)
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


def test_mandant_pflicht_und_vorgabe_aus_dem_kontext(db):
    conn, _ = db
    for table in ISOLATED:
        notnull, default = conn.execute(sa.text(
            "SELECT a.attnotnull, pg_get_expr(d.adbin, d.adrelid) FROM pg_attribute a LEFT JOIN pg_attrdef d "
            "ON d.adrelid = a.attrelid AND d.adnum = a.attnum WHERE a.attrelid = to_regclass(:t) AND a.attname = 'tenant_id'"),
            {"t": table}).one()
        assert (notnull, default) == (True, "rls_current_tenant()"), table


@pytest.mark.parametrize("child,column,parent", LINKS, ids=[f"{c.split('.')[1]}.{col}" for c, col, _ in LINKS])
def test_kein_verweis_auf_fremden_eltern(db, child, column, parent):
    conn, rows = db
    constraint = f"fk_{child.split('.')[1]}_{column}_tenant"[:63]
    with tenant_scope(A, "test"):
        message = support.rejected(conn, f"UPDATE {child} SET {column} = :p WHERE id = :i",
                                   {"p": rows["spare", parent], "i": rows[child, A]})
    assert constraint in message, message


def test_rahmenvertragsnummer_je_mandant(db):
    conn, rows = db
    tabelle = f"{OPS}.ops_rahmenvertraege"
    nummer = f"RV-{uuid4().hex[:8]}"
    savepoint = conn.begin_nested()
    try:
        conn.execute(sa.text("RESET ROLE"))
        conn.execute(sa.text(f"UPDATE {tabelle} SET nummer = :n WHERE id IN (:a, :b)"),
                     {"n": nummer, "a": rows[tabelle, A], "b": rows[tabelle, B]})
        with pytest.raises(sa.exc.IntegrityError, match="duplicate key"):
            with conn.begin_nested():
                conn.execute(sa.text(f"UPDATE {tabelle} SET nummer = :n WHERE id = :s"),
                             {"n": nummer, "s": rows[tabelle, SYSTEM]})
                conn.execute(sa.text(f"UPDATE {tabelle} SET tenant_id = :a WHERE id = :s"),
                             {"a": A, "s": rows[tabelle, SYSTEM]})
    finally:
        savepoint.rollback()


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


ANFRAGE = SimpleNamespace(state=SimpleNamespace(token_claims={"sub": "nutzer-a"}))


def _status(aufruf) -> int:
    with pytest.raises(HTTPException) as info:
        asyncio.run(aufruf)
    return info.value.status_code


def test_dokumente_nur_im_eigenen_mandanten_urheber_aus_token(fach):
    db, _ = fach
    neu = asyncio.run(dokumente.create_dokument(
        {"name": "Lieferschein.pdf", "typ": "PDF", "kategorie": "Lieferscheine", "hochgeladen_von": "gefaelscht",
         "tenant_id": B}, request=ANFRAGE, tenant_id=A, db=db))
    assert (neu.tenant_id, neu.hochgeladen_von, neu.created_by) == (A, "nutzer-a", "nutzer-a")
    assert asyncio.run(dokumente.get_dokument(neu.id, tenant_id=A, db=db)).id == neu.id
    assert _status(dokumente.get_dokument(neu.id, tenant_id=B, db=db)) == 404
    assert _status(dokumente.update_dokument(neu.id, {"name": "x"}, request=ANFRAGE, tenant_id=B, db=db)) == 404
    assert _status(dokumente.delete_dokument(neu.id, request=ANFRAGE, hard_delete=False, tenant_id=B, db=db)) == 404
    assert _status(dokumente.create_version(neu.id, {"name": "v2"}, request=ANFRAGE, tenant_id=B, db=db)) == 404
    version = asyncio.run(dokumente.create_version(neu.id, {"name": "v2", "erstellt_von": "gefaelscht"},
                                                   request=ANFRAGE, tenant_id=A, db=db))
    assert (version.tenant_id, version.erstellt_von, version.version) == (A, "nutzer-a", 1)
    ids_b = {d.id for d in asyncio.run(dokumente.list_dokumente(kategorie=None, typ=None, suche=None, skip=0, limit=100,
                                                                 tenant_id=B, db=db))["items"]}
    assert neu.id not in ids_b
    asyncio.run(dokumente.delete_dokument(neu.id, request=ANFRAGE, hard_delete=False, tenant_id=A, db=db))
    assert DokumentRepository(db, A).get_by_id(neu.id).geloescht_von == "nutzer-a"


def test_lieferanten_dokumente_im_eigenen_mandanten(fach):
    db, _ = fach
    lieferant = f"L-{uuid4().hex[:6]}"
    asyncio.run(compat.create_supplier_document(lieferant, {"name": "Zertifikat", "hochgeladenVon": "gefaelscht"},
                                                request=ANFRAGE, tenant_id=A, db=db))
    eigene = asyncio.run(compat.supplier_documents(lieferant, tenant_id=A, db=db))
    assert len(eigene) == 1
    assert asyncio.run(compat.supplier_documents(lieferant, tenant_id=B, db=db)) == []
    assert _status(compat.delete_supplier_document(lieferant, eigene[0]["id"], tenant_id=B, db=db)) == 404
    assert db.execute(sa.text("SELECT hochgeladen_von FROM domain_ops.ops_dokumente WHERE id = :i"),
                      {"i": eigene[0]["id"]}).scalar() == "nutzer-a"


def test_waage_und_wiegung_mit_partie(fach):
    db, rows = fach
    w = asyncio.run(waage.create_waage({"standort": "Hof", "typ": "LKW-Waage", "max_kapazitaet": 60, "created_by": "x"},
                                       request=ANFRAGE, tenant_id=A, db=db))
    assert (w["tenant_id"], w["created_by"]) == (A, "nutzer-a")
    assert _status(waage.get_waage(w["id"], tenant_id=B, db=db)) == 404
    roh = {"kennzeichen": "LER-AB 1", "artikel": "Weizen", "brutto": 40.0, "tara": 15.0,
           "zeitstempel": datetime(2026, 10, 28, tzinfo=timezone.utc), "wiegetyp": "ROHWARE", "partie_id": "P-77"}
    # fremde Waage: 404 statt Verweis ueber die Mandantengrenze
    assert _status(waage.create_wiegung({**roh, "waage_id": rows[WAAGEN, B]}, request=ANFRAGE, tenant_id=A, db=db)) == 404
    wiegung = asyncio.run(waage.create_wiegung({**roh, "waage_id": w["id"]}, request=ANFRAGE, tenant_id=A, db=db))
    assert (wiegung["chargennummer"], wiegung["netto"], wiegung["tenant_id"]) == ("P-77", 25.0, A)
    assert _status(waage.create_wiegung({**roh, "unbekannt": 1}, request=ANFRAGE, tenant_id=A, db=db)) == 422
    assert _status(waage.get_wiegung(wiegung["id"], tenant_id=B, db=db)) == 404
    assert _status(waage.delete_waage(w["id"], tenant_id=B, db=db)) == 404
    assert WaageRepository(db, A).get_by_id(w["id"]) is not None


def test_fahrzeug_schaden_im_eigenen_mandanten_urheber_aus_token(fach):
    db, rows = fach
    fahrzeug = rows[FAHRZEUGE, A]
    payload = SchadenPayload(datum=datetime(2026, 10, 20, tzinfo=timezone.utc), ort="Leer", beschreibung="Delle links",
                             erstellt_von="gefaelscht")
    assert _status(fuhrpark.create_schaden(fahrzeug, payload, request=ANFRAGE, db=db, tenant_id=B)) == 404
    neu = asyncio.run(fuhrpark.create_schaden(fahrzeug, payload, request=ANFRAGE, db=db, tenant_id=A))
    assert (neu["tenant_id"], neu["erstellt_von"]) == (A, "nutzer-a")
    liste = asyncio.run(fuhrpark.list_schaeden(fahrzeug, status=None, db=db, tenant_id=A))
    assert neu["id"] in {s["id"] for s in liste}


def test_frachttarife_und_rahmenvertraege_im_eigenen_mandanten(fach):
    db, _ = fach
    tarif = asyncio.run(strecke_speditionen.create_frachttarif(
        strecke_speditionen.FrachttarifPayload(plz_von="26000", plz_bis="26999", spediteur="Sped Nord", preis_eur_t=9.5),
        tenant_id=A, db=db))
    tid = tarif["id"] if isinstance(tarif, dict) else tarif.id
    assert _status(strecke_speditionen.get_frachttarif(tid, tenant_id=B, db=db)) == 404
    roh = dict(nummer=f"RV-{uuid4().hex[:6]}", partner="Hof", partner_id="P1", typ="EK", artikel="Weizen",
               artikel_id="A1", menge=100, restmenge=100, preis=200, laufzeit_bis="2027-06-30T00:00:00+00:00")
    rv = asyncio.run(vertraege.create_rahmenvertrag(vertraege.VertragCreate(**roh), tenant_id=A, db=db))
    assert _status(vertraege.get_rahmenvertrag(rv["id"], tenant_id=B, db=db)) == 404
    # dieselbe Nummer im anderen Mandanten
    assert asyncio.run(vertraege.create_rahmenvertrag(vertraege.VertragCreate(**roh), tenant_id=B, db=db))["id"]
    assert _status(vertraege.create_rahmenvertrag(vertraege.VertragCreate(**roh), tenant_id=A, db=db)) == 409


def test_jeder_weg_hat_den_mandanten_aus_dem_token():
    from app.core.tenant import get_tenant_id
    from app.auth.tenant import get_verified_tenant_id

    funde = []
    for modul in (dokumente, waage, strecke_speditionen, vertraege, fuhrpark):
        for route in modul.router.routes:
            parameter = inspect.signature(route.endpoint).parameters
            if "db" not in parameter:
                continue
            quelle = inspect.getsource(route.endpoint)
            if not any(name in quelle for name in ("Repository(", "domain_ops.")):
                continue
            dep = getattr(parameter.get("tenant_id"), "default", None)
            if getattr(dep, "dependency", None) not in (get_tenant_id, get_verified_tenant_id):
                funde.append(f"{modul.__name__}:{route.path}")
    assert funde == []
