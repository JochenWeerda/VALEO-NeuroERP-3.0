#!/usr/bin/env python3
"""Findet Stellen, an denen ein ``except`` eine tote Transaktion verdeckt.

Das Muster
----------

    try:
        db.execute(...)          # scheitert, die Transaktion ist ab hier tot
    except Exception as fehler:
        log.append({"error": str(fehler)})   # gefangen, aber nicht zurueckgerollt

    db.execute(...)              # scheitert mit InFailedSqlTransaction
    db.commit()                  # scheitert ebenfalls

Postgres bricht bei einem Fehler die **ganze** Transaktion ab. Ein ``except``
faengt die Ausnahme, aber ohne ``rollback()`` oder Savepoint
(``begin_nested()``) ist jede weitere Anweisung verloren — und weil die
Fehlermeldung im Protokoll landet statt beim Aufrufer, sieht das Ergebnis aus
wie ein Ergebnis.

Gefunden am 29.09.2026 im Loeschlauf nach Art. 17 DSGVO: Eine fehlende
Nebentabelle brach die Transaktion ab, der Antrag lief komplett ins Leere, und
der Aufrufer bekam 503 „Failed to update erasure request" — ohne zu erfahren,
woran es lag. Eine Rechtspflicht blieb unerfuellt.

Was als Fund gilt
-----------------

Ein ``try``, dessen Koerper eine Datenbankanweisung ausfuehrt
(``execute``/``flush``/``commit``/``scalar``/``add``), und dessen
``except``-Zweig **keines** davon tut:

- ``rollback()`` — die Transaktion aufraeumen
- ``raise`` — weitergeben
- eine nutzersichtbare Fehlerantwort (``HTTPException``, ``abort``,
  ``JSONResponse`` mit Fehlerstatus, eine projekteigene Fehlerklasse)
- ``pytest.skip`` (ein Test, der sich selbst ueberspringt, faelscht kein
  Ergebnis)

Ein ``try`` innerhalb eines ``with db.begin_nested()`` gilt als abgesichert:
Der Savepoint wird beim Verlassen zurueckgerollt.

**Und — das ist der entscheidende Zusatz — die Sitzung muss danach noch
benutzt werden.** Ein geschluckter Fehler, nach dem nichts mehr passiert, ist
harmlos: Die Anfrage endet, und die Sitzungsabhaengigkeit rollt beim Schliessen
ohnehin zurueck. Schaden entsteht erst, wenn danach weitergearbeitet wird.
Gezaehlt wird deshalb nur, wenn eines von beidem zutrifft:

- das ``try`` steht in einer Schleife (der naechste Durchlauf fuehrt wieder
  eine Anweisung aus — genau der Art.-17-Fall), oder
- nach dem ``try`` folgt in derselben Funktion eine weitere
  Datenbankanweisung.

Ohne diese Einschraenkung meldet die Suche 351 Stellen, von denen die meisten
nichts anrichten. Mit ihr bleiben die uebrig, die wirklich ein Scheinergebnis
erzeugen koennen.

Aufruf
------

    python scripts/check_dead_transactions.py                 # Ratsche pruefen
    python scripts/check_dead_transactions.py --liste         # alle Funde zeigen
    python scripts/check_dead_transactions.py --json          # maschinenlesbar
    python scripts/check_dead_transactions.py --schwelle N    # andere Ratsche
"""

from __future__ import annotations

import argparse
import ast
import json
import pathlib
import sys

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]

#: Wo gesucht wird. Tests bleiben aussen vor: Dort ist ein geschluckter
#: Datenbankfehler oft der Zweck (Ueberspringen ohne Datenbank).
SUCHPFADE = ("app", "modules")

#: Namen, die eine Datenbankanweisung anzeigen.
DB_AUFRUFE = {"execute", "flush", "commit", "scalar", "scalars", "add", "add_all", "delete"}

#: Namen, die im except-Zweig als Behandlung gelten.
HEILUNG = {"rollback", "raise", "skip"}

#: Fehlerklassen, deren Auslösen als nutzersichtbare Antwort gilt.
FEHLERANTWORTEN = {
    "HTTPException", "RequestValidationError", "abort",
    "DomainError", "StornoError", "BusinessError", "ValidationError",
    "NotFoundError", "ConflictError",
}

#: Stand 2026-09-30: 78 Erstbefunde minus zwei Zahlungs- und ein CSV-Importbefund.
#: Aktueller Codebestand: 75. Darf sinken, nicht steigen.
#:
#: Davon 19 in mutierenden Funktionen (Buchung, Zahlung, Loeschung, Freigabe,
#: Anlage/Import) und 59 in lesenden. Die Fundliste mit Einordnung je Stelle
#: steht in docs/quality-assurance/tote-transaktion-2026-09-30.md.
#:
#: Der Loeschweg nach Art. 17 DSGVO ist nicht mehr darunter: Er hat seit
#: 2026-09-29 Savepoints je Anweisung.
SCHWELLE = 75


class _Besuch(ast.NodeVisitor):
    def __init__(self, datei: pathlib.Path) -> None:
        self.datei = datei
        self.funde: list[dict] = []
        self._savepoint_tiefe = 0
        self._schleifen_tiefe = 0
        self._funktionen: list[ast.AST] = []

    # ---- Hilfen -------------------------------------------------------

    @staticmethod
    def _ist_db_aufruf(knoten: ast.AST) -> bool:
        """``db.execute(...)``, ``session.commit()``, ``conn.scalar(...)``."""
        for kind in ast.walk(knoten):
            if isinstance(kind, ast.Call) and isinstance(kind.func, ast.Attribute):
                if kind.func.attr in DB_AUFRUFE:
                    return True
        return False

    @classmethod
    def _db_aufruf_ohne_savepoint(cls, knoten: ast.AST) -> bool:
        """Wie ``_ist_db_aufruf``, aber ohne das, was im Savepoint steht.

        Der verbreitete und richtige Weg ist

            try:
                with db.begin_nested():
                    db.execute(...)
            except Exception:
                weiter

        Hier liegt der Savepoint **innerhalb** des ``try``. Wer nur die
        Verschachtelung um das ``try`` herum prueft, meldet diese Stelle
        faelschlich — genau das tat die erste Fassung dieses Skripts und
        markierte damit den Loeschweg, der am 29.09. behoben wurde.
        """
        if isinstance(knoten, ast.With) and cls._ist_savepoint(knoten):
            return False
        if isinstance(knoten, ast.Call) and isinstance(knoten.func, ast.Attribute):
            if knoten.func.attr in DB_AUFRUFE:
                return True
        for kind in ast.iter_child_nodes(knoten):
            if cls._db_aufruf_ohne_savepoint(kind):
                return True
        return False

    @staticmethod
    def _wird_behandelt(zweig: ast.ExceptHandler) -> bool:
        for kind in ast.walk(zweig):
            if isinstance(kind, ast.Raise):
                return True
            if isinstance(kind, ast.Call):
                if isinstance(kind.func, ast.Attribute) and kind.func.attr in HEILUNG:
                    return True
                name = None
                if isinstance(kind.func, ast.Name):
                    name = kind.func.id
                elif isinstance(kind.func, ast.Attribute):
                    name = kind.func.attr
                if name in FEHLERANTWORTEN or name in HEILUNG:
                    return True
            # `return JSONResponse(..., status_code=5xx)` oder ein Dict mit
            # "error" gilt nicht als Behandlung: Der Aufrufer erfaehrt zwar
            # etwas, die Transaktion bleibt aber tot.
        return False

    @staticmethod
    def _ist_savepoint(knoten: ast.With) -> bool:
        for element in knoten.items:
            ausdruck = element.context_expr
            for kind in ast.walk(ausdruck):
                if isinstance(kind, ast.Call) and isinstance(kind.func, ast.Attribute):
                    if kind.func.attr in {"begin_nested", "begin"}:
                        return True
        return False

    # ---- Besuch -------------------------------------------------------

    def visit_With(self, knoten: ast.With) -> None:
        if self._ist_savepoint(knoten):
            self._savepoint_tiefe += 1
            self.generic_visit(knoten)
            self._savepoint_tiefe -= 1
        else:
            self.generic_visit(knoten)

    def visit_For(self, knoten: ast.For) -> None:
        self._schleifen_tiefe += 1
        self.generic_visit(knoten)
        self._schleifen_tiefe -= 1

    def visit_While(self, knoten: ast.While) -> None:
        self._schleifen_tiefe += 1
        self.generic_visit(knoten)
        self._schleifen_tiefe -= 1

    def visit_FunctionDef(self, knoten: ast.FunctionDef) -> None:
        self._funktionen.append(knoten)
        self.generic_visit(knoten)
        self._funktionen.pop()

    visit_AsyncFunctionDef = visit_FunctionDef  # type: ignore[assignment]

    def _wird_danach_weitergearbeitet(self, knoten: ast.Try) -> str | None:
        """Passiert nach diesem ``try`` noch etwas auf derselben Sitzung?

        Gibt den Grund zurueck, warum die tote Transaktion schadet — oder
        ``None``, wenn nichts mehr folgt und der Fehler damit harmlos ist.
        """
        if self._schleifen_tiefe > 0:
            return "in einer Schleife: der naechste Durchlauf faellt mit"
        if not self._funktionen:
            return None
        # ast.walk laeuft auch ueber Knoten ohne Zeilennummer (ast.Store und
        # Verwandte) — die werden uebergangen, nicht geraten.
        zeilen = [
            z for z in (
                getattr(k, "end_lineno", None) or getattr(k, "lineno", None)
                for k in ast.walk(knoten)
            ) if z is not None
        ]
        ende = max(zeilen) if zeilen else knoten.lineno
        for anweisung in self._funktionen[-1].body:
            if anweisung.lineno > ende and self._ist_db_aufruf(anweisung):
                return f"danach folgt in Zeile {anweisung.lineno} eine weitere Anweisung"
        return None

    def visit_Try(self, knoten: ast.Try) -> None:
        if self._savepoint_tiefe == 0 and any(
            self._db_aufruf_ohne_savepoint(anweisung) for anweisung in knoten.body
        ):
            grund = self._wird_danach_weitergearbeitet(knoten)
            if grund:
                for zweig in knoten.handlers:
                    if not self._wird_behandelt(zweig):
                        self.funde.append({
                            "datei": str(self.datei.relative_to(REPO_ROOT)).replace("\\", "/"),
                            "zeile": zweig.lineno,
                            "ausnahme": ast.unparse(zweig.type) if zweig.type else "alles",
                            "grund": grund,
                        })
        self.generic_visit(knoten)


def suche(pfade: tuple[str, ...] = SUCHPFADE) -> list[dict]:
    funde: list[dict] = []
    for wurzel in pfade:
        for datei in sorted((REPO_ROOT / wurzel).rglob("*.py")):
            if "__pycache__" in datei.parts:
                continue
            try:
                baum = ast.parse(datei.read_text(encoding="utf-8", errors="ignore"))
            except SyntaxError:
                continue
            besuch = _Besuch(datei)
            besuch.visit(baum)
            funde.extend(besuch.funde)
    return funde


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--liste", action="store_true", help="Alle Funde zeigen.")
    parser.add_argument("--json", action="store_true", help="Maschinenlesbar ausgeben.")
    parser.add_argument("--schwelle", type=int, default=SCHWELLE)
    args = parser.parse_args()

    funde = suche()

    if args.json:
        print(json.dumps(funde, ensure_ascii=False, indent=2))
        return 0 if len(funde) <= args.schwelle else 1

    print(f"Tote Transaktionen: {len(funde)} (Schwelle: {args.schwelle})")
    zeigen = funde if args.liste else funde[:20]
    for fund in zeigen:
        print(f"  {fund['datei']}:{fund['zeile']}  except {fund['ausnahme']}")
        print(f"      {fund['grund']}")
    if not args.liste and len(funde) > len(zeigen):
        print(f"  … {len(funde) - len(zeigen)} weitere (--liste zeigt alle)")

    if len(funde) > args.schwelle:
        print(
            f"\nFEHLER: {len(funde)} Fundstellen ueber der Schwelle {args.schwelle}.\n"
            "Jede Stelle braucht rollback(), einen Savepoint (begin_nested) oder\n"
            "eine nutzersichtbare Fehlerantwort — ein Protokolleintrag genuegt nicht."
        )
        return 1

    print("OK — keine neue tote Transaktion.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
