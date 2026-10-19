#!/usr/bin/env python3
"""CLI-Register: welche Maskenaktionen die VALEO-CLI ausfuehren kann — abgeleitet, nicht behauptet.

    python scripts/generate_cli_mask_commands.py           # schreiben
    python scripts/generate_cli_mask_commands.py --check   # pruefen (CI, ueber tests/test_valeo_cli.py)

Die Entscheidung trifft ``valeo_cli.support.support`` — dieselbe Funktion, mit der die CLI zur Laufzeit
ausfuehrt oder ablehnt. Die Aktionsliste ist die des Masken-Studio-Inventars (alle registrierten
ScreenDefinitions einschliesslich der Belegvarianten). ``scripts/mask_studio_inventory.py`` liest dieses
Register fuer den CLI-Befund seiner Ratsche.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from valeo_cli.support import support  # noqa: E402

ZIEL = ROOT / "config/cli_mask_commands.json"


def _inventory():
    spec = importlib.util.spec_from_file_location("mask_studio_inventory", ROOT / "scripts/mask_studio_inventory.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def register() -> dict:
    inv = _inventory()
    supported: list[str] = []
    reasons: Counter[str] = Counter()
    for screen_id, definition in sorted(inv._definitions().items()):
        seen: set[str] = set()
        for action in inv._iter_actions(definition):
            if action["key"] in seen:
                continue
            seen.add(action["key"])
            checked = support(action)
            if checked.supported:
                supported.append(f"mask:{screen_id}:{action['key']}")
            else:
                reasons[checked.reason.split(":", 1)[0] + (":" + checked.reason.split(":", 1)[1]
                                                           if checked.reason.startswith("adapter:") else "")] += 1
    return {"_hinweis": "Erzeugt von scripts/generate_cli_mask_commands.py; nicht von Hand pflegen.",
            "mask_action_ids": sorted(supported),
            "nicht_unterstuetzt": dict(sorted(reasons.items()))}


def rendered() -> str:
    return json.dumps(register(), ensure_ascii=False, indent=1) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    text = rendered()
    if args.check:
        if not ZIEL.is_file() or ZIEL.read_text(encoding="utf-8") != text:
            print("config/cli_mask_commands.json veraltet: python scripts/generate_cli_mask_commands.py")
            return 1
        print("CLI-Register aktuell")
        return 0
    ZIEL.write_text(text, encoding="utf-8")
    data = json.loads(text)
    print(f"{len(data['mask_action_ids'])} Aktionen per CLI; nicht unterstuetzt: {data['nicht_unterstuetzt']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
