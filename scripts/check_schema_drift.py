#!/usr/bin/env python3
"""Vergleicht eine Ziel-Datenbank mit einer frisch migrierten.

Warum
-----

``scripts/pruefstand_db.py`` liefert eine Datenbank, die genau dem entspricht,
was die Migrationen sagen. Es sagt aber nichts darueber, ob die **gewachsene**
Datenbank noch dazu passt. Genau diese Luecke verdeckte am 29.09.2026
neunundfuenfzig rote Tests: Die Entwicklungsdatenbank hatte Fremdschluessel und
Pruefbedingungen **verloren** und Spalten und Tabellen **gewonnen**, die keine
Migration anlegt. Beides blieb unsichtbar, bis CI auf einer frischen Datenbank
lief.

Dieses Skript raet nicht, sondern stellt gegenueber. Verglichen wird je Schema:

- Tabellen
- Spalten mit Datentyp, Laenge/Genauigkeit und Nullbarkeit
- Fremdschluessel
- CHECK-Bedingungen
- UNIQUE-Bedingungen
- Indizes

Ausgabe je Fund: **fehlt** (in der Ziel-Datenbank nicht vorhanden),
**zusaetzlich** (dort, aber nicht im Migrationsstand) oder **anders**.

Die drei Entscheidungen
----------------------

Ein Fund ist kein Fehler, sondern eine Frage. Es gibt genau drei Antworten,
und sie fuehren zu verschiedenen Massnahmen:

(a) **Die Migration fehlt, der Code braucht die Spalte.** → Migration
    schreiben. So entstanden am 29.09. ``verkauf_fehlende_spalten_20260929``
    und ``lieferschein_status_bedingung_20260929``.
(b) **Die Dev-Datenbank ist verbastelt.** → Reparaturskript fuer die
    Dev-Datenbank, **keine** Migration. Eine Migration wuerde den Fehler in
    jede Installation tragen.
(c) **Die Spalte ist ungenutzt.** → dokumentieren, nicht still loeschen. Ein
    stilles DROP verliert Daten, deren Zweck niemand mehr kennt.

Aufruf
------

    # Die Entwicklungsdatenbank gegen den Migrationsstand
    python scripts/check_schema_drift.py

    # Ausdruecklich
    python scripts/check_schema_drift.py --ziel "$DATABASE_URL" \\
                                         --referenz "$TEST_DATABASE_URL"

    python scripts/check_schema_drift.py --json
    python scripts/check_schema_drift.py --schema domain_crm domain_sales

Ohne ``--referenz`` wird ``TEST_DATABASE_URL`` benutzt, ohne ``--ziel``
``DATABASE_URL``. Die Referenz muss frisch migriert sein
(``python scripts/pruefstand_db.py``); ist sie es nicht, vergleicht das Skript
zwei gewachsene Staende und sagt wenig.

Der Exitcode ist 1, sobald es Funde gibt — aber **nicht** als Ratsche gedacht:
Der Abstand zwischen einer gewachsenen und einer frischen Datenbank ist eine
Bestandsaufnahme, keine Regressionsschwelle. Deshalb laeuft das Skript nicht in
CI, sondern von Hand.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

# ── Die Abfragen: nur Lesen aus den Katalogen ──────────────────────────

SPALTEN_SQL = """
SELECT table_schema, table_name, column_name, data_type,
       coalesce(character_maximum_length, numeric_precision, -1) AS laenge,
       coalesce(numeric_scale, -1) AS skala,
       is_nullable, column_default
FROM information_schema.columns
WHERE table_schema = ANY(:schemata)
"""

BEDINGUNGEN_SQL = """
SELECT n.nspname AS schema, c.relname AS tabelle, con.conname AS name,
       con.contype AS art, pg_get_constraintdef(con.oid) AS definition
FROM pg_constraint con
JOIN pg_class c ON c.oid = con.conrelid
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname = ANY(:schemata)
"""

INDIZES_SQL = """
SELECT schemaname AS schema, tablename AS tabelle, indexname AS name, indexdef AS definition
FROM pg_indexes
WHERE schemaname = ANY(:schemata)
"""

SCHEMATA_SQL = """
SELECT nspname FROM pg_namespace
WHERE nspname NOT LIKE 'pg_%' AND nspname <> 'information_schema'
ORDER BY nspname
"""


# ── Die Vergleichslogik: reine Funktionen, ohne Datenbank ──────────────


def spalten_schluessel(zeile: dict) -> tuple[str, str, str]:
    return (zeile["table_schema"], zeile["table_name"], zeile["column_name"])


def spalten_form(zeile: dict) -> dict:
    """Die Eigenschaften einer Spalte, auf die es beim Vergleich ankommt.

    Der Vorgabewert (``column_default``) bleibt bewusst aussen vor: Er
    unterscheidet sich zwischen Staenden auch dann, wenn beide richtig sind
    (etwa ``nextval`` mit unterschiedlichen Sequenznamen), und ein Unterschied
    dort aendert am Vertrag der Spalte nichts.
    """
    return {
        "typ": zeile["data_type"],
        "laenge": zeile["laenge"],
        "skala": zeile["skala"],
        "nullbar": zeile["is_nullable"],
    }


def vergleiche_spalten(ziel: list[dict], referenz: list[dict]) -> list[dict]:
    z = {spalten_schluessel(r): spalten_form(r) for r in ziel}
    r = {spalten_schluessel(x): spalten_form(x) for x in referenz}
    funde: list[dict] = []

    for schluessel in sorted(set(r) - set(z)):
        funde.append({
            "art": "spalte", "befund": "fehlt",
            "wo": ".".join(schluessel), "referenz": r[schluessel], "ziel": None,
        })
    for schluessel in sorted(set(z) - set(r)):
        funde.append({
            "art": "spalte", "befund": "zusaetzlich",
            "wo": ".".join(schluessel), "referenz": None, "ziel": z[schluessel],
        })
    for schluessel in sorted(set(z) & set(r)):
        if z[schluessel] != r[schluessel]:
            unterschiede = {
                feld: {"ziel": z[schluessel][feld], "referenz": r[schluessel][feld]}
                for feld in r[schluessel]
                if z[schluessel][feld] != r[schluessel][feld]
            }
            funde.append({
                "art": "spalte", "befund": "anders",
                "wo": ".".join(schluessel), "unterschiede": unterschiede,
            })
    return funde


#: Wie Postgres die Bedingungsarten abkuerzt.
ARTEN = {"f": "fremdschluessel", "c": "check", "u": "unique", "p": "primaerschluessel"}


def vergleiche_bedingungen(ziel: list[dict], referenz: list[dict]) -> list[dict]:
    """Bedingungen werden ueber ihre **Definition** verglichen, nicht ueber den Namen.

    Ein automatisch erzeugter Name (``customers_pkey1``) unterscheidet sich
    zwischen Staenden, ohne dass sich etwas geaendert haette. Die Definition
    (``PRIMARY KEY (id)``) ist die Aussage, auf die es ankommt.
    """
    def form(zeilen: list[dict]) -> dict[tuple, str]:
        return {
            (z["schema"], z["tabelle"], ARTEN.get(z["art"], z["art"]), z["definition"]): z["name"]
            for z in zeilen
        }

    z, r = form(ziel), form(referenz)
    funde: list[dict] = []
    for schluessel in sorted(set(r) - set(z)):
        schema, tabelle, art, definition = schluessel
        funde.append({
            "art": art, "befund": "fehlt",
            "wo": f"{schema}.{tabelle}", "definition": definition, "name": r[schluessel],
        })
    for schluessel in sorted(set(z) - set(r)):
        schema, tabelle, art, definition = schluessel
        funde.append({
            "art": art, "befund": "zusaetzlich",
            "wo": f"{schema}.{tabelle}", "definition": definition, "name": z[schluessel],
        })
    return funde


def vergleiche_indizes(ziel: list[dict], referenz: list[dict]) -> list[dict]:
    def form(zeilen: list[dict]) -> dict[tuple, str]:
        # Der Indexname steckt in der Definition; fuer den Vergleich wird er
        # herausgenommen, damit ein anderer Name nicht als Unterschied gilt.
        ergebnis = {}
        for z in zeilen:
            definition = z["definition"]
            marke = " ON "
            if marke in definition:
                definition = "INDEX" + definition[definition.index(marke):]
            ergebnis[(z["schema"], z["tabelle"], definition)] = z["name"]
        return ergebnis

    z, r = form(ziel), form(referenz)
    funde: list[dict] = []
    for schluessel in sorted(set(r) - set(z)):
        schema, tabelle, definition = schluessel
        funde.append({
            "art": "index", "befund": "fehlt",
            "wo": f"{schema}.{tabelle}", "definition": definition, "name": r[schluessel],
        })
    for schluessel in sorted(set(z) - set(r)):
        schema, tabelle, definition = schluessel
        funde.append({
            "art": "index", "befund": "zusaetzlich",
            "wo": f"{schema}.{tabelle}", "definition": definition, "name": z[schluessel],
        })
    return funde


def vergleiche_tabellen(ziel: list[dict], referenz: list[dict]) -> list[dict]:
    z = {(r["table_schema"], r["table_name"]) for r in ziel}
    r = {(x["table_schema"], x["table_name"]) for x in referenz}
    funde: list[dict] = []
    for schluessel in sorted(r - z):
        funde.append({"art": "tabelle", "befund": "fehlt", "wo": ".".join(schluessel)})
    for schluessel in sorted(z - r):
        funde.append({"art": "tabelle", "befund": "zusaetzlich", "wo": ".".join(schluessel)})
    return funde


def vergleiche(ziel: dict[str, list[dict]], referenz: dict[str, list[dict]]) -> list[dict]:
    """Der ganze Vergleich. Nimmt Katalogauszuege, gibt Funde zurueck.

    Tabellen zuerst: Fehlt eine Tabelle, sind ihre Spalten kein eigener Fund —
    sonst ertraenkt eine fehlende Tabelle mit dreissig Spalten die Liste.
    """
    funde = vergleiche_tabellen(ziel["spalten"], referenz["spalten"])
    betroffene = {f["wo"] for f in funde}

    def ohne_ganze_tabellen(liste: list[dict]) -> list[dict]:
        return [
            f for f in liste
            if not any(f["wo"].startswith(t + ".") or f["wo"] == t for t in betroffene)
        ]

    funde += ohne_ganze_tabellen(
        vergleiche_spalten(ziel["spalten"], referenz["spalten"])
    )
    funde += ohne_ganze_tabellen(
        vergleiche_bedingungen(ziel["bedingungen"], referenz["bedingungen"])
    )
    funde += ohne_ganze_tabellen(
        vergleiche_indizes(ziel["indizes"], referenz["indizes"])
    )
    return funde


# ── Der Datenbankzugriff ───────────────────────────────────────────────


def lies_katalog(url: str, schemata: list[str]) -> dict[str, list[dict]]:
    from sqlalchemy import create_engine, text

    engine = create_engine(url)
    with engine.connect() as verbindung:
        if not schemata:
            schemata = [r[0] for r in verbindung.execute(text(SCHEMATA_SQL))]
        param = {"schemata": schemata}
        return {
            "schemata": schemata,
            "spalten": [dict(r) for r in verbindung.execute(
                text(SPALTEN_SQL).bindparams(**param)).mappings()],
            "bedingungen": [dict(r) for r in verbindung.execute(
                text(BEDINGUNGEN_SQL).bindparams(**param)).mappings()],
            "indizes": [dict(r) for r in verbindung.execute(
                text(INDIZES_SQL).bindparams(**param)).mappings()],
        }


def _ausgeben(funde: list[dict]) -> None:
    from collections import Counter

    print(f"Schema-Abweichungen: {len(funde)}\n")
    zaehler = Counter((f["art"], f["befund"]) for f in funde)
    for (art, befund), anzahl in sorted(zaehler.items()):
        print(f"  {anzahl:5d}  {art:20s} {befund}")
    print()

    for befund in ("fehlt", "zusaetzlich", "anders"):
        teil = [f for f in funde if f["befund"] == befund]
        if not teil:
            continue
        titel = {
            "fehlt": "FEHLT in der Ziel-Datenbank (der Migrationsstand hat es)",
            "zusaetzlich": "ZUSAETZLICH in der Ziel-Datenbank (keine Migration legt es an)",
            "anders": "ANDERS",
        }[befund]
        # Reines ASCII: Kastenzeichen brechen auf einer cp1252-Konsole.
        print(f"--- {titel} ---")
        for f in teil:
            zusatz = f.get("definition") or f.get("unterschiede") or ""
            if isinstance(zusatz, dict):
                zusatz = ", ".join(
                    f"{k}: {v['ziel']} statt {v['referenz']}" for k, v in zusatz.items()
                )
            print(f"  [{f['art']}] {f['wo']}  {zusatz}")
        print()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--ziel", default=os.environ.get("DATABASE_URL"))
    parser.add_argument("--referenz", default=os.environ.get("TEST_DATABASE_URL"))
    parser.add_argument("--schema", nargs="*", default=[])
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if not args.ziel:
        raise SystemExit("Keine Ziel-Datenbank: --ziel oder DATABASE_URL setzen.")
    if not args.referenz:
        raise SystemExit(
            "Keine Referenz: --referenz oder TEST_DATABASE_URL setzen.\n"
            "Die Referenz muss frisch migriert sein: python scripts/pruefstand_db.py"
        )
    if args.ziel == args.referenz:
        raise SystemExit(
            "Ziel und Referenz sind dieselbe Datenbank — der Vergleich waere leer."
        )

    ziel = lies_katalog(args.ziel, list(args.schema))
    referenz = lies_katalog(args.referenz, list(args.schema))
    funde = vergleiche(ziel, referenz)

    if args.json:
        print(json.dumps(funde, ensure_ascii=False, indent=2, default=str))
    else:
        _ausgeben(funde)
        if funde:
            print(
                "Jeder Fund ist eine Frage mit drei moeglichen Antworten:\n"
                "  (a) Die Migration fehlt, der Code braucht es  -> Migration schreiben\n"
                "  (b) Die Dev-Datenbank ist verbastelt          -> Reparaturskript, KEINE Migration\n"
                "  (c) Ungenutzt                                 -> dokumentieren, nicht still loeschen\n"
                "Einordnung je Fund: docs/quality-assurance/schema-drift-2026-09-30.md"
            )

    return 1 if funde else 0


if __name__ == "__main__":
    raise SystemExit(main())
