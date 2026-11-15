"""Vitest- und Smoke-Faelle der Runtime46-Altlast: nur schrumpfen (Weg 2, 02.11.2026).

Seit ca50c46f7/deeb707b4 sind viele Seiten Native-Seiten; ihre alten Tests pruefen den Quelltext oder die Bedienung
der frueheren handgebauten Seite. Sie laufen als ``it.fails`` mit der Marke unten: solange die Seite nicht wieder
passt, sind sie gruen; passt sie, wird der Fall rot und die Marke muss weg. Neue Marken sind keine Ausnahme,
sondern ein neuer Fehler. Abbau: Studio-Umbau (Workboard STUDIO-UMBAU-RUNTIME46).
"""
from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKE = "// Runtime46-Altlast (STUDIO-UMBAU-RUNTIME46)"
HOECHSTENS = 131  # Stand 14.11.2026 (Klassen, Workflow, Sorten und Listen verhaltensgeprueft); nur senken
# E2E-Smoke: Faelle ohne echte Maske (fehlende Maske oder batch15-Platzhalter) laufen als test.fixme.
HOECHSTENS_SMOKE = 9  # Stand 03.11.2026 (Lagerbestand repariert); nur senken


def _marken(wurzel: str = "packages/frontend-web/src/__tests__") -> list[tuple[str, int, str]]:
    dateien = subprocess.run(["git", "ls-files", wurzel], capture_output=True, text=True, cwd=ROOT).stdout.split()
    funde = []
    for datei in dateien:
        zeilen = (ROOT / datei).read_text(encoding="utf-8", errors="ignore").splitlines()
        for i, zeile in enumerate(zeilen):
            if zeile.strip().startswith(MARKE):
                funde.append((datei, i + 1, zeilen[i + 1] if i + 1 < len(zeilen) else ""))
    return funde


def test_jede_marke_steht_vor_einem_it_fails():
    falsch = [(d, n) for d, n, folge in _marken() if not re.match(r"\s*(it|test)\.fails\(", folge)]
    assert not falsch, f"Marke ohne folgendes it.fails: {falsch}"


def test_altlast_schrumpft_nur():
    anzahl = len(_marken())
    assert anzahl <= HOECHSTENS, f"{anzahl} Runtime46-Altlastfaelle, hoechstens {HOECHSTENS}: neue Fehler nicht markieren"
    assert anzahl == HOECHSTENS, f"Altlast auf {anzahl} gesunken - bitte HOECHSTENS in diesem Test senken"


def test_smoke_altlast_schrumpft_nur():
    marken = _marken("playwright-tests/specs")
    falsch = [(d, n) for d, n, folge in marken if not re.match(r"\s*test\.fixme\(", folge)]
    assert not falsch, f"Smoke-Marke ohne folgendes test.fixme: {falsch}"
    assert len(marken) <= HOECHSTENS_SMOKE, f"{len(marken)} Smoke-Altlastfaelle, hoechstens {HOECHSTENS_SMOKE}"
    assert len(marken) == HOECHSTENS_SMOKE, f"Smoke-Altlast auf {len(marken)} gesunken - HOECHSTENS_SMOKE senken"
