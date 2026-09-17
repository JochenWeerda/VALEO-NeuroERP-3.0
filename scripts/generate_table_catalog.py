#!/usr/bin/env python3
"""Erntet das physische domain_*-Schema aus information_schema.

Ausgabe:
  - docs/admin/table-catalog.md
  - docs/admin/table-catalog.json

Verwendung:
    python scripts/generate_table_catalog.py
    python scripts/generate_table_catalog.py --check

Muss gegen eine migrierte Datenbank laufen (nach ``alembic upgrade head`` /
``scripts/init_db.py``), nicht im Doc-Meta-Check ohne Postgres.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

from sqlalchemy import create_engine, text

from scripts.table_ownership import SCHEMA_TO_DOMAIN, classify_table

REPO_ROOT = Path(__file__).resolve().parents[1]
MD_OUTPUT = REPO_ROOT / "docs" / "admin" / "table-catalog.md"
JSON_OUTPUT = REPO_ROOT / "docs" / "admin" / "table-catalog.json"

# Zwei Fachmodelle, die nebeneinander stehen muessen — nicht unter einem Namen.
KNOWN_SIBLING_MODELS: tuple[tuple[str, str, str, str], ...] = (
    ("domain_crm", "crm_consents", "domain_crm", "crm_contact_consents"),
)

_COLUMNS_SQL = """
SELECT table_schema, table_name, column_name, data_type, is_nullable, ordinal_position
FROM information_schema.columns
WHERE table_schema LIKE 'domain\\_%' ESCAPE '\\'
ORDER BY table_schema, table_name, ordinal_position
"""

_TABLES_SQL = """
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_type = 'BASE TABLE'
  AND table_schema LIKE 'domain\\_%' ESCAPE '\\'
ORDER BY table_schema, table_name
"""

_PK_SQL = """
SELECT tc.table_schema, tc.table_name, kcu.column_name, kcu.ordinal_position
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_schema = kcu.constraint_schema
 AND tc.constraint_name = kcu.constraint_name
WHERE tc.constraint_type = 'PRIMARY KEY'
  AND tc.table_schema LIKE 'domain\\_%' ESCAPE '\\'
ORDER BY tc.table_schema, tc.table_name, kcu.ordinal_position
"""

_FK_SQL = """
SELECT
  tc.table_schema,
  tc.table_name,
  kcu.column_name,
  ccu.table_schema AS foreign_schema,
  ccu.table_name AS foreign_table,
  ccu.column_name AS foreign_column
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_schema = kcu.constraint_schema
 AND tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_schema = tc.constraint_schema
 AND ccu.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema LIKE 'domain\\_%' ESCAPE '\\'
ORDER BY tc.table_schema, tc.table_name, kcu.column_name
"""


def database_url() -> str:
    return os.environ.get(
        "DATABASE_URL",
        "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_neuro_erp",
    )


def harvest(url: str | None = None) -> dict[str, Any]:
    engine = create_engine(url or database_url())
    try:
        with engine.connect() as conn:
            tables = [(r[0], r[1]) for r in conn.execute(text(_TABLES_SQL))]
            columns = list(conn.execute(text(_COLUMNS_SQL)))
            pks = list(conn.execute(text(_PK_SQL)))
            fks = list(conn.execute(text(_FK_SQL)))
    finally:
        engine.dispose()
    return assemble_catalog(tables, columns, pks, fks)


def assemble_catalog(
    tables: list[tuple[str, str]],
    columns: list[Any],
    pks: list[Any],
    fks: list[Any],
) -> dict[str, Any]:
    schemas: dict[str, dict[str, Any]] = {}
    for schema, table in tables:
        schemas.setdefault(schema, {"tables": {}})
        schemas[schema]["tables"].setdefault(
            table,
            {"columns": [], "primary_key": [], "foreign_keys": []},
        )

    for schema, schema_body in schemas.items():
        for table, bucket in schema_body["tables"].items():
            verdict = classify_table(schema, table)
            bucket["owner_domain"] = verdict["owner_domain"]
            bucket["placement"] = verdict["placement"]
            if verdict.get("reason"):
                bucket["ownership_reason"] = verdict["reason"]

    for schema, table, name, data_type, nullable, _pos in columns:
        bucket = schemas.get(schema, {}).get("tables", {}).get(table)
        if bucket is None:
            continue
        bucket["columns"].append(
            {
                "name": name,
                "type": data_type,
                "nullable": nullable == "YES",
            }
        )

    pk_map: dict[tuple[str, str], list[str]] = defaultdict(list)
    for schema, table, name, _pos in pks:
        pk_map[(schema, table)].append(name)
    for (schema, table), names in pk_map.items():
        bucket = schemas.get(schema, {}).get("tables", {}).get(table)
        if bucket is not None:
            bucket["primary_key"] = names

    for schema, table, column, f_schema, f_table, f_column in fks:
        bucket = schemas.get(schema, {}).get("tables", {}).get(table)
        if bucket is None:
            continue
        bucket["foreign_keys"].append(
            {
                "column": column,
                "references": f"{f_schema}.{f_table}.{f_column}",
            }
        )

    payload = {"schemas": {name: schemas[name] for name in sorted(schemas)}}
    payload["same_name_across_schemas"] = _same_name_across_schemas(payload)
    payload["sibling_models"] = [
        {
            "left": f"{a}.{b}",
            "right": f"{c}.{d}",
            "reason": "Zwei Fachmodelle, zwei Tabellen — nicht umdeuten.",
        }
        for a, b, c, d in KNOWN_SIBLING_MODELS
        if b in payload["schemas"].get(a, {}).get("tables", {})
        and d in payload["schemas"].get(c, {}).get("tables", {})
    ]
    return payload


def _same_name_across_schemas(payload: dict[str, Any]) -> list[dict[str, Any]]:
    by_name: dict[str, list[str]] = defaultdict(list)
    for schema, body in payload["schemas"].items():
        for table in body.get("tables", {}):
            by_name[table].append(schema)
    return [
        {"table": name, "schemas": sorted(schemas)}
        for name, schemas in sorted(by_name.items())
        if len(schemas) > 1
    ]


def catalog_for_check(payload: dict[str, Any]) -> dict[str, Any]:
    """Zeitstempel raus — der Vergleich gilt dem Schema, nicht dem Lauf."""
    return {
        "schemas": payload.get("schemas", {}),
        "same_name_across_schemas": payload.get("same_name_across_schemas", []),
        "sibling_models": payload.get("sibling_models", []),
    }


def render_json(payload: dict[str, Any]) -> str:
    body = catalog_for_check(payload)
    return json.dumps(body, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def render_markdown(payload: dict[str, Any], today: str | None = None) -> str:
    today = today or date.today().isoformat()
    schemas = payload.get("schemas") or {}
    table_count = sum(len(body.get("tables") or {}) for body in schemas.values())
    column_count = sum(
        len(table.get("columns") or {})
        for body in schemas.values()
        for table in (body.get("tables") or {}).values()
    )
    lines = [
        "---",
        "title: Tabellenkatalog (physisch)",
        "type: reference",
        "audience: [entwickler, architect, betrieb]",
        "owner: Cursor",
        "status: aktiv",
        f"last_reviewed: {today}",
        "version: 1.0.0",
        "description: Generierter Katalog der domain_*-Tabellen aus information_schema.",
        "---",
        "",
        "# Tabellenkatalog (physisch)",
        "",
        "> Automatisch generiert via `python scripts/generate_table_catalog.py`. **Nicht manuell bearbeiten.**",
        "",
        "Quelle: `information_schema` nach `alembic upgrade head`. Logisches Modell:",
        "[ERD Canonical Domain](../architecture/views/erd-canonical-domain.md).",
        "Lebenszyklus (Maske ≠ Drop): [Datenmodell & Tenancy](../entwickler/datenmodell-tenancy.md).",
        "",
        f"**{len(schemas)} Schemas, {table_count} Tabellen, {column_count} Spalten.**",
        "",
        "## Schemas",
        "",
        "| Schema | Domain | Tabellen | Spalten |",
        "|---|---|---|---|",
    ]
    for schema in sorted(schemas):
        tables = schemas[schema].get("tables") or {}
        cols = sum(len(t.get("columns") or []) for t in tables.values())
        domain = SCHEMA_TO_DOMAIN.get(schema, "—")
        lines.append(f"| `{schema}` | `{domain}` | {len(tables)} | {cols} |")

    siblings = payload.get("sibling_models") or []
    if siblings:
        lines.extend(["", "## Geschwister-Modelle", ""])
        for item in siblings:
            lines.append(f"- `{item['left']}` neben `{item['right']}` — {item['reason']}")

    cross = payload.get("same_name_across_schemas") or []
    if cross:
        lines.extend(["", "## Gleicher Tabellenname in mehreren Schemas", ""])
        for item in cross:
            joined = ", ".join(f"`{s}`" for s in item["schemas"])
            lines.append(f"- `{item['table']}` in {joined}")

    for schema in sorted(schemas):
        lines.extend(["", f"## `{schema}`", "", "| Tabelle | Domain | Lage | PK | Spalten |", "|---|---|---|---|---|"])
        tables = schemas[schema].get("tables") or {}
        for table in sorted(tables):
            body = tables[table]
            pk = ", ".join(f"`{c}`" for c in body.get("primary_key") or []) or "—"
            cols = ", ".join(c["name"] for c in body.get("columns") or [])
            domain = body.get("owner_domain") or "—"
            lage = body.get("placement") or "—"
            lines.append(f"| `{table}` | `{domain}` | {lage} | {pk} | {cols} |")
    lines.append("")
    return "\n".join(lines)


def normalize_markdown(text: str) -> str:
    lines = []
    for line in text.splitlines():
        if line.startswith("last_reviewed:"):
            continue
        if line.startswith("> Automatisch generiert"):
            continue
        lines.append(line)
    return "\n".join(lines).strip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Physischen Tabellenkatalog erzeugen")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Drift gegen die committeten Dateien (Exit 1 bei Abweichung).",
    )
    args = parser.parse_args()

    try:
        payload = harvest()
    except Exception as exc:  # noqa: BLE001 — CLI soll den Grund zeigen, nicht den Trace verschlucken
        print(f"FEHLER: Katalog konnte nicht geerntet werden: {exc}", file=sys.stderr)
        return 2

    md = render_markdown(payload)
    js = render_json(payload)

    if args.check:
        problems: list[str] = []
        if not JSON_OUTPUT.exists() or not MD_OUTPUT.exists():
            print(
                "FEHLT: Tabellenkatalog nicht committet. "
                "Bitte 'python scripts/generate_table_catalog.py' ausfuehren.",
                file=sys.stderr,
            )
            return 1
        if JSON_OUTPUT.read_text(encoding="utf-8") != js:
            problems.append(str(JSON_OUTPUT.relative_to(REPO_ROOT)))
        if normalize_markdown(MD_OUTPUT.read_text(encoding="utf-8")) != normalize_markdown(md):
            problems.append(str(MD_OUTPUT.relative_to(REPO_ROOT)))
        if problems:
            print(
                "DRIFT: Tabellenkatalog nicht aktuell. "
                "Bitte 'python scripts/generate_table_catalog.py' nach "
                "'alembic upgrade head' ausfuehren.",
                file=sys.stderr,
            )
            for path in problems:
                print(f"  - {path}", file=sys.stderr)
            return 1
        table_count = sum(len(s.get("tables") or {}) for s in payload["schemas"].values())
        print(f"OK: Tabellenkatalog aktuell ({table_count} Tabellen).")
        return 0

    MD_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    MD_OUTPUT.write_text(md, encoding="utf-8")
    JSON_OUTPUT.write_text(js, encoding="utf-8")
    table_count = sum(len(s.get("tables") or {}) for s in payload["schemas"].values())
    print(f"Geschrieben: {MD_OUTPUT.relative_to(REPO_ROOT)} ({table_count} Tabellen).")
    print(f"Geschrieben: {JSON_OUTPUT.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
