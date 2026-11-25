#!/usr/bin/env python3
"""Domaenenabnahme (Fahrplan M4): Abnahmeblatt je Domaene aus Prozessliste und maschinellen Belegen.

    python scripts/domaenen_abnahme.py            # Blaetter und Uebersicht neu schreiben
    python scripts/domaenen_abnahme.py --check    # CI/vor_push: Blaetter aktuell und Regeln eingehalten

Quelle je Domaene ist ``docs/abnahme/domaenen/<id>.yaml``: die Prozessliste aus der L3-Referenz mit Zuordnung zu
VALEO-Routen, Rolle, Nachweisen, Status und Luecken. Das Skript ergaenzt die Belege aus dem Masken-Studio-Inventar
(Stufe je Route, generische Platzhaltermasken, Aktionen ohne CLI oder ohne Wirkung), sucht Demo- und Festwerte in
den Seitenquellen und schreibt ``<id>.md`` sowie die Uebersicht ``README.md``.

Regeln (``--check`` scheitert sonst):

- Jede genannte Route existiert im Inventar, jeder Nachweis als Datei.
- ``abgenommen`` nur mit Nachweis, ohne offene P0/P1-Luecke und ohne Route auf einer Platzhaltermaske.
- Luecken tragen eine Prioritaet P0 bis P3.

Eine generische Platzhaltermaske ist eine Listenmaske, deren Spalten nur aus Kennung, Name, Status und Datum bestehen
und die ausser dem CSV-Export keine Aktion hat. Die Stufe ``studio_versioniert`` sagt nichts ueber den fachlichen
Inhalt; am 23.11.2026 traf das unter anderem Zahlungsabgleich und Kassen-Tagesabschluss.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

BLAETTER = ROOT / "docs" / "abnahme" / "domaenen"
ROLLEN_RATSCHE = ROOT / "config" / "write_routes_without_roles.json"

STATUS = ("abgenommen", "teilweise", "fehlt")
PRIORITAETEN = ("P0", "P1", "P2", "P3")
GENERISCHE_SPALTEN = frozenset({"id", "name", "status", "datum", "updated_at", "created_at"})
#: Stichworte fuer Demo- und Festwerte in Seitenquellen (Fahrplan M4: "keine Demo- oder Festwerte").
FESTWERT = re.compile(r"\b(mock\w*|demo\w*|dummy|fake\w*|lorem|placeholder[A-Z]\w*|beispieldaten|testdaten)\b", re.I)


@dataclass
class Pruefung:
    fehler: list[str] = field(default_factory=list)

    def melde(self, text: str) -> None:
        self.fehler.append(text)


# ------------------------------------------------------------------------------------------------- reine Regeln

def ist_platzhalter(definition: dict) -> bool:
    """Listenmaske, die nur Kennung/Name/Status/Datum zeigt und ausser dem Export nichts kann."""
    tabellen = definition.get("tables") or []
    if definition.get("mode") != "list" or not tabellen:
        return False
    spalten = {spalte.get("key") for tabelle in tabellen for spalte in tabelle.get("columns") or []}
    zeilenaktionen = [aktion for tabelle in tabellen for aktion in tabelle.get("rowActions") or []]
    aktionen = {aktion.get("key") for aktion in definition.get("actions") or []}
    return bool(spalten) and spalten <= GENERISCHE_SPALTEN and aktionen <= {"export"} and not zeilenaktionen


def nachweis_pfad(nachweis: str) -> str:
    return nachweis.split("::", 1)[0]


def pruefe_prozess(prozess: dict, routen: dict[str, dict], platzhalter: set[str], pruefung: Pruefung) -> None:
    pid = prozess.get("id", "?")
    status = prozess.get("status")
    if status not in STATUS:
        pruefung.melde(f"{pid}: Status {status!r} unbekannt ({', '.join(STATUS)})")
    for route in prozess.get("routen") or []:
        if route not in routen:
            pruefung.melde(f"{pid}: Route {route!r} nicht im Masken-Inventar")
    for nachweis in prozess.get("nachweise") or []:
        if not (ROOT / nachweis_pfad(nachweis)).is_file():
            pruefung.melde(f"{pid}: Nachweis {nachweis!r} existiert nicht")
    for luecke in prozess.get("luecken") or []:
        if luecke.get("prio") not in PRIORITAETEN:
            pruefung.melde(f"{pid}: Luecke ohne Prioritaet P0-P3: {luecke.get('text', '')[:60]}")
    if status == "abgenommen":
        if not prozess.get("nachweise"):
            pruefung.melde(f"{pid}: abgenommen ohne Nachweis")
        if any(luecke.get("prio") in ("P0", "P1") for luecke in prozess.get("luecken") or []):
            pruefung.melde(f"{pid}: abgenommen trotz offener P0/P1-Luecke")
        hohl = [r for r in prozess.get("routen") or [] if set(routen.get(r, {}).get("screen_ids", [])) & platzhalter]
        if hohl:
            pruefung.melde(f"{pid}: abgenommen, aber Platzhaltermaske hinter {', '.join(hohl)}")


# ------------------------------------------------------------------------------------------------- Erhebung

def erhebe() -> dict:
    import mask_studio_inventory as inventar

    definitionen = inventar._definitions()
    inv = inventar.inventory()
    return {
        "routen": {zeile["route"]: zeile for zeile in inv["seiten"]},
        "aktionen": inv["aktionen"],
        "definitionen": {sid: {"domain": d.get("domain"), "title": d.get("title"), "platzhalter": ist_platzhalter(d)}
                         for sid, d in definitionen.items()},
    }


def festwerte(dateien: list[str]) -> list[tuple[str, int, str]]:
    treffer = []
    for datei in sorted(set(dateien)):
        pfad = ROOT / datei
        if not pfad.is_file():
            continue
        for nummer, zeile in enumerate(pfad.read_text(encoding="utf-8", errors="replace").splitlines(), start=1):
            if FESTWERT.search(zeile) and not zeile.lstrip().startswith(("import ", "//", "*")):
                treffer.append((datei, nummer, zeile.strip()[:100]))
    return treffer


# ------------------------------------------------------------------------------------------------- Ausgabe

def _zelle(text: object) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def blatt(quelle: dict, erhebung: dict, pruefung: Pruefung) -> tuple[str, dict]:
    routen, definitionen = erhebung["routen"], erhebung["definitionen"]
    platzhalter = {sid for sid, d in definitionen.items() if d["platzhalter"]}
    bereiche = set(quelle.get("bereiche") or [])
    screen_domains = set(quelle.get("screen_domains") or bereiche)
    prozesse = quelle.get("prozesse") or []
    for prozess in prozesse:
        pruefe_prozess(prozess, routen, platzhalter, pruefung)

    eigene_routen = [z for r, z in sorted(routen.items()) if z["bereich"] in bereiche]
    stufen = Counter(z["stufe"] for z in eigene_routen)
    eigene_platzhalter = sorted(sid for sid, d in definitionen.items() if d["platzhalter"] and d["domain"] in screen_domains)
    eigene_masken = {sid for sid, d in definitionen.items() if d["domain"] in screen_domains}
    aktionen = [a for a in erhebung["aktionen"] if a["maske"] in eigene_masken]
    wirksam = [a for a in aktionen if a["art"] == "serverwirksam"]
    funde = festwerte([d for z in eigene_routen for d in z.get("dateien", [])])
    luecken = [(p["id"], l) for p in prozesse for l in p.get("luecken") or []]
    status = Counter(p.get("status") for p in prozesse)
    hoechste = min((l["prio"] for _, l in luecken if l.get("prio") in PRIORITAETEN), default="keine")

    def maske(route: str) -> str:
        zeile = routen.get(route)
        if not zeile:
            return f"`{route}` **fehlt**"
        hohl = set(zeile["screen_ids"]) & platzhalter
        return f"`{route}` ({zeile['stufe']}{', **Platzhalter**' if hohl else ''})"

    zeilen = [
        f"# Abnahmeblatt {quelle['titel']}", "",
        "Erzeugt mit `python scripts/domaenen_abnahme.py` aus "
        f"[`{quelle['id']}.yaml`]({quelle['id']}.yaml); nicht von Hand bearbeiten.", "",
        f"- Reifematrix: {quelle.get('reifematrix', '—')}; L3-Referenz: `{quelle.get('l3_referenz', '—')}`",
        f"- Prozesse: {len(prozesse)} — abgenommen {status['abgenommen']}, teilweise {status['teilweise']}, "
        f"fehlt {status['fehlt']}; hoechste offene Luecke: {hoechste}",
        f"- Erhoben: {quelle.get('erhoben', '—')} von {quelle.get('pruefer', '—')}", "",
        "## Prozessliste (L3-Referenz)", "",
        "| ID | Prozess | L3 | VALEO-Maske | Rolle | Nachweis | Status |", "|---|---|---|---|---|---|---|",
    ]
    for p in prozesse:
        nachweise = "<br>".join(f"`{n}`" for n in p.get("nachweise") or []) or "—"
        zeilen.append(
            f"| {p['id']} | {_zelle(p['name'])} | {_zelle(p.get('l3', '—'))} | "
            f"{'<br>'.join(maske(r) for r in p.get('routen') or []) or '—'} | {_zelle(p.get('rolle', '—'))} | "
            f"{nachweise} | {p.get('status')} |")
    zeilen += ["", "## Befunde je Prozess", ""]
    for p in prozesse:
        if p.get("befund"):
            zeilen += [f"- **{p['id']} {_zelle(p['name'])}:** {_zelle(p['befund'])}"]
    zeilen += ["", "## Luecken", "", "| Prio | Prozess | Luecke | Eintrag |", "|---|---|---|---|"]
    for pid, l in sorted(luecken, key=lambda x: (x[1].get("prio", "P9"), x[0])):
        zeilen.append(f"| {l.get('prio')} | {pid} | {_zelle(l.get('text', ''))} | {l.get('eintrag', '—')} |")
    if not luecken:
        zeilen.append("| — | — | keine | — |")
    zeilen += [
        "", "## Maskenabnahme (maschinell)", "",
        f"Bereiche im Inventar: {', '.join(sorted(bereiche))}. Routen: {len(eigene_routen)} — "
        + ", ".join(f"{s} {n}" for s, n in sorted(stufen.items())) + ".", "",
        f"Generische Platzhaltermasken (nur Kennung/Name/Status/Datum, nur Export): {len(eigene_platzhalter)}"
        + (":" if eigene_platzhalter else "."), "",
    ]
    zeilen += [f"- `{sid}` — {definitionen[sid]['title']}" for sid in eigene_platzhalter]
    zeilen += [
        "", f"Aktionen der Domaenenmasken: {len(aktionen)}, davon serverwirksam {len(wirksam)}; "
        f"ohne CLI {sum(1 for a in wirksam if not a['cli'])}; nicht verfuegbar "
        f"{sum(1 for a in aktionen if a['art'] == 'nicht_verfuegbar')}; nicht deklariert "
        f"{sum(1 for a in aktionen if a['art'] == 'nicht_deklariert')}.", "",
        "## Demo- und Festwerte (Stichwortsuche in den Seitenquellen)", "",
    ]
    zeilen += [f"- `{d}:{n}` {_zelle(t)}" for d, n, t in funde] or ["Keine Treffer."]
    rollen = len(json.loads(ROLLEN_RATSCHE.read_text(encoding="utf-8"))["wege"])
    zeilen += [
        "", "## Rollen", "",
        f"Schreibwege ohne erkennbare Rollenpruefung systemweit: {rollen} "
        "(`python scripts/check_write_routes_roles.py --check`). Die Rolle je Prozess steht in der Prozessliste; "
        "sie ist am Endpunkt gelesen, nicht nur an der Navigation.", "",
    ]
    kennzahlen = {
        "id": quelle["id"], "titel": quelle["titel"], "reifematrix": quelle.get("reifematrix"),
        "prozesse": len(prozesse), "abgenommen": status["abgenommen"], "teilweise": status["teilweise"],
        "fehlt": status["fehlt"], "hoechste_luecke": hoechste, "platzhalter": len(eigene_platzhalter),
        "festwerte": len(funde),
    }
    return "\n".join(zeilen), kennzahlen


def uebersicht(kennzahlen: list[dict]) -> str:
    zeilen = [
        "# Domaenenabnahme (Fahrplan M4)", "",
        "Erzeugt mit `python scripts/domaenen_abnahme.py`; Quelle je Domaene ist die YAML-Datei daneben. "
        "Kriterien: Prozessliste aus der L3-Referenz, Maskenabnahme, keine Demo- oder Festwerte, Rollen geprueft "
        "([Fahrplan](../../roadmap/fahrplan-verkaufsprodukt.md)).", "",
        "| Domaene | Reifematrix | Prozesse | abgenommen | teilweise | fehlt | hoechste Luecke | Platzhaltermasken | Festwert-Treffer |",
        "|---|---|---:|---:|---:|---:|---|---:|---:|",
    ]
    for k in kennzahlen:
        zeilen.append(
            f"| [{k['titel']}]({k['id']}.md) | {k['reifematrix'] or '—'} | {k['prozesse']} | {k['abgenommen']} | "
            f"{k['teilweise']} | {k['fehlt']} | {k['hoechste_luecke']} | {k['platzhalter']} | {k['festwerte']} |")
    return "\n".join(zeilen) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    erhebung = erhebe()
    pruefung = Pruefung()
    ausgaben: dict[Path, str] = {}
    kennzahlen = []
    for quelle_pfad in sorted(BLAETTER.glob("*.yaml")):
        quelle = yaml.safe_load(quelle_pfad.read_text(encoding="utf-8"))
        text, k = blatt(quelle, erhebung, pruefung)
        ausgaben[quelle_pfad.with_suffix(".md")] = text
        kennzahlen.append(k)
    ausgaben[BLAETTER / "README.md"] = uebersicht(kennzahlen)

    veraltet = [p for p, t in ausgaben.items() if not p.is_file() or p.read_text(encoding="utf-8") != t]
    if args.check:
        for p in veraltet:
            pruefung.melde(f"{p.relative_to(ROOT).as_posix()} veraltet — python scripts/domaenen_abnahme.py")
    else:
        for p in veraltet:
            p.write_text(ausgaben[p], encoding="utf-8", newline="\n")
    for fehler in pruefung.fehler:
        print(f"FEHLER {fehler}")
    if pruefung.fehler:
        return 1
    print(f"Domaenenabnahme OK: {len(kennzahlen)} Blaetter" + ("" if args.check else f", {len(veraltet)} geschrieben"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
