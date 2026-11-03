#!/usr/bin/env python3
"""Spiegelt config/wertetypen.json und die Einheiten aus app/core/agrar_units.py ins Frontend.

Das Frontend-Image enthaelt nur packages/frontend-web; deshalb eine erzeugte Kopie statt eines Imports.

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
    sys.path.insert(0, str(ROOT))
    from app.core import agrar_units

    daten = json.loads(QUELLE.read_text(encoding="utf-8"))
    daten["_hinweis"] = ("Erzeugt von scripts/generate_wertetypen_frontend.py aus config/wertetypen.json und "
                         "app/core/agrar_units.py; nicht von Hand pflegen.")
    # Masse/Volumen exakt umrechenbar (Faktor in kg bzw. l); Zaehleinheiten nie global (agrar_units).
    daten["einheiten"] = {
        "masseInKg": {e: float(f) for e, f in agrar_units.MASSE_IN_KG.items()},
        "volumenInL": {e: float(f) for e, f in agrar_units.VOLUMEN_IN_L.items()},
        "aliase": dict(sorted(agrar_units.ALIASE.items())),
        "zaehleinheiten": sorted(agrar_units.ZAEHLEINHEITEN),
        "anzeigeMasse": "dt",
        "anzeigeVolumen": "l",
    }
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
