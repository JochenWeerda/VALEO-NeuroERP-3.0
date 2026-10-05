#!/usr/bin/env python3
"""
CI-Gate: PostgreSQL-Cast auf einem Bind-Parameter.

Prueft, ob in SQLAlchemy-``text()``-Anweisungen die Schreibweise
``:name::typ`` vorkommt. Sie sieht richtig aus, bindet den Parameter aber
**nicht** — SQLAlchemy verschluckt das letzte Zeichen des Namens:

    >>> from sqlalchemy import text
    >>> list(text("SELECT :data::jsonb")._bindparams)
    ['dat']
    >>> list(text("SELECT :date_from::DATE")._bindparams)
    ['date_fro']

Der uebergebene Wert landet damit nie in der Anweisung. Je nach Aufrufpfad
schlaegt die Ausfuehrung fehl ("bind parameter without a value") oder ein
stiller Fallback greift und verdeckt den Fehler — genau das ist in
``app/documents/repository.py`` passiert: der INSERT schlug fehl, der
In-Memory-Fallback meldete Erfolg, und der spaetere Lesezugriff lief in 404.

Richtig ist die ANSI-Schreibweise, die den Parameter vollstaendig bindet:

    CAST(:name AS jsonb)

Nicht betroffen sind Casts auf **Spalten** (``data::jsonb->>'status'``); dort
steht vor dem Doppelpunktpaar kein Parametername.

Exit 0 = OK, Exit 1 = mindestens eine betroffene Stelle.
"""
from __future__ import annotations

import argparse
import io
import re
import subprocess
import sys

# :name::typ - der Lookbehind haelt Spaltencasts und bereits verdoppelte
# Doppelpunkte heraus.
PATTERN = re.compile(r'(?<![\w:]):([a-zA-Z_]\w*)::([a-zA-Z_]\w*(?:\s*\[\s*\])?)')

DEFAULT_ROOTS = ("app", "modules", "services", "tools", "scripts")

# Dieses Gate selbst zeigt das Anti-Muster im Docstring und in den Meldungen -
# sonst waere nicht erklaerbar, wogegen es schuetzt. Es darf sich deshalb nicht
# selbst melden. Die Ausnahme gilt genau fuer diese eine Datei, nicht fuer ein
# Verzeichnis, damit sie nicht unbemerkt waechst.
SELBSTAUSNAHME = "scripts/check_sql_bind_casts.py"


def read_text(path: str) -> str:
    raw = io.open(path, "rb").read()
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        # Einzelne Altdateien liegen in cp1252 vor.
        return raw.decode("cp1252", errors="replace")


def find_hits(roots):
    files = subprocess.check_output(["git", "ls-files", *roots], text=True).split()
    hits = []
    for path in files:
        if not path.endswith(".py") or path.replace("\\", "/") == SELBSTAUSNAHME:
            continue
        for number, line in enumerate(read_text(path).split("\n"), 1):
            for match in PATTERN.finditer(line):
                hits.append((path, number, match.group(1), match.group(2), line.strip()))
    return hits


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", action="append", dest="roots", default=None)
    args = parser.parse_args()
    hits = find_hits(tuple(args.roots) if args.roots else DEFAULT_ROOTS)

    if not hits:
        print("SQL-Bind-Cast-Gate: keine Stelle mit ':name::typ' gefunden.")
        return 0

    print("SQL-Bind-Cast-Gate fehlgeschlagen:\n")
    print("Die Schreibweise ':name::typ' bindet den Parameter nicht - SQLAlchemy")
    print("verschluckt das letzte Zeichen des Namens. Bitte auf 'CAST(:name AS typ)'")
    print("umstellen.\n")
    for path, number, name, cast_type, line in hits:
        print(f"- {path}:{number}: ':{name}::{cast_type}' -> 'CAST(:{name} AS {cast_type})'")
        print(f"    {line}")
    return 1


if __name__ == "__main__":
    sys.exit(main())
