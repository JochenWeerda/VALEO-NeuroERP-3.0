#!/usr/bin/env python3
"""Abbild der ScreenDefinition-Registry fuer das Frontend — die eine Quelle ist Python.

    python scripts/generate_screen_registry_snapshot.py           # schreiben
    python scripts/generate_screen_registry_snapshot.py --check   # pruefen (CI)

``app/core/screen_definitions*.py`` ist die kanonische Quelle der ScreenDefinitions.
Das JSON-Abbild und ``generate_capture_screens.py`` projizieren dieselben 31 verfassten
Definitionen fuer das Frontend. ``capture-screens-sync.test.ts`` vergleicht beide
Ausgaben ohne zugelassene Abweichungen. Beide Generatoren besitzen einen --check-Modus;
neue Masken lesen die Registry oder eine ihrer generierten Projektionen.

Der Agentenvertrag (``agentContract``) gehoert nicht ins Abbild: Er ist fuer den Server und die Agenten.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.screen_definitions import _SCREEN_DEFINITIONS  # noqa: E402

ZIEL = ROOT / "packages/frontend-web/src/masks/screen-registry.snapshot.json"

# Exportname in capture-screens.ts -> Kennung in der Registry.
EXPORTE: dict[str, str] = {
    "streckeStreckengeschaeftScreen": "strecke/streckengeschaeft",
    "versandAvisScreen": "versand/versand-avis",
    "streckeVorlaeufigScreen": "strecke/vorlaeufig",
    "streckeDispositionScreen": "strecke/disposition",
    "betriebsauftragScreen": "verkauf/betriebsauftrag",
    "nawaroLieferungenScreen": "strecke/nawaro-lieferungen",
    "qualitaetsAbweichungScreen": "strecke/qualitaets-abweichung",
    "fuhrparkUebersichtScreen": "fuhrpark/uebersicht",
    "streckeDokumenteDruckenScreen": "strecke/dokumente-drucken",
    "nawaroErnterklaerungScreen": "strecke/nawaro-ernterklaerung-drucken",
    "fuhrparkFahrzeugeScreen": "fuhrpark/fahrzeuge",
    "logistikFrachtbriefScreen": "logistik/frachtbrief",
    "logistikVerladungScreen": "logistik/verladung",
    "tourenplanungScreen": "logistik/tourenplanung",
    "transporteFahrerScreen": "transporte/fahrer",
    "tourFrachtArbeitsraumScreen": "logistik/tour-fracht-arbeitsraum",
    "frachttabellenScreen": "logistik/frachttabellen",
    "versandprofileScreen": "logistik/versandprofile",
    "fuhrparkTerminartenScreen": "fuhrpark/terminarten",
    "fuhrparkRechnungenScreen": "fuhrpark/rechnungen",
    "fuhrparkAusgehendeDokumenteScreen": "fuhrpark/ausgehende-dokumente",
    "fuhrparkFahrzeugStammScreen": "fuhrpark/fahrzeug-stamm",
    "personalQualifikationenScreen": "personal/qualifikationen",
    "personalOnboardingScreen": "personal/onboarding",
    "personalSchulungenScreen": "personal/schulungen",
    "personalBewerbungenScreen": "personal/bewerbungen",
    "personalBewerbungEinwilligungScreen": "personal/bewerbung-einwilligung",
    "personalEinwilligungserklaerungenScreen": "personal/einwilligungserklaerungen",
    "adminPostfaecherScreen": "admin/postfaecher",
    "salesGutschriftScreen": "sales/gutschrift",
    "financeSteuerschluesselScreen": "finance/steuerschluessel",
}


def abbild() -> str:
    screens = {}
    for kennung in sorted(set(EXPORTE.values())):
        # Die verfasste Definition. Beim Ausliefern ergaenzt der Server Abgeleitetes (Belegketten, Layoutvorgaben).
        definition = dict(_SCREEN_DEFINITIONS[kennung]())
        definition.pop("agentContract", None)
        screens[kennung] = definition
    daten = {
        "hinweis": "Erzeugt von scripts/generate_screen_registry_snapshot.py aus app/core/screen_definitions*.py. Nicht von Hand aendern.",
        "exports": dict(sorted(EXPORTE.items())),
        "screens": screens,
    }
    return json.dumps(daten, ensure_ascii=False, indent=1, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="nur pruefen, ob das Abbild aktuell ist")
    args = parser.parse_args()
    neu = abbild()
    if args.check:
        alt = ZIEL.read_text(encoding="utf-8").replace("\r\n", "\n") if ZIEL.exists() else ""
        if alt != neu:
            print(f"DRIFT: {ZIEL.relative_to(ROOT)} weicht ab — python scripts/generate_screen_registry_snapshot.py ausfuehren",
                  file=sys.stderr)
            return 1
        print(f"OK: {ZIEL.relative_to(ROOT)} ({len(EXPORTE)} Definitionen)")
        return 0
    ZIEL.write_text(neu, encoding="utf-8", newline="\n")
    print(f"Geschrieben: {ZIEL.relative_to(ROOT)} ({len(EXPORTE)} Definitionen)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
