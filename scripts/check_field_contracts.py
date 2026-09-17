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
    """Die GET-Operation zu einem Endpunkt — Parameter tolerant verglichen."""
    konkret = re.sub(r"\{[^}]+\}", "x", endpunkt.split("?")[0]).rstrip("/")
    for pfad, operationen in spec["paths"].items():
        muster = re.escape(pfad)
        muster = re.sub(r"\\\{[^}]*:path\\\}", ".+", muster)
        muster = re.sub(r"\\\{[^}]*\\\}", "[^/]+", muster)
        if re.match("^" + muster + "/?$", konkret):
            return operationen.get("get")
    return None


def _eigenschaften(spec: dict, operation: dict | None) -> set[str] | None:
    """Die Feldnamen der Antwort — oder None, wenn sie nicht deklariert sind."""
    if not operation:
        return None
    inhalt = ((operation.get("responses") or {}).get("200") or {}).get("content") or {}
    schema = (inhalt.get("application/json") or {}).get("schema") or {}
    if schema.get("type") == "array":
        schema = schema.get("items") or {}
    referenz = schema.get("$ref")
    if not referenz:
        return None
    name = referenz.split("/")[-1]
    komponente = (spec.get("components", {}).get("schemas") or {}).get(name) or {}
    eigenschaften = komponente.get("properties") or {}

    # Eine Huelle, die zusaetzliche Felder ausdruecklich zulaesst und selbst
    # kaum welche nennt, ist kein Vertrag, sondern ein Platzhalter
    # (`extra="allow"` ohne Modell). Daraus laesst sich **nicht** folgern, dass
    # ein Maskenfeld fehlt — nur, dass niemand es zugesagt hat.
    if komponente.get("additionalProperties") is True and len(eigenschaften) <= 2:
        return None
    # Eine Huelle mit `items` ist eine Seite, keine Zeile: Dann steckt die
    # Zeilenform im Listeneintrag, und die ist hier meist nicht deklariert.
    if set(eigenschaften) and set(eigenschaften) <= {"items", "total", "page", "size", "pages",
                                                     "has_next", "has_prev", "limit", "offset"}:
        return None
    return set(eigenschaften) or None


def pruefe() -> dict:
    from app.core.screen_definitions import SCREEN_DEFINITION_BUILDERS, get_screen_definition

    spec = _spec()
    abweichungen: list[dict] = []
    nicht_pruefbar: list[str] = []
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

    return {
        "geprueft": geprueft,
        "abweichungen": abweichungen,
        "nicht_pruefbar": sorted(set(nicht_pruefbar)),
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
        f"{len(ergebnis['nicht_pruefbar'])} Quellen ohne deklarierte Antwort."
    )

    for eintrag in ergebnis["abweichungen"]:
        hinweis = f" — meinten Sie '{eintrag['vorschlag']}'?" if eintrag["vorschlag"] else ""
        print(f"  {eintrag['screen']}/{eintrag['tab']}: '{eintrag['feld']}' fehlt in der Antwort{hinweis}")
        print(f"      {eintrag['endpunkt']}")

    if args.list:
        print("\nNicht pruefbar (Antwort ist nicht typisiert):")
        for zeile in ergebnis["nicht_pruefbar"]:
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
