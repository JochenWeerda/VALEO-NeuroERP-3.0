#!/usr/bin/env python3
"""Ruft das Frontend Endpunkte auf, die es nicht gibt?

Der Fehler, der nicht auffaellt
-------------------------------

Ein Aufruf an eine nicht existierende Route ergibt einen 404. Steht darum ein
``catch`` mit leerer Liste — und das ist im Frontend die Regel, nicht die
Ausnahme — dann zeigt die Maske eine **leere Liste** statt eines Fehlers. So
sah die Faktura-Liste monatelang aus, als haette dieses Haus keine Rechnungen
(`GET /sales/invoices` existierte nicht), und die Lieferliste rief
`/sales/deliveries` auf, waehrend der Beleg `/sales/delivery-notes` heisst.

Dieses Skript haelt jeden Aufruf im Frontend gegen die echten Routen der App.

Was es **nicht** kann
---------------------

Zusammengesetzte Pfade (``${BASE}/feeds``) loest es nicht auf; gezaehlt werden
nur Zeilen, die selbst einen Aufruf absetzen (``apiClient.get`` und
Verwandte, ``fetch(``) und dabei einen literalen ``/api/v1``-Pfad tragen.
Platzhalter (``${id}``) werden zu einem Segment. Ein Treffer ist damit ein
starker Hinweis, kein Beweis — und eine leere Liste ist kein Freibrief.

Aufruf:  python scripts/check_frontend_api_calls.py [--threshold N] [--list]
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys

# Das Skript laeuft aus dem Repo-Wurzelverzeichnis; die App liegt daneben.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

FRONTEND = pathlib.Path("packages/frontend-web/src")
#: Stand bei Einfuehrung des Gates. Die Zahl darf sinken, nicht steigen.
BASELINE = 110

_PFAD = re.compile(r"['\"`](/api/v1/[^'\"`\s]*)['\"`]")
_AUFRUF = re.compile(r"apiClient\.(get|post|put|patch|delete)|fetch\(")


def _route_muster() -> list[re.Pattern[str]]:
    from app.main import app

    muster: list[re.Pattern[str]] = []
    for route in app.routes:
        pfad = getattr(route, "path", "")
        if not pfad.startswith("/api/"):
            continue
        ausdruck = re.escape(pfad)
        ausdruck = re.sub(r"\\\{[^}]*:path\\\}", ".+", ausdruck)
        ausdruck = re.sub(r"\\\{[^}]*\\\}", "[^/]+", ausdruck)
        muster.append(re.compile("^" + ausdruck + "/?$"))
    return muster


def _vereinfacht(endpunkt: str) -> str:
    """Template-Literale und Parameter auf je ein Segment reduzieren."""
    pfad = re.sub(r"\$\{[^}]*\}", "x", endpunkt)
    pfad = re.sub(r"\{[^}]+\}", "x", pfad)
    return pfad.split("?")[0].rstrip("/")


def finde_tote_aufrufe() -> dict[str, list[str]]:
    muster = _route_muster()

    def erreichbar(pfad: str) -> bool:
        return any(m.match(pfad) or m.match(pfad + "/") for m in muster)

    fund: dict[str, list[str]] = {}
    for datei in FRONTEND.rglob("*.ts*"):
        name = str(datei)
        if "__tests__" in name or ".gen." in name:
            continue
        try:
            zeilen = datei.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue
        for nummer, zeile in enumerate(zeilen, start=1):
            if not _AUFRUF.search(zeile):
                continue
            for treffer in _PFAD.findall(zeile):
                pfad = _vereinfacht(treffer)
                if not erreichbar(pfad):
                    stelle = name.split("src", 1)[-1].lstrip("\\/") + f":{nummer}"
                    fund.setdefault(pfad, []).append(stelle)
    return fund


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold", type=int, default=BASELINE)
    parser.add_argument("--list", action="store_true", help="alle Fundstellen ausgeben")
    args = parser.parse_args()

    fund = finde_tote_aufrufe()
    print(f"Frontend-Aufrufe ohne passende Route: {len(fund)} (Schwelle: {args.threshold})")

    if args.list:
        for pfad in sorted(fund):
            print(f"  {pfad}")
            for stelle in sorted(fund[pfad])[:5]:
                print(f"      {stelle}")

    if len(fund) > args.threshold:
        print(
            "FEHLER: Es sind neue Aufrufe auf nicht existierende Routen dazugekommen.\n"
            "        Entweder den Pfad korrigieren oder den Endpunkt bauen — ein 404 im\n"
            "        catch sieht in der Maske aus wie 'keine Daten'."
        )
        return 1
    print("OK: keine neuen toten Aufrufe.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
