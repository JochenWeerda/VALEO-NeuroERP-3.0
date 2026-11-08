#!/usr/bin/env python3
"""Inventar fuer die Mandantentrennung in der Datenbank (RLS-Plan, Phase P0).

Ausgabe: ``docs/admin/rls-inventory.json`` mit zwei Teilen.

``tables`` – jede Tabelle der **frischen** Datenbank (Pruefstand, siehe
``scripts/pruefstand_db.py``) mit Klasse:

    A  tenant_id NOT NULL                 -> Policy direkt
    B  tenant_id nullbar                  -> erst Daten/Spalte klaeren, dann Policy
    C  ohne tenant_id, FK auf A/B-Tabelle -> tenant_id nachziehen (Plan, Abschnitt 2.6)
    D  ohne tenant_id, ohne solchen FK    -> global oder verwaist, Einzelentscheidung

dazu Typ von tenant_id, RLS-Status und Policy-Zahl. Liegt der Pruefstand hinter
dem Kopf der Alembic-Kette, spielt das Skript die fehlenden Revisionen in einer
Transaktion ein und rollt sie zurueck: kein Reset, kein Stempeln, keine Spur.

``code_paths`` – Stellen, an denen Code den Mandantenkontext der Anwendung
umgehen oder ersetzen kann (Sitzungen ausserhalb von Requests, direkte
Verbindungen, eigene Engines, Treiberverbindungen, Rueckfall auf den
Standardmandanten). Rein statisch, ohne Datenbank.

Verwendung:
    python scripts/rls_inventory.py            # beide Teile neu schreiben
    python scripts/rls_inventory.py --check    # Abweichung -> Exit 1
    python scripts/rls_inventory.py --code-only [--check]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT = REPO_ROOT / "docs" / "admin" / "rls-inventory.json"

CODE_ROOTS = ("app", "modules", "services")
CODE_PATTERNS = {
    "session_local": re.compile(r"\bSessionLocal\(\)"),
    "engine_direct": re.compile(r"\bengine\.(?:connect|begin)\("),
    "new_engine": re.compile(r"\bcreate_(?:async_)?engine\("),
    "driver_connect": re.compile(r"\b(?:psycopg2?|asyncpg)\.(?:connect|create_pool)\("),
    "default_tenant": re.compile(r"\bDEFAULT_TENANT_ID\b"),
}
# Nur gezaehlt, nicht im geprueften Inventar: aendert sich mit jeder Fachfunktion.
FILTER_PATTERNS = {
    "sql_tenant_filter": re.compile(r"tenant_id\s*=\s*:"),
    "orm_tenant_filter": re.compile(r"\.tenant_id\s*=="),
}

SYSTEM_SCHEMAS = ("pg_catalog", "information_schema")

TABLES_SQL = """
WITH t AS (
    SELECT c.oid, n.nspname AS schema, c.relname AS name,
           c.relrowsecurity AS rls, c.relforcerowsecurity AS force_rls,
           (SELECT count(*) FROM pg_policy p WHERE p.polrelid = c.oid) AS policies,
           (SELECT format_type(a.atttypid, a.atttypmod) FROM pg_attribute a
             WHERE a.attrelid = c.oid AND a.attname = 'tenant_id' AND NOT a.attisdropped) AS tenant_type,
           (SELECT a.attnotnull FROM pg_attribute a
             WHERE a.attrelid = c.oid AND a.attname = 'tenant_id' AND NOT a.attisdropped) AS tenant_not_null
      FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace
     WHERE c.relkind IN ('r', 'p') AND NOT c.relispartition
       AND n.nspname NOT IN ('pg_catalog', 'information_schema') AND n.nspname NOT LIKE 'pg_toast%'
)
SELECT t.schema, t.name, t.rls, t.force_rls, t.policies, t.tenant_type, t.tenant_not_null,
       ARRAY(SELECT DISTINCT p.schema || '.' || p.name
               FROM pg_constraint k JOIN t p ON p.oid = k.confrelid
              WHERE k.conrelid = t.oid AND k.contype = 'f' AND p.tenant_type IS NOT NULL
                AND p.oid <> t.oid
              ORDER BY 1) AS tenant_parents
  FROM t ORDER BY t.schema, t.name
"""


def classify(tenant_type: str | None, tenant_not_null: bool | None, tenant_parents: list[str]) -> str:
    if tenant_type is not None:
        return "A" if tenant_not_null else "B"
    return "C" if tenant_parents else "D"


def table_rows(rows) -> list[dict]:
    out = []
    for schema, name, rls, force_rls, policies, tenant_type, not_null, parents in rows:
        parents = list(parents or [])
        entry = {
            "table": f"{schema}.{name}",
            "class": classify(tenant_type, not_null, parents),
            "tenant_type": tenant_type,
            "rls": bool(rls),
            "force_rls": bool(force_rls),
            "policies": int(policies),
        }
        if entry["class"] == "C":
            entry["tenant_parents"] = parents
        out.append(entry)
    return out


def _pending_upgrade(conn) -> list[str]:
    """Spielt fehlende Revisionen auf ``conn`` ein (Aufrufer haelt die Transaktion)."""
    from alembic.config import Config
    from alembic.migration import MigrationContext
    from alembic.operations import Operations
    from alembic.script import ScriptDirectory

    script = ScriptDirectory.from_config(Config(str(REPO_ROOT / "alembic.ini")))
    current = MigrationContext.configure(conn).get_current_heads()
    known = {rev.revision for rev in script.walk_revisions()}
    unknown = [rev for rev in current if rev not in known]
    if unknown:
        raise SystemExit(f"Pruefstand steht auf unbekannter Revision {unknown}; erst abstimmen.")
    pending = list(reversed(list(script.iterate_revisions(script.get_heads(), current or "base"))))
    if not pending:
        return []
    context = MigrationContext.configure(conn)
    with Operations.context(context):
        for rev in pending:
            rev.module.upgrade()
    return [rev.revision for rev in pending]


def scan_tables(url: str) -> tuple[list[dict], list[str]]:
    import sqlalchemy as sa

    engine = sa.create_engine(url, connect_args={"application_name": "rls_inventory"})
    try:
        with engine.connect() as conn:
            tx = conn.begin()
            try:
                replayed = _pending_upgrade(conn)
                rows = conn.execute(sa.text(TABLES_SQL)).all()
            finally:
                tx.rollback()
    finally:
        engine.dispose()
    return table_rows(rows), replayed


def _code_files():
    for root in CODE_ROOTS:
        base = REPO_ROOT / root
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.py")):
            rel = path.relative_to(REPO_ROOT).as_posix()
            parts = set(rel.split("/"))
            if parts & {"tests", "test", "node_modules", "__pycache__", "alembic"}:
                continue
            yield rel, path.read_text(encoding="utf-8", errors="replace")


def scan_code() -> tuple[dict, dict]:
    paths: dict[str, dict[str, int]] = {name: {} for name in CODE_PATTERNS}
    filters: Counter = Counter()
    for rel, text in _code_files():
        for name, pattern in CODE_PATTERNS.items():
            hits = len(pattern.findall(text))
            if hits:
                paths[name][rel] = hits
        for name, pattern in FILTER_PATTERNS.items():
            filters[name] += len(pattern.findall(text))
    return paths, dict(filters)


def summary(tables: list[dict]) -> dict:
    classes = Counter(t["class"] for t in tables)
    return {
        "tables": len(tables),
        "by_class": {k: classes.get(k, 0) for k in "ABCD"},
        "rls_enabled": sum(t["rls"] for t in tables),
        "tenant_types": dict(sorted(Counter(t["tenant_type"] for t in tables if t["tenant_type"]).items())),
    }


def render(tables: list[dict], code_paths: dict) -> str:
    doc = {
        "_note": "Generiert von scripts/rls_inventory.py; nicht von Hand aendern. "
                 "Plan: docs/architecture/rls-mandantenkernel-plan.md",
        "summary": summary(tables),
        "code_paths": code_paths,
        "tables": tables,
    }
    return json.dumps(doc, ensure_ascii=False, indent=1, sort_keys=False) + "\n"


def _probe_url() -> str:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))
    from pruefstand_db import pruefstand_url  # noqa: E402

    return pruefstand_url().render_as_string(hide_password=False)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true", help="nur vergleichen, Exit 1 bei Abweichung")
    parser.add_argument("--code-only", action="store_true", help="nur die Codepfade, Tabellen aus der Datei")
    args = parser.parse_args()

    code_paths, filters = scan_code()
    existing = json.loads(OUTPUT.read_text(encoding="utf-8")) if OUTPUT.exists() else None
    if args.code_only:
        if existing is None:
            print("Kein Inventar vorhanden; erst ohne --code-only erzeugen.")
            return 1
        tables, replayed = existing["tables"], []
    else:
        tables, replayed = scan_tables(_probe_url())

    text = render(tables, code_paths)
    print(f"Handfilter (nur Information): {filters}")
    if replayed:
        print(f"Zurueckgerollt eingespielt: {', '.join(replayed)}")
    if args.check:
        if existing is None or render(existing["tables"] if args.code_only else tables, code_paths) != OUTPUT.read_text(encoding="utf-8"):
            print(f"DRIFT: {OUTPUT.relative_to(REPO_ROOT)} nicht aktuell. 'python scripts/rls_inventory.py' ausfuehren.")
            return 1
        print(f"OK: {OUTPUT.relative_to(REPO_ROOT)} aktuell.")
        return 0
    OUTPUT.write_text(text, encoding="utf-8")
    print(f"Geschrieben: {OUTPUT.relative_to(REPO_ROOT)} ({len(tables)} Tabellen)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
