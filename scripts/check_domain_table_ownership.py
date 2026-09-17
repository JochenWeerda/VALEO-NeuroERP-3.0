"""Verify table ownership across ERP domain schemas.

Enforces:
1. Every domain_* schema has a documented Architecture-OS domain (only-up).
2. Exact ownership for selected anchor tables.
3. Prefix-based ownership for tables whose naming encodes a schema.
4. Documented tolerated legacy placements — unnamed mismatches fail.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from sqlalchemy import create_engine, text

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from scripts.table_ownership import (  # noqa: E402
    EXACT_TABLE_OWNERSHIP,
    SCHEMA_TO_DOMAIN,
    TOLERATED_LEGACY_LOCATIONS,
    classify_table,
)


def load_locations(database_url: str) -> set[tuple[str, str]]:
    engine = create_engine(database_url)
    try:
        with engine.connect() as conn:
            rows = conn.execute(
                text(
                    """
                    SELECT table_schema, table_name
                    FROM information_schema.tables
                    WHERE table_type = 'BASE TABLE'
                      AND table_schema LIKE 'domain\\_%' ESCAPE '\\'
                    ORDER BY table_schema, table_name
                    """
                )
            ).fetchall()
    finally:
        engine.dispose()
    return {(row[0], row[1]) for row in rows}


def evaluate(locations: set[tuple[str, str]]) -> tuple[list[str], list[str], int]:
    failures: list[str] = []
    notes: list[str] = []
    classified = 0

    live_schemas = {schema for schema, _table in locations}
    extra = sorted(live_schemas - set(SCHEMA_TO_DOMAIN))
    for schema in extra:
        failures.append(f"{schema}: Schema ohne Architecture-Domain (SCHEMA_TO_DOMAIN ergaenzen).")

    schema_by_table: dict[str, set[str]] = {}
    for schema, table in locations:
        schema_by_table.setdefault(table, set()).add(schema)

    for schema, tables in EXACT_TABLE_OWNERSHIP.items():
        for table in tables:
            if (schema, table) not in locations:
                actual = sorted(schema_by_table.get(table, set()))
                failures.append(
                    f"{table}: expected {schema}, found {', '.join(actual) if actual else 'missing'}"
                )

    for schema, table in sorted(locations):
        verdict = classify_table(schema, table)
        classified += 1
        if verdict["placement"] == "legacy":
            notes.append(f"{schema}.{table}: {verdict['reason']}")
        if not verdict["ok"]:
            failures.append(f"{schema}.{table}: {verdict['reason']}")

    return failures, notes, classified


def main() -> None:
    database_url = os.environ.get(
        "DATABASE_URL",
        "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_neuro_erp",
    )
    locations = load_locations(database_url)
    failures, notes, classified = evaluate(locations)

    if notes:
        print("Documented legacy placements:")
        for note in notes:
            print(f"- {note}")

    if failures:
        raise SystemExit(
            "Domain table ownership drift detected:\n- " + "\n- ".join(sorted(failures))
        )

    print(
        f"Domain table ownership OK ({classified} Tabellen, "
        f"{len(SCHEMA_TO_DOMAIN)} Schemas, {len(notes)} Legacy-Lagen)."
    )


if __name__ == "__main__":
    main()
