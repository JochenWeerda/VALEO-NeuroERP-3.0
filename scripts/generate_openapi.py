#!/usr/bin/env python
"""Erzeugt die OpenAPI-Spezifikation aus der FastAPI-App.

Single Source of Truth ist der Code: Dieses Skript importiert ``app.main:app``
und schreibt die Spezifikation nach ``docs/schnittstellen/openapi.json``.

Bewusst vom Docs-Build entkoppelt: Der Import der vollstaendigen App ist
schwergewichtig (~2 min) und benoetigt die Backend-Abhaengigkeiten. Daher wird
das Artefakt versioniert eingecheckt und der MkDocs-Build bettet nur die fertige
JSON ein.

Verwendung:
    python scripts/generate_openapi.py
    python scripts/generate_openapi.py --check   # nur pruefen, ob aktuell
    VALEO_API_VERSION=3.0.0 python scripts/generate_openapi.py  # optionaler Override
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT = REPO_ROOT / "docs" / "schnittstellen" / "openapi.json"
DEFAULT_API_VERSION = "3.0.0"


def build_spec() -> dict:
    sys.path.insert(0, str(REPO_ROOT))
    import importlib

    main = importlib.import_module("app.main")
    app = getattr(main, "app")
    spec = app.openapi()

    version = os.environ.get("VALEO_API_VERSION", DEFAULT_API_VERSION)
    spec.setdefault("info", {})["version"] = version
    spec.setdefault("info", {}).setdefault("title", "VALEO NeuroERP API")
    return spec


def render(spec: dict) -> str:
    return json.dumps(spec, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="OpenAPI-Spec generieren")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Nur pruefen, ob die committete Spec aktuell ist (Exit 1 bei Drift).",
    )
    args = parser.parse_args()

    spec = build_spec()
    content = render(spec)

    if args.check:
        if not OUTPUT.exists():
            print(f"FEHLT: {OUTPUT} existiert nicht. Bitte generieren.", file=sys.stderr)
            return 1
        current = OUTPUT.read_text(encoding="utf-8")
        if current != content:
            print(
                f"DRIFT: {OUTPUT} ist nicht aktuell. Bitte 'python scripts/generate_openapi.py' ausfuehren.",
                file=sys.stderr,
            )
            return 1
        print(f"OK: {OUTPUT} ist aktuell ({len(spec.get('paths', {}))} Pfade).")
        return 0

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(content, encoding="utf-8")
    print(f"Geschrieben: {OUTPUT} ({len(spec.get('paths', {}))} Pfade).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
