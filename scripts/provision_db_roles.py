#!/usr/bin/env python3
"""Richtet die getrennten Datenbankrollen ein (DB-Governance Stufe 3).

Warum
-----
Bis 2026-10-26 verbanden sich Backend, Migrationen, Domaenendienste und Agenten mit
derselben Superuser-Rolle. Das DDL-Protokoll (``governance.ddl_events``) konnte damit nur
die *angegebene* Herkunft festhalten, und jede Sitzung durfte das Schema aendern.

Rollen (clusterweit, idempotent)
--------------------------------
- ``valeo_owner``      NOLOGIN, Eigentuemer der Fachschemata und -objekte
- ``valeo_migrator``   LOGIN, Mitglied von valeo_owner: einzige Rolle fuer DDL
- ``valeo_app``        LOGIN, Daten lesen/schreiben, keine Schemaaenderung
- ``valeo_agent``      LOGIN, wie valeo_app (Agenten; DDL nur ueber valeo_migrator)
- ``valeo_audit``      LOGIN, liest nur ``governance.ddl_events``
- ``valeo_governance`` NOLOGIN, Eigentuemer des Protokolls; valeo_owner darf nur einfuegen

Der Superuser bleibt fuer Entwicklung, Einrichtung und Anpassungen (Nutzerentscheidung
2026-10-26); seine Aenderungen weist ``check_ddl_provenance.py`` gesondert aus.

Passwoerter kommen ausschliesslich aus der Umgebung (``VALEO_DB_PASSWORD_MIGRATOR``,
``…_APP``, ``…_AGENT``, ``…_AUDIT``); ohne Variable bleibt ein vorhandenes Passwort
unveraendert bzw. die Rolle ohne Passwort. Ausgegeben werden sie nie.

Aufruf (als Superuser, je Datenbank)
------------------------------------
    python scripts/provision_db_roles.py --url "$SUPERUSER_URL"                  # nur Plan
    python scripts/provision_db_roles.py --url "$SUPERUSER_URL" --anwenden       # Rollen + Rechte
    python scripts/provision_db_roles.py --url "$SUPERUSER_URL" --anwenden --eigentum
    python scripts/provision_db_roles.py --url "$URL" --anwenden --eigentum --rollback  # Probelauf

``--eigentum`` uebertraegt Fachschemata und ihre Objekte von ihrem bisherigen Eigentuemer
auf valeo_owner; ohne diesen Schritt kann valeo_migrator bestehende Tabellen nicht aendern.
"""
from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass

OWNER, GOVERNANCE, MIGRATOR, APP, AGENT, AUDIT = (
    "valeo_owner", "valeo_governance", "valeo_migrator", "valeo_app", "valeo_agent", "valeo_audit",
)
LOGIN_ROLES = {MIGRATOR: "MIGRATOR", APP: "APP", AGENT: "AGENT", AUDIT: "AUDIT"}
NOLOGIN_ROLES = (OWNER, GOVERNANCE)
DATA_ROLES = (APP, AGENT)
SKIPPED_SCHEMAS = ("governance", "information_schema")


def _ident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


@dataclass(frozen=True)
class Plan:
    roles: list[str]
    grants: list[str]
    ownership: list[str]


def role_statements() -> list[str]:
    statements = []
    for role in (*NOLOGIN_ROLES, *LOGIN_ROLES):
        login = "LOGIN" if role in LOGIN_ROLES else "NOLOGIN"
        statements.append(
            f"DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{role}') "
            f"THEN CREATE ROLE {role} {login}; END IF; END $$"
        )
        statements.append(f"ALTER ROLE {role} {login} NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS INHERIT")
    statements.append(f"GRANT {OWNER} TO {MIGRATOR}")
    # Every migrator login acts as the owner, so new objects never belong to a login role.
    statements.append(f"ALTER ROLE {MIGRATOR} SET role = '{OWNER}'")
    return statements


def grant_statements(database: str, schemas: list[str], creators: list[str], governance: bool) -> list[str]:
    data = ", ".join(DATA_ROLES)
    statements = [
        f"GRANT CONNECT, TEMPORARY ON DATABASE {_ident(database)} TO {data}",
        f"GRANT CONNECT ON DATABASE {_ident(database)} TO {MIGRATOR}, {AUDIT}",
        # Migrations create new schemas; the owner needs CREATE on the database for that.
        f"GRANT CONNECT, CREATE ON DATABASE {_ident(database)} TO {OWNER}",
        "REVOKE CREATE ON SCHEMA public FROM PUBLIC",
    ]
    for schema in schemas:
        s = _ident(schema)
        statements += [
            f"GRANT USAGE, CREATE ON SCHEMA {s} TO {OWNER}",
            f"GRANT USAGE ON SCHEMA {s} TO {data}",
            f"GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA {s} TO {data}",
            f"GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA {s} TO {data}",
            f"GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA {s} TO {data}",
        ]
        for creator in creators:
            c = _ident(creator)
            statements += [
                f"ALTER DEFAULT PRIVILEGES FOR ROLE {c} IN SCHEMA {s} GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO {data}",
                f"ALTER DEFAULT PRIVILEGES FOR ROLE {c} IN SCHEMA {s} GRANT USAGE, SELECT, UPDATE ON SEQUENCES TO {data}",
                f"ALTER DEFAULT PRIVILEGES FOR ROLE {c} IN SCHEMA {s} GRANT EXECUTE ON FUNCTIONS TO {data}",
            ]
    if governance:
        statements += [
            f"ALTER SCHEMA governance OWNER TO {GOVERNANCE}",
            f"ALTER TABLE governance.ddl_events OWNER TO {GOVERNANCE}",
            f"ALTER FUNCTION governance.log_ddl_command_end() OWNER TO {GOVERNANCE}",
            f"ALTER FUNCTION governance.log_sql_drop() OWNER TO {GOVERNANCE}",
            "REVOKE ALL ON SCHEMA governance FROM PUBLIC",
            "REVOKE ALL ON ALL TABLES IN SCHEMA governance FROM PUBLIC",
            f"GRANT USAGE ON SCHEMA governance TO {OWNER}, {AUDIT}",
            f"GRANT INSERT ON governance.ddl_events TO {OWNER}",
            f"GRANT USAGE ON SEQUENCE governance.ddl_events_id_seq TO {OWNER}",
            f"GRANT SELECT ON governance.ddl_events TO {AUDIT}",
        ]
    return statements


def ownership_statements(objects: list[tuple[str, str]]) -> list[str]:
    """objects: (kind, qualified identity) with kind SCHEMA, TABLE, VIEW, MATERIALIZED VIEW,
    SEQUENCE, FUNCTION, PROCEDURE, TYPE."""
    return [f"ALTER {kind} {identity} OWNER TO {OWNER}" for kind, identity in objects]


# Catalog reads -------------------------------------------------------------------------

_SCHEMAS_SQL = """
SELECT nspname FROM pg_namespace
 WHERE nspname NOT LIKE 'pg\\_%' AND nspname <> ALL(:skipped)
 ORDER BY nspname
"""

# Objects of the application schemas not owned by valeo_owner and not part of an extension.
# Sequences owned by a table column follow their table and are skipped.
_OBJECTS_SQL = """
WITH app AS (
    SELECT oid, nspname FROM pg_namespace
     WHERE nspname NOT LIKE 'pg\\_%' AND nspname <> ALL(:skipped)
), ext AS (
    SELECT objid, classid FROM pg_depend WHERE deptype = 'e'
)
SELECT 'SCHEMA', quote_ident(a.nspname)
  FROM app a JOIN pg_namespace n ON n.oid = a.oid
 WHERE pg_get_userbyid(n.nspowner) <> :owner AND a.nspname <> 'public'
UNION ALL
SELECT CASE c.relkind WHEN 'r' THEN 'TABLE' WHEN 'p' THEN 'TABLE' WHEN 'v' THEN 'VIEW'
                      WHEN 'm' THEN 'MATERIALIZED VIEW' WHEN 'S' THEN 'SEQUENCE' WHEN 'f' THEN 'FOREIGN TABLE' END,
       quote_ident(a.nspname) || '.' || quote_ident(c.relname)
  FROM pg_class c JOIN app a ON a.oid = c.relnamespace
 WHERE c.relkind IN ('r', 'p', 'v', 'm', 'S', 'f')
   AND pg_get_userbyid(c.relowner) <> :owner
   AND NOT EXISTS (SELECT 1 FROM ext e WHERE e.objid = c.oid AND e.classid = 'pg_class'::regclass)
   AND NOT (c.relkind = 'S' AND EXISTS (SELECT 1 FROM pg_depend d WHERE d.objid = c.oid
                                        AND d.classid = 'pg_class'::regclass AND d.deptype IN ('a', 'i')))
UNION ALL
SELECT CASE p.prokind WHEN 'p' THEN 'PROCEDURE' ELSE 'FUNCTION' END,
       quote_ident(a.nspname) || '.' || quote_ident(p.proname) || '(' || pg_get_function_identity_arguments(p.oid) || ')'
  FROM pg_proc p JOIN app a ON a.oid = p.pronamespace
 WHERE p.prokind IN ('f', 'p') AND pg_get_userbyid(p.proowner) <> :owner
   AND NOT EXISTS (SELECT 1 FROM ext e WHERE e.objid = p.oid AND e.classid = 'pg_proc'::regclass)
UNION ALL
SELECT 'TYPE', quote_ident(a.nspname) || '.' || quote_ident(t.typname)
  FROM pg_type t JOIN app a ON a.oid = t.typnamespace
 WHERE t.typtype IN ('e', 'd', 'r', 'm') AND pg_get_userbyid(t.typowner) <> :owner
   AND NOT EXISTS (SELECT 1 FROM ext e WHERE e.objid = t.oid AND e.classid = 'pg_type'::regclass)
"""


def build_plan(conn, with_ownership: bool) -> Plan:
    from sqlalchemy import text

    database, current = conn.execute(text("SELECT current_database(), current_user")).one()
    skipped = list(SKIPPED_SCHEMAS)
    schemas = [r[0] for r in conn.execute(text(_SCHEMAS_SQL), {"skipped": skipped})]
    governance = conn.execute(text("SELECT to_regclass('governance.ddl_events') IS NOT NULL")).scalar()
    # Default privileges for the future owner and for the superuser who still creates objects.
    creators = [OWNER] if current == OWNER else [OWNER, current]
    ownership: list[str] = []
    if with_ownership:
        objects = [(r[0], r[1]) for r in conn.execute(text(_OBJECTS_SQL), {"skipped": skipped, "owner": OWNER})]
        ownership = ownership_statements(objects)
    return Plan(role_statements(), grant_statements(database, schemas, creators, bool(governance)), ownership)


def apply_plan(conn, plan: Plan) -> int:
    """Executes the plan on conn; passwords only through bound parameters."""
    from sqlalchemy import text

    for statement in [*plan.roles, *plan.ownership, *plan.grants]:
        conn.execute(text(statement))
    changed = 0
    for role, suffix in LOGIN_ROLES.items():
        secret = os.environ.get(f"VALEO_DB_PASSWORD_{suffix}")
        if secret:
            # Role names are constants; the password is passed as a bound literal.
            conn.execute(text(f"ALTER ROLE {role} PASSWORD :secret"), {"secret": secret})
            changed += 1
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--url", default=os.environ.get("DATABASE_URL"), help="Superuser-Verbindung zur Zieldatenbank")
    parser.add_argument("--anwenden", action="store_true", help="ausfuehren statt nur planen")
    parser.add_argument("--eigentum", action="store_true", help="Fachschemata und -objekte an valeo_owner uebertragen")
    parser.add_argument("--rollback", action="store_true", help="in einer Transaktion ausfuehren und zuruecknehmen")
    args = parser.parse_args()
    if not args.url:
        raise SystemExit("Keine Datenbank: --url oder DATABASE_URL setzen.")

    from sqlalchemy import create_engine, text

    engine = create_engine(args.url, connect_args={"application_name": "provision-db-roles"})
    try:
        with engine.connect() as conn:
            trans = conn.begin()
            if not conn.execute(text("SELECT rolsuper FROM pg_roles WHERE rolname = current_user")).scalar():
                trans.rollback()
                raise SystemExit("Rollen und Eigentum lassen sich nur als Superuser einrichten.")
            plan = build_plan(conn, args.eigentum)
            print(f"Rollen: {len(plan.roles)} Anweisungen, Eigentum: {len(plan.ownership)} Objekte, "
                  f"Rechte: {len(plan.grants)} Anweisungen")
            if not args.anwenden:
                trans.rollback()
                print("Nur Plan (ohne --anwenden), nichts geaendert.")
                return 0
            passwords = apply_plan(conn, plan)
            print(f"Passwoerter aus der Umgebung gesetzt: {passwords} von {len(LOGIN_ROLES)}")
            if args.rollback:
                trans.rollback()
                print("Probelauf: zurueckgenommen.")
            else:
                trans.commit()
                print("Angewendet.")
    finally:
        engine.dispose()
    return 0


if __name__ == "__main__":
    sys.exit(main())
