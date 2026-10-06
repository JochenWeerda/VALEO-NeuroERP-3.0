"""Ratsche: Ein Platzhalter darf den Mount-Fetch nicht verhindern.

Der Fehler
----------
`initialData` schreibt einen Wert in den React-Query-Cache, **als wäre er vom Server
gekommen**. Zusammen mit `staleTime` gilt er für dessen Dauer als frisch — und die
Abfrage fragt in dieser Zeit **gar nicht**. Die Maske zeigt „keine Einträge", und
niemand sieht, dass nie gefragt wurde.

Am 17.07.2026 meldete der Nutzer genau das: „Ackerschlagkartei zeigte initial weder
Schläge noch Maßnahmen — erst nach einer Mutation erschienen die Seed-Daten."
Regressionstest: `src/__tests__/lib/portal-feldbuch-hooks.test.tsx`.

Was geprüft wird
----------------
1. **Jede** `initialData`-Option in einem `useQuery`-artigen Aufruf muss im selben
   Aufruf `initialDataUpdatedAt: 0` tragen. Das macht den Platzhalter sofort
   veraltet; der Mount-Fetch findet statt. Ein Verstoß ist ein Fehler, keine Zahl.
2. Die **Gesamtzahl** der `initialData`-Stellen ist down-only. Das Ziel ist
   `placeholderData`: Es schreibt den Cache nicht an und markiert sich als
   Platzhalter. Die Umstellung macht `data` im Fehlerfall `undefined` und ist damit
   je Aufrufer eine eigene Änderung — die Ratsche hält die Zahl fest, damit der Weg
   weitergeht statt zu versanden.

Was **nicht** geprüft wird: ob eine Maske `isError` liest. Im Fehlerfall bleibt der
Platzhalter sichtbar, weil er im Cache steht. Das ist die zweite Hälfte des Fehlers
und liegt in den Masken.

Aufruf:  python scripts/check_initial_data.py [--list]
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

WURZEL = pathlib.Path("packages/frontend-web/src")

#: 2026-10-06, erstmals gemessen: 205 Stellen, alle mit `initialDataUpdatedAt: 0`.
#: Jede Umstellung auf `placeholderData` senkt die Zahl. Nur nach unten.
BASELINE_STELLEN = 205

START = re.compile(r"^(\s*)initialData:")
AUFRUF = re.compile(r"\buse(Query|InfiniteQuery|SuspenseQuery|SuspenseInfiniteQuery)\s*\(")
MUTATION = re.compile(r"\buseMutation\s*\(")


def _ausgeglichen(text: str) -> bool:
    return (
        text.count("{") == text.count("}")
        and text.count("[") == text.count("]")
        and text.count("(") == text.count(")")
    )


def _umgebender_aufruf(zeilen: list[str], i: int) -> int | None:
    """Die Zeile des Abfrage-Aufrufs, in dessen Optionen Zeile ``i`` liegt."""
    for j in range(i - 1, max(-1, i - 400), -1):
        if AUFRUF.search(zeilen[j]):
            return j
        if MUTATION.search(zeilen[j]):
            return None
    return None


def _block(zeilen: list[str], start: int) -> str:
    gesammelt: list[str] = []
    for j in range(start, len(zeilen)):
        gesammelt.append(zeilen[j])
        if _ausgeglichen("\n".join(gesammelt)):
            break
    return "\n".join(gesammelt)


def pruefe() -> dict:
    stellen: list[str] = []
    ohne_gegenmassnahme: list[str] = []
    for pfad in sorted(WURZEL.rglob("*.ts")) + sorted(WURZEL.rglob("*.tsx")):
        name = str(pfad)
        if ".gen." in name:
            continue
        zeilen = pfad.read_text(encoding="utf-8", errors="ignore").split("\n")
        for i, zeile in enumerate(zeilen):
            if not START.match(zeile):
                continue
            ort = f"{pfad.as_posix()}:{i + 1}"
            stellen.append(ort)
            if "__tests__" in name:
                # Ein Test darf einen Platzhalter bewusst so setzen, wie er ihn
                # prueft.
                continue
            aufruf = _umgebender_aufruf(zeilen, i)
            if aufruf is None:
                continue
            if "initialDataUpdatedAt" not in _block(zeilen, aufruf):
                ohne_gegenmassnahme.append(ort)
    return {"stellen": stellen, "offen": ohne_gegenmassnahme}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true")
    argumente = parser.parse_args()

    if not WURZEL.exists():
        print(f"FEHLER: {WURZEL} nicht gefunden — aus dem Repo-Wurzelverzeichnis aufrufen.")
        return 2

    ergebnis = pruefe()
    anzahl = len(ergebnis["stellen"])
    offen = ergebnis["offen"]

    print(
        f"initialData: {anzahl} Stellen (Schwelle {BASELINE_STELLEN}), "
        f"{len(offen)} ohne initialDataUpdatedAt: 0"
    )

    if argumente.list:
        for ort in ergebnis["stellen"]:
            print(f"  {ort}")

    fehler = 0
    if offen:
        print("\nFEHLER: Platzhalter, der den Mount-Fetch verhindert:")
        for ort in offen:
            print(f"  {ort}")
        print(
            "        `initialDataUpdatedAt: 0` daneben setzen — oder besser auf\n"
            "        `placeholderData` umstellen. Ohne das fragt die Abfrage fuer die\n"
            "        Dauer von `staleTime` nicht, und die Maske zeigt einen leeren\n"
            "        Stand als Tatsache (Nutzermeldung 17.07.2026)."
        )
        fehler = 1

    if anzahl > BASELINE_STELLEN:
        print(
            f"\nFEHLER: {anzahl} initialData-Stellen, erlaubt sind {BASELINE_STELLEN}.\n"
            "        Neue Abfragen nehmen `placeholderData`: Es schreibt den Cache\n"
            "        nicht an und markiert sich als Platzhalter."
        )
        fehler = 1

    if not fehler:
        print("OK: kein Platzhalter verdeckt einen fehlenden Mount-Fetch.")
    return fehler


if __name__ == "__main__":
    sys.exit(main())
