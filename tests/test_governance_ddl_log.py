"""governance.ddl_events protokolliert Schemaaenderungen jeder Herkunft.

Laeuft auf der Test-Datenbank in einer Transaktion, die zurueckgerollt wird.
"""
from __future__ import annotations

import os

import pytest
from sqlalchemy import text

pytestmark = pytest.mark.integration

SCHEMA = "governance_ddl_log_test"


def _events(conn):
    return conn.execute(text(
        "SELECT event, command_tag, object_type, object_identity, application_name, source "
        "FROM governance.ddl_events WHERE schema_name = :schema ORDER BY id"
    ), {"schema": SCHEMA}).mappings().all()


def test_ddl_is_logged_with_its_declared_source(require_db):
    from app.core.database import engine

    with engine.connect() as conn:
        trans = conn.begin()
        try:
            if not conn.execute(text("SELECT to_regclass('governance.ddl_events') IS NOT NULL")).scalar():
                message = "Migration governance_ddl_log_20261026 ist auf dieser Datenbank nicht angewandt"
                if os.environ.get("CI", "").lower() == "true":
                    pytest.fail(message)
                pytest.skip(message)

            conn.execute(text("SET LOCAL application_name = 'agent:governance-test'"))
            conn.execute(text(f"CREATE SCHEMA {SCHEMA}"))
            conn.execute(text(f"CREATE TABLE {SCHEMA}.probe (id integer PRIMARY KEY)"))
            conn.execute(text("SET LOCAL application_name = ''"))
            conn.execute(text(f"DROP TABLE {SCHEMA}.probe"))
            conn.execute(text(f"CREATE TEMP TABLE governance_ignored_temp (id integer)"))

            rows = _events(conn)
            created = [r for r in rows if r["event"] == "ddl_command_end" and r["object_type"] == "table"]
            dropped = [r for r in rows if r["event"] == "sql_drop" and r["object_type"] == "table"]
            assert [(r["object_identity"], r["source"]) for r in created] == [(f"{SCHEMA}.probe", "agent")]
            assert created[0]["application_name"] == "agent:governance-test"
            assert [(r["command_tag"], r["source"]) for r in dropped] == [("DROP TABLE", "unbekannt")]
            temp = conn.execute(text(
                "SELECT count(*) FROM governance.ddl_events WHERE object_identity LIKE '%governance_ignored_temp%'"
            )).scalar()
            assert temp == 0
        finally:
            trans.rollback()
