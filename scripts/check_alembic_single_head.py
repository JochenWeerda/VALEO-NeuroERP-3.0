"""
CI guard: ensure Alembic has exactly one head.

Multiple heads mean migration drift (missing merge migration) and will break
deterministic DB bootstrap in CI/CD.
"""

from __future__ import annotations

import sys
from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def main() -> None:
    cfg = Config(str(PROJECT_ROOT / "alembic.ini"))
    script = ScriptDirectory.from_config(cfg)
    heads = script.get_heads()

    if len(heads) != 1:
        raise SystemExit(f"Expected exactly 1 Alembic head, got {len(heads)}: {heads}")

    print(f"Alembic head OK: {heads[0]}")


if __name__ == "__main__":
    main()

