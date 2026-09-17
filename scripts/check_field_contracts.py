#!/usr/bin/env python3
"""Spricht der Endpunkt die Sprache der Maske?

Der Fehler hinter dem Fehler
----------------------------

Dass eine Route existiert, prueft `check_frontend_api_calls.py` und
`tests/test_mask_endpoint_inventory.py`. Beide sagen nichts darueber, ob die
**Schluessel** stimmen. Genau daran sind acht Masken gescheitert: Der Endpunkt
antwortete mit 200, die Maske fragte nach `beleg_nr`, geliefert wurde
`rechnungsnr` — und der Kopf blieb leer. Leer sieht aus wie „nichts erfasst".

Dieses Skript haelt die Feldschluessel jeder ScreenDefinition gegen die
Antwortschemata der Endpunkte, die sie liest.

Kopf **und** Zeile
------------------

Geprueft werden die Kopffelder einer Maske gegen die ``entity``-Quelle **und**
die Tabellenspalten gegen die Zeilenform ihrer Quelle. Die Spalten sind die
groessere Haelfte (305 gegen 204) und haben dasselbe Versagen: Eine Spalte mit
falschem Schluessel bleibt leer, und leer sieht aus wie „nichts erfasst".

Eine Zeilenform ist lesbar, wenn die Antwort eine Liste typisierter Zeilen ist
(``list[ZeileOut]``) oder eine Seiten-Huelle mit typisiertem ``items``. Wo die
Zeile nicht deklariert ist, zaehlt die Quelle als **nicht pruefbar** — dieselbe
Ratsche wie beim Kopf.

Was es prueft und was nicht
---------------------------

Geprueft wird gegen das **deklarierte** Antwortschema aus dem OpenAPI-Vertrag.
Wo ein Endpunkt seine Antwort nicht typisiert (``extra="allow"`` ohne Felder,
rohe ``dict``-Rueckgaben), kann das Skript nichts sagen — solche Quellen
erscheinen als **nicht pruefbar** und werden gezaehlt. Diese Zahl ist die
eigentliche Aussage: Sie sagt, wie viel Maskenflaeche auf ungetypten Antworten
steht.

Aufruf:  python scripts/check_field_contracts.py [--list] [--threshold N]
"""

from __future__ import annotations

import argparse
import difflib
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

#: Stand bei Einfuehrung. Abweichungen duerfen nicht zunehmen.
BASELINE = 0


def _spec():
    from app.main import app

    return app.openapi()


def _operation(spec: dict, endpunkt: str) -> dict | None:
    """Die GET-Operation zu einem Endpunkt — Parameter tolerant verglichen.

    Mehrere OpenAPI-Pfade koennen denselben konkreten Pfad matchen
    (``{item_id}`` neben ``{misch_id}``). Ohne GET (nur DELETE) wird
    uebersprungen, sonst waere der Kopf unpruefbar obwohl ein GET existiert.
    """
    konkret = re.sub(r"\{[^}]+\}", "x", endpunkt.split("?")[0]).rstrip("/")
    treffer: list[tuple[str, dict]] = []
    for pfad, operationen in spec["paths"].items():
        muster = re.escape(pfad)
        muster = re.sub(r"\\\{[^}]*:path\\\}", ".+", muster)
        muster = re.sub(r"\\\{[^}]*\\\}", "[^/]+", muster)
        if re.match("^" + muster + "/?$", konkret):
            get_op = operationen.get("get")
            if get_op:
                treffer.append((pfad, get_op))
    if not treffer:
        return None
    # Der **woertlichste** Pfad gewinnt, nicht der laengste: Ein Sammelpfad wie
    # `/sales/{doc_type}` ist als Zeichenkette laenger als `/sales/invoices`,
    # meint aber etwas anderes. Erst wenige Platzhalter, dann laengerer Pfad.
    treffer.sort(key=lambda item: (item[0].count("{"), -len(item[0])))
    return treffer[0][1]


def _komponente(spec: dict, schema: dict) -> dict:
    """Folgt einem ``$ref``, sonst bleibt das Schema selbst."""
    referenz = schema.get("$ref")
    if not referenz:
        return schema
    return (spec.get("components", {}).get("schemas") or {}).get(referenz.split("/")[-1]) or {}


def _objektfelder(schema: dict) -> set[str] | None:
    """Feldnamen eines Objekts — oder None, wenn es nichts zusagt."""
    eigenschaften = schema.get("properties") or {}
    # extra="allow" ohne Modell: Platzhalter, kein Vertrag.
    if schema.get("additionalProperties") is True and len(eigenschaften) <= 2:
        return None
    return set(eigenschaften) or None


def _eigenschaften(spec: dict, operation: dict | None) -> set[str] | None:
    """Die Feldnamen der Antwort — oder None, wenn sie nicht deklariert sind."""
    if not operation:
        return None
    inhalt = ((operation.get("responses") or {}).get("200") or {}).get("content") or {}
    schema = (inhalt.get("application/json") or {}).get("schema") or {}
    if schema.get("type") == "array":
        schema = schema.get("items") or {}
    komponente = _komponente(spec, schema)
    eigenschaften = komponente.get("properties") or {}

    if komponente.get("additionalProperties") is True and len(eigenschaften) <= 2:
        return None
    # Eine Huelle mit `items` ist eine Seite, keine Zeile: Dann steckt die
    # Zeilenform im Listeneintrag, und die ist hier meist nicht deklariert.
    if set(eigenschaften) and set(eigenschaften) <= {"items", "total", "page", "size", "pages",
                                                     "has_next", "has_prev", "limit", "offset"}:
        return None
    return set(eigenschaften) or None


def _zeilenform(spec: dict, operation: dict | None) -> set[str] | None:
    """Die Feldnamen **einer Zeile** — oder None, wenn sie nicht deklariert ist.

    Zwei Formen kommen vor: eine Liste typisierter Zeilen und eine Seiten-Huelle
    mit typisiertem ``items``. Alles andere sagt ueber die Zeile nichts.
    """
    if not operation:
        return None
    inhalt = ((operation.get("responses") or {}).get("200") or {}).get("content") or {}
    schema = (inhalt.get("application/json") or {}).get("schema") or {}

    if schema.get("type") == "array":
        return _objektfelder(_komponente(spec, schema.get("items") or {}))

    if not schema.get("$ref"):
        return None
    huelle = _komponente(spec, schema)
    items = _komponente(spec, (huelle.get("properties") or {}).get("items") or {})
    if items.get("type") == "array" or "items" in items:
        return _objektfelder(_komponente(spec, items.get("items") or {}))
    if items.get("properties"):
        return _objektfelder(items)
    return None


def pruefe() -> dict:
    from app.core.screen_definitions import SCREEN_DEFINITION_BUILDERS, get_screen_definition

    spec = _spec()
    abweichungen: list[dict] = []
    nicht_pruefbar: list[str] = []
    zeilen_nicht_pruefbar: list[str] = []
    geprueft = 0

    for screen_id in sorted(SCREEN_DEFINITION_BUILDERS):
        screen = get_screen_definition(screen_id)
        if screen is None or (screen.get("adapter") or {}).get("temporary"):
            continue

        quellen = {q.get("key"): q.get("endpoint") for q in screen.get("dataSources") or []}

        for tab in screen.get("tabs") or []:
            quelle = tab.get("dataSourceKey")
            felder = [f.get("key") for f in tab.get("fields") or [] if f.get("key")]
            if not quelle or not felder:
                continue
            endpunkt = quellen.get(quelle)
            if not endpunkt or not endpunkt.startswith("/api/"):
                continue

            vorhanden = _eigenschaften(spec, _operation(spec, endpunkt))
            if vorhanden is None:
                nicht_pruefbar.append(f"{screen_id}/{tab.get('key')} -> {endpunkt}")
                continue

            for feld in felder:
                geprueft += 1
                if feld in vorhanden:
                    continue
                vorschlag = difflib.get_close_matches(feld, sorted(vorhanden), n=1, cutoff=0.6)
                abweichungen.append(
                    {
                        "screen": screen_id,
                        "tab": tab.get("key"),
                        "feld": feld,
                        "endpunkt": endpunkt,
                        "vorschlag": vorschlag[0] if vorschlag else None,
                    }
                )

        # ── Tabellenspalten gegen die Zeilenform ───────────────────────────
        for tab in screen.get("tabs") or []:
            for tabelle in tab.get("tables") or []:
                spalten = [c.get("key") for c in tabelle.get("columns") or [] if c.get("key")]
                endpunkt = quellen.get(tabelle.get("dataSourceKey"))
                if not spalten or not endpunkt or not endpunkt.startswith("/api/"):
                    continue

                zeile = _zeilenform(spec, _operation(spec, endpunkt))
                if zeile is None:
                    zeilen_nicht_pruefbar.append(
                        f"{screen_id}/{tab.get('key')}/{tabelle.get('key')} -> {endpunkt}"
                    )
                    continue

                for spalte in spalten:
                    geprueft += 1
                    if spalte in zeile:
                        continue
                    vorschlag = difflib.get_close_matches(spalte, sorted(zeile), n=1, cutoff=0.6)
                    abweichungen.append(
                        {
                            "screen": screen_id,
                            "tab": f"{tab.get('key')}/{tabelle.get('key')}",
                            "feld": spalte,
                            "endpunkt": endpunkt,
                            "vorschlag": vorschlag[0] if vorschlag else None,
                        }
                    )

    return {
        "geprueft": geprueft,
        "abweichungen": abweichungen,
        "nicht_pruefbar": sorted(set(nicht_pruefbar)),
        "zeilen_nicht_pruefbar": sorted(set(zeilen_nicht_pruefbar)),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--threshold", type=int, default=BASELINE)
    parser.add_argument("--list", action="store_true")
    args = parser.parse_args()

    ergebnis = pruefe()
    print(
        f"Feldvertrag: {ergebnis['geprueft']} Felder gegen deklarierte Antworten geprueft, "
        f"{len(ergebnis['abweichungen'])} Abweichungen (Schwelle: {args.threshold}); "
        f"{len(ergebnis['nicht_pruefbar'])} Kopfquellen und "
        f"{len(ergebnis['zeilen_nicht_pruefbar'])} Tabellenquellen ohne deklarierte Form."
    )

    for eintrag in ergebnis["abweichungen"]:
        hinweis = f" — meinten Sie '{eintrag['vorschlag']}'?" if eintrag["vorschlag"] else ""
        print(f"  {eintrag['screen']}/{eintrag['tab']}: '{eintrag['feld']}' fehlt in der Antwort{hinweis}")
        print(f"      {eintrag['endpunkt']}")

    if args.list:
        print("\nKopfquellen ohne deklarierte Antwort:")
        for zeile in ergebnis["nicht_pruefbar"]:
            print(f"  {zeile}")
        print("\nTabellenquellen ohne deklarierte Zeilenform:")
        for zeile in ergebnis["zeilen_nicht_pruefbar"]:
            print(f"  {zeile}")

    if len(ergebnis["abweichungen"]) > args.threshold:
        print(
            "\nFEHLER: Die Maske fragt nach Feldern, die der Endpunkt nicht liefert.\n"
            "        Das ergibt kein 404, sondern leere Felder — und leer sieht aus\n"
            "        wie 'nichts erfasst'."
        )
        return 1
    print("OK: keine neuen Abweichungen zwischen Maske und Antwort.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
