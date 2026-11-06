"""Batch 9: Compliance-Register und Zertifikate im Mandanten; Disposition und zertifikate_api entfernt.

Bis 04.11.2026 legten die Register-Wege (compliance.py) und /zertifikate bei jedem Lesezugriff Seed-Daten an und
kannten keinen Mandanten; Gefahrstoffdoku, Naehrstoffstrom und Chargenbericht lasen die Lieferscheine aller Mandanten.
/disposition war eine handgepflegte Bestandsliste (ersetzt durch den Bestellvorschlag), zertifikate_api ein
ueberdeckter zweiter Zertifikatsweg mit Mandant aus dem Pfad.

Teil 1 prueft den Code ohne Datenbank, Teil 2 Policies und Wege auf dem frischen Pruefstand
(tests/rls_domain_support.py: Migrationen in einer zurueckgerollten Transaktion).
"""

from __future__ import annotations

import asyncio
import inspect
from datetime import datetime
from pathlib import Path

import pytest
import sqlalchemy as sa
from fastapi import HTTPException
from sqlalchemy.orm import Session

import rls_domain_support as support
from app.api.v1.endpoints import compliance, zertifikate
from app.core.tenant import get_tenant_id
from app.domains.operations.models import SachkundeEintrag, VVVOEintrag, ZertifikatEintrag
from rls_domain_support import A, B, SYSTEM

ROOT = Path(__file__).resolve().parents[1]
OPS = "domain_ops"
TABELLEN = tuple(f"{OPS}.{t}" for t in (
    "ops_compliance_items", "ops_enni_meldungen", "ops_qs_checks", "ops_sachkunde_register",
    "ops_saatgut_nachbau", "ops_vvvo_register", "ops_zertifikate"))
REGISTERWEGE = ("list_cross_compliance", "list_enni_meldungen", "list_qs_checkliste",
                "list_sachkunde", "list_saatgut_nachbau", "list_vvvo", "get_compliance_stats", "get_compliance_report_pdf",
                "export_gefahrstoffdoku", "export_gefahrstoffdoku_csv", "export_naehrstoffstrom", "export_chargen_trace_report")


# --- Teil 1: Code ohne Datenbank -------------------------------------------------------------------------------


def test_kein_seed_mehr():
    for modul in (compliance, zertifikate):
        quelle = inspect.getsource(modul)
        assert "_seed(db)" not in quelle and "def _seed" not in quelle, modul.__name__
    assert "def seed_compliance_data" not in (ROOT / "app/services/compliance_service.py").read_text(encoding="utf-8")


@pytest.mark.parametrize("name", REGISTERWEGE)
def test_registerwege_mit_mandant_aus_dem_token(name):
    dep = getattr(inspect.signature(getattr(compliance, name)).parameters.get("tenant_id"), "default", None)
    assert getattr(dep, "dependency", None) is get_tenant_id


def test_zertifikatwege_mit_mandant_und_text_kennung():
    for route in zertifikate.router.routes:
        parameter = inspect.signature(route.endpoint).parameters
        assert getattr(parameter["tenant_id"].default, "dependency", None) is get_tenant_id, route.path
        if "zertifikat_id" in parameter:
            assert parameter["zertifikat_id"].annotation in (str, "str"), route.path


def test_disposition_und_zertifikate_api_sind_weg():
    from app.main import app

    pfade = {getattr(r, "path", "") for r in app.routes}
    assert not [p for p in pfade if p == "/api/v1/disposition" or p.startswith("/api/v1/disposition/")]
    assert not [p for p in pfade if p.startswith("/api/v1/zertifikate/tenant") or p == "/api/v1/zertifikate/ablaufend"]
    for seite in ("disposition/liste.tsx", "disposition/engpass-monitor.tsx"):
        text = (ROOT / "packages/frontend-web/src/pages" / seite).read_text(encoding="utf-8")
        assert 'screenId="einkauf/bestellvorschlaege-liste"' in text, seite


# --- Teil 2: Pruefstand ----------------------------------------------------------------------------------------


@pytest.fixture(scope="module")
def probe():
    with support.probe(TABELLEN) as conn:
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


def test_entfernte_tabellen(db):
    conn, _ = db
    for table in ("ops_disposition", "ops_zertifikate_api", "ops_zulassungen_register"):
        assert conn.execute(sa.text(f"SELECT to_regclass('{OPS}.{table}')")).scalar() is None, table


@pytest.fixture
def fach(db):
    conn, rows = db
    conn.execute(sa.text("RESET ROLE"))
    session = Session(bind=conn, join_transaction_mode="create_savepoint")
    try:
        yield session, rows
    finally:
        session.close()


def test_register_lesen_nur_den_eigenen_mandanten(fach):
    db, _ = fach
    db.add_all([
        SachkundeEintrag(tenant_id=A, kunde="Hof A", kundennr="K-A1", nachweis_nr="SK-A", status="gueltig",
                         gueltig_bis=datetime(2027, 1, 1)),
        VVVOEintrag(tenant_id=B, betriebsname="Hof B", vvvo="03-000-000001", status="aktiv"),
    ])
    db.flush()
    eigene = asyncio.run(compliance.list_sachkunde(status=None, tenant_id=A, db=db))["items"]
    assert "SK-A" in {i["nachweis_nr"] for i in eigene}
    assert "SK-A" not in {i["nachweis_nr"] for i in asyncio.run(compliance.list_sachkunde(status=None, tenant_id=B, db=db))["items"]}
    assert "Hof B" not in {i["betriebsname"] for i in asyncio.run(compliance.list_vvvo(tenant_id=A, db=db))["items"]}


def test_zertifikat_im_eigenen_mandanten(fach):
    db, _ = fach
    neu = zertifikate.ZertifikatCreate(art="Bio-Zertifikat", standard="EU-Bio", nummer="BIO-T-1", gueltig_bis=datetime(2027, 6, 30).date())
    z = asyncio.run(zertifikate.create_zertifikat(neu, tenant_id=A, db=db))
    assert db.get(ZertifikatEintrag, z["id"]).tenant_id == A
    with pytest.raises(HTTPException) as fremd:
        asyncio.run(zertifikate.update_zertifikat(z["id"], zertifikate.ZertifikatUpdate(status="ablaufend"), tenant_id=B, db=db))
    assert fremd.value.status_code == 404
    geaendert = asyncio.run(zertifikate.update_zertifikat(z["id"], zertifikate.ZertifikatUpdate(status="ablaufend"), tenant_id=A, db=db))
    assert geaendert["status"] == "ablaufend"
