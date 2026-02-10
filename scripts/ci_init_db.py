"""
Fallback-only DB bootstrap (create_all).

This script exists as an emergency escape hatch, not as the default DB init path.

Preferred path:
- Use Alembic migrations: `python scripts/init_db.py` (or `alembic upgrade head`).

Why keep this around:
- When migrations are temporarily broken during development, we may still want to
  bring up an ephemeral DB for quick test iterations.

Guardrail:
- This script refuses to run unless `VALEO_ALLOW_CREATE_ALL=1` is set.
  That prevents accidental use in CI or production-like environments.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

from sqlalchemy import text

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.core.database import Base, engine


def main() -> None:
    if os.getenv("VALEO_ALLOW_CREATE_ALL") != "1":
        raise SystemExit(
            "Refusing to run create_all bootstrap. "
            "Use Alembic: `python scripts/init_db.py` "
            "or set VALEO_ALLOW_CREATE_ALL=1 to override."
        )

    ***REMOVED*** Register models on Base metadata.
    ***REMOVED*** Import side effects are intentional here.
    import app.infrastructure.models  ***REMOVED*** noqa: F401

    schemas = sorted({t.schema for t in Base.metadata.tables.values() if t.schema})

    ***REMOVED*** Ensure schemas exist before creating tables inside them.
    with engine.begin() as conn:
        for schema in schemas:
            conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema}"'))

    Base.metadata.create_all(bind=engine)
    print("CI DB bootstrap complete (schemas + tables).")


if __name__ == "__main__":
    main()
