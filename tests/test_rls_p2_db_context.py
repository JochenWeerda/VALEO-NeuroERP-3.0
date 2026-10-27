"""RLS-Plan P2: jede Transaktion traegt app.tenant_id aus dem Mandantenkontext.

Geprueft gegen echte PostgreSQL-Verbindungen (frischer Pruefstand), weil Pool, Savepoints und
transaktionslokale Einstellungen sich nur dort ehrlich verhalten.
"""

from __future__ import annotations

import os

import pytest
import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.core.rls_session import SETTING, install_tenant_setting
from app.core.tenant_context import cross_tenant_scope, tenant_scope

pytestmark = pytest.mark.integration

URL = os.environ.get("TEST_DATABASE_URL")
CURRENT = sa.text(f"SELECT current_setting('{SETTING}', true)")


@pytest.fixture(scope="module")
def engine():
    if not URL:
        pytest.skip("TEST_DATABASE_URL (frischer Pruefstand) nicht gesetzt")
    eng = install_tenant_setting(sa.create_engine(URL, pool_size=1, max_overflow=0))
    yield eng
    eng.dispose()


def test_app_engine_ist_ausgestattet():
    from sqlalchemy import event
    from app.core import database
    from app.core.rls_session import _apply
    assert event.contains(database.engine, "before_cursor_execute", _apply)


def test_ohne_kontext_leer(engine):
    with engine.connect() as conn:
        assert conn.execute(CURRENT).scalar() == ""


def test_mandant_im_scope(engine):
    with tenant_scope("t-1", "test"), engine.connect() as conn:
        assert conn.execute(CURRENT).scalar() == "t-1"


def test_wechsel_innerhalb_einer_transaktion(engine):
    with Session(engine) as db:
        with tenant_scope("t-1", "test"):
            assert db.execute(CURRENT).scalar() == "t-1"
        with tenant_scope("t-2", "test"):
            assert db.execute(CURRENT).scalar() == "t-2"
        with cross_tenant_scope("test"):
            assert db.execute(CURRENT).scalar() == ""


def test_nach_commit_und_aus_dem_pool_neu_gesetzt(engine):
    with tenant_scope("t-1", "test"):
        with Session(engine) as db:
            assert db.execute(CURRENT).scalar() == "t-1"
            db.commit()
            # neue Transaktion auf derselben Verbindung: Wert ist weg, muss neu gesetzt werden
            assert db.execute(CURRENT).scalar() == "t-1"
        # pool_size=1: dieselbe Verbindung kommt zurueck, Cache darf nicht ueberspringen
        with Session(engine) as db:
            assert db.execute(CURRENT).scalar() == "t-1"
    with Session(engine) as db:
        assert db.execute(CURRENT).scalar() == ""


def test_savepoint_rollback_stellt_den_mandanten_wieder_her(engine):
    with tenant_scope("t-1", "test"), Session(engine) as db:
        assert db.execute(CURRENT).scalar() == "t-1"
        nested = db.begin_nested()
        with tenant_scope("t-2", "test"):
            assert db.execute(CURRENT).scalar() == "t-2"
        nested.rollback()
        assert db.execute(CURRENT).scalar() == "t-1"


def test_wert_ist_transaktionslokal(engine):
    with tenant_scope("t-1", "test"), engine.connect() as conn:
        conn.execute(CURRENT)
        conn.commit()
        raw = conn.connection.dbapi_connection.cursor()
        raw.execute(f"SELECT current_setting('{SETTING}', true)")
        assert raw.fetchone()[0] in ("", None)
        raw.close()
