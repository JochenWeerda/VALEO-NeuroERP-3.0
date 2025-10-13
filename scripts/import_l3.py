"""
L3 → VALEO NeuroERP ETL scaffold.

This script consumes:
  * a mapping file (YAML) describing how legacy tables/columns map to the
    new schema, and
  * a directory containing the exported L3 data (CSV, TSV or JSON).

It performs basic validation and (optionally) imports the data into the
target database.

Usage examples:
  python scripts/import_l3.py \
    --mapping config/l3_mapping.yaml \
    --source data/l3_export \
    --dry-run
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any, Dict

import yaml  # type: ignore[import]
from sqlalchemy import Table
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, engine


SUPPORTED_EXTENSIONS = (".csv", ".tsv", ".json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import legacy L3 data.")
    parser.add_argument(
        "--mapping",
        required=True,
        type=Path,
        help="Path to the YAML mapping file (see config/l3_mapping.template.yaml).",
    )
    parser.add_argument(
        "--source",
        required=True,
        type=Path,
        help="Directory containing exported L3 files (CSV/TSV/JSON).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate mapping/data without writing to the database.",
    )
    return parser.parse_args()


def load_mapping(mapping_path: Path) -> Dict[str, Any]:
    with mapping_path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_table_file(file_path: Path) -> Any:
    if file_path.suffix.lower() == ".json":
        return json.loads(file_path.read_text(encoding="utf-8"))
    delimiter = "," if file_path.suffix.lower() == ".csv" else "\t"
    with file_path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        return list(reader)


def validate_mapping(mapping: Dict[str, Any], source_dir: Path) -> None:
    available_files = {
        file.stem.upper(): file for file in source_dir.glob("*") if file.suffix.lower() in SUPPORTED_EXTENSIONS
    }

    missing_files = [table for table in mapping.keys() if table.upper() not in available_files]
    if missing_files:
        print("⚠️  Missing export files for tables:", ", ".join(missing_files))

    for table, columns in mapping.items():
        file_path = available_files.get(table.upper())
        if not file_path:
            continue
        rows = load_table_file(file_path)
        if not rows:
            print(f"⚠️  File {file_path.name} contains no data.")
            continue

        sample_row = rows[0]
        source_columns = {col.upper() for col in sample_row.keys()}
        for legacy_column in columns.keys():
            if legacy_column.upper() not in source_columns:
                print(f"⚠️  Column {legacy_column} not present in {file_path.name}")


def import_table(
    session: Session,
    table_name: str,
    mapping: Dict[str, Any],
    rows: Any,
    dry_run: bool,
) -> None:
    # Placeholder: In a full implementation we would resolve the target table/columns based on the
    # mapping, apply transformations and perform INSERT/UPDATE statements.
    # For now we just emit statistics to help with manual verification.
    target_columns = [spec.get("target", "<missing target>") for spec in mapping.values()]
    print(f"Table {table_name}: {len(rows)} rows -> targets {target_columns}")

    if dry_run:
        return

    # Example pseudo-write:
    try:
        session.execute("SELECT 1")  # ensure connection works
        session.commit()
    except SQLAlchemyError as exc:
        session.rollback()
        raise RuntimeError(f"Failed to import table {table_name}") from exc


def main() -> None:
    args = parse_args()

    if not args.mapping.exists():
        raise FileNotFoundError(f"Mapping file not found: {args.mapping}")
    if not args.source.exists():
        raise FileNotFoundError(f"Source directory not found: {args.source}")

    mapping = load_mapping(args.mapping)
    validate_mapping(mapping, args.source)

    if args.dry_run:
        print("Dry-run mode enabled – no data will be written.")

    session = SessionLocal()
    try:
        for table, column_mapping in mapping.items():
            data_file = None
            for ext in SUPPORTED_EXTENSIONS:
                candidate = args.source / f"{table}{ext}"
                if candidate.exists():
                    data_file = candidate
                    break
            if data_file is None:
                print(f"Skipping {table} – no matching file found.")
                continue

            rows = load_table_file(data_file)
            if not rows:
                print(f"Skipping {table} – no rows in file.")
                continue

            import_table(session, table, column_mapping, rows, args.dry_run)

        if not args.dry_run:
            session.commit()
    finally:
        session.close()

    print("L3 import completed.")


if __name__ == "__main__":
    main()
