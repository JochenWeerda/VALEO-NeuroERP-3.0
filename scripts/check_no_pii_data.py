#!/usr/bin/env python3
"""PII-/Lead-Daten-Guard — blockiert das Einchecken personenbezogener Lead-/GAP-Daten.

Zweidimensionaler Schutz (fail-closed):
  1. Pfad-/Namensmuster (Lead-/GAP-/PLZ-Datendateien)
  2. Inhaltsheuristik auf strukturierte Personendaten (Name+PLZ+Ort/Betrag) in
     Daten-Dateien (.json/.csv), auch bei unauffaelligem Dateinamen

Nutzung:
  - pre-commit:  python scripts/check_no_pii_data.py --staged
  - CI:          python scripts/check_no_pii_data.py --tracked
  - Ad-hoc:      python scripts/check_no_pii_data.py <pfad> [<pfad> ...]

Exit 1 = Fund (Commit/Push blockieren). Whitelist ueber .pii-guard-allow.txt
(eine Pfad-Glob je Zeile) fuer bewusste Ausnahmen mit Begruendung im Commit.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from fnmatch import fnmatch
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ALLOW_FILE = REPO_ROOT / ".pii-guard-allow.txt"

# 1. Verbotene Pfad-/Namensmuster (Lead-/GAP-/PLZ-Rohdaten und -Tooling)
FORBIDDEN_GLOBS = [
    "*_leads.json",
    "*_leads.csv",
    "ostfriesland*",
    "*plz_26*",
    "PLZ_*.json",
    "find_plz_*",
    "find_all_*26*",
    "find_all_plz_*",
    "search_ostfriesland*",
    "analyze_filtered_*",
    "*gap*leads*",
    "*_final_leads.*",
]

# 2. Inhaltsheuristik: nur Datendateien pruefen
DATA_SUFFIXES = {".json", ".csv", ".ndjson"}
# Felder, die zusammen auf strukturierte Personen-Lead-Daten hindeuten
PERSON_KEYS = {"name", "vorname", "nachname", "besitzer", "beneficiary", "besitzer_raw"}
LOCATION_KEYS = {"plz", "postal_code", "postleitzahl", "ort", "city", "gemeinde"}
LEAD_KEYS = {"lead_score", "gap_amount", "gap_direct_total_eur", "amount_total",
             "foerderbetrag", "praemie", "flaechenpraemie", "measure_code"}
# Schwelle: wie viele Datensaetze mit Person+Ort/Lead => Block
CONTENT_HITS_THRESHOLD = 3


def load_allow() -> list[str]:
    if not ALLOW_FILE.exists():
        return []
    return [ln.strip() for ln in ALLOW_FILE.read_text(encoding="utf-8").splitlines()
            if ln.strip() and not ln.startswith("#")]


def is_allowed(path: str, allow: list[str]) -> bool:
    return any(fnmatch(path, pat) for pat in allow)


def path_violates(path: str) -> bool:
    name = Path(path).name.lower()
    return any(fnmatch(name, g.lower()) for g in FORBIDDEN_GLOBS)


def _iter_records(data):
    """Liefert dict-Records aus JSON-Struktur (Top-Liste oder verschachtelte Listen)."""
    if isinstance(data, list):
        for x in data:
            if isinstance(x, dict):
                yield x
    elif isinstance(data, dict):
        for v in data.values():
            if isinstance(v, list):
                for x in v:
                    if isinstance(x, dict):
                        yield x


def content_violates(path: Path) -> bool:
    if path.suffix.lower() not in DATA_SUFFIXES:
        return False
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    if path.suffix.lower() == ".json":
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return False
        hits = 0
        for rec in _iter_records(data):
            keys = {k.lower() for k in rec.keys()}
            has_person = bool(keys & PERSON_KEYS)
            has_loc = bool(keys & LOCATION_KEYS)
            has_lead = bool(keys & LEAD_KEYS)
            # Person + (Ort oder Lead-Kennzahl) mit nicht-leerem Namen
            if has_person and (has_loc or has_lead):
                name_val = next((rec[k] for k in rec if k.lower() in PERSON_KEYS), "")
                if isinstance(name_val, str) and name_val.strip():
                    hits += 1
            if hits >= CONTENT_HITS_THRESHOLD:
                return True
        return False
    # CSV: Header-Heuristik
    header = raw.splitlines()[0].lower() if raw else ""
    cols = set(re.split(r"[;,\t]", header))
    return bool((cols & PERSON_KEYS) and (cols & (LOCATION_KEYS | LEAD_KEYS)))


def collect_paths(args) -> list[str]:
    if args.paths:
        return args.paths
    if args.staged:
        out = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
                             capture_output=True, text=True).stdout
        return [p for p in out.splitlines() if p.strip()]
    if args.tracked:
        out = subprocess.run(["git", "ls-files"], capture_output=True, text=True).stdout
        return [p for p in out.splitlines() if p.strip()]
    return []


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("paths", nargs="*")
    ap.add_argument("--staged", action="store_true", help="git-staged Dateien pruefen (pre-commit)")
    ap.add_argument("--tracked", action="store_true", help="alle getrackten Dateien pruefen (CI)")
    args = ap.parse_args()

    allow = load_allow()
    violations: list[str] = []
    for p in collect_paths(args):
        if is_allowed(p, allow):
            continue
        if path_violates(p):
            violations.append(f"{p}  [Name-/Pfadmuster: Lead-/GAP-/PLZ-Daten]")
            continue
        abs_p = REPO_ROOT / p
        if abs_p.exists() and content_violates(abs_p):
            violations.append(f"{p}  [Inhalt: strukturierte Personen-Lead-Daten]")

    if violations:
        print("BLOCKIERT: mutmassliche personenbezogene Lead-/GAP-Daten erkannt:", file=sys.stderr)
        for v in violations:
            print(f"  - {v}", file=sys.stderr)
        print("\nSolche Daten gehoeren NICHT ins Repository (DSGVO). Entfernen (git rm --cached),", file=sys.stderr)
        print("ausserhalb des Repos speichern. Bewusste Ausnahme: Pfad-Glob in .pii-guard-allow.txt", file=sys.stderr)
        print("mit Begruendung im Commit dokumentieren.", file=sys.stderr)
        return 1

    print("OK: keine personenbezogenen Lead-/GAP-Daten in der Pruefmenge.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
