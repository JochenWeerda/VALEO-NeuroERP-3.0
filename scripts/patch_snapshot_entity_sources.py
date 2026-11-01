"""Patch entity dataSources in screen-registry snapshot for gate fixes."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / "packages" / "frontend-web" / "src" / "masks" / "screen-registry.snapshot.json"
SOURCE = ROOT / ".cursor" / "snapshot-head.json"


def main() -> None:
    path = SOURCE if SOURCE.is_file() else SNAPSHOT
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    screens = data["screens"]
    screens["fuhrpark/fahrzeug-stamm"]["dataSources"] = [
        {"key": "entity", "endpoint": "/api/v1/fuhrpark/fahrzeuge/{entity_id}", "pageSize": 1},
    ]
    be = screens["personal/bewerbung-einwilligung"]
    ds = list(be["dataSources"])
    for i, item in enumerate(ds):
        if item.get("key") in ("bewerbung", "entity") and "{entity_id}" in item.get("endpoint", ""):
            ds[i] = {"key": "entity", "endpoint": "/api/v1/personal/applications/{entity_id}", "pageSize": 1}
            break
    be["dataSources"] = ds
    SNAPSHOT.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"patched {SNAPSHOT}")


if __name__ == "__main__":
    main()
