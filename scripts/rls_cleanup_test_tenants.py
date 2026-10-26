#!/usr/bin/env python3
"""Testreste aus der gewachsenen Datenbank entfernen (RLS-Plan P4, Nutzerentscheidung 2026-10-26).

Loescht Zeilen eindeutig erkennbarer Testmandanten aus allen Tabellen mit ``tenant_id`` und die
zufaelligen ``test-<hex>``-Eintraege im Mandantenregister. Alles in EINER Transaktion; ohne
``--execute`` wird am Ende zurueckgerollt (Trockenlauf). Vorher eine Sicherung anlegen
(``pg_dump -Fc``) und ihren Pfad mit ``--backup`` angeben – ohne existierende Sicherung keine
Ausfuehrung.

Nicht angefasst (unklar, unter RLS ohnehin unsichtbar): ``legacy-unassigned``, ``NULL``,
``default``, ``valeo``, ``SYSTEM``, ``sd-*``, ``meridian-abnahme``. Der Registereintrag
``test-tenant`` bleibt (pytest-Suiten nutzen ihn als Fremdschluesselziel).

FK-Reihenfolge wird nicht vorausberechnet: das Skript loescht tabellenweise in Savepoints und
wiederholt, bis nichts mehr fehlschlaegt oder kein Fortschritt mehr moeglich ist. Was dann noch
scheitert, wird gemeldet und bleibt stehen.

    python scripts/rls_cleanup_test_tenants.py --url postgresql://… --backup <datei>            # Trockenlauf
    python scripts/rls_cleanup_test_tenants.py --url postgresql://… --backup <datei> --execute
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import sqlalchemy as sa

TEST_TENANT = re.compile(
    r"^(?:test-[0-9a-f]{8}|test-tenant|test-tenant-pos-001|test-tenant-finance-001|"
    r"tenant-a|tenant-a-persist|tenant-api-test|TENANT-TEST|tenant-agent-persist|t1)$"
)
REGISTRY_REMOVABLE = re.compile(r"^test-[0-9a-f]{8}$")

TABLES_WITH_TENANT = """
SELECT c.table_schema, c.table_name
  FROM information_schema.columns c
  JOIN information_schema.tables t
    ON t.table_schema = c.table_schema AND t.table_name = c.table_name AND t.table_type = 'BASE TABLE'
 WHERE c.column_name = 'tenant_id' AND c.table_schema NOT IN ('pg_catalog', 'information_schema')
 ORDER BY 1, 2
"""


CHILDREN_WITHOUT_TENANT = """
SELECT cn.nspname, cc.relname, ca.attname, pa.attname
  FROM pg_constraint k
  JOIN pg_class cc ON cc.oid = k.conrelid JOIN pg_namespace cn ON cn.oid = cc.relnamespace
  JOIN pg_attribute ca ON ca.attrelid = k.conrelid AND ca.attnum = k.conkey[1]
  JOIN pg_attribute pa ON pa.attrelid = k.confrelid AND pa.attnum = k.confkey[1]
 WHERE k.contype = 'f' AND k.confrelid = to_regclass(:parent) AND array_length(k.conkey, 1) = 1
   AND NOT EXISTS (SELECT 1 FROM pg_attribute a WHERE a.attrelid = k.conrelid
                    AND a.attname = 'tenant_id' AND NOT a.attisdropped)
"""


def delete_children_without_tenant(conn, schema: str, table: str, values: list[str]) -> dict[str, int]:
    """Class-C children (no tenant_id) of the parent rows that are about to go."""
    removed = {}
    for c_schema, c_table, c_col, p_col in conn.execute(
            sa.text(CHILDREN_WITHOUT_TENANT), {"parent": f'"{schema}"."{table}"'}).all():
        n = conn.execute(sa.text(
            f'DELETE FROM "{c_schema}"."{c_table}" WHERE "{c_col}" IN '  # nosec B608 - catalog names
            f'(SELECT "{p_col}" FROM "{schema}"."{table}" WHERE tenant_id::text = ANY(:v))'), {"v": values}).rowcount
        removed[f"{c_schema}.{c_table}"] = n
    return removed


def tenant_values(conn, schema: str, table: str) -> list[str]:
    return [v for v in conn.execute(sa.text(
        f'SELECT DISTINCT tenant_id::text FROM "{schema}"."{table}" WHERE tenant_id IS NOT NULL'  # nosec B608 - catalog names
    )).scalars() if TEST_TENANT.match(v)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--url", required=True)
    parser.add_argument("--backup", required=True, help="Pfad der vorher angelegten pg_dump-Sicherung")
    parser.add_argument("--execute", action="store_true")
    args = parser.parse_args()
    if not Path(args.backup).is_file() or Path(args.backup).stat().st_size == 0:
        print(f"Keine Sicherung unter {args.backup}; Abbruch.")
        return 2

    engine = sa.create_engine(args.url, connect_args={"application_name": "agent:claude rls-p4-cleanup"})
    with engine.connect() as conn:
        tx = conn.begin()
        try:
            targets = []
            for schema, table in conn.execute(sa.text(TABLES_WITH_TENANT)).all():
                values = tenant_values(conn, schema, table)
                if values:
                    targets.append((schema, table, values))
            pending = list(targets)
            deleted: dict[str, int] = {}
            failed: dict[str, str] = {}
            for _ in range(len(pending) + 1):
                progress = False
                still = []
                for schema, table, values in pending:
                    name = f"{schema}.{table}"
                    nested = conn.begin_nested()
                    try:
                        for child, m in delete_children_without_tenant(conn, schema, table, values).items():
                            deleted[child] = deleted.get(child, 0) + m
                        n = conn.execute(sa.text(
                            f'DELETE FROM "{schema}"."{table}" WHERE tenant_id::text = ANY(:v)'  # nosec B608 - catalog names
                        ), {"v": values}).rowcount
                        nested.commit()
                        deleted[name] = deleted.get(name, 0) + n
                        failed.pop(name, None)
                        progress = True
                    except sa.exc.DBAPIError as exc:
                        nested.rollback()
                        failed[name] = str(exc.orig).splitlines()[0]
                        still.append((schema, table, values))
                pending = still
                if not pending or not progress:
                    break
            registry = conn.execute(sa.text("SELECT id FROM domain_shared.tenants")).scalars().all()
            removable = [t for t in registry if REGISTRY_REMOVABLE.match(t)]
            nested = conn.begin_nested()
            try:
                registry_deleted = conn.execute(sa.text(
                    "DELETE FROM domain_shared.tenants WHERE id = ANY(:v)"), {"v": removable}).rowcount
                nested.commit()
            except sa.exc.DBAPIError as exc:
                nested.rollback()
                registry_deleted = 0
                failed["domain_shared.tenants"] = str(exc.orig).splitlines()[0]

            for name, n in sorted(deleted.items()):
                print(f"geloescht {n:6d}  {name}")
            print(f"Register: {registry_deleted} von {len(removable)} test-<hex>-Eintraegen entfernt")
            print(f"Summe Zeilen: {sum(deleted.values())} in {len(deleted)} Tabellen")
            for name, reason in sorted(failed.items()):
                print(f"NICHT geloescht  {name}: {reason}")
            if args.execute and not failed:
                tx.commit()
                print("AUSGEFUEHRT (commit).")
            else:
                tx.rollback()
                print("Trockenlauf oder Fehler: zurueckgerollt.")
        except Exception:
            tx.rollback()
            raise
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
