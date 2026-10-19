#!/usr/bin/env python3
"""MASK-STUDIO-INVENTAR — wie weit ist der Weg zu "nur Studio-generierte Masken"?

    python scripts/mask_studio_inventory.py                 # Bericht auf stdout
    python scripts/mask_studio_inventory.py --json out.json # vollstaendiges Inventar
    python scripts/mask_studio_inventory.py --markdown f.md # Bericht als Datei
    python scripts/mask_studio_inventory.py --check         # Ratsche (CI)
    python scripts/mask_studio_inventory.py --write-baseline

Nutzerentscheid 2026-10-19: Kuenftig sind nur Studio-generierte Masken gewuenscht; ein- und ausgehende
Belege sind eine Maske mit Varianten; jede Maskenfunktion soll zusaetzlich per CLI und MCP erreichbar und
in CI geprueft sein. Dieses Skript misst den Abstand dazu, ohne etwas zu aendern.

**Seiten** (jede Route aus ``route-aliases.json``) bekommen genau eine Stufe:

``studio_versioniert``
    Rendert eine ScreenDefinition einer versionierten Familie (``config/document_screen_versions.json``).
``screen_definition``
    Rendert eine ScreenDefinition ueber die Builder-Kette (``UniversalNative*Page``, ``UniversalMaskRenderer``,
    ``useScreenDefinition``). Ueber den Studio-Import als Ausgangsfassung uebernehmbar, aber nicht versioniert.
``builder_altmuster``
    Konfigurierte Altkomponenten (``ObjectPage``, ``ListReport``, ``Wizard`` …) ohne ScreenDefinition.
``handgebaut``
    Freies JSX ohne Builder.
``weiterleitung``
    Kleine Seite, die nur umleitet; zaehlt nicht als Maske.

Die Stufe wird statisch aus dem Quelltext bestimmt: Die Routendatei und die von ihr importierten Dateien unter
``pages/`` und ``features/`` (nicht ``components/``: ein gemeinsamer Baustein macht keine Seite zur Maske).

**Aktionen** (jede Aktion jeder registrierten ScreenDefinition einschliesslich der Belegvarianten) bekommen je
Zugang einen Befund: REST (``commandEndpoint``/``inputFlow``), MCP (Klassifikation in
``config/mcp_mask_action_map.yaml``) und CLI. Reine Navigation ist ausgenommen. Eine Aktion ohne jeden
deklarierten Weg (typisch Zeilenaktionen wie ``edit``, ``print``, ``open_source``, die erst Renderer oder Seite
verdrahten) heisst ``nicht_deklariert``: Ohne Vertrag kann es fuer sie weder MCP noch CLI geben.

**Ratsche** (``config/mask_studio_ratchet.json``): Eine neue Route darf weder handgebaut noch Altmuster sein,
eine neue Aktion nicht undeklariert, eine neue serverwirksame Aktion nicht ohne MCP-Klassifikation und nicht ohne
CLI-Zugang. Bestandsluecken
stehen in der Ratschendatei und duerfen nur schrumpfen; ein geschlossener Eintrag wird gemeldet und mit
``--write-baseline`` entfernt.

Exit 0 = OK, Exit 1 = neue Luecke.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

SRC = ROOT / "packages/frontend-web/src"
ROUTES = SRC / "app/route-aliases.json"
FAMILIES = ROOT / "config/document_screen_versions.json"
MCP_MAP = ROOT / "config/mcp_mask_action_map.yaml"
RATCHET = ROOT / "config/mask_studio_ratchet.json"

STUFEN = ("studio_versioniert", "screen_definition", "builder_altmuster", "handgebaut", "weiterleitung")

#: MCP-Befunde aus der Aktionskarte. "gesperrt" ist eine bewusste Entscheidung, keine Luecke.
MCP_ZUGANG = {"mapped", "mapped_read", "mapped_propose_only", "adjacent"}
MCP_GESPERRT = {"blocked_human_only"}
MCP_OHNE_SERVERWIRKUNG = {"local_ui"}

_IMPORT = re.compile(r"""(?:import|export)\s[^'"]*?from\s+['"]([^'"]+)['"]|import\(\s*['"]([^'"]+)['"]\s*\)""")
_SCREEN_ID = re.compile(r"""screenId\s*=\s*(?:\{\s*)?[`'"]([^`'"]+)[`'"]|useScreenDefinition\(\s*[`'"]([^`'"]+)[`'"]""")
_BUILDER = re.compile(r"\b(UniversalNative(?:Detail|Create|Cockpit)Page|UniversalMaskRenderer|useScreenDefinition|"
                      r"compileRenderPlanFromScreenDefinition|CaptureScreenHost)\b")
_ALTMUSTER = re.compile(r"""from\s+['"]@/components/(?:mask-builder/(?:ObjectPage|ListReport|Wizard|Worklist|OverviewPage)"""
                        r"""|patterns/(?:ListReport|Wizard)|mask-builder['"])""")
_BELEG_ROUTE = re.compile(r"angebot|auftrag(?!s?-?positionen)|bestellung|lieferschein|wareneingang|(?<!kostenstellen)rechnung|gutschrift")
_WEITERLEITUNG = re.compile(r"<Navigate\b|\bredirect\(|navigate\([^()]*\{\s*replace:\s*true")


# --------------------------------------------------------------------------------------------- Seiten

def _resolve(spec: str, origin: Path) -> Path | None:
    if spec.startswith("@/"):
        base = SRC / spec[2:]
    elif spec.startswith("."):
        base = (origin.parent / spec).resolve()
    else:
        return None
    for cand in (base, *(base.with_name(base.name + ext) for ext in (".tsx", ".ts", ".jsx", ".js")),
                 base / "index.tsx", base / "index.ts"):
        if cand.is_file():
            return cand
    return None


def _followable(path: Path) -> bool:
    rel = path.relative_to(SRC).as_posix() if path.is_relative_to(SRC) else ""
    return rel.startswith(("pages/", "features/")) and "__tests__" not in rel


def _page_sources(entry: Path, depth: int = 4) -> list[Path]:
    seen: dict[Path, None] = {}
    todo = [(entry, 0)]
    while todo:
        path, level = todo.pop()
        if path in seen:
            continue
        seen[path] = None
        if level >= depth:
            continue
        for match in _IMPORT.finditer(path.read_text(encoding="utf-8", errors="replace")):
            target = _resolve(match.group(1) or match.group(2), path)
            if target and _followable(target):
                todo.append((target, level + 1))
    return list(seen)


def classify_page(entry: Path, family_prefixes: tuple[str, ...]) -> dict:
    sources = _page_sources(entry)
    texts = {p: p.read_text(encoding="utf-8", errors="replace") for p in sources}
    screen_ids = sorted({m.group(1) or m.group(2) for t in texts.values() for m in _SCREEN_ID.finditer(t)})
    builder = any(_BUILDER.search(t) for t in texts.values())
    altmuster = any(_ALTMUSTER.search(t) for t in texts.values())
    entry_text = texts[entry]
    if builder and any(sid.startswith(family_prefixes) for sid in screen_ids):
        stufe = "studio_versioniert"
    elif builder:
        stufe = "screen_definition"
    elif altmuster:
        stufe = "builder_altmuster"
    elif len(sources) == 1 and _WEITERLEITUNG.search(entry_text) and entry_text.count("\n") < 60:
        stufe = "weiterleitung"
    else:
        stufe = "handgebaut"
    return {"stufe": stufe, "screen_ids": screen_ids,
            "dateien": [p.relative_to(ROOT).as_posix() for p in sources]}


def pages(family_prefixes: tuple[str, ...]) -> list[dict]:
    rows = []
    for alias in json.loads(ROUTES.read_text(encoding="utf-8"))["aliases"]:
        entry = _resolve(alias["module"], ROUTES)
        path = alias.get("path", "/" if alias.get("index") else "")
        row = {"route": path, "modul": alias["module"], "bereich": path.split("/")[0] or "start"}
        if entry is None:
            row.update(stufe="handgebaut", screen_ids=[], dateien=[], fehler="modul_nicht_gefunden")
        else:
            row.update(classify_page(entry, family_prefixes))
        rows.append(row)
    return sorted(rows, key=lambda r: r["route"])


# --------------------------------------------------------------------------------------------- Aktionen

def _definitions() -> dict[str, dict]:
    from app.core.screen_definitions import SCREEN_DEFINITION_BUILDERS, get_screen_definition
    from app.core.screen_definitions_beleg import BELEGARTEN, build_beleg_screen_definition, screen_id

    defs = {sid: get_screen_definition(sid) or {} for sid in SCREEN_DEFINITION_BUILDERS}
    for art in BELEGARTEN:
        defs[screen_id(art)] = build_beleg_screen_definition(art)
    return defs


def _iter_actions(definition: dict):
    from app.services.studio_validation import _iter_actions as iter_actions
    for action in iter_actions(definition):
        if isinstance(action, dict) and action.get("key"):
            yield action


def _mcp_coverage() -> dict[str, str]:
    import yaml
    data = yaml.safe_load(MCP_MAP.read_text(encoding="utf-8")) or {}
    return {m["mask_action_id"]: m["coverage"] for m in data.get("mappings", []) if m.get("mask_action_id")}


def _cli_commands() -> set[str]:
    """Maskenaktionen mit CLI-Zugang. Bis eine CLI existiert, ist die Menge leer — ehrlich, nicht geschoent."""
    registry = ROOT / "config/cli_mask_commands.json"
    if not registry.is_file():
        return set()
    return set(json.loads(registry.read_text(encoding="utf-8")).get("mask_action_ids", []))


#: Bewusst Menschen vorbehalten: so deklariert die ScreenDefinition (oder ein Adapter/Eingabefluss der Maske).
AGENT_GESPERRT = {"fuer_agenten_gesperrt", "menschliche_genehmigung", "adapter_nur_mensch", "eingabe_in_maske"}


def actions() -> list[dict]:
    from app.services.mcp_mask_actions import agent_block

    mcp = _mcp_coverage()
    cli = _cli_commands()
    rows = []
    for sid, definition in sorted(_definitions().items()):
        seen = set()
        for action in _iter_actions(definition):
            key = action["key"]
            if key in seen:
                continue
            seen.add(key)
            flow = action.get("inputFlow") if isinstance(action.get("inputFlow"), dict) else {}
            rest = action.get("commandEndpoint") or flow.get("submitEndpoint")
            navigation = (bool(action.get("navigationRoute")) or bool(action.get("localEffect"))) and not rest
            action_id = f"mask:{sid}:{key}"
            coverage = mcp.get(action_id)
            if navigation or coverage in MCP_OHNE_SERVERWIRKUNG:
                art = "ohne_serverwirkung"
            elif rest or action.get("command"):
                art = "serverwirksam"
            else:
                art = "nicht_deklariert"
            block = agent_block(action)
            if coverage in MCP_ZUGANG:
                mcp_state = "zugang"
            elif block is None:
                mcp_state = "generisch"  # mask.action.execute: derselbe Kommando-Endpunkt mit dem Token des Agenten
            elif coverage in MCP_GESPERRT or block in AGENT_GESPERRT:
                mcp_state = "gesperrt"
            else:
                mcp_state = coverage or "unklassifiziert"
            rows.append({
                "id": action_id, "maske": sid, "aktion": key, "label": action.get("label"), "art": art,
                "rest": rest, "mcp": mcp_state, "mcp_grund": block, "cli": action_id in cli,
            })
    return rows


# --------------------------------------------------------------------------------------------- Studio-Katalog

STUDIO_CATALOG = ROOT / "config/studio_data_sources.yaml"
OPENAPI = ROOT / "docs/schnittstellen/openapi.json"
#: MCP kann die Aktion ausfuehren (oder sie ist bewusst Menschen vorbehalten). ``mapped_read`` liest nur Status.
MCP_BEDIENBAR = {"mapped", "mapped_propose_only", "blocked_human_only"}


def _route_key(path: str) -> str:
    return re.sub(r"\{[^}]+\}", "{}", path).rstrip("/")


def catalog() -> dict:
    """Eine Studio-Maske kann nur Quellen und Aktionen aus dem Katalog tragen. Ist jede Katalogaktion per CLI
    und MCP bedienbar und zeigt jede Quelle auf eine echte Route, gilt das fuer jede Studio-Maske."""
    import yaml

    from valeo_cli.support import support

    data = yaml.safe_load(STUDIO_CATALOG.read_text(encoding="utf-8")) or {}
    routes = {_route_key(path) for path in json.loads(OPENAPI.read_text(encoding="utf-8"))["paths"]}
    mappings = (yaml.safe_load(MCP_MAP.read_text(encoding="utf-8")) or {}).get("mappings", [])
    rows = []
    for action in data.get("command_actions") or []:
        endpoint = action.get("commandEndpoint") or ""
        coverages = sorted({m["coverage"] for m in mappings if m.get("command_endpoint") == endpoint})
        rows.append({"aktion": action["key"], "endpunkt": endpoint, "route": _route_key(endpoint) in routes,
                     "cli": support(action).supported, "mcp": coverages,
                     "mcp_bedienbar": bool(set(coverages) & MCP_BEDIENBAR)})
    sources = [{"quelle": ds["key"], "endpunkt": ds["endpoint"], "route": _route_key(ds["endpoint"]) in routes}
               for ds in data.get("data_sources") or []]
    return {"aktionen": rows, "quellen": sources}


# --------------------------------------------------------------------------------------------- Auswertung

def inventory() -> dict:
    families = json.loads(FAMILIES.read_text(encoding="utf-8"))
    prefixes = (families["family"] + "/",)
    page_rows = pages(prefixes)
    action_rows = actions()
    routed = {sid for row in page_rows for sid in row["screen_ids"]}
    registered = sorted({row["maske"] for row in action_rows} | set(_definitions()))
    return {
        "stand": date.today().isoformat(),
        "familien": {families["family"]: families["current"]},
        "seiten": page_rows,
        "aktionen": action_rows,
        "studio_katalog": catalog(),
        "masken_ohne_route": [sid for sid in registered
                              if sid not in routed and not any(r.startswith(sid.split("/")[0] + "/${") for r in routed)],
    }


def gaps(inv: dict) -> dict[str, list[str]]:
    wirksam = [a for a in inv["aktionen"] if a["art"] == "serverwirksam"]
    return {
        "handgebaut_routen": sorted(r["route"] for r in inv["seiten"] if r["stufe"] == "handgebaut"),
        "altmuster_routen": sorted(r["route"] for r in inv["seiten"] if r["stufe"] == "builder_altmuster"),
        "aktionen_nicht_deklariert": sorted(a["id"] for a in inv["aktionen"] if a["art"] == "nicht_deklariert"),
        "aktionen_ohne_mcp_klassifikation": sorted(a["id"] for a in wirksam if a["mcp"] == "unklassifiziert"),
        "aktionen_ohne_cli": sorted(a["id"] for a in wirksam if not a["cli"]),
        "studio_katalog_nicht_bedienbar": sorted(
            [f"aktion:{a['aktion']}:ohne_route" for a in inv["studio_katalog"]["aktionen"] if not a["route"]]
            + [f"aktion:{a['aktion']}:ohne_cli" for a in inv["studio_katalog"]["aktionen"] if not a["cli"]]
            + [f"aktion:{a['aktion']}:mcp_nicht_ausfuehrbar" for a in inv["studio_katalog"]["aktionen"]
               if not a["mcp_bedienbar"]]
            + [f"quelle:{q['quelle']}:ohne_route" for q in inv["studio_katalog"]["quellen"] if not q["route"]]),
    }


def check(inv: dict) -> int:
    baseline = json.loads(RATCHET.read_text(encoding="utf-8"))
    current = gaps(inv)
    bad = 0
    for name, entries in current.items():
        allowed = set(baseline.get(name, []))
        new = sorted(set(entries) - allowed)
        closed = sorted(allowed - set(entries))
        if new:
            bad += len(new)
            print(f"FEHLER {name}: {len(new)} neu (nur Studio-/Builder-Masken und Aktionen mit MCP/CLI zulaessig)")
            for item in new:
                print(f"  + {item}")
        if closed:
            print(f"Hinweis {name}: {len(closed)} geschlossen — mit --write-baseline aus der Ratsche nehmen")
    if not bad:
        print("Masken-Studio-Ratsche OK: " + ", ".join(f"{k}={len(v)}" for k, v in current.items()))
    return 1 if bad else 0


def markdown(inv: dict) -> str:
    seiten = inv["seiten"]
    stufen = Counter(r["stufe"] for r in seiten)
    masken = [r for r in seiten if r["stufe"] != "weiterleitung"]
    wirksam = [a for a in inv["aktionen"] if a["art"] == "serverwirksam"]
    by_area: dict[str, Counter] = defaultdict(Counter)
    for row in seiten:
        by_area[row["bereich"]][row["stufe"]] += 1
    lines = [
        f"# Masken-Studio-Inventar ({inv['stand']})", "",
        "Erzeugt mit `python scripts/mask_studio_inventory.py --markdown <datei>`. Ziel: nur Studio-generierte",
        "Masken; jede Maskenfunktion auch per CLI und MCP, in CI geprueft (Nutzerentscheid 2026-10-19).", "",
        "## Seiten", "",
        "| Stufe | Routen | Anteil an Masken |", "|---|---:|---:|",
    ]
    for stufe in STUFEN:
        share = "" if stufe == "weiterleitung" else f"{100 * stufen[stufe] / max(len(masken), 1):.1f} %"
        lines.append(f"| {stufe} | {stufen[stufe]} | {share} |")
    lines += ["", f"Gesamt {len(seiten)} Routen, davon {len(masken)} Masken.", "",
              "## Aktionen", "",
              "| Befund | Anzahl |", "|---|---:|",
              f"| Aktionen gesamt (ohne Doppel je Maske) | {len(inv['aktionen'])} |",
              f"| davon serverwirksam | {len(wirksam)} |",
              f"| … mit REST-Kommandoweg | {sum(1 for a in wirksam if a['rest'])} |",
              f"| … mit eigenem MCP-Werkzeug | {sum(1 for a in wirksam if a['mcp'] == 'zugang')} |",
              f"| … per generischem MCP-Werkzeug (`mask.action.execute`) | {sum(1 for a in wirksam if a['mcp'] == 'generisch')} |",
              f"| … MCP bewusst gesperrt | {sum(1 for a in wirksam if a['mcp'] == 'gesperrt')} |",
              f"| … MCP offen (`open_high` u. a.) | {sum(1 for a in wirksam if a['mcp'] not in ('zugang', 'generisch', 'gesperrt', 'unklassifiziert'))} |",
              f"| … MCP unklassifiziert | {sum(1 for a in wirksam if a['mcp'] == 'unklassifiziert')} |",
              f"| … mit CLI-Zugang | {sum(1 for a in wirksam if a['cli'])} |",
              f"| nicht deklariert (kein Kommando, Endpunkt, Navigation) | "
              f"{sum(1 for a in inv['aktionen'] if a['art'] == 'nicht_deklariert')} |",
              "", "## Versionierte Familien", ""]
    for family, variants in inv["familien"].items():
        lines.append(f"- `{family}`: {len(variants)} Varianten — " + ", ".join(
            f"{k} {v}" for k, v in sorted(variants.items())))
    lines += ["", "## Studio-Katalog", "",
              "Studio-Masken tragen nur Katalogaktionen. Was hier bedienbar ist, ist es in jeder Studio-Maske.", "",
              "| Katalogaktion | Route | CLI | MCP |", "|---|---|---|---|"]
    for a in inv["studio_katalog"]["aktionen"]:
        mcp = ", ".join(a["mcp"]) or "keine Abbildung"
        lines.append(f"| `{a['aktion']}` | {'ja' if a['route'] else '**fehlt**'} | {'ja' if a['cli'] else 'nein'} | "
                     f"{mcp}{'' if a['mcp_bedienbar'] else ' — **nicht ausfuehrbar**'} |")
    missing = [q["quelle"] for q in inv["studio_katalog"]["quellen"] if not q["route"]]
    lines += ["", f"Datenquellen: {len(inv['studio_katalog']['quellen'])}, ohne Route: {', '.join(missing) or 'keine'}."]
    beleg = [r for r in seiten if r["stufe"] in ("screen_definition", "builder_altmuster", "handgebaut")
             and _BELEG_ROUTE.search(r["route"])]
    lines += ["", "## Beleg-Einstiege ausserhalb der Belegfamilie", "",
              "Stichwortsuche im Routenpfad (Angebot, Auftrag, Bestellung, Lieferschein, Wareneingang, Rechnung,",
              "Gutschrift). Jeder Treffer ist Kandidat fuer eine Variante der Familie `beleg` oder ihre Liste — die",
              "fachliche Zuordnung fuehrt `docs/design/beleg-studio-variantenmatrix.md`.", "",
              "| Route | Stufe |", "|---|---|"]
    lines += [f"| `{r['route']}` | {r['stufe']} |" for r in beleg]
    lines += ["", f"Registrierte ScreenDefinitions ohne eigene Route: {len(inv['masken_ohne_route'])}.", "",
              "## Bereiche (Rollout-Reihenfolge nach Anzahl handgebauter Masken)", "",
              "| Bereich | studio_versioniert | screen_definition | builder_altmuster | handgebaut | weiterleitung |",
              "|---|---:|---:|---:|---:|---:|"]
    for area, counts in sorted(by_area.items(), key=lambda kv: (-kv[1]["handgebaut"], kv[0])):
        lines.append(f"| {area} | " + " | ".join(str(counts[s]) for s in STUFEN) + " |")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write-baseline", action="store_true")
    parser.add_argument("--json", type=Path)
    parser.add_argument("--markdown", type=Path)
    args = parser.parse_args(argv)
    inv = inventory()
    if args.write_baseline:
        RATCHET.write_text(json.dumps({"_hinweis": "Nur schrumpfen. Erzeugt von scripts/mask_studio_inventory.py "
                                                    "--write-baseline; siehe Modul-Docstring.", **gaps(inv)},
                                      ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if args.json:
        args.json.write_text(json.dumps(inv, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if args.markdown:
        args.markdown.write_text(markdown(inv), encoding="utf-8")
    if args.check:
        return check(inv)
    if not (args.json or args.markdown or args.write_baseline):
        print(markdown(inv))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
