"""Prozessketten-Validierung (UIX-091) — Quality-Gate.

Prueft config/process_chains.yaml: Struktur + jede step.screenId existiert in der
ScreenDefinition-Registry. Exit 1 bei Fehlern (fuer quality-gate).

Aufruf: python scripts/check_process_chains.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

_REPO_ROOT = Path(__file__).resolve().parents[1]
_CONFIG = _REPO_ROOT / "config" / "process_chains.yaml"


def _registry_screen_ids() -> set[str]:
    sys.path.insert(0, str(_REPO_ROOT))
    from app.core.screen_definitions import _SCREEN_DEFINITIONS  # noqa: PLC0415

    return set(_SCREEN_DEFINITIONS.keys())


def validate(config: dict | None = None, known_screen_ids: set[str] | None = None) -> list[str]:
    """Gibt eine Liste von Fehlern zurueck (leer = ok)."""
    if config is None:
        config = yaml.safe_load(_CONFIG.read_text(encoding="utf-8")) or {}
    known = known_screen_ids if known_screen_ids is not None else _registry_screen_ids()

    errors: list[str] = []
    chains = config.get("chains")
    if not isinstance(chains, dict) or not chains:
        return ["chains fehlt oder leer"]

    for chain_id, chain in chains.items():
        steps = (chain or {}).get("steps")
        if not isinstance(steps, list) or not steps:
            errors.append(f"{chain_id}: steps fehlen")
            continue
        seen_keys: set[str] = set()
        for i, step in enumerate(steps):
            if not isinstance(step, dict):
                errors.append(f"{chain_id}.steps[{i}]: kein Objekt")
                continue
            key = step.get("key")
            screen_id = step.get("screenId")
            if not key:
                errors.append(f"{chain_id}.steps[{i}]: key fehlt")
            elif key in seen_keys:
                errors.append(f"{chain_id}.steps[{i}]: doppelter key '{key}'")
            else:
                seen_keys.add(key)
            if not step.get("label"):
                errors.append(f"{chain_id}.steps[{i}]: label fehlt")
            if not screen_id:
                errors.append(f"{chain_id}.steps[{i}]: screenId fehlt")
            elif screen_id not in known:
                errors.append(f"{chain_id}.steps[{i}]: screenId '{screen_id}' nicht in Registry")
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("FAIL check_process_chains:", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print("OK check_process_chains: alle Ketten valide")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
