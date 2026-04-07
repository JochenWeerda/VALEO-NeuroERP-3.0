"""
Database bootstrap helper.

Sets up the VALEO NeuroERP schemas and optional seed data in a safe, repeatable
fashion. The script is conservative by default:

- it refuses to modify non-empty databases unless `--force` is used,
- destructive actions require an environment-specific confirmation token, and
- production-like environments require an explicit override.

It can also export the repo-local Superglue onboarding templates so a fresh
installation immediately has the required tenant/env placeholders for Ops.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sqlalchemy import inspect, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.engine.url import make_url

from app.core.config import settings
from app.core.database import SessionLocal, engine
from app.integrations.services.superglue_onboarding_templates import (
    render_superglue_onboarding_env_template,
    render_superglue_onboarding_pack_json,
    render_superglue_onboarding_vault_template,
)

SYSTEM_SCHEMAS = {"information_schema", "pg_catalog"}
PRODUCTION_ENVS = {"prod", "production"}


def resolve_runtime_environment() -> str:
    raw_env = (os.getenv("VALEO_ENV") or settings.APP_ENV or "development").strip().lower()
    aliases = {
        "prd": "production",
        "stage": "staging",
        "dev": "development",
        "local": "development",
    }
    return aliases.get(raw_env, raw_env)


def confirmation_token_for_env(environment: str) -> str:
    return f"DELETE-{environment.upper()}"


def list_existing_tables() -> list[str]:
    inspector = inspect(engine)
    tables: list[str] = []
    for schema_name in inspector.get_schema_names():
        if schema_name in SYSTEM_SCHEMAS or schema_name.startswith("pg_toast"):
            continue
        for table_name in inspector.get_table_names(schema=schema_name):
            tables.append(f"{schema_name}.{table_name}")
    return sorted(tables)


def has_existing_tables() -> bool:
    return bool(list_existing_tables())


def drop_all_user_schemas() -> None:
    with engine.begin() as connection:
        rows = connection.execute(
            text(
                """
                SELECT schema_name
                FROM information_schema.schemata
                WHERE schema_name NOT IN ('information_schema', 'pg_catalog')
                  AND schema_name NOT LIKE 'pg_toast%'
                  AND schema_name NOT LIKE 'pg_temp_%'
                ORDER BY schema_name
                """
            )
        ).scalars()
        for schema_name in rows:
            connection.execute(text(f'DROP SCHEMA IF EXISTS "{schema_name}" CASCADE'))


def run_alembic_upgrade() -> None:
    subprocess.run(["alembic", "upgrade", "head"], check=True)


def run_seed_scripts() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    subprocess.run([sys.executable, str(repo_root / "scripts" / "init_db.py")], check=True)
    subprocess.run([sys.executable, "-m", "app.seeds.inventory_seed"], check=True)


def run_pg_dump_backup(target_dir: Path) -> Path:
    target_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    output_path = target_dir / f"bootstrap-pre-force-{timestamp}.sql"

    url = make_url(settings.DATABASE_URL)
    if not str(url.drivername).startswith("postgresql"):
        raise RuntimeError("Automatic bootstrap backup currently supports PostgreSQL only.")

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


def export_superglue_onboarding_bundle(tenant_id: str, output_dir: Path) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    artifacts = {
        "json": output_dir / "superglue-onboarding.json",
        "env": output_dir / "superglue-onboarding.env",
        "vault": output_dir / "superglue-onboarding.vault",
    }
    artifacts["json"].write_text(render_superglue_onboarding_pack_json(tenant_id), encoding="utf-8")
    artifacts["env"].write_text(render_superglue_onboarding_env_template(tenant_id), encoding="utf-8")
    artifacts["vault"].write_text(render_superglue_onboarding_vault_template(tenant_id), encoding="utf-8")
    return {name: str(path) for name, path in artifacts.items()}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bootstrap VALEO NeuroERP database.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Drop and recreate all non-system schemas before bootstrapping.",
    )
    parser.add_argument(
        "--confirm",
        help="Required confirmation token for --force, e.g. DELETE-DEVELOPMENT or DELETE-PRODUCTION.",
    )
    parser.add_argument(
        "--allow-prod-force",
        action="store_true",
        help="Allow destructive bootstrap in production-like environments when combined with --force.",
    )
    parser.add_argument(
        "--backup-before-force",
        action="store_true",
        help="Create a pg_dump backup before dropping data when --force is used.",
    )
    parser.add_argument(
        "--backup-dir",
        type=Path,
        default=Path("logs/db/backups"),
        help="Target directory for automatic pg_dump backups.",
    )
    parser.add_argument(
        "--skip-migrations",
        action="store_true",
        help="Do not run Alembic migrations after teardown / emptiness check.",
    )
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Run deterministic seed scripts after migrations.",
    )
    parser.add_argument(
        "--superglue-tenant",
        help="Optional tenant ID for exporting Superglue onboarding templates after bootstrap.",
    )
    parser.add_argument(
        "--superglue-output-dir",
        type=Path,
        default=Path("runtime/first-install/superglue"),
        help="Output directory for exported Superglue onboarding artifacts.",
    )
    parser.add_argument(
        "--report-json",
        type=Path,
        help="Optional path for a machine-readable bootstrap summary.",
    )
    return parser.parse_args()


def validate_force_request(args: argparse.Namespace, environment: str, table_count: int) -> None:
    if table_count == 0:
        return
    if not args.force:
        print(
            "Database already contains user tables. "
            "Aborting - use --force with the required confirmation token to continue."
        )
        raise SystemExit(1)

    if environment in PRODUCTION_ENVS and not args.allow_prod_force:
        print(
            f"Refusing destructive bootstrap in {environment!r}. "
            "Re-run with --allow-prod-force if this is intentional."
        )
        raise SystemExit(1)

    expected_token = confirmation_token_for_env(environment)
    if args.confirm != expected_token:
        print(f"Refusing to drop data without exact confirmation token {expected_token}.")
        raise SystemExit(1)


def write_report(report_path: Path, payload: dict[str, Any]) -> None:
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(payload, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    environment = resolve_runtime_environment()
    summary: dict[str, Any] = {
        "environment": environment,
        "database_url_driver": make_url(settings.DATABASE_URL).drivername,
        "force": args.force,
        "seed": args.seed,
        "skip_migrations": args.skip_migrations,
        "started_at": datetime.now(timezone.utc).isoformat(),
        "status": "started",
    }

    try:
        existing_tables = list_existing_tables()
        summary["existing_tables"] = existing_tables

        validate_force_request(args, environment, len(existing_tables))

        if existing_tables:
            if args.backup_before_force:
                backup_path = run_pg_dump_backup(args.backup_dir)
                summary["pre_force_backup"] = str(backup_path)
                print(f"Pre-force backup written to {backup_path}")

            print("Dropping all non-system schemas (force mode enabled).")
            drop_all_user_schemas()
        else:
            print("Database is empty. Proceeding with bootstrap.")

        if not args.skip_migrations:
            print("Running Alembic migrations.")
            run_alembic_upgrade()

        if args.seed:
            print("Running seed scripts.")
            run_seed_scripts()

        if args.superglue_tenant:
            artifacts = export_superglue_onboarding_bundle(args.superglue_tenant, args.superglue_output_dir)
            summary["superglue_onboarding"] = {
                "tenant_id": args.superglue_tenant,
                "artifacts": artifacts,
            }
            print(
                "Exported Superglue onboarding templates "
                f"for tenant {args.superglue_tenant} to {args.superglue_output_dir}"
            )

        summary["status"] = "completed"
        print("Bootstrap completed successfully.")
    except OperationalError as exc:
        summary["status"] = "failed"
        summary["error"] = f"Failed to connect to the database: {exc}"
        print(summary["error"])
        raise SystemExit(2) from exc
    except subprocess.CalledProcessError as exc:
        summary["status"] = "failed"
        summary["error"] = f"Subprocess failed with exit code {exc.returncode}: {exc.cmd}"
        print(summary["error"])
        raise SystemExit(exc.returncode or 1) from exc
    except Exception as exc:  # pragma: no cover - defensive
        summary["status"] = "failed"
        summary["error"] = str(exc)
        print(f"Bootstrap failed: {exc}")
        raise SystemExit(1) from exc
    finally:
        summary["finished_at"] = datetime.now(timezone.utc).isoformat()
        if args.report_json:
            write_report(args.report_json, summary)
        SessionLocal.close_all()


if __name__ == "__main__":
    main()
