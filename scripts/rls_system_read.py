#!/usr/bin/env python3
"""Befund: welche RLS-Tabellen 'system'-Zeilen haben oder im Code als gemeinsam gelesen werden.

Grundlage der systemweiten Entscheidung, wo SELECT gemeinsame 'system'-Zeilen zeigen darf
(docs/admin/rls-exceptions.json -> system_lesbar). Ohne Beleg liest eine Tabelle nur den
eigenen Mandanten (rls_system_read_justified_20261027).

    frisch   'system'-Zeilen im frischen Schema (TEST_DATABASE_URL, alle Revisionen
             zurueckgerollt eingespielt: Seeds der Migrationen)
    live     'system'-Zeilen in der gewachsenen Datenbank (LIVE_DATABASE_URL, nur lesend)
    code     Dateien, die die Tabelle nennen und 'system' als Mandanten verwenden

    python scripts/rls_system_read.py   # schreibt docs/admin/rls-system-read.json
"""
from __future__ import annotations

import json
import os
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import rls_rollout  # noqa: E402

REPO_ROOT = rls_rollout.REPO_ROOT
OUTPUT = REPO_ROOT / "docs" / "admin" / "rls-system-read.json"
SYSTEM_TENANT = re.compile(
    r"tenant_id\s*(?:=|==|IN\s*\()\s*[^\n]{0,40}['\"]system['\"]|['\"]system['\"]\s*(?:AS|as)\s+tenant_id"
    r"|tenant_id['\"]?\s*:\s*['\"]system['\"]|tenant_id\s*=\s*['\"]system['\"]", re.I)


def rls_tables(conn) -> list[str]:
    import sqlalchemy as sa

    return [r[0] for r in conn.execute(sa.text(
        "SELECT c.oid::regclass::text FROM pg_class c WHERE c.relrowsecurity ORDER BY 1"))]


def _qualified(name: str) -> str:
    return name if "." in name else f"public.{name}"


def system_rows(conn, tables) -> dict[str, int]:
    import sqlalchemy as sa

    counts = {}
    for table in tables:
        has_tenant = conn.execute(sa.text(
            "SELECT 1 FROM pg_attribute WHERE attrelid = to_regclass(:t) AND attname = 'tenant_id' "
            "AND NOT attisdropped"), {"t": table}).scalar()
        if not has_tenant:  # Tabelle fehlt oder Spalte kommt erst mit einer offenen Migration
            continue
        counts[_qualified(table)] = conn.execute(
            sa.text(f"SELECT count(*) FROM {table} WHERE tenant_id::text = 'system'")).scalar()
    return counts


def code_hits(tables) -> dict[str, list[str]]:
    files = list(rls_rollout._code_files())
    hits: dict[str, list[str]] = {}
    for table in tables:
        schema, name = _qualified(table).split(".")
        rx = (re.compile(rf"(?:\bpublic\.{name}\b|(?:FROM|JOIN|INTO|UPDATE)\s+\"?{name}\b|__tablename__\s*=\s*['\"]{name}['\"])", re.I)
              if schema == "public" else re.compile(rf"\b{schema}\.\"?{name}\b"))
        found = []
        for rel, text in files:
            if name not in text or not rx.search(text):
                continue
            found += [f"{rel}:{i}" for i, line in enumerate(text.splitlines(), 1) if SYSTEM_TENANT.search(line)]
        if found:
            hits[_qualified(table)] = found
    return hits


def main() -> int:
    import sqlalchemy as sa
    import rls_inventory

    probe, live = os.environ.get("TEST_DATABASE_URL"), os.environ.get("LIVE_DATABASE_URL")
    if not probe or not live:
        print("TEST_DATABASE_URL und LIVE_DATABASE_URL setzen.")
        return 2
    engine = sa.create_engine(probe)
    with engine.connect() as conn:
        tx = conn.begin()
        try:
            rls_inventory._pending_upgrade(conn)
            tables = rls_tables(conn)
            fresh = system_rows(conn, tables)
        finally:
            tx.rollback()
    engine.dispose()
    engine = sa.create_engine(live)
    with engine.connect() as conn:
        conn.execute(sa.text("SET TRANSACTION READ ONLY"))
        grown = system_rows(conn, tables)
        conn.rollback()
    engine.dispose()
    code = code_hits(tables)
    result = {
        "_note": "Generiert von scripts/rls_system_read.py (frisch zurueckgerollt, live nur lesend).",
        "stand": date.today().isoformat(),
        "tables": {
            _qualified(t): {"frisch": fresh.get(_qualified(t), 0), "live": grown.get(_qualified(t)),
                            "code": code.get(_qualified(t), [])}
            for t in tables
        },
    }
    OUTPUT.write_text(json.dumps(result, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    belegt = {t: v for t, v in result["tables"].items() if v["frisch"] or v["live"] or v["code"]}
    print(f"Geschrieben: {OUTPUT.relative_to(REPO_ROOT)}; {len(result['tables'])} RLS-Tabellen, belegt: {len(belegt)}")
    for t, v in belegt.items():
        print(f"  {t}: frisch {v['frisch']}, live {v['live']}, code {v['code'][:3]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
