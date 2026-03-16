from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class JsonStateContractError(RuntimeError):
    pass


def load_json_state(
    path: str | Path,
    *,
    default: dict[str, Any] | None = None,
    required_keys: dict[str, type] | None = None,
) -> dict[str, Any]:
    state_path = Path(path)

    if not state_path.exists():
        if default is not None:
            return dict(default)
        raise JsonStateContractError(f"JSON-State-Datei nicht gefunden: {state_path}")

    try:
        data = json.loads(state_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise JsonStateContractError(f"JSON-State-Datei enthaelt ungueltiges JSON: {state_path}") from exc

    if not isinstance(data, dict):
        raise JsonStateContractError(f"JSON-State-Datei muss ein Objekt enthalten: {state_path}")

    if required_keys:
        for key, expected_type in required_keys.items():
            value = data.get(key)
            if not isinstance(value, expected_type):
                raise JsonStateContractError(
                    f"JSON-State-Datei verletzt Contract: '{key}' muss vom Typ {expected_type.__name__} sein."
                )

    return data


def save_json_state(path: str | Path, payload: dict[str, Any]) -> None:
    state_path = Path(path)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
