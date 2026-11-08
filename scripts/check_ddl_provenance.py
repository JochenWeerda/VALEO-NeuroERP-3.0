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
Sind die Rollen aus ``scripts/provision_db_roles.py`` eingerichtet, entscheidet
stattdessen die handelnde Rolle: DDL ueber valeo_owner/valeo_migrator ist in Ordnung,
DDL direkt als Superuser ist ein Hinweis (mit ``--ohne-superuser`` ein Befund), jede
andere Rolle ein Befund; eine angegebene Werkzeugquelle ohne Migratorrolle gilt als
vorgetaeuscht. Konzept: docs/architecture/db-governance-20261026.md.

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
MIGRATOR_ROLES = {"valeo_owner", "valeo_migrator"}
TOOL_SOURCES = {"alembic", "drizzle-kit", "orm-create-all"}


def _zeile(e: dict[str, Any], grund: str) -> str:
    return (
        f"{e['occurred_at']} {grund} ({e['application_name'] or '-'}, Rolle {e['session_role']}"
        f"/{e.get('current_role_name') or e['session_role']}): "
        f"{e['command_tag']} {e['object_identity'] or e['object_type'] or ''}".rstrip()
    )


def bewerte(
    zustand: dict[str, Any], erlaubt: set[str], superuser_erlaubt: bool = True
) -> tuple[int, list[str], list[str]]:
    """Exit-Code, Befunde und Hinweise aus dem gelesenen Zustand ableiten."""
    befunde: list[str] = []
    hinweise: list[str] = []
    if not zustand["tabelle"]:
        return 2, ["governance.ddl_events fehlt: Migration governance_ddl_log_20261026 nicht angewandt"], []
    fehlend = [t for t in TRIGGERS if zustand["trigger"].get(t) is None]
    inaktiv = [t for t, status in zustand["trigger"].items() if status == "D"]
    if fehlend:
        befunde.append(f"Event-Trigger fehlen: {', '.join(fehlend)} (Superuser-Rechte bei der Migration?)")
    if inaktiv:
        befunde.append(f"Event-Trigger deaktiviert: {', '.join(inaktiv)}")
    if befunde:
        return 2, befunde, []
    for e in zustand["ereignisse"]:
        if not zustand.get("rollen_eingerichtet"):
            if e["source"] not in erlaubt:
                befunde.append(_zeile(e, e["source"]))
            continue
        handelnd = e.get("current_role_name") or e["session_role"]
        if handelnd in MIGRATOR_ROLES:
            continue
        if e.get("session_super") and handelnd == e["session_role"]:
            (hinweise if superuser_erlaubt else befunde).append(_zeile(e, f"superuser/{e['source']}"))
        elif e["source"] in TOOL_SOURCES:
            befunde.append(_zeile(e, f"vorgetaeuscht {e['source']} ohne Migratorrolle"))
        else:
            befunde.append(_zeile(e, f"DDL ohne Migratorrolle ({e['source']})"))
    return (1 if befunde else 0), befunde, hinweise


def lies_zustand(url: str, seit: str | None) -> dict[str, Any]:
    from sqlalchemy import create_engine, text

    engine = create_engine(url)
    try:
        with engine.connect() as conn:
            tabelle = conn.execute(text("SELECT to_regclass('governance.ddl_events') IS NOT NULL")).scalar()
            rollen = conn.execute(text("SELECT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'valeo_migrator')")).scalar()
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
                    "SELECT e.occurred_at, e.event, e.command_tag, e.object_type, e.schema_name, e.object_identity, "
                    "e.session_role, e.current_role_name, e.application_name, e.source, "
                    "coalesce(r.rolsuper, false) AS session_super "
                    "FROM governance.ddl_events e LEFT JOIN pg_roles r ON r.rolname = e.session_role "
                    + ("WHERE e.occurred_at >= CAST(:seit AS timestamptz) " if seit else "")
                    + "ORDER BY e.occurred_at, e.id"
                )
                ereignisse = [dict(r._mapping) for r in conn.execute(text(sql), {"seit": seit} if seit else {})]
    finally:
        engine.dispose()
    return {"tabelle": bool(tabelle), "trigger": trigger, "ereignisse": ereignisse, "rollen_eingerichtet": bool(rollen)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--url", default=os.environ.get("DATABASE_URL"))
    parser.add_argument("--seit", help="nur Ereignisse ab diesem Zeitpunkt (ISO-Datum/-Zeit)")
    parser.add_argument("--erlaubt", nargs="+", default=["alembic", "drizzle-kit"])
    parser.add_argument("--ohne-superuser", action="store_true", help="Superuser-DDL als Befund werten")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not args.url:
        raise SystemExit("Keine Datenbank: --url oder DATABASE_URL setzen.")

    zustand = lies_zustand(args.url, args.seit)
    code, befunde, hinweise = bewerte(zustand, set(args.erlaubt), superuser_erlaubt=not args.ohne_superuser)
    quellen: dict[str, int] = {}
    for e in zustand["ereignisse"]:
        quellen[e["source"]] = quellen.get(e["source"], 0) + 1

    if args.json:
        print(json.dumps({"exit": code, "rollen_eingerichtet": zustand["rollen_eingerichtet"], "quellen": quellen,
                          "befunde": befunde, "hinweise": hinweise}, ensure_ascii=False, indent=2))
    else:
        modus = "handelnde Rolle" if zustand["rollen_eingerichtet"] else "angegebene Quelle"
        print(f"DDL-Ereignisse nach Quelle: {quellen or 'keine'} (Bewertung nach {modus})")
        for b in befunde:
            print(f"- {b}")
        for h in hinweise:
            print(f"  Hinweis: {h}")
        if code == 0:
            print("Alle protokollierten Schemaaenderungen stammen aus erlaubten Quellen.")
    return code


if __name__ == "__main__":
    sys.exit(main())
