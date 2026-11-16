"""Provision only the existing system role's three portal-directory read sources.

Defaults to a plan. DATABASE_URL stays in the environment; no credentials printed.
Coordinate database ownership before --apply; --rollback rehearses the grants.
No role creation, ownership change, default privileges or write grants.
"""
from __future__ import annotations

import argparse
import os

from sqlalchemy import create_engine, text

TABLES = ("domain_portal.kundenzugaenge", "domain_crm.customers", "domain_shared.tenants")


def grant_plan() -> tuple[str, ...]:
    return tuple(f"GRANT USAGE ON SCHEMA {table.split('.')[0]} TO valeo_system" for table in TABLES) + tuple(
        f"GRANT SELECT ON TABLE {table} TO valeo_system" for table in TABLES
    )


def provision(conn, *, apply: bool) -> None:
    role = conn.execute(text(
        "SELECT rolsuper, rolbypassrls FROM pg_roles WHERE rolname='valeo_system'"
    )).one_or_none()
    if role is None or role[0] or not role[1]:
        raise RuntimeError("Existing non-superuser BYPASSRLS system role required")
    for table in TABLES:
        if conn.execute(text("SELECT to_regclass(:table)"), {"table": table}).scalar_one() is None:
            raise RuntimeError("Required directory source missing")
    for statement in grant_plan():
        print(statement)
        if apply:
            conn.execute(text(statement))
    if apply:
        for table in TABLES:
            allowed = conn.execute(text(
                "SELECT has_schema_privilege('valeo_system', :schema, 'USAGE') "
                "AND has_table_privilege('valeo_system', :table, 'SELECT')"
            ), {"schema": table.split('.')[0], "table": table}).scalar_one()
            if not allowed:
                raise RuntimeError("Directory read verification failed")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--rollback", action="store_true")
    args = parser.parse_args()
    url = os.environ.get("DATABASE_URL")
    if not url:
        parser.error("DATABASE_URL required")
    engine = create_engine(url, connect_args={
        "application_name": os.environ.get("PGAPPNAME", "agent:portal-directory-provision"),
        "connect_timeout": 5,
    })
    try:
        with engine.connect() as conn:
            transaction = conn.begin()
            try:
                provision(conn, apply=args.apply)
                if args.apply and not args.rollback:
                    transaction.commit()
                    print("Directory read grants applied and verified.")
                else:
                    transaction.rollback()
                    print("Plan/rehearsal rolled back; no changes persisted.")
            except Exception:
                transaction.rollback()
                raise
    finally:
        engine.dispose()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
