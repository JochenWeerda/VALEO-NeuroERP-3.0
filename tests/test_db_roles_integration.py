"""Getrennte Datenbankrollen wirken wie vorgesehen (DB-Governance Stufe 3).

Richtet Rollen, Eigentum und Rechte mit scripts/provision_db_roles.py in EINER Transaktion
auf der Test-Datenbank ein, prueft per SET ROLE und rollt alles zurueck (CREATE ROLE und
ALTER ... OWNER sind in PostgreSQL transaktional).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from provision_db_roles import apply_plan, build_plan  # noqa: E402

from app.core.migration_session import prepare_migration_session  # noqa: E402

pytestmark = pytest.mark.integration

PROBE_TABLE = "domain_shared.tenants"


def _denied(conn, statement: str) -> bool:
    savepoint = conn.begin_nested()
    try:
        conn.execute(text(statement))
    except ProgrammingError as error:
        savepoint.rollback()
        return "permission denied" in str(error.orig) or "must be owner" in str(error.orig)
    savepoint.rollback()
    return False


def _as(conn, role: str) -> None:
    conn.execute(text("RESET ROLE"))
    conn.execute(text(f"SET ROLE {role}"))


def test_roles_separate_ddl_dml_and_the_log(require_db):
    from app.core.database import engine

    with engine.connect() as conn:
        trans = conn.begin()
        try:
            if not conn.execute(text("SELECT rolsuper FROM pg_roles WHERE rolname = current_user")).scalar():
                pytest.skip("Rolleneinrichtung braucht eine Superuser-Verbindung")
            apply_plan(conn, build_plan(conn, with_ownership=True))
            governance = conn.execute(text("SELECT to_regclass('governance.ddl_events') IS NOT NULL")).scalar()

            _as(conn, "valeo_app")
            conn.execute(text(f"SELECT count(*) FROM {PROBE_TABLE}"))
            assert _denied(conn, "CREATE TABLE domain_shared.governance_role_probe (id int)")
            assert _denied(conn, f"ALTER TABLE {PROBE_TABLE} ADD COLUMN governance_role_probe int")
            conn.execute(text("CREATE TEMP TABLE governance_role_temp (id int)"))
            if governance:
                assert _denied(conn, "SELECT count(*) FROM governance.ddl_events")

            _as(conn, "valeo_agent")
            conn.execute(text(f"SELECT count(*) FROM {PROBE_TABLE}"))
            assert _denied(conn, "CREATE TABLE domain_shared.governance_role_probe (id int)")

            _as(conn, "valeo_migrator")
            conn.execute(text("CREATE TABLE domain_shared.governance_role_probe (id int)"))
            conn.execute(text(f"COMMENT ON TABLE {PROBE_TABLE} IS 'migrator owns transferred objects'"))
            owner = conn.execute(text(
                "SELECT pg_get_userbyid(relowner) FROM pg_class WHERE oid = 'domain_shared.governance_role_probe'::regclass"
            )).scalar()
            # SET ROLE skips the role default "role = valeo_owner"; a real migrator login acts as valeo_owner
            assert owner == "valeo_migrator"
            if governance:
                assert _denied(conn, "DELETE FROM governance.ddl_events")
                assert _denied(conn, "UPDATE governance.ddl_events SET source = 'x'")

            # Alembic/init_db path: superuser session switches to valeo_owner (app.core.migration_session)
            conn.execute(text("RESET ROLE"))
            assert prepare_migration_session(conn, "alembic") is True
            conn.execute(text("CREATE TABLE domain_shared.governance_owner_probe (id int)"))
            assert conn.execute(text(
                "SELECT pg_get_userbyid(relowner) FROM pg_class WHERE oid = 'domain_shared.governance_owner_probe'::regclass"
            )).scalar() == "valeo_owner"

            if governance:
                _as(conn, "valeo_audit")
                rows = conn.execute(text(
                    "SELECT current_role_name FROM governance.ddl_events "
                    "WHERE object_identity = 'domain_shared.governance_role_probe'"
                )).scalars().all()
                assert rows == ["valeo_migrator"]
                logged = conn.execute(text(
                    "SELECT current_role_name, source FROM governance.ddl_events "
                    "WHERE object_identity = 'domain_shared.governance_owner_probe'"
                )).all()
                assert [tuple(r) for r in logged] == [("valeo_owner", "alembic")]
                assert _denied(conn, f"SELECT count(*) FROM {PROBE_TABLE}")
        finally:
            trans.rollback()
