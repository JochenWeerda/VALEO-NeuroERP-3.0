#!/usr/bin/env python3
"""Belegvertrag als JSON-Schema und als lesbare Uebersicht — erzeugt aus ``app/core/belegvertrag.py``.

    python scripts/generate_belegvertrag.py           # schreiben
    python scripts/generate_belegvertrag.py --check   # pruefen (CI)

Geschrieben werden ``docs/schnittstellen/contracts/belegvertrag.schema.json`` (die Form) und
``docs/schnittstellen/belegvertrag.md`` (Varianten, Bausteine, Abbildung der bisherigen Feldnamen).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.belegvertrag import (  # noqa: E402
    ABBILDUNG, BAUSTEINE, BELEGARTEN, PREISFELDER, STATUS, VERTRAGSVERSION, Beleg,
)

SCHEMA = ROOT / "docs/schnittstellen/contracts/belegvertrag.schema.json"
UEBERSICHT = ROOT / "docs/schnittstellen/belegvertrag.md"


def schema() -> str:
    daten = Beleg.model_json_schema()
    daten["title"] = "Belegvertrag"
    daten["x-vertragsversion"] = VERTRAGSVERSION
    daten["x-status"] = list(STATUS)
    daten["x-preisfelder"] = list(PREISFELDER)
    daten["x-belegarten"] = {
        art: {
            "bezeichnung": v.bezeichnung, "partnerrolle": v.partnerrolle, "richtung": v.richtung,
            "mit_preisen": v.mit_preisen, "bucht": v.bucht, "folgebelege": list(v.folgebelege),
        }
        for art, v in BELEGARTEN.items()
    }
    return json.dumps(daten, ensure_ascii=False, indent=1, sort_keys=True) + "\n"


# Zuletzt fachlich geprueft — von Hand nachziehen, wenn jemand die Uebersicht durchsieht (Doku-Staleness-Gate).
# Kein Tagesdatum: sonst waere ``--check`` jeden Tag rot.
GEPRUEFT_AM = "2026-10-15"


def uebersicht() -> str:
    ja = lambda wert: "ja" if wert else "nein"  # noqa: E731
    z = [
        "---",
        "title: Belegvertrag",
        "type: reference",
        "audience: [entwickler, integrator, agent]",
        "owner: Codex",
        "status: aktiv",
        f"last_reviewed: {GEPRUEFT_AM}",
        f"version: {VERTRAGSVERSION}.0",
        "description: Eine Form fuer alle Belegarten — Varianten, Bausteine und Abbildung der bisherigen Feldnamen.",
        "---",
        "",
        "# Belegvertrag",
        "",
        "Erzeugt von `scripts/generate_belegvertrag.py` aus `app/core/belegvertrag.py`. Nicht von Hand ändern.",
        "",
        f"Version {VERTRAGSVERSION}. Die Form steht in `contracts/belegvertrag.schema.json`.",
        "",
        "## Varianten",
        "",
        "| Belegart | Bezeichnung | Partner | Steuerrichtung | Preise | Finance bucht | Folgebelege |",
        "|---|---|---|---|---|---|---|",
    ]
    for art, v in BELEGARTEN.items():
        folge = ", ".join(f"`{f}`" for f in v.folgebelege) or "—"
        z.append(f"| `{art}` | {v.bezeichnung} | {v.partnerrolle} | {v.richtung} | {ja(v.mit_preisen)} | {ja(v.bucht)} | {folge} |")
    z += [
        "",
        "Ohne Preise heißt: Der Server liefert weder die Preisfelder der Position ("
        + ", ".join(f"`{f}`" for f in PREISFELDER) + ") noch `summen`. Dasselbe gilt für Leser ohne Preisrecht.",
        "",
        "## Bausteine",
        "",
        "Fachliche Sonderteile, die eine Variante einhängt; sie gehören nicht zum Grundgerüst.",
        "",
        "| Baustein | Inhalt |",
        "|---|---|",
    ]
    z += [f"| `{name}` | {inhalt} |" for name, inhalt in BAUSTEINE.items()]
    z += [
        "",
        "## Abbildung der bisherigen Feldnamen",
        "",
        "Je Beleg-ScreenDefinition: Feld im Reiter `kopf` und Spalte der Tabelle `positionen`.",
    ]
    for kennung, teile in ABBILDUNG.items():
        z += ["", f"### `{kennung}`", "", "| Bereich | Bisher | Im Vertrag |", "|---|---|---|"]
        for bereich, felder in teile.items():
            z += [f"| {bereich} | `{alt}` | `{ziel}` |" for alt, ziel in felder.items()]
    return "\n".join(z) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="nur pruefen, ob die Dateien aktuell sind")
    args = parser.parse_args()
    abweichend = []
    for ziel, inhalt in ((SCHEMA, schema()), (UEBERSICHT, uebersicht())):
        if args.check:
            alt = ziel.read_text(encoding="utf-8").replace("\r\n", "\n") if ziel.exists() else ""
            if alt != inhalt:
                abweichend.append(ziel.relative_to(ROOT).as_posix())
        else:
            ziel.write_text(inhalt, encoding="utf-8", newline="\n")
            print(f"Geschrieben: {ziel.relative_to(ROOT).as_posix()}")
    if abweichend:
        print(f"DRIFT: {', '.join(abweichend)} — python scripts/generate_belegvertrag.py ausfuehren", file=sys.stderr)
        return 1
    if args.check:
        print("OK: Belegvertrag aktuell")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
