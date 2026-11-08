"""Fachrollen: Was der Code verlangt, muss der Anmeldedienst vergeben koennen.

Die Wege pruefen Rollen wie ``FINANCE_BEARBEITEN`` oder ``KONTENPLAN_PFLEGE``. Eine Rolle, die es im
Anmeldedienst nicht gibt, kann niemand bekommen — der Weg ist dann fuer alle ausser ``admin`` zu.
Am 12.10.2026 verlangte der Code 34 Fachrollen; die Realm-Datei kannte keine davon.

Der Katalog ``config/keycloak/fachrollen.json`` ist die Liste, aus der der Anmeldedienst eingerichtet
wird. Dieses Skript haelt ihn am Code fest und zeigt, was dem Realm fehlt.

    python scripts/check_fachrollen.py            # Katalog aus dem Code neu schreiben (Beschreibungen bleiben)
    python scripts/check_fachrollen.py --check    # Exit 1, wenn Code und Katalog auseinanderlaufen
    python scripts/check_fachrollen.py --realm    # zeigt, welche Katalogrollen der Realm-Datei fehlen
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
KATALOG = REPO / "config" / "keycloak" / "fachrollen.json"
REALM = REPO / "config" / "keycloak" / "realm-export.json"
ROLLE = re.compile(r"""["']([A-Z][A-Z0-9]*_(?:LESEN|BEARBEITEN|ADMIN|LOESCHEN|PFLEGE))["']""")

BEREICH = {
    "AGRAR": "Agrar", "CRM": "Vertrieb und Kundenpflege", "EINKAUF": "Einkauf", "FINANCE": "Finanzbuchhaltung",
    "FUTTERMITTEL": "Futtermittel", "HARVEST": "Ernteannahme", "KONTRAKT": "Kontrakte", "LAGER": "Lager",
    "PERSONAL": "Personal", "QUALITAET": "Qualitaetssicherung", "SALES": "Verkauf", "SETTLEMENT": "Abrechnung",
    "KONTENPLAN": "Kontenplan", "KONTENRAHMEN": "Gemeinsamer Kontenrahmen",
}
STUFE = {
    "LESEN": "ansehen", "BEARBEITEN": "anlegen und aendern", "ADMIN": "leiten: freigeben, loeschen, abschliessen",
    "LOESCHEN": "loeschen", "PFLEGE": "pflegen (delegierbar, unabhaengig von der Leitungsrolle)",
}


def rollen_im_code() -> dict[str, list[str]]:
    """Rolle -> Dateien unter app/, die sie nennen."""
    gefunden: dict[str, set[str]] = {}
    for datei in sorted((REPO / "app").rglob("*.py")):
        try:
            text = datei.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for rolle in set(ROLLE.findall(text)):
            gefunden.setdefault(rolle, set()).add(datei.relative_to(REPO).as_posix())
    return {rolle: sorted(dateien) for rolle, dateien in sorted(gefunden.items())}


def beschreibung(rolle: str) -> str:
    bereich, _, stufe = rolle.rpartition("_")
    return f"{BEREICH.get(bereich, bereich.title())}: {STUFE[stufe]}"


def katalog_aus_code(bestehend: dict | None = None) -> dict:
    alt = {r["name"]: r for r in (bestehend or {}).get("rollen", [])}
    rollen = []
    for name in rollen_im_code():
        rollen.append({
            "name": name,
            "beschreibung": alt.get(name, {}).get("beschreibung") or beschreibung(name),
            **({"vertrag": alt[name]["vertrag"]} if "vertrag" in alt.get(name, {}) else {}),
        })
    return {
        "hinweis": (
            "Fachrollen, die der Code prueft. Erzeugt von scripts/check_fachrollen.py; Beschreibungen duerfen "
            "von Hand geschaerft werden und bleiben erhalten. Jede Rolle muss im Anmeldedienst als Realm-Rolle "
            "bestehen, sonst kann sie niemand bekommen. admin, manager und user sind keine Fachrollen und stehen "
            "hier nicht."
        ),
        "rollen": rollen,
        "grundrollen": (bestehend or {}).get("grundrollen", []),
    }


VERTRAGSFELDER = ("zweck", "personenkreis", "geltungsbereich", "erlaubt", "ausgeschlossen", "freigaben", "vergabe")


def vertragsfehler(katalog: dict, realm: dict | None = None) -> list[str]:
    """Beschreibungen sind pruefbare Grenzen, keine zusaetzliche Rechtequelle."""
    fehler = []
    namen = set()
    for rolle in [*katalog.get("rollen", []), *katalog.get("grundrollen", [])]:
        name = rolle.get("name", "")
        if not isinstance(name, str) or not name.strip() or name in namen:
            fehler.append("Fehlender oder doppelter Rollenname")
        namen.add(name)
        if not isinstance(rolle.get("beschreibung"), str) or not rolle["beschreibung"].strip():
            fehler.append(f"{name}: Beschreibung fehlt")
        vertrag = rolle.get("vertrag")
        if not isinstance(vertrag, dict):
            fehler.append(f"{name}: Rollenvertrag fehlt")
            continue
        for feld in VERTRAGSFELDER:
            wert = vertrag.get(feld)
            if not isinstance(wert, str) or not wert.strip():
                fehler.append(f"{name}: {feld} fehlt")
    if realm is not None:
        for rolle in realm.get("roles", {}).get("realm", []):
            if rolle["name"] not in namen:
                fehler.append(f"{rolle['name']}: Realm-Rolle ohne Beschreibungskontrakt")
    return fehler


def render(katalog: dict) -> str:
    return json.dumps(katalog, ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Fachrollen-Katalog am Code festhalten")
    parser.add_argument("--check", action="store_true", help="Exit 1 bei Abweichung zwischen Code und Katalog")
    parser.add_argument("--realm", action="store_true", help="Katalogrollen zeigen, die der Realm-Datei fehlen")
    args = parser.parse_args()

    bestehend = json.loads(KATALOG.read_text(encoding="utf-8")) if KATALOG.exists() else None
    soll = katalog_aus_code(bestehend)

    fehler = vertragsfehler(soll, json.loads(REALM.read_text(encoding="utf-8")))
    if fehler:
        print("\n".join(fehler), file=sys.stderr)
        return 1

    if args.realm:
        realm = {r["name"] for r in json.loads(REALM.read_text(encoding="utf-8")).get("roles", {}).get("realm", [])}
        fehlen = [r["name"] for r in soll["rollen"] if r["name"] not in realm]
        print(f"Katalog: {len(soll['rollen'])} Fachrollen. Realm-Datei kennt davon {len(soll['rollen']) - len(fehlen)}.")
        for name in fehlen:
            print(f"  fehlt im Realm: {name}")
        return 1 if fehlen else 0

    if args.check:
        if bestehend is None or render(bestehend) != render(soll):
            print("DRIFT: Fachrollen-Katalog nicht aktuell. Bitte 'python scripts/check_fachrollen.py' ausfuehren.",
                  file=sys.stderr)
            return 1
        print(f"OK: Fachrollen-Katalog aktuell ({len(soll['rollen'])} Rollen).")
        return 0

    KATALOG.write_text(render(soll), encoding="utf-8", newline="\n")
    print(f"Geschrieben: {KATALOG.relative_to(REPO).as_posix()} ({len(soll['rollen'])} Rollen).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
