"""
Database initialization helper for Release/Neuinstallation.
Führt alle Alembic-Migrationen bis zum aktuellen Head aus (ein gemeinsamer Head
via merge_heads_20260301: Agrar, Einkauf RE-Workflow, Docflow GoBD Schritt 3).
Voraussetzung: DB ist leer oder alle Vorgänger-Revisionen sind bereits angewendet.
"""

import os
import time
from pathlib import Path
import sys

from alembic import command
from alembic.config import Config
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _ensure_wide_version_table(database_url: str) -> None:
    """Ensure alembic_version.version_num can hold long revision IDs (>32 chars).

    On a fresh DB the table doesn't exist yet — create it with varchar(128).
    On an existing DB widen the column if it's still varchar(32).
    """
    engine = create_engine(database_url)
    with engine.begin() as conn:
        conn.execute(text(
            "CREATE TABLE IF NOT EXISTS alembic_version ("
            "  version_num VARCHAR(128) NOT NULL, "
            "  CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)"
            ");"
        ))
        conn.execute(text(
            "ALTER TABLE alembic_version "
            "ALTER COLUMN version_num TYPE VARCHAR(128);"
        ))
    engine.dispose()


def main() -> None:
    config_path = PROJECT_ROOT / "alembic.ini"
    alembic_cfg = Config(str(config_path))

    database_url = os.environ.get(
        "DATABASE_URL",
        "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_neuro_erp",
    )

    # CI / local ephemeral Postgres can be briefly unavailable even after the
    # container reports "started". Retry to avoid flaky pipelines.
    deadline = time.time() + 60
    last_err: Exception | None = None
    while time.time() < deadline:
        try:
            _ensure_wide_version_table(database_url)
            command.upgrade(alembic_cfg, "head")
            last_err = None
            break
        except OperationalError as e:
            last_err = e
            time.sleep(2)

    if last_err is not None:
        raise last_err

    print("Database schema migrated to head.")


if __name__ == "__main__":
    main()
