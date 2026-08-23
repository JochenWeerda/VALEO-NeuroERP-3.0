#!/usr/bin/env python3
"""
CI-Gate: SQL f-string Injection Check.

Prueft, ob SQL-f-Strings ohne wirksames ``# nosec B608  # `` eingefuegt wurden.

WICHTIG — Platzierung des Kommentars:
    Bandit (Regel B608) unterdrueckt nur, wenn der ``# nosec``-Kommentar auf
    einer Zeile des gemeldeten Ausdrucks steht. Ein Kommentar auf einer Zeile
    *darueber* wirkt nicht. Genau das hat die fruehere Fassung dieses Gates
    akzeptiert (``lines[i-3:i+1]``) und damit repo-weit eine Platzierung
    antrainiert, die Bandit ignoriert.

    Dieses Gate bildet deshalb Bandits Semantik nach: es sucht den Kommentar im
    Zeilenbereich des Aufrufknotens (``lineno``..``end_lineno``).

    Bei mehrzeiligen f-Strings ist die schliessende Klammerzeile die richtige
    Stelle:

        rows = db.execute(text(f\"\"\"
            SELECT ... WHERE {where}
        \"\"\"), params)  # nosec B608  # reviewed-safe: <Begruendung>

    An die oeffnende Zeile angehaengt landet der Text *im String* und
    veraendert das SQL.

WICHTIG — Kennung und Begruendung:
    Die Regel heisst bei Bandit ``B608``; ``S608`` ist die Ruff-Kennung. Bandit
    liest alles nach ``nosec`` bis zum naechsten ``#`` als Liste von Test-IDs
    (``NOSEC_COMMENT = r"#\s*nosec:?\s*(?P<tests>[^#]+)?#?"``). Steht dort keine
    gueltige ID, wirkt die Zeile als *pauschales* nosec und unterdrueckt jeden
    Bandit-Check darauf.

    Deshalb: Kennung zuerst, Begruendung hinter einem zweiten ``#`` —
    ``# nosec B608  # reviewed-safe: <Begruendung>``. So wird genau eine Regel
    unterdrueckt und die Prosa nicht als ID-Liste fehlgelesen.

Exit 0 = OK, Exit 1 = SQL-f-Strings ohne wirksames nosec.
"""
from __future__ import annotations

import argparse
import ast
import io
import json
import sys
import tokenize
from pathlib import Path

SUCHPFADE = ("app",)
BASELINE = Path("config/sql_fstring_review_baseline.json")


def _nosec_zeilen(pfad: Path) -> set[int]:
    """Zeilennummern, die einen ``# nosec``-Kommentar tragen."""
    treffer: set[int] = set()
    try:
        with tokenize.open(pfad) as fh:
            for tok in tokenize.generate_tokens(fh.readline):
                if tok.type == tokenize.COMMENT and "nosec" in tok.string:
                    treffer.add(tok.start[0])
    except (OSError, SyntaxError, tokenize.TokenError, UnicodeDecodeError):
        return treffer
    return treffer


def _ist_dynamisch(knoten: ast.AST) -> bool:
    """True, wenn der Ausdruck zur Laufzeit zusammengesetzten SQL-Text ergibt.

    Erfasst beide Bauformen, die Bandit meldet:
      * f-String mit eingesetzten Ausdruecken  — f"... {where}"
      * String-Konkatenation mit Nicht-Konstante — \"\"\"...\"\"\" + suffix
    """
    if isinstance(knoten, ast.JoinedStr):
        return any(isinstance(teil, ast.FormattedValue) for teil in knoten.values)
    if isinstance(knoten, ast.BinOp) and isinstance(knoten.op, ast.Add):
        for seite in (knoten.left, knoten.right):
            if isinstance(seite, ast.Constant):
                continue
            if _ist_dynamisch(seite):
                return True
            # Name/Attribute/Call auf einer Seite einer String-Addition
            if isinstance(seite, (ast.Name, ast.Attribute, ast.Call, ast.IfExp)):
                return True
    return False


def _hat_fstring_arg(knoten: ast.Call) -> bool:
    """True, wenn ein Argument dynamisch zusammengesetzten SQL-Text traegt."""
    return any(_ist_dynamisch(arg) for arg in knoten.args)


def _ist_sql_aufruf(knoten: ast.Call) -> bool:
    func = knoten.func
    if isinstance(func, ast.Name) and func.id == "text":
        return True
    if isinstance(func, ast.Attribute) and func.attr in ("execute", "exec_driver_sql"):
        return True
    return False


def pruefe_datei(pfad: Path) -> list[str]:
    try:
        quelle = io.open(pfad, encoding="utf-8", errors="replace").read()
        baum = ast.parse(quelle)
    except (OSError, SyntaxError, ValueError):
        return []

    nosec = _nosec_zeilen(pfad)
    zeilen = quelle.splitlines()
    verstoesse: list[str] = []

    for knoten in ast.walk(baum):
        if not isinstance(knoten, ast.Call) or not _ist_sql_aufruf(knoten):
            continue
        if not _hat_fstring_arg(knoten):
            continue
        start = knoten.lineno
        ende = getattr(knoten, "end_lineno", start) or start
        # Bandit-Semantik: nosec irgendwo im Zeilenbereich des Knotens.
        if any(z in nosec for z in range(start, ende + 1)):
            continue
        text_zeile = zeilen[start - 1].strip()[:100] if start <= len(zeilen) else ""
        verstoesse.append(f"{pfad}:{start}: {text_zeile}")
    return verstoesse


def _lade_baseline() -> set[str]:
    """Bekannte, noch ungereviewte Stellen (SPEC-P1-05-Restschuld).

    Die Baseline darf nur schrumpfen: neue Stellen lassen das Gate fallen,
    abgearbeitete werden mit ``--update-baseline`` ausgetragen.
    """
    if not BASELINE.exists():
        return set()
    daten = json.loads(BASELINE.read_text(encoding="utf-8"))
    return set(daten.get("offen", []))


def _schluessel(verstoss: str) -> str:
    """Datei:Zeile ohne Codeausschnitt — der Ausschnitt aendert sich zu leicht."""
    datei, zeile, _ = verstoss.split(":", 2)
    return f"{datei.replace(chr(92), '/')}:{zeile}"


def check(update_baseline: bool = False) -> int:
    verstoesse: list[str] = []
    for wurzel in SUCHPFADE:
        for py in sorted(Path(wurzel).rglob("*.py")):
            verstoesse.extend(pruefe_datei(py))

    # Ein Aufruf kann verschachtelt doppelt erfasst werden (db.execute(text(f"...")));
    # nach Datei:Zeile deduplizieren.
    eindeutig = sorted(set(verstoesse))
    bekannt = _lade_baseline()
    aktuell = {_schluessel(v) for v in eindeutig}

    if update_baseline:
        BASELINE.parent.mkdir(parents=True, exist_ok=True)
        BASELINE.write_text(
            json.dumps(
                {
                    "_hinweis": (
                        "SPEC-P1-05-Restschuld: SQL-f-Strings ohne Security-Review. "
                        "Die Liste darf nur schrumpfen. Eintrag entfernen, sobald die "
                        "Stelle reviewed und mit wirksamem '# nosec B608  # ' versehen ist."
                    ),
                    "offen": sorted(aktuell),
                },
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"[OK] Baseline geschrieben: {len(aktuell)} offene Stellen")
        return 0

    neu = sorted(aktuell - bekannt)
    erledigt = sorted(bekannt - aktuell)

    if erledigt:
        print(f"[INFO] {len(erledigt)} Baseline-Stellen sind erledigt — bitte mit")
        print("       'python scripts/check_sql_fstrings.py --update-baseline' austragen.")

    if neu:
        print(f"[FAIL] {len(neu)} NEUE SQL-f-String(s) ohne wirksames nosec:")
        for v in eindeutig:
            if _schluessel(v) in set(neu):
                print(f"  {v}")
        print()
        print("Behebung: parametrisierte Query verwenden — oder, wenn reviewed,")
        print("  # nosec B608  # <Begruendung> auf eine Zeile DES AUFRUFS setzen.")
        print("  Bei mehrzeiligen f-Strings gehoert der Kommentar an die")
        print("  schliessende Klammerzeile, nicht an die oeffnende (dort landet")
        print("  er im String und veraendert das SQL).")
        return 1

    if aktuell:
        print(
            f"[OK] Keine neuen Stellen. Offene SPEC-P1-05-Restschuld: "
            f"{len(aktuell)} (Baseline {BASELINE})."
        )
    else:
        print("[OK] Alle SQL-f-Strings tragen ein wirksames nosec B608.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--update-baseline",
        action="store_true",
        help="Baseline neu schreiben (nur nach bewusster Abarbeitung)",
    )
    args = parser.parse_args()
    sys.exit(check(update_baseline=args.update_baseline))
