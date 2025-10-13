"""
Database bootstrap helper.

Sets up the VALEO NeuroERP schemas and (optional) seed data in a safe,
repeatable fashion. The script is intentionally conservative: it refuses
to modify a non-empty database unless the user explicitly confirms.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from sqlalchemy import inspect
from sqlalchemy.exc import OperationalError

from app.core.database import Base, SessionLocal, engine


def has_existing_tables() -> bool:
    inspector = inspect(engine)
    return bool(inspector.get_table_names())


def drop_all_tables() -> None:
    Base.metadata.drop_all(bind=engine)


def run_alembic_upgrade() -> None:
    subprocess.run(["alembic", "upgrade", "head"], check=True)


def run_seed_scripts() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    subprocess.run([sys.executable, str(repo_root / "scripts" / "init_db.py")], check=True)
    subprocess.run([sys.executable, "-m", "app.seeds.inventory_seed"], check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bootstrap VALEO NeuroERP database.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Drop existing tables before recreating them. Dangerous – only for local/CI use.",
    )
    parser.add_argument(
        "--confirm",
        help='Confirmation string required when using --force (e.g. --confirm "DELETE-DEV").',
    )
    parser.add_argument(
        "--skip-migrations",
        action="store_true",
        help="Do not run alembic migrations (only table-drop if --force is set).",
    )
    parser.add_argument(
        "--seed",
        action="store_true",
        help="Run seed scripts after migrations (init_db.py + inventory_seed).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        if has_existing_tables():
            if not args.force:
                print(
                    "Database already contains tables. "
                    "Aborting – use --force --confirm <token> to drop existing data."
                )
                sys.exit(1)
            if not args.confirm:
                print("Refusing to drop data without --confirm token.")
                sys.exit(1)
            print("Dropping all tables (force mode enabled).")
            drop_all_tables()
        else:
            print("Database is empty. Proceeding with bootstrap.")

        if not args.skip_migrations:
            run_alembic_upgrade()

        if args.seed:
            run_seed_scripts()

        print("Bootstrap completed successfully.")
    except OperationalError as exc:
        print(f"Failed to connect to the database: {exc}")
        sys.exit(2)
    finally:
        # Ensure connections are closed cleanly
        SessionLocal.close_all()


if __name__ == "__main__":
    main()
