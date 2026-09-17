#!/usr/bin/env python3
"""Liest ein Endpunkt eine Tabelle, die es nicht gibt?

Die dritte Ebene
----------------

Drei Gates, drei Ebenen desselben stillen Fehlers:

1. `check_frontend_api_calls.py` — ruft die Maske eine Route auf, die es gibt?
2. `check_field_contracts.py` — spricht die Antwort die Sprache der Maske?
3. **dieses hier** — liest der Endpunkt eine Tabelle, die es gibt?

Die dritte ist die leiseste. Ein `SELECT` auf eine fehlende Tabelle wirft, das
`except` faengt, und die Maske zeigt **0,00** oder eine leere Liste. Eine Null
sieht aus wie ein Ergebnis, nicht wie ein Fehler — so meldete die
Liquiditaetssicht monatelang „nichts offen", waehrend 18.000 EUR offen waren.

Lebend und ruhend
-----------------

Getrennt gezaehlt wird, ob die betroffene Datei ueberhaupt eine Route hat, die
eine Maske oder das Frontend aufruft:

- **lebend** — jemand sieht das Ergebnis. Diese Zahl ist die dringende.
- **ruhend** — Code ohne Weg dorthin. Ob er gebaut oder geloescht gehoert, ist
  eine Produktentscheidung, keine Aufraeumarbeit.

Aufruf:  python scripts/check_table_references.py [--list]
"""

from __future__ import annotations

import argparse
import collections
import os
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

#: Stand 2026-09-17 nach den Verweisfixes (Einfuehrung: 29 / 23).
#: Beide Zahlen duerfen sinken, nicht steigen.
BASELINE_LEBEND = 28
BASELINE_RUHEND = 19

ENDPUNKTE = pathlib.Path("app/api/v1/endpoints")
FRONTEND = pathlib.Path("packages/frontend-web/src")

_TABELLE = re.compile(r"\b(?:FROM|JOIN|INTO|UPDATE)\s+(domain_[a-z_]+\.[a-z_]+)", re.IGNORECASE)
_FE_PFAD = re.compile(r"['\"`](/api/v1/[^'\"`\s]*)['\"`]")


def _tabellen_je_datei() -> dict[str, set[str]]:
    gefunden: dict[str, set[str]] = {}
    for datei in ENDPUNKTE.glob("*.py"):
        text_ = datei.read_text(encoding="utf-8", errors="ignore")
        treffer = {t.lower() for t in _TABELLE.findall(text_)}
        if treffer:
            gefunden[datei.name] = treffer
    return gefunden


def _vorhandene_tabellen() -> set[str]:
    from sqlalchemy import create_engine, text

    url = os.environ.get(
        "DATABASE_URL", "postgresql://valeo_dev:valeo_dev_2024@127.0.0.1:5432/valeo_neuro_erp"
    )
    with create_engine(url).connect() as verbindung:
        zeilen = verbindung.execute(
            text(
                "SELECT table_schema, table_name FROM information_schema.tables "
                "WHERE table_schema LIKE 'domain%'"
            )
        ).fetchall()
    return {f"{z[0]}.{z[1]}" for z in zeilen}


def _erreichbare_dateien() -> set[str]:
    """Dateien, deren Routen eine Maske oder das Frontend wirklich aufruft."""
    from app.core.screen_definitions import SCREEN_DEFINITION_BUILDERS, get_screen_definition
    from app.main import app

    modul_routen: dict[str, set[str]] = collections.defaultdict(set)
    for route in app.routes:
        modul = getattr(getattr(route, "endpoint", None), "__module__", "") or ""
        if ".endpoints." in modul:
            modul_routen[modul.split(".")[-1] + ".py"].add(getattr(route, "path", ""))

    gerufen: set[str] = set()
    for screen_id in SCREEN_DEFINITION_BUILDERS:
        screen = get_screen_definition(screen_id) or {}
        for quelle in screen.get("dataSources") or []:
            if quelle.get("endpoint"):
                gerufen.add(re.sub(r"\{[^}]+\}", "x", quelle["endpoint"].split("?")[0]))
    for datei in FRONTEND.rglob("*.ts*"):
        name = str(datei)
        if "__tests__" in name or ".gen." in name:
            continue
        for pfad in _FE_PFAD.findall(datei.read_text(encoding="utf-8", errors="ignore")):
            gerufen.add(re.sub(r"\$\{[^}]*\}", "x", pfad.split("?")[0]))

    erreichbar = set()
    for datei, pfade in modul_routen.items():
        for pfad in pfade:
            if re.sub(r"\{[^}]+\}", "x", pfad) in gerufen:
                erreichbar.add(datei)
                break
    return erreichbar


def pruefe() -> dict:
    je_datei = _tabellen_je_datei()
    vorhanden = _vorhandene_tabellen()
    erreichbar = _erreichbare_dateien()

    alle = {t for s in je_datei.values() for t in s}
    fehlend = sorted(t for t in alle if t not in vorhanden)

    lebend: list[tuple[str, list[str]]] = []
    ruhend: list[tuple[str, list[str]]] = []
    for tabelle in fehlend:
        dateien = sorted(d for d, ts in je_datei.items() if tabelle in ts)
        (lebend if any(d in erreichbar for d in dateien) else ruhend).append((tabelle, dateien))

    return {
        "referenziert": len(alle),
        "fehlend": fehlend,
        "lebend": lebend,
        "ruhend": ruhend,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()

    try:
        ergebnis = pruefe()
    except Exception as fehler:  # noqa: BLE001 — ohne Datenbank keine Aussage
        print(f"UEBERSPRUNGEN: keine Datenbank erreichbar ({fehler})")
        return 0

    print(
        f"Tabellenverweise: {ergebnis['referenziert']} referenziert, "
        f"{len(ergebnis['fehlend'])} fehlen — "
        f"{len(ergebnis['lebend'])} an lebenden Wegen (Schwelle {BASELINE_LEBEND}), "
        f"{len(ergebnis['ruhend'])} ruhend (Schwelle {BASELINE_RUHEND})."
    )

    if args.list:
        print("\nAn lebenden Wegen — jemand sieht das Ergebnis:")
        for tabelle, dateien in ergebnis["lebend"]:
            print(f"  {tabelle}  ({', '.join(dateien[:3])})")
        print("\nRuhend — kein Weg dorthin:")
        for tabelle, dateien in ergebnis["ruhend"]:
            print(f"  {tabelle}  ({', '.join(dateien[:3])})")

    schlecht = False
    if len(ergebnis["lebend"]) > BASELINE_LEBEND:
        print("\nFEHLER: Neue fehlende Tabelle an einem lebenden Weg.")
        schlecht = True
    if len(ergebnis["ruhend"]) > BASELINE_RUHEND:
        print("\nFEHLER: Neue fehlende Tabelle in ruhendem Code.")
        schlecht = True
    if schlecht:
        print(
            "        Entweder die Tabelle bauen oder den Verweis korrigieren —\n"
            "        ein gefangener Fehler wird in der Maske zu einer Null."
        )
        return 1

    print("OK: keine neuen Verweise ins Leere.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
