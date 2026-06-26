#!/usr/bin/env python3
"""Validiert config/ai_data_classification.yaml auf Schema-Konsistenz.

Aufruf:
  python scripts/validate_data_classification.py [--config PATH]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG = REPO_ROOT / "config" / "ai_data_classification.yaml"

VALID_LEVELS = {"PUBLIC", "EU_ONLY", "LOCAL_ONLY", "SYNTHETIC_ALLOWED", "NEVER"}
REQUIRED_LEVEL_FIELDS = {"id", "label", "description", "external_model_allowed", "never_in_context"}
REQUIRED_CATEGORY_FIELDS = {"id", "label", "examples", "level", "rationale"}


def load(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate(config: dict) -> list[str]:
    errors: list[str] = []

    # ── Version / Pflichtfelder ────────────────────────────────────────────────
    for field in ("version", "updated", "owner", "levels", "categories"):
        if field not in config:
            errors.append(f"Pflichtfeld '{field}' fehlt im Root")

    levels_raw: list[dict] = config.get("levels", [])
    categories: list[dict] = config.get("categories", [])

    # ── Level-Definitionen ─────────────────────────────────────────────────────
    defined_level_ids: set[str] = set()
    for lvl in levels_raw:
        lid = lvl.get("id", "<unbekannt>")
        defined_level_ids.add(lid)
        for f in REQUIRED_LEVEL_FIELDS:
            if f not in lvl:
                errors.append(f"Level '{lid}': Pflichtfeld '{f}' fehlt")
        if lid not in VALID_LEVELS:
            errors.append(f"Level '{lid}' nicht in erlaubter Liste {VALID_LEVELS}")

    # ── Kategorien ─────────────────────────────────────────────────────────────
    seen_category_ids: set[str] = set()
    for cat in categories:
        cid = cat.get("id", "<unbekannt>")
        for f in REQUIRED_CATEGORY_FIELDS:
            if f not in cat:
                errors.append(f"Kategorie '{cid}': Pflichtfeld '{f}' fehlt")

        # Level muss definiert sein
        level = cat.get("level")
        if level and level not in defined_level_ids:
            errors.append(f"Kategorie '{cid}': Level '{level}' nicht in levels definiert")

        # examples muss nicht-leer sein
        examples = cat.get("examples", [])
        if not isinstance(examples, list) or len(examples) == 0:
            errors.append(f"Kategorie '{cid}': 'examples' muss eine nicht-leere Liste sein")

        # Duplikate
        if cid in seen_category_ids:
            errors.append(f"Duplikate Kategorie-ID: '{cid}'")
        seen_category_ids.add(cid)

        # rationale darf nicht leer sein
        if not cat.get("rationale", "").strip():
            errors.append(f"Kategorie '{cid}': 'rationale' ist leer")

    # ── Mindestanforderungen ───────────────────────────────────────────────────
    never_cats = [c for c in categories if c.get("level") == "NEVER"]
    if len(never_cats) < 3:
        errors.append(
            f"Mindestens 3 NEVER-Kategorien erwartet (Credentials, Audit, Zahlung) — "
            f"gefunden: {len(never_cats)}"
        )

    return errors


def summary(config: dict) -> dict:
    categories: list[dict] = config.get("categories", [])
    counts: dict[str, int] = {}
    for c in categories:
        lvl = c.get("level", "UNKNOWN")
        counts[lvl] = counts.get(lvl, 0) + 1
    return {
        "total_categories": len(categories),
        "by_level": counts,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Validiere ai_data_classification.yaml")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    args = parser.parse_args()

    path = Path(args.config)
    if not path.exists():
        print(f"FEHLER: Datei nicht gefunden: {path}", file=sys.stderr)
        sys.exit(1)

    config = load(path)
    errors = validate(config)
    s = summary(config)

    print(f"\nAI-Datenklassen-Validierung: {path.name}")
    print(f"  Kategorien gesamt: {s['total_categories']}")
    for level, count in sorted(s["by_level"].items()):
        print(f"  {level:<20} {count}")

    if errors:
        print(f"\n  {len(errors)} Fehler gefunden:")
        for e in errors:
            print(f"    ✗ {e}")
        sys.exit(1)
    else:
        print(f"\n  Validierung erfolgreich — keine Fehler.\n")


if __name__ == "__main__":
    main()
