#!/usr/bin/env python3
"""Initialize dashboard directories and seed files for the enhanced GENXAIS dashboard."""

from __future__ import annotations

import json
from pathlib import Path

DATA_DIR = Path("data/dashboard")
FILES = {
    "phases.json": {"current_phase": "idle", "statuses": {}, "last_updated": None},
    "pipelines.json": {"statuses": {}, "last_updated": None},
    "artifacts.json": {"statuses": {}, "last_updated": None},
    "graphiti.json": {"config": {}, "nodes": [], "edges": [], "last_updated": None},
}


def main() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    for filename, payload in FILES.items():
        path = DATA_DIR / filename
        if not path.exists():
            path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Dashboard data initialized in {DATA_DIR}")


if __name__ == "__main__":
    main()
