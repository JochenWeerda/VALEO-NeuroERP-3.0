"""
Database initialization helper.
Executes Alembic migrations up to the latest revision.
"""

import time
from pathlib import Path
import sys

from alembic import command
from alembic.config import Config
from sqlalchemy.exc import OperationalError

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main() -> None:
    config_path = PROJECT_ROOT / "alembic.ini"
    alembic_cfg = Config(str(config_path))
    # CI / local ephemeral Postgres can be briefly unavailable even after the
    # container reports "started". Retry to avoid flaky pipelines.
    deadline = time.time() + 60
    last_err: Exception | None = None
    while time.time() < deadline:
        try:
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
