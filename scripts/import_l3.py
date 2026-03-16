"""
L3 -> VALEO NeuroERP ETL scaffold.

This script consumes:
  * a mapping file (YAML) describing how legacy tables/columns map to the
    new schema, and
  * a directory containing the exported L3 data (CSV, TSV or JSON).

It performs strict source-contract validation before any import starts.

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
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from scripts.validate_mapping import ValidationError, load_mapping as load_mapping_definition


SUPPORTED_EXTENSIONS = (".csv", ".tsv", ".json")


@dataclass(frozen=True)
class ImportIssue:
    table: str
    message: str


class ImportContractError(RuntimeError):
    def __init__(self, issues: list[ImportIssue]):
        self.issues = issues
        super().__init__(format_import_issues(issues))


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


def load_mapping(mapping_path: Path) -> dict[str, Any]:
    try:
        return load_mapping_definition(mapping_path)
    except ValidationError as exc:
        raise ImportContractError([ImportIssue(table="<mapping>", message=str(exc))]) from exc


def _normalize_rows(file_path: Path, raw_rows: Any) -> list[dict[str, Any]]:
    if isinstance(raw_rows, dict):
        rows = raw_rows.get("rows")
    else:
        rows = raw_rows

    if not isinstance(rows, list):
        raise ImportContractError(
            [ImportIssue(table=file_path.stem, message=f"{file_path.name} must contain a list of row objects.")]
        )

    normalized_rows: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        if not isinstance(row, dict):
            raise ImportContractError(
                [
                    ImportIssue(
                        table=file_path.stem,
                        message=f"{file_path.name} row {index} is not an object and cannot be imported.",
                    )
                ]
            )
        normalized_rows.append({str(key): value for key, value in row.items()})
    return normalized_rows


def load_table_file(file_path: Path) -> list[dict[str, Any]]:
    if file_path.suffix.lower() == ".json":
        return _normalize_rows(file_path, json.loads(file_path.read_text(encoding="utf-8")))
    delimiter = "," if file_path.suffix.lower() == ".csv" else "\t"
    with file_path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        return _normalize_rows(file_path, list(reader))


def discover_source_files(source_dir: Path) -> dict[str, Path]:
    return {
        file.stem.upper(): file
        for file in source_dir.glob("*")
        if file.suffix.lower() in SUPPORTED_EXTENSIONS
    }


def _iter_required_columns(columns: dict[str, Any]) -> list[str]:
    required_columns: list[str] = []
    for legacy_column, spec in columns.items():
        if isinstance(spec, dict) and spec.get("skip"):
            continue
        required_columns.append(legacy_column)
    return required_columns


def collect_import_issues(mapping: dict[str, Any], source_dir: Path) -> list[ImportIssue]:
    issues: list[ImportIssue] = []
    available_files = discover_source_files(source_dir)

    for table, columns in mapping.items():
        file_path = available_files.get(table.upper())
        if not file_path:
            issues.append(ImportIssue(table=table, message="Missing export file for mapped table."))
            continue

        rows = load_table_file(file_path)
        if not rows:
            issues.append(ImportIssue(table=table, message=f"{file_path.name} contains no rows."))
            continue

        source_columns = {str(col).upper() for col in rows[0].keys()}
        for legacy_column in _iter_required_columns(columns):
            if legacy_column.upper() not in source_columns:
                issues.append(
                    ImportIssue(
                        table=table,
                        message=f"Column {legacy_column} not present in {file_path.name}.",
                    )
                )

    return issues


def format_import_issues(issues: list[ImportIssue]) -> str:
    lines = ["L3 import contract validation failed:"]
    for issue in issues:
        lines.append(f"- {issue.table}: {issue.message}")
    return "\n".join(lines)


def validate_source_contract(mapping: dict[str, Any], source_dir: Path) -> None:
    issues = collect_import_issues(mapping, source_dir)
    if issues:
        raise ImportContractError(issues)


def validate_mapping(mapping: dict[str, Any], source_dir: Path) -> None:
    validate_source_contract(mapping, source_dir)


def import_table(
    session: Session,
    table_name: str,
    mapping: dict[str, Any],
    rows: list[dict[str, Any]],
    dry_run: bool,
) -> None:
    # Placeholder: In a full implementation we would resolve the target table/columns based on the
    # mapping, apply transformations and perform INSERT/UPDATE statements.
    # For now we just emit statistics to help with manual verification.
    target_columns = [spec.get("target", "<missing target>") for spec in mapping.values()]
    print(f"Table {table_name}: {len(rows)} rows -> targets {target_columns}")

    if dry_run:
        return

    try:
        session.execute("SELECT 1")
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
    validate_source_contract(mapping, args.source)

    if args.dry_run:
        print("Dry-run mode enabled - no data will be written.")

    session = SessionLocal()
    try:
        available_files = discover_source_files(args.source)
        for table, column_mapping in mapping.items():
            data_file = available_files[table.upper()]
            rows = load_table_file(data_file)
            import_table(session, table, column_mapping, rows, args.dry_run)

        if not args.dry_run:
            session.commit()
    finally:
        session.close()

    print("L3 import completed.")


if __name__ == "__main__":
    main()
