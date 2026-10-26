#!/usr/bin/env python3
"""Berichtet, woher die Schemaaenderungen einer Datenbank stammen.

Warum
-----
Schemaaenderungen kommen aus Alembic, aus drizzle-kit, von Agenten oder von Hand
mit ``psql``. Bisher war nur der Zustand pruefbar (``check_schema_drift.py``),
nicht der Weg dorthin. Die Migration ``governance_ddl_log_20261026`` schreibt per
Event-Trigger jede Aenderung nach ``governance.ddl_events``; dieses Skript wertet
das Protokoll aus.

Was geprueft wird
-----------------
- Schema, Protokolltabelle und beide Event-Trigger sind vorhanden und aktiv
  (sonst Exit 2: ohne Protokoll ist keine Aussage moeglich).
- Jede protokollierte Aenderung seit ``--seit`` stammt aus einer erlaubten Quelle
  (``--erlaubt``, Standard alembic und drizzle-kit); sonst Exit 1 mit Liste.

Die Quelle leitet sich aus ``application_name`` ab, den der Client selbst setzt.
Sie belegt, wer sich wie ausgegeben hat, nicht wer es war; belastbar wird sie erst
mit getrennten Rollen (Konzept: docs/architecture/db-governance-20261026.md).

Aufruf
------
    python scripts/check_ddl_provenance.py                       # DATABASE_URL
    python scripts/check_ddl_provenance.py --url "$TEST_DATABASE_URL" --seit 2026-10-26
    python scripts/check_ddl_provenance.py --erlaubt alembic     # CI nach alembic upgrade
    python scripts/check_ddl_provenance.py --json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

TRIGGERS = ("governance_ddl_command_end", "governance_sql_drop")


def bewerte(zustand: dict[str, Any], erlaubt: set[str]) -> tuple[int, list[str]]:
    """Exit-Code und Befunde aus dem gelesenen Zustand ableiten."""
    befunde: list[str] = []
    if not zustand["tabelle"]:
        return 2, ["governance.ddl_events fehlt: Migration governance_ddl_log_20261026 nicht angewandt"]
    fehlend = [t for t in TRIGGERS if zustand["trigger"].get(t) is None]
    inaktiv = [t for t, status in zustand["trigger"].items() if status == "D"]
    if fehlend:
        befunde.append(f"Event-Trigger fehlen: {', '.join(fehlend)} (Superuser-Rechte bei der Migration?)")
    if inaktiv:
        befunde.append(f"Event-Trigger deaktiviert: {', '.join(inaktiv)}")
    if befunde:
        return 2, befunde
    fremd = [e for e in zustand["ereignisse"] if e["source"] not in erlaubt]
    for e in fremd:
        befunde.append(
            f"{e['occurred_at']} {e['source']} ({e['application_name'] or '-'}, Rolle {e['session_role']}): "
            f"{e['command_tag']} {e['object_identity'] or e['object_type'] or ''}".rstrip()
        )
    return (1 if fremd else 0), befunde


def lies_zustand(url: str, seit: str | None) -> dict[str, Any]:
    from sqlalchemy import create_engine, text

    engine = create_engine(url)
    try:
        with engine.connect() as conn:
            tabelle = conn.execute(text("SELECT to_regclass('governance.ddl_events') IS NOT NULL")).scalar()
            trigger = {
                name: status
                for name, status in conn.execute(
                    text("SELECT evtname, evtenabled FROM pg_event_trigger WHERE evtname = ANY(:namen)"),
                    {"namen": list(TRIGGERS)},
                )
            }
            ereignisse: list[dict[str, Any]] = []
            if tabelle:
                sql = (
                    "SELECT occurred_at, event, command_tag, object_type, schema_name, object_identity, "
                    "session_role, application_name, source FROM governance.ddl_events "
                    + ("WHERE occurred_at >= CAST(:seit AS timestamptz) " if seit else "")
                    + "ORDER BY occurred_at, id"
                )
                ereignisse = [dict(r._mapping) for r in conn.execute(text(sql), {"seit": seit} if seit else {})]
    finally:
        engine.dispose()
    return {"tabelle": bool(tabelle), "trigger": trigger, "ereignisse": ereignisse}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--url", default=os.environ.get("DATABASE_URL"))
    parser.add_argument("--seit", help="nur Ereignisse ab diesem Zeitpunkt (ISO-Datum/-Zeit)")
    parser.add_argument("--erlaubt", nargs="+", default=["alembic", "drizzle-kit"])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.url:
        raise SystemExit("Keine Datenbank: --url oder DATABASE_URL setzen.")

    zustand = lies_zustand(args.url, args.seit)
    code, befunde = bewerte(zustand, set(args.erlaubt))
    quellen: dict[str, int] = {}
    for e in zustand["ereignisse"]:
        quellen[e["source"]] = quellen.get(e["source"], 0) + 1

    if args.json:
        print(json.dumps({"exit": code, "quellen": quellen, "befunde": befunde}, ensure_ascii=False, indent=2))
    else:
        print(f"DDL-Ereignisse nach Quelle: {quellen or 'keine'}")
        for b in befunde:
            print(f"- {b}")
        if code == 0:
            print("Alle protokollierten Schemaaenderungen stammen aus erlaubten Quellen.")
    return code


if __name__ == "__main__":
    sys.exit(main())
