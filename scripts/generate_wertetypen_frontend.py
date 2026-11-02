#!/usr/bin/env python3
"""Spiegelt config/wertetypen.json ins Frontend (das Frontend-Image enthaelt nur packages/frontend-web).

    python scripts/generate_wertetypen_frontend.py          # schreiben
    python scripts/generate_wertetypen_frontend.py --check  # Drift pruefen (CI)
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
QUELLE = ROOT / "config" / "wertetypen.json"
ZIEL = ROOT / "packages/frontend-web/src/components/mask-builder/runtime/wertetypen.generated.json"


def render() -> str:
    daten = json.loads(QUELLE.read_text(encoding="utf-8"))
    daten["_hinweis"] = "Erzeugt von scripts/generate_wertetypen_frontend.py aus config/wertetypen.json; nicht von Hand pflegen."
    return json.dumps(daten, ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    inhalt = render()
    if args.check:
        if not ZIEL.is_file() or ZIEL.read_text(encoding="utf-8") != inhalt:
            print(f"DRIFT: {ZIEL.relative_to(ROOT)} - bitte neu erzeugen.")
            return 1
        print("OK: Wertetypen im Frontend aktuell.")
        return 0
    with open(ZIEL, "w", encoding="utf-8", newline="\n") as datei:
        datei.write(inhalt)
    print(f"Geschrieben: {ZIEL.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
