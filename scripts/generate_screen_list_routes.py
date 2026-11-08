"""Erzeugt config/screen_list_routes.generated.json: Listen-Route je Maske aus den Frontend-Routen.

    python scripts/generate_screen_list_routes.py           # schreiben
    python scripts/generate_screen_list_routes.py --check   # nur vergleichen, Exit 1 bei Abweichung

Die Omnibox navigiert ueber ``get_screen_list_route``. Kuratiert ist ``_SCREEN_LIST_ROUTE`` in
``app/core/screen_definitions.py``; fuer alle uebrigen Masken nimmt diese Datei die Route der Seite, die die Maske
rendert (``route-aliases.json`` -> Seite -> ``screenId``, ermittelt von ``scripts/mask_studio_inventory.py``).
``ohne_route`` sind Masken, die keine Seite rendert (Altlast STUDIO-UMBAU-RUNTIME46); die Liste darf nur schrumpfen.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
ZIEL = ROOT / "config/screen_list_routes.generated.json"


def erzeugen() -> dict:
    from app.core.screen_definitions import SCREEN_DEFINITION_BUILDERS, _SCREEN_LIST_ROUTE, _CURATED_SCREEN_LIST_ROUTE_IDS
    from app.core.stamm_object_page_parent import ensure_stamm_screen_registry

    # Explizite Ursprungsmenge statt vom Aufrufzeitpunkt abhaengiger Registry-Snapshot.
    kuratiert = _CURATED_SCREEN_LIST_ROUTE_IDS
    spec = importlib.util.spec_from_file_location("mask_studio_inventory", ROOT / "scripts/mask_studio_inventory.py")
    inventar_modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(inventar_modul)
    inventar = inventar_modul.inventory()

    ensure_stamm_screen_registry()
    stamm = {s: r for s, r in _SCREEN_LIST_ROUTE.items() if s not in kuratiert}

    seiten: dict[str, str] = {}
    for seite in sorted(inventar["seiten"], key=lambda s: s["route"]):
        for screen_id in sorted(seite.get("screen_ids") or []):
            seiten.setdefault(screen_id, "/" + seite["route"].lstrip("/"))
    seiten = {**seiten, **stamm}
    offen = sorted(s for s in SCREEN_DEFINITION_BUILDERS if s not in kuratiert and not s.startswith("tenant/"))
    return {
        "_hinweis": "Erzeugt von scripts/generate_screen_list_routes.py; nicht von Hand pflegen.",
        "routen": {s: seiten[s] for s in offen if s in seiten},
        "ohne_route": [s for s in offen if s not in seiten],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    inhalt = json.dumps(erzeugen(), ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not ZIEL.is_file() or ZIEL.read_text(encoding="utf-8") != inhalt:
            print("DRIFT: config/screen_list_routes.generated.json - bitte neu erzeugen.")
            return 1
        print("OK: Listen-Routen aktuell.")
        return 0
    with open(ZIEL, "w", encoding="utf-8", newline="\n") as datei:
        datei.write(inhalt)
    daten = json.loads(inhalt)
    print(f"Geschrieben: {ZIEL.relative_to(ROOT)} ({len(daten['routen'])} Routen, {len(daten['ohne_route'])} ohne Route)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
