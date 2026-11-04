"""Batch 8 Scheinwege: Foerderantraege und Laborproben/-auftraege im Mandanten, Marketingkampagnen ins CRM.

Bis 03.11.2026 legten die drei Wege bei jedem Lesezugriff Demodaten an, kannten keinen Mandanten, nahmen
Text-Kennungen als Zahl an (Aendern/Loeschen immer 422) und gaben Befundangaben zurueck, ohne sie zu speichern.
Kampagnen fuehrt seit 04.11.2026 domain_crm.crm_campaigns (Nutzerentscheidung); der Marketingweg ist entfernt.

Teil 1 prueft den Code ohne Datenbank, Teil 2 Policies und Fachwege auf dem frischen Pruefstand
(tests/rls_domain_support.py: Migrationen in einer zurueckgerollten Transaktion).
"""

from __future__ import annotations

import asyncio
import inspect
from datetime import date
from uuid import uuid4

import pytest
import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy.orm import Session

import rls_domain_support as support
from app.api.v1.endpoints import foerderung, labor
from app.core.tenant import get_tenant_id
from rls_domain_support import A, B, SYSTEM

OPS = "domain_ops"
TABELLEN = (f"{OPS}.ops_foerderantraege", f"{OPS}.ops_labor_proben", f"{OPS}.ops_labor_auftraege")
MODULE = (foerderung, labor)


# --- Teil 1: Code ohne Datenbank -------------------------------------------------------------------------------


@pytest.mark.parametrize("modul", MODULE, ids=lambda m: m.__name__.rsplit(".", 1)[1])
def test_kein_seed_mehr(modul):
    quelle = inspect.getsource(modul)
    assert "def _seed" not in quelle and "_seed(db)" not in quelle and "db.add_all" not in quelle


@pytest.mark.parametrize("modul", MODULE, ids=lambda m: m.__name__.rsplit(".", 1)[1])
def test_jeder_weg_mit_mandant_aus_dem_token_und_text_kennung(modul):
    for route in modul.router.routes:
        parameter = inspect.signature(route.endpoint).parameters
        dep = getattr(parameter.get("tenant_id"), "default", None)
        assert getattr(dep, "dependency", None) is get_tenant_id, f"{modul.__name__}:{route.path}"
        for name, p in parameter.items():
            if name.endswith("_id") and name != "tenant_id":
                assert p.annotation in (str, "str"), f"{route.path}: {name} ist {p.annotation}"


def test_kampagnen_nur_noch_im_crm():
    """Ein Kampagnenbestand: kein /marketing-Weg, die Marketingseite zeigt die CRM-Liste."""
    from pathlib import Path

    from app.main import app

    assert not [r.path for r in app.routes if getattr(r, "path", "").startswith("/api/v1/marketing")]
    seite = (Path(__file__).resolve().parents[1] / "packages/frontend-web/src/pages/marketing/kampagnen.tsx").read_text(encoding="utf-8")
    assert 'screenId="crm/kampagnen-liste"' in seite


# --- Teil 2: Pruefstand ----------------------------------------------------------------------------------------


@pytest.fixture(scope="module")
def probe():
    with support.probe(TABELLEN + (f"{OPS}.ops_chargen",)) as conn:
        support.ensure_tenants(conn, A, B, SYSTEM)
        rows = {(t, m): str(support.seed_row(conn, t, m)["id"]) for t in TABELLEN for m in (A, B, SYSTEM)}
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
    for table in TABELLEN:
        assert support.shape(conn, table) == ("getrennt", ""), table


@pytest.mark.parametrize("table", TABELLEN)
def test_mandantengrenze_je_tabelle(db, table):
    conn, rows = db
    support.assert_tenant_isolation(conn, table, rows[table, A], rows[table, B], rows[table, SYSTEM])


def test_mandant_pflicht_und_vorgabe_aus_dem_kontext(db):
    conn, _ = db
    for table in TABELLEN:
        notnull, default = conn.execute(sa.text(
            "SELECT a.attnotnull, pg_get_expr(d.adbin, d.adrelid) FROM pg_attribute a LEFT JOIN pg_attrdef d "
            "ON d.adrelid = a.attrelid AND d.adnum = a.attnum WHERE a.attrelid = to_regclass(:t) AND a.attname = 'tenant_id'"),
            {"t": table}).one()
        assert (notnull, default) == (True, "rls_current_tenant()"), table


@pytest.fixture
def fach(db):
    conn, rows = db
    conn.execute(sa.text("RESET ROLE"))
    session = Session(bind=conn, join_transaction_mode="create_savepoint")
    try:
        yield session, rows
    finally:
        session.close()


def _status(aufruf) -> int:
    with pytest.raises(HTTPException) as info:
        asyncio.run(aufruf)
    return info.value.status_code


def test_foerderantrag_im_eigenen_mandanten(fach):
    db, _ = fach
    nummer = f"FA-{uuid4().hex[:6]}"
    neu = foerderung.FoerderAntragCreate(nummer=nummer, programm="Agrarumwelt", antragsdatum=date(2026, 5, 2), betrag=900)
    antrag = asyncio.run(foerderung.create_antrag(neu, tenant_id=A, db=db))
    assert _status(foerderung.get_antrag(antrag["id"], tenant_id=B, db=db)) == 404
    geaendert = asyncio.run(foerderung.update_antrag(antrag["id"], foerderung.FoerderAntragUpdate(status="eingereicht"),
                                                     tenant_id=A, db=db))
    assert geaendert["status"] == "eingereicht"
    assert _status(foerderung.delete_antrag(antrag["id"], tenant_id=A, db=db)) == 409  # eingereicht bleibt
    assert _status(foerderung.create_antrag(neu, tenant_id=A, db=db)) == 409  # Nummer je Mandant eindeutig
    assert asyncio.run(foerderung.create_antrag(neu, tenant_id=B, db=db))["nummer"] == nummer
    liste = asyncio.run(foerderung.list_antraege(status=None, limit=500, tenant_id=B, db=db))
    assert antrag["id"] not in {i["id"] for i in liste["items"]}




def test_laborauftrag_braucht_eigene_charge_und_befund_speichert(fach):
    db, _ = fach
    charge = f"CH-{uuid4().hex[:6]}"
    db.execute(sa.text("INSERT INTO domain_ops.ops_chargen (id, tenant_id, chargen_id, artikel, artikel_id, menge, lagerort, eingang) "
                       "VALUES (:i, :t, :c, 'Weizen', 'A-1', 250, 'Silo 1', now())"), {"i": str(uuid4()), "t": A, "c": charge})
    auftrag = labor.LaborAuftragCreate(chargenId=charge, labor="LUFA Nord-West", analysen=["Feuchte", "Protein"])
    assert _status(labor.create_labor_auftrag(auftrag, tenant_id=B, db=db)) == 404  # fremde Charge
    neu = asyncio.run(labor.create_labor_auftrag(auftrag, tenant_id=A, db=db))
    assert neu["analysen"] == 2
    befund = labor.LaborBefundCreate(entscheidung="freigeben", analysewerte={"Feuchte": 14.2},
                                     grenzwerte={"Feuchte": 15.0}, bemerkung="ok")
    assert _status(labor.create_labor_befund(neu["id"], befund, tenant_id=B, db=db)) == 404
    asyncio.run(labor.create_labor_befund(neu["id"], befund, tenant_id=A, db=db))
    gelesen = asyncio.run(labor.get_labor_auftrag(neu["id"], tenant_id=A, db=db))
    assert (gelesen["status"], gelesen["qs_entscheidung"]) == ("abgeschlossen", "freigeben")
    assert (gelesen["analysewerte"], gelesen["grenzwerte"], gelesen["bemerkung"]) == ({"Feuchte": 14.2}, {"Feuchte": 15.0}, "ok")
    assert neu["id"] not in {i["id"] for i in asyncio.run(labor.list_labor_auftraege(limit=500, tenant_id=B, db=db))["items"]}


def test_marketingtabelle_ist_entfernt(db):
    conn, _ = db
    assert conn.execute(sa.text("SELECT to_regclass('domain_ops.ops_marketing_kampagnen')")).scalar() is None
