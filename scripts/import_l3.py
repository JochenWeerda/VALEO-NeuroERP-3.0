"""
L3 -> VALEO NeuroERP ETL / landing-zone import.

The current implementation focuses on safe migration preparation:

- strict source-contract validation against the mapping file,
- dry-run by default,
- optional raw landing-zone load into `l3_staging`,
- append-only run tracking in `app_control.l3_import_runs`,
- optional incremental filtering via `--since`,
- optional pre-execute `pg_dump` backup.

It deliberately stops short of domain-specific transforms. Those are expected to
follow after staging and domain-owner review.
"""

from __future__ import annotations

import argparse
import csv
import json
import logging
import os
import re
import subprocess
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from sqlalchemy import text
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from scripts.validate_mapping import ValidationError, load_mapping as load_mapping_definition


SUPPORTED_EXTENSIONS = (".csv", ".tsv", ".json")
INCREMENTAL_CANDIDATE_COLUMNS = (
    "UPDATED_AT",
    "MODIFIED_AT",
    "AENDERUNGSDATUM",
    "CHANGE_DATE",
    "DTAENDERUNG",
    "DATUM",
)

logger = logging.getLogger("l3_import")


@dataclass(frozen=True)
class ImportIssue:
    table: str
    message: str


@dataclass(frozen=True)
class TableImportSummary:
    table: str
    source_file: str
    staging_table: str
    total_rows: int
    selected_rows: int
    loaded_rows: int
    skipped_rows: int
    since_column: str | None = None


class ImportContractError(RuntimeError):
    def __init__(self, issues: list[ImportIssue]):
        self.issues = issues
        super().__init__(format_import_issues(issues))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import legacy L3 data into the raw staging zone.")
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
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate mapping/data without writing to the database.",
    )
    mode_group.add_argument(
        "--execute",
        action="store_true",
        help="Load validated source rows into l3_staging and record the import run.",
    )
    parser.add_argument(
        "--since",
        help="Optional lower bound for incremental loads (ISO date/datetime).",
    )
    parser.add_argument(
        "--since-column",
        help="Preferred legacy column to evaluate for incremental filtering.",
    )
    parser.add_argument(
        "--source-system",
        default="service-erp-l3",
        help="Source system label recorded in app_control.l3_import_runs.",
    )
    parser.add_argument(
        "--tenant-id",
        default="default",
        help="Tenant label recorded for the import run metadata.",
    )
    parser.add_argument(
        "--report-json",
        type=Path,
        help="Optional path for a machine-readable import report.",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=Path("logs/db/import_l3.log"),
        help="Path for the import log file.",
    )
    parser.add_argument(
        "--backup-before-execute",
        action="store_true",
        help="Create a pg_dump backup before loading rows into l3_staging.",
    )
    parser.add_argument(
        "--backup-dir",
        type=Path,
        default=Path("logs/db/backups"),
        help="Target directory for pg_dump backups.",
    )
    return parser.parse_args()


def configure_logging(log_path: Path) -> None:
    log_path.parent.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_path, encoding="utf-8"),
        ],
        force=True,
    )


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


def parse_since_value(raw_value: str | None) -> datetime | None:
    if not raw_value:
        return None
    normalized = raw_value.strip()
    if not normalized:
        return None
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        parsed_date = date.fromisoformat(normalized)
        parsed = datetime.combine(parsed_date, datetime.min.time())
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def parse_row_timestamp(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, date):
        parsed = datetime.combine(value, datetime.min.time())
    else:
        raw = str(value).strip()
        if not raw:
            return None
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        try:
            parsed = datetime.fromisoformat(raw)
        except ValueError:
            for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%Y%m%d", "%Y-%m-%d %H:%M:%S", "%d.%m.%Y %H:%M:%S"):
                try:
                    parsed = datetime.strptime(raw, fmt)
                    break
                except ValueError:
                    continue
            else:
                return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def select_rows_since(
    rows: list[dict[str, Any]],
    since: datetime | None,
    preferred_column: str | None = None,
) -> tuple[list[dict[str, Any]], str | None]:
    if since is None:
        return rows, None

    candidate_columns: list[str] = []
    if preferred_column:
        candidate_columns.append(preferred_column)
    candidate_columns.extend(INCREMENTAL_CANDIDATE_COLUMNS)

    used_column: str | None = None
    selected_rows = rows

    for candidate in candidate_columns:
        for row in rows:
            if candidate not in row:
                continue
            parsed = parse_row_timestamp(row.get(candidate))
            if parsed is None:
                continue
            used_column = candidate
            selected_rows = [
                row_payload
                for row_payload in rows
                if (parsed_ts := parse_row_timestamp(row_payload.get(candidate))) is not None and parsed_ts >= since
            ]
            return selected_rows, used_column

    return rows, used_column


def quote_pg_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def normalize_table_identifier(name: str) -> str:
    normalized = re.sub(r"[^a-z0-9_]+", "_", name.strip().lower())
    normalized = re.sub(r"_+", "_", normalized).strip("_")
    return normalized or "legacy_table"


def ensure_control_tables(session: Session) -> None:
    session.execute(text("CREATE SCHEMA IF NOT EXISTS app_control"))
    session.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS app_control.l3_import_runs (
                run_id TEXT PRIMARY KEY,
                source_system TEXT NOT NULL,
                tenant_id TEXT NOT NULL,
                mode TEXT NOT NULL,
                mapping_path TEXT NOT NULL,
                source_path TEXT NOT NULL,
                since_filter TEXT NULL,
                status TEXT NOT NULL,
                tables_total INTEGER NOT NULL DEFAULT 0,
                rows_total INTEGER NOT NULL DEFAULT 0,
                staging_rows_loaded INTEGER NOT NULL DEFAULT 0,
                backup_path TEXT NULL,
                report_json JSONB NULL,
                error_message TEXT NULL,
                started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                finished_at TIMESTAMPTZ NULL
            )
            """
        )
    )
    session.execute(text("CREATE SCHEMA IF NOT EXISTS l3_staging"))


def start_import_run(
    session: Session,
    *,
    run_id: str,
    args: argparse.Namespace,
    mode: str,
    since_filter: str | None,
) -> None:
    session.execute(
        text(
            """
            INSERT INTO app_control.l3_import_runs (
                run_id,
                source_system,
                tenant_id,
                mode,
                mapping_path,
                source_path,
                since_filter,
                status
            ) VALUES (
                :run_id,
                :source_system,
                :tenant_id,
                :mode,
                :mapping_path,
                :source_path,
                :since_filter,
                'running'
            )
            """
        ),
        {
            "run_id": run_id,
            "source_system": args.source_system,
            "tenant_id": args.tenant_id,
            "mode": mode,
            "mapping_path": str(args.mapping),
            "source_path": str(args.source),
            "since_filter": since_filter,
        },
    )


def finish_import_run(
    session: Session,
    *,
    run_id: str,
    status: str,
    report_payload: dict[str, Any],
    backup_path: str | None = None,
    error_message: str | None = None,
) -> None:
    session.execute(
        text(
            """
            UPDATE app_control.l3_import_runs
            SET status = :status,
                tables_total = :tables_total,
                rows_total = :rows_total,
                staging_rows_loaded = :staging_rows_loaded,
                backup_path = :backup_path,
                report_json = CAST(:report_json AS JSONB),
                error_message = :error_message,
                finished_at = now()
            WHERE run_id = :run_id
            """
        ),
        {
            "run_id": run_id,
            "status": status,
            "tables_total": int(report_payload["tables_total"]),
            "rows_total": int(report_payload["rows_total"]),
            "staging_rows_loaded": int(report_payload["staging_rows_loaded"]),
            "backup_path": backup_path,
            "report_json": json.dumps(report_payload, ensure_ascii=True),
            "error_message": error_message,
        },
    )


def ensure_staging_columns(session: Session, legacy_table: str, column_names: list[str]) -> str:
    table_name = normalize_table_identifier(legacy_table)
    quoted_table = quote_pg_identifier(table_name)

    session.execute(
        text(
            f"""
            CREATE TABLE IF NOT EXISTS l3_staging.{quoted_table} (
                _import_run_id TEXT NOT NULL,
                _source_file TEXT NOT NULL,
                _source_row_number INTEGER NOT NULL,
                _loaded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                _payload JSONB NOT NULL DEFAULT '{{}}'::jsonb
            )
            """
        )
    )

    for column_name in column_names:
        quoted_column = quote_pg_identifier(column_name)
        session.execute(
            text(
                f'ALTER TABLE l3_staging.{quoted_table} ADD COLUMN IF NOT EXISTS {quoted_column} TEXT'
            )
        )

    return f"l3_staging.{table_name}"


def load_rows_into_staging(
    session: Session,
    *,
    run_id: str,
    legacy_table: str,
    source_file: Path,
    rows: list[dict[str, Any]],
) -> TableImportSummary:
    column_names = sorted({str(column) for row in rows for column in row.keys()})
    staging_table = ensure_staging_columns(session, legacy_table, column_names)
    table_name = normalize_table_identifier(legacy_table)
    quoted_table = quote_pg_identifier(table_name)

    bind_names = {column_name: f"c{index}" for index, column_name in enumerate(column_names)}
    quoted_source_columns = [quote_pg_identifier(column_name) for column_name in column_names]
    metadata_columns = ["_import_run_id", "_source_file", "_source_row_number", "_payload"]
    bind_tokens = [f":{bind_names[column_name]}" for column_name in column_names]
    bind_tokens.extend([":_import_run_id", ":_source_file", ":_source_row_number", "CAST(:_payload AS JSONB)"])

    insert_sql = text(
        f"""
        INSERT INTO l3_staging.{quoted_table} (
            {", ".join(quoted_source_columns + metadata_columns)}
        ) VALUES (
            {", ".join(bind_tokens)}
        )
        """
    )

    payloads: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        payload = {bind_names[column_name]: None if row.get(column_name) is None else str(row.get(column_name)) for column_name in column_names}
        payload["_import_run_id"] = run_id
        payload["_source_file"] = source_file.name
        payload["_source_row_number"] = index
        payload["_payload"] = json.dumps(row, ensure_ascii=True)
        payloads.append(payload)

    if payloads:
        session.execute(insert_sql, payloads)

    return TableImportSummary(
        table=legacy_table,
        source_file=source_file.name,
        staging_table=staging_table,
        total_rows=len(rows),
        selected_rows=len(rows),
        loaded_rows=len(rows),
        skipped_rows=0,
    )


def run_pg_dump_backup(target_dir: Path) -> Path:
    target_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = target_dir / f"l3-import-pre-execute-{timestamp}.sql"

    url = make_url(settings.DATABASE_URL)
    if not str(url.drivername).startswith("postgresql"):
        raise RuntimeError("Automatic L3 import backup currently supports PostgreSQL only.")

    command = [
        "pg_dump",
        "-h",
        url.host or "localhost",
        "-p",
        str(url.port or 5432),
        "-U",
        url.username or "postgres",
        "-d",
        url.database or "",
        "-f",
        str(output_path),
    ]
    env = os.environ.copy()
    if url.password:
        env["PGPASSWORD"] = url.password
    subprocess.run(command, check=True, env=env)
    return output_path


def build_report(
    *,
    run_id: str,
    args: argparse.Namespace,
    mode: str,
    backup_path: str | None,
    table_summaries: list[TableImportSummary],
) -> dict[str, Any]:
    rows_total = sum(item.total_rows for item in table_summaries)
    staging_rows_loaded = sum(item.loaded_rows for item in table_summaries)
    return {
        "run_id": run_id,
        "mode": mode,
        "source_system": args.source_system,
        "tenant_id": args.tenant_id,
        "mapping_path": str(args.mapping),
        "source_path": str(args.source),
        "since": args.since,
        "since_column": args.since_column,
        "backup_path": backup_path,
        "tables_total": len(table_summaries),
        "rows_total": rows_total,
        "staging_rows_loaded": staging_rows_loaded,
        "tables": [
            {
                "table": item.table,
                "source_file": item.source_file,
                "staging_table": item.staging_table,
                "total_rows": item.total_rows,
                "selected_rows": item.selected_rows,
                "loaded_rows": item.loaded_rows,
                "skipped_rows": item.skipped_rows,
                "since_column": item.since_column,
            }
            for item in table_summaries
        ],
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def write_report(report_path: Path, payload: dict[str, Any]) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    configure_logging(args.log_file)

    if not args.mapping.exists():
        raise FileNotFoundError(f"Mapping file not found: {args.mapping}")
    if not args.source.exists():
        raise FileNotFoundError(f"Source directory not found: {args.source}")

    mapping = load_mapping(args.mapping)
    validate_source_contract(mapping, args.source)

    since_filter = parse_since_value(args.since)
    mode = "execute" if args.execute else "dry-run"
    run_id = uuid4().hex
    backup_path: str | None = None

    logger.info(
        "Starting L3 import run %s in %s mode for source %s (tenant=%s)",
        run_id,
        mode,
        args.source_system,
        args.tenant_id,
    )

    available_files = discover_source_files(args.source)
    table_inputs: list[tuple[str, Path, list[dict[str, Any]]]] = []
    table_summaries: list[TableImportSummary] = []

    for table, column_mapping in mapping.items():
        data_file = available_files[table.upper()]
        rows = load_table_file(data_file)
        filtered_rows, used_since_column = select_rows_since(rows, since_filter, args.since_column)
        summary = TableImportSummary(
            table=table,
            source_file=data_file.name,
            staging_table=f"l3_staging.{normalize_table_identifier(table)}",
            total_rows=len(rows),
            selected_rows=len(filtered_rows),
            loaded_rows=0,
            skipped_rows=len(rows) - len(filtered_rows),
            since_column=used_since_column,
        )
        table_summaries.append(summary)
        table_inputs.append((table, data_file, filtered_rows))
        logger.info(
            "Prepared table %s from %s: total=%s selected=%s skipped=%s",
            table,
            data_file.name,
            summary.total_rows,
            summary.selected_rows,
            summary.skipped_rows,
        )

    if not args.execute:
        logger.info("Dry-run mode enabled - no data will be written.")
        report_payload = build_report(
            run_id=run_id,
            args=args,
            mode=mode,
            backup_path=backup_path,
            table_summaries=table_summaries,
        )
        if args.report_json:
            write_report(args.report_json, report_payload)
        print("L3 import completed (dry-run).")
        return

    session = SessionLocal()
    try:
        ensure_control_tables(session)
        start_import_run(session, run_id=run_id, args=args, mode=mode, since_filter=args.since)

        if args.backup_before_execute:
            backup_path = str(run_pg_dump_backup(args.backup_dir))
            logger.info("Pre-execute backup created at %s", backup_path)

        executed_summaries: list[TableImportSummary] = []
        for table, data_file, filtered_rows in table_inputs:
            executed_summary = load_rows_into_staging(
                session,
                run_id=run_id,
                legacy_table=table,
                source_file=data_file,
                rows=filtered_rows,
            )
            original_summary = next(item for item in table_summaries if item.table == table)
            executed_summaries.append(
                TableImportSummary(
                    table=executed_summary.table,
                    source_file=executed_summary.source_file,
                    staging_table=executed_summary.staging_table,
                    total_rows=original_summary.total_rows,
                    selected_rows=original_summary.selected_rows,
                    loaded_rows=executed_summary.loaded_rows,
                    skipped_rows=original_summary.skipped_rows,
                    since_column=original_summary.since_column,
                )
            )

        report_payload = build_report(
            run_id=run_id,
            args=args,
            mode=mode,
            backup_path=backup_path,
            table_summaries=executed_summaries,
        )
        finish_import_run(
            session,
            run_id=run_id,
            status="completed",
            report_payload=report_payload,
            backup_path=backup_path,
        )
        session.commit()

        if args.report_json:
            write_report(args.report_json, report_payload)
        logger.info("L3 execute run %s completed successfully.", run_id)
    except Exception as exc:
        session.rollback()
        error_payload = build_report(
            run_id=run_id,
            args=args,
            mode=mode,
            backup_path=backup_path,
            table_summaries=table_summaries,
        )
        try:
            finish_import_run(
                session,
                run_id=run_id,
                status="failed",
                report_payload=error_payload,
                backup_path=backup_path,
                error_message=str(exc),
            )
            session.commit()
        except SQLAlchemyError:
            session.rollback()
        logger.error("L3 import failed: %s", exc)
        raise
    finally:
        session.close()

    print("L3 import completed.")


if __name__ == "__main__":
    main()
