#!/usr/bin/env python3
"""SPEC-P1-05: Review-Artefakt fuer SQL-f-Strings — Verdikt aus Bandit, nicht aus Prosa.

Die erste Fassung dieses Skripts leitete ihr Verdikt aus dem *Wortlaut* des
Kommentars ab: enthielt er "whitelist", "column" oder "parametr", galt die
Stelle als ``ok_documented``. Das hat zwei Dinge nicht gemessen —

  1. ob die Suppression ueberhaupt greift (Bandits ``nosec`` ist an die Zeilen
     des gemeldeten Ausdrucks gebunden; ein Kommentar darueber oder innerhalb
     des SQL-Strings wirkt nicht), und
  2. ob an der Stelle ueberhaupt jemals ein Review stattgefunden hat.

Dadurch standen 132 Stellen als "ok_documented" im Bericht, waehrend Bandit
sie unveraendert meldete. Diese Fassung fragt stattdessen den Scanner:

  * ``suppressed``   — Bandit meldet die Stelle nicht mehr: Suppression wirkt.
  * ``unsuppressed`` — Kommentar vorhanden, aber wirkungslos platziert.
  * ``unreviewed``   — SQL-f-String ganz ohne ``nosec``.

Nur ``suppressed`` ist ein belastbarer Zustand. Die Begruendungstexte werden
weiterhin mitgefuehrt, aber nicht mehr als Nachweis gewertet.
"""
from __future__ import annotations

import argparse
import ast
import io
import json
import subprocess  # nosec B404  # fester Aufruf ohne Shell, Argumente aus dem Code
import sys
import tempfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "app"
OUT = ROOT / "docs" / "operations" / "appsec-s608-review.md"
BASELINE = ROOT / "config" / "sql_fstring_review_baseline.json"

sys.path.insert(0, str(ROOT / "scripts"))
from check_sql_fstrings import (  # noqa: E402
    _hat_fstring_arg,
    _ist_sql_aufruf,
    _nosec_zeilen,
)


def bandit_befunde() -> set[tuple[str, int]]:
    """(relativer Pfad, Zeile) aller offenen B608-Befunde."""
    with tempfile.TemporaryDirectory() as tmp:
        bericht = Path(tmp) / "b608.json"
        subprocess.run(  # nosec B603  # feste Argumentliste, keine Shell
            [
                sys.executable, "-m", "bandit", "-r", str(APP),
                "-t", "B608", "-f", "json", "-o", str(bericht), "-q",
            ],
            cwd=ROOT,
            check=False,
            capture_output=True,
        )
        if not bericht.exists():
            raise SystemExit(
                "Bandit lieferte keinen Bericht — ist 'bandit' installiert? "
                "(pip install bandit)"
            )
        daten = json.loads(bericht.read_text(encoding="utf-8"))
    treffer = set()
    for eintrag in daten["results"]:
        pfad = Path(eintrag["filename"])
        try:
            rel = pfad.resolve().relative_to(ROOT).as_posix()
        except ValueError:
            rel = pfad.as_posix()
        treffer.add((rel, eintrag["line_number"]))
    return treffer


def sql_stellen() -> list[dict]:
    """Alle SQL-f-String-Aufrufe mit Zeilenbereich und Begruendungstext."""
    stellen = []
    for py in sorted(APP.rglob("*.py")):
        try:
            quelle = io.open(py, encoding="utf-8", errors="replace").read()
            baum = ast.parse(quelle)
        except (OSError, SyntaxError, ValueError):
            continue
        nosec = _nosec_zeilen(py)
        zeilen = quelle.splitlines()
        gesehen = set()
        for knoten in ast.walk(baum):
            if not isinstance(knoten, ast.Call) or not _ist_sql_aufruf(knoten):
                continue
            if not _hat_fstring_arg(knoten):
                continue
            start = knoten.lineno
            ende = getattr(knoten, "end_lineno", start) or start
            if start in gesehen:
                continue
            gesehen.add(start)
            nosec_zeile = next(
                (z for z in range(start, ende + 1) if z in nosec), None
            )
            begruendung = ""
            if nosec_zeile:
                roh = zeilen[nosec_zeile - 1]
                if "#" in roh:
                    begruendung = roh[roh.index("#"):].strip()[:120]
            stellen.append(
                {
                    "datei": py.relative_to(ROOT).as_posix(),
                    "start": start,
                    "ende": ende,
                    "hat_nosec": nosec_zeile is not None,
                    "begruendung": begruendung,
                }
            )
    return stellen


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument(
        "--fail-on-unsuppressed",
        action="store_true",
        help="Exit 1, wenn wirkungslos platzierte Suppressions existieren",
    )
    args = parser.parse_args()

    offen = bandit_befunde()
    stellen = sql_stellen()

    for s in stellen:
        gemeldet = any(
            (s["datei"], z) in offen for z in range(s["start"], s["ende"] + 1)
        )
        if not gemeldet:
            s["verdikt"] = "suppressed"
        elif s["hat_nosec"]:
            s["verdikt"] = "unsuppressed"
        else:
            s["verdikt"] = "unreviewed"

    zaehler = {"suppressed": 0, "unsuppressed": 0, "unreviewed": 0}
    for s in stellen:
        zaehler[s["verdikt"]] += 1

    baseline_anzahl = 0
    if BASELINE.exists():
        baseline_anzahl = len(
            json.loads(BASELINE.read_text(encoding="utf-8")).get("offen", [])
        )

    out = [
        "---",
        "title: AppSec S608 Review",
        "type: reference",
        "audience: [sicherheit, entwickler]",
        "owner: Claude Code",
        "status: aktiv",
        f"last_reviewed: {date.today().isoformat()}",
        "version: 2.0.0",
        "description: SPEC-P1-05 — SQL-f-String-Inventar; Verdikt aus dem Bandit-Lauf.",
        "---",
        "",
        "# AppSec S608-Review (SPEC-P1-05)",
        "",
        f"Stand: **{date.today().isoformat()}** — erzeugt von "
        "`scripts/generate_s608_review.py`.",
        "",
        "Das Verdikt stammt aus einem echten `bandit -t B608`-Lauf, nicht aus dem",
        "Wortlaut der Kommentare. Version 1.0 dieses Berichts hatte nach Prosa",
        "klassifiziert und deshalb 132 Stellen als geprueft ausgewiesen, die Bandit",
        "unveraendert meldete.",
        "",
        f"SQL-f-String-Aufrufe gesamt: **{len(stellen)}**",
        "",
        "| Verdikt | Anzahl | Bedeutung |",
        "|---|---:|---|",
        f"| `suppressed` | {zaehler['suppressed']} | Bandit meldet die Stelle nicht mehr — Suppression wirkt |",
        f"| `unsuppressed` | {zaehler['unsuppressed']} | Kommentar vorhanden, aber wirkungslos platziert |",
        f"| `unreviewed` | {zaehler['unreviewed']} | SQL-f-String ohne jedes `nosec` — echtes Review offen |",
        "",
        "## Platzierung",
        "",
        "Bandit unterdrueckt nur, wenn `# nosec` auf einer Zeile **des gemeldeten",
        "Ausdrucks** steht. Zwei Formen wirken nicht:",
        "",
        "```python",
        "# nosec B608  # Begruendung        <- Zeile DARUEBER: wirkungslos",
        'rows = db.execute(text(f"SELECT ... {where}"), params)',
        "",
        'rows = db.execute(text(f"""  -- nosec S608 ...   <- im SQL-String: wirkungslos',
        "    SELECT ... {where}",
        '"""), params)',
        "```",
        "",
        "Richtig ist die schliessende Klammerzeile:",
        "",
        "```python",
        'rows = db.execute(text(f"""',
        "    SELECT ... {where}",
        '"""), params)  # nosec B608  # reviewed-safe: <Begruendung>',
        "```",
        "",
        "## Gate",
        "",
        "`scripts/check_sql_fstrings.py` bildet dieselbe Semantik ab und faellt bei",
        "**neuen** ungeflaggten Stellen. Die bekannte Restschuld steht in",
        f"`config/sql_fstring_review_baseline.json` ({baseline_anzahl} Stellen) und",
        "darf nur schrumpfen.",
        "",
    ]

    for verdikt, titel in (
        ("unsuppressed", "Wirkungslos platziert — vorrangig"),
        ("unreviewed", "Ohne Review — SPEC-P1-05-Restschuld"),
        ("suppressed", "Wirksam unterdrueckt"),
    ):
        passend = [s for s in stellen if s["verdikt"] == verdikt]
        if not passend:
            continue
        out.extend(
            (
                f"## {titel} ({len(passend)})",
                "",
                "| Datei | Zeilen | Begruendung |",
                "|---|---:|---|",
            )
        )
        for s in passend:
            text_ = (s["begruendung"] or "—").replace("|", "\\|")
            bereich = (
                str(s["start"])
                if s["start"] == s["ende"]
                else f"{s['start']}-{s['ende']}"
            )
            out.append(f"| `{s['datei']}` | {bereich} | `{text_}` |")
        out.append("")

    out.extend(
        (
            "## Naechste Schritte",
            "",
            "1. `unsuppressed` beheben — Kommentar auf die Aufrufzeile verschieben.",
            "2. `unreviewed` fachlich pruefen: Identifier aus Allowlist? Werte",
            "   gebunden? Danach `nosec` setzen und aus der Baseline austragen.",
            "3. Erst wenn die Baseline leer ist, ist SPEC-P1-05 erledigt.",
            "",
        )
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text("\n".join(out), encoding="utf-8")
    print(
        f"geschrieben: {args.out.relative_to(ROOT)} — "
        f"suppressed={zaehler['suppressed']} "
        f"unsuppressed={zaehler['unsuppressed']} "
        f"unreviewed={zaehler['unreviewed']}"
    )
    if args.fail_on_unsuppressed and zaehler["unsuppressed"]:
        print("FEHLER: wirkungslos platzierte Suppressions vorhanden.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
