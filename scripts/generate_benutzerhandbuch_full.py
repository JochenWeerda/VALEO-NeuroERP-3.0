"""Generiert vollständiges Benutzerhandbuch aus Navigation + Route-Inventory.

DOC-USER-MANUAL-004: Jede Nav-Maske und jede App-Route erhält Eintrag im
Maskenregister; Kapitel folgen dem Muster Ziel/Voraussetzungen/Schritte/Ergebnis/Fehler/Quellen.

Usage:
  python scripts/generate_benutzerhandbuch_full.py
  python scripts/generate_benutzerhandbuch_full.py --check   # Abdeckung prüfen
"""
from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

REPO = Path(__file__).parent.parent
HANDBUCH = REPO / "docs" / "benutzerhandbuch"
NAV_DIR = REPO / "packages" / "frontend-web" / "src" / "app" / "navigation" / "domains"
ROUTE_INV = REPO / "packages" / "frontend-web" / "src" / "app" / "routing" / "route-inventory.gen.json"
TODAY = date.today().isoformat()

# Kapitel: (dateiname, titel, pfad-präfixe, kurzbeschreibung)
# Reihenfolge = Zuordnungspriorität (spezifischer zuerst innerhalb der Liste durch längeres Prefix-Matching)
CHAPTERS: list[tuple[str, str, list[str], str]] = [
    ("einstieg.md", "Einstieg und Navigation", [
        "hilfe", "auth", "login", "einstellungen", "setup/firma", "start-dashboard",
        "benachrichtigungen", "alerts", "errors/NotFound", "public/verify", "verify",
    ], "Anmeldung, Mandant, Suche, Tastatur, Benachrichtigungen."),
    ("dashboard-workflows.md", "Dashboard und Workflows", [
        "workflow", "workflows", "dashboard", "dashboards", "management/executive-dashboard",
        "monitoring", "system/live-monitor", "copilot", "policy-manager", "policies",
    ], "Leitstand, Flow Spine, Freigaben, Prozessüberwachung, KI-Copilot."),
    ("wissensbasis-kundenportal.md", "Wissensbasis und Kundenportal", [
        "wissen", "portal",
    ], "Interne Wissensdatenbank und externes Kundenportal."),
    ("annahme.md", "Ernteannahme und Waage", [
        "agrar/annahme", "agrar/partie", "agrar/wetter", "agrar/hofliste", "agrar/warteschlange",
        "agrar/waage", "annahme", "waage", "weighing",
    ], "LKW, Waage, Qualität, Hofliste, Wiegung."),
    ("agrar-kontrakte.md", "Agrar-Kontrakte", [
        "kontrakte", "contracts", "contracts-v2", "vertrag", "agrar/kontrakt", "agrar/kontrakte",
        "agrar/fixierung", "agrar/settlement", "agrar/preisfixierung",
    ], "Kontrakt, Fixierung, Erfüllung, Settlement."),
    ("agrar-warenwirtschaft.md", "Agrar-Warenwirtschaft", [
        "agrar/psm", "agrar/duengung", "agrar/saatgut", "agrar/feldbuch", "agrar/ernteplanung",
        "agrar/milchvieh", "agrar/saatzucht", "agrar/bodenprobe", "agrar/duenger",
        "agrar/pflanzenschutz", "agrar/silo", "agrar/lager", "agrar/bestellung", "agribusiness",
        "agrar/duengemittel", "agrar/ernte", "agrar/futter", "agrar/kultur", "agrar/maschine",
        "agrar/sorte", "agrar/tier", "agrar/betrieb", "agrar/flaeche", "agrar/naehrstoff",
    ], "PSM, Düngung, Saatgut, Feldbuch, Tierhaltung, Agrar-Stammdaten."),
    ("verkauf.md", "Verkauf (Auftrag bis Rechnung)", [
        "verkauf", "sales", "vertrieb",
    ], "O2C-Belegkette, Angebot, Auftrag, Lieferschein, Rechnung."),
    ("einkauf.md", "Einkauf und Beschaffung", [
        "einkauf", "disposition", "rfq", "edi", "inbox",
    ], "P2P, Bestellung, Wareneingang, Lieferantenbewertung, Bestell-Inbox."),
    ("vertreter-provisionen.md", "Vertreter und Provisionen", [
        "crm/vertreterstamm", "crm/vertreterprovisionen",
    ], "Außendienst, Vertreterstamm, Provisionsabrechnung."),
    ("crm.md", "CRM und Marketing", [
        "crm", "marketing", "prospecting", "termine",
    ], "Kontakte, Leads, Kampagnen, DSGVO, KIM, Termine."),
    ("preise-kalkulation.md", "Preise und Kalkulation", [
        "preise", "kalkulation", "pricing",
    ], "Preislisten, Kalkulation, Konditionen."),
    ("artikel-stammdaten.md", "Artikel und Stammdaten", [
        "artikel", "stammdaten/artikel", "charge", "stammdaten", "etiketten",
    ], "Artikelstamm, Chargen, Warengruppen, Etikettendruck."),
    ("lager.md", "Lager und Bestände", [
        "lager", "inventory", "inventory-dashboard", "inventory-reports",
        "stock-management", "silo", "verladung",
    ], "Bestand, Bewegungen, Inventur, Silo, Verladung, Rückverfolgbarkeit."),
    ("futtermittel-produktion.md", "Futtermittel und Produktion", [
        "futtermittel", "futter", "produktion", "mischfutter", "rezept", "rezepte",
    ], "Rezeptur, Produktionsauftrag, Chargen."),
    ("qualitaetssicherung.md", "Qualitätssicherung", [
        "qualitaet", "labor", "probe", "lager/qs",
    ], "Proben, Labor, QS-Leitstand, Reklamation."),
    ("compliance-meldewesen.md", "Compliance und Meldewesen", [
        "compliance", "meldewesen", "zertifikate", "eudr", "esg", "foerderung",
        "nachhaltigkeit", "subventionen",
    ], "Register, Meldungen, GoBD, PCN/UFI, ESG, EUDR."),
    ("nawaro.md", "NaWaRo", ["nawaro"], "Verträge, Anbauflächen, Mitteilungen."),
    ("strecke-handelsgeschaeft.md", "Streckengeschäft", ["strecke"], "Streckenhandel, Dokumente, Abrechnung."),
    ("logistik.md", "Logistik und Touren", [
        "logistik", "versand", "epod", "transporte",
    ], "Disposition, Touren, Frachtbriefe, Fahrer."),
    ("fuhrpark.md", "Fuhrpark", ["fuhrpark", "tankstelle"], "Fahrzeuge, Wartung, Kosten, Tankstelle."),
    ("finanzbuchhaltung.md", "Finanzbuchhaltung", [
        "fibu", "finance", "bank", "banken", "elster", "datev", "ustva", "atlas",
        "fibu-suite", "mahnwesen", "export/ustva", "export/umsatzsteuervoranmeldung",
        "finanzplanung", "document",
    ], "Hauptbuch, OP, Zahlungen, Abschluss, Bank, Mahnwesen, Schnittstellen."),
    ("controlling-kostenrechnung.md", "Controlling und Kostenrechnung", [
        "controlling", "kostenrechnung", "kostenstelle", "bab",
    ], "Kostenstellen, Umlagen, Auswertungen."),
    ("pos-kasse.md", "POS und Kasse", ["pos", "kasse", "tse"], "Bon, Zahlungsarten, Tagesabschluss."),
    ("personal-lohn.md", "Personal, Zeit und Lohn", [
        "personal", "hr", "lohn", "zeit", "payroll", "schichtplan",
    ], "Zeiterfassung, Abwesenheit, Schichtplan, Lohnabrechnung."),
    ("genossenschaft.md", "Genossenschaft", ["genossenschaft"], "Mitglieder, Geschäftsanteile, Dividende."),
    ("dokumente-belegarchiv.md", "Dokumente und Belegarchiv", [
        "dokumente", "docflow", "beleg", "archiv", "dms",
    ], "DMS, Versand, Archivierung."),
    ("reports-analytics.md", "Reports und Analytics", [
        "reports", "analytics", "auswertung", "statistik",
    ], "Standardreports, KPI-Dashboards, Statistik."),
    ("service-support.md", "Service und Support", [
        "service", "ticket", "support", "projekte", "schaeden", "versicherungen",
        "wartung", "energie", "mobile/scanner",
    ], "Servicefälle, Projekte, Schäden, Wartung, Versicherungen, Energie."),
]

# Admin-Routen → Verweis statt Endnutzer-Kapitel
ADMIN_PREFIXES = ("admin", "admin-suite", "api-docs", "mcp")

PRESERVE_MARKER = "## Maskenregister"


@dataclass
class NavItem:
    nav_id: str
    label: str
    route_path: str
    module: str
    source_file: str


@dataclass
class RouteEntry:
    path: str
    module: str
    source: str
    label: str = ""


def module_to_path(module: str) -> str:
    if not module or not module.startswith("@/pages/"):
        return ""
    return module.removeprefix("@/pages/").removesuffix("/index")


def parse_nav_file(path: Path) -> list[NavItem]:
    text = path.read_text(encoding="utf-8")
    items: list[NavItem] = []
    # Blockweise: id, label, optional preferredPath/path/module
    block_re = re.compile(
        r"\{\s*"
        r"id:\s*'([^']+)'"
        r"(?:(?!^\s*\{).)*?"
        r"label:\s*'((?:\\'|[^'])*)'"
        r"(?:(?!^\s*\{).)*?"
        r"(?:preferredPath:\s*'([^']*)')?"
        r"(?:(?!^\s*\{).)*?"
        r"(?:path:\s*'([^']*)')?"
        r"(?:(?!^\s*\{).)*?"
        r"(?:module:\s*'(@/pages/[^']+)')?"
        r"(?:(?!^\s*\{).)*?"
        r"\}",
        re.MULTILINE | re.DOTALL,
    )
    for m in block_re.finditer(text):
        nav_id, label = m.group(1), m.group(2).replace("\\'", "'")
        preferred = (m.group(3) or "").strip().lstrip("/")
        raw_path = (m.group(4) or "").strip().lstrip("/")
        module = m.group(5) or ""
        route_path = preferred or raw_path or module_to_path(module)
        if route_path in ("", "/"):
            route_path = "" if nav_id == "dashboard" else route_path
        items.append(NavItem(nav_id, label, route_path, module, path.name))
    return items


def load_routes() -> list[RouteEntry]:
    data = json.loads(ROUTE_INV.read_text(encoding="utf-8"))
    return [
        RouteEntry(
            path=(r.get("path") or "").strip().lstrip("/"),
            module=r.get("module") or "",
            source=r.get("source") or "",
        )
        for r in data.get("routes", [])
    ]


def build_label_map(nav_items: list[NavItem], routes: list[RouteEntry]) -> dict[str, str]:
    labels: dict[str, str] = {}
    for n in nav_items:
        if n.route_path:
            labels[n.route_path] = n.label
        mp = module_to_path(n.module)
        if mp:
            labels[mp] = n.label
    for r in routes:
        if r.path and r.path not in labels:
            labels[r.path] = path_to_label(r.path)
    return labels


def path_to_label(path: str) -> str:
    if not path:
        return "Start-Dashboard"
    last = path.split("/")[-1]
    return last.replace("-", " ").replace("_", " ").title()


def match_chapter(path: str) -> tuple[str, str, str, str] | None:
    if not path:
        return next((c for c in CHAPTERS if c[0] == "dashboard-workflows.md"), None)
    if path.startswith(ADMIN_PREFIXES):
        return None
    # Restliche agrar/* ohne spezifischeres Kapitel → Agrar-Warenwirtschaft
    if path.startswith("agrar/") or path == "agrar":
        fallback = next(c for c in CHAPTERS if c[0] == "agrar-warenwirtschaft.md")
        best: tuple[str, str, list[str], str] | None = fallback
        best_len = 5
    else:
        best = None
        best_len = -1
    for ch in CHAPTERS:
        for prefix in ch[2]:
            p = prefix.rstrip("/")
            if path == p or path.startswith(p + "/") or (p.endswith("/") and path.startswith(p)):
                if len(p) > best_len:
                    best = ch
                    best_len = len(p)
    return best


def assign_routes(routes: list[RouteEntry], labels: dict[str, str]) -> dict[str, list[RouteEntry]]:
    by_chapter: dict[str, list[RouteEntry]] = {c[0]: [] for c in CHAPTERS}
    unassigned: list[RouteEntry] = []
    seen: set[str] = set()
    for r in routes:
        if r.path in seen:
            continue
        seen.add(r.path)
        if r.path.startswith(ADMIN_PREFIXES):
            continue
        r.label = labels.get(r.path, path_to_label(r.path))
        ch = match_chapter(r.path)
        if ch:
            by_chapter[ch[0]].append(r)
        else:
            unassigned.append(r)
    # Unassigned → versuche root-segment
    for r in unassigned[:]:
        root = r.path.split("/")[0] if r.path else ""
        for ch in CHAPTERS:
            if root in ch[2]:
                by_chapter[ch[0]].append(r)
                unassigned.remove(r)
                break
    if unassigned:
        extra = "sonstige-masken.md"
        if extra not in by_chapter:
            by_chapter[extra] = []
        by_chapter[extra].extend(sorted(unassigned, key=lambda x: x.path))
    return by_chapter


def mask_steps(label: str, path: str) -> list[str]:
    route_hint = f"`/{path}`" if path else "Startseite"
    return [
        f"Sidebar oder Suche: **{label}** öffnen ({route_hint}).",
        "Filter und Spalten nach Bedarf setzen; bei ListReport Zeilen per Doppelklick oder Aktion öffnen.",
        "Bei Belegen: Kopfdaten prüfen, Positionen erfassen oder ändern, **Speichern** bzw. workflowgebundene Aktion (Freigabe, Folgebeleg) ausführen.",
        "Ergebnis in Liste, Detailansicht oder Folgebeleg verifizieren; bei Fehlern Meldungstext und Status prüfen.",
    ]


def render_mask_section(r: RouteEntry) -> str:
    anchor = re.sub(r"[^a-z0-9]+", "-", r.path.lower()).strip("-") or "start"
    lines = [
        f"### {r.label}",
        "",
        f"**Route:** `/{r.path}` · **Modul:** `{r.module}`",
        "",
        "**Schritte:**",
        "",
    ]
    for i, step in enumerate(mask_steps(r.label, r.path), 1):
        lines.append(f"{i}. {step}")
    lines.extend([
        "",
        "**Ergebnis:** Datensatz gespeichert, Liste aktualisiert oder Folgeprozess ausgelöst.",
        "",
        "**Häufige Fehler:**",
        "",
        "| Symptom | Ursache | Maßnahme |",
        "|---------|---------|----------|",
        "| Maske lädt nicht | Modul nicht freigeschaltet oder fehlende Berechtigung | Administrator: Modul/RBAC prüfen |",
        "| Speichern fehlgeschlagen | Pflichtfeld, Status oder Validierung | Meldung lesen, Pflichtfelder ergänzen |",
        "| Aktion ausgegraut | Workflow-Status oder Sperre | Vorbeleg freigeben oder Berechtigung klären |",
        "",
    ])
    return "\n".join(lines)


def render_chapter(
    filename: str,
    title: str,
    description: str,
    routes: list[RouteEntry],
    nav_items: list[NavItem],
) -> str:
    routes_sorted = sorted(routes, key=lambda x: x.path)
    nav_in_chapter = [
        n for n in nav_items
        if match_chapter(n.route_path) and match_chapter(n.route_path)[0] == filename
    ]
    nav_labels = {n.route_path for n in nav_in_chapter if n.route_path}

    lines = [
        "---",
        f"title: {title}",
        "type: how-to",
        "audience: [endnutzer, power-user]",
        "owner: Cursor",
        "status: aktiv",
        f"last_reviewed: {TODAY}",
        "version: 3.2.0",
        "---",
        "",
        f"# {title}",
        "",
        description,
        "",
        "## Ziel",
        "",
        f"Sie arbeiten sicher in allen Masken des Bereichs **{title}** — von der Navigation",
        "bis zu Speichern, Freigabe und Folgebelegen.",
        "",
        "## Voraussetzungen",
        "",
        "- Gültige Anmeldung und Mandant (`X-Tenant-ID`).",
        "- Modul für diesen Fachbereich ist installiert (siehe Administration → Module).",
        "- Ihre Rolle hat Lese- bzw. Schreibberechtigung für die jeweilige Maske.",
        "",
        PRESERVE_MARKER,
        "",
        f"Vollständige Abdeckung: **{len(routes_sorted)}** App-Routen",
        f"({len(nav_labels)} explizit in der Sidebar-Navigation).",
        "",
        "| Maske | Route | Modul |",
        "|-------|-------|-------|",
    ]
    for r in routes_sorted:
        lines.append(f"| {r.label} | `/{r.path}` | `{r.module}` |")

    lines.extend([
        "",
        "## Masken im Detail",
        "",
        "Für jede Route: Navigation, Bearbeitung, Ergebnis und typische Fehler.",
        "",
    ])

    for r in routes_sorted:
        lines.append(render_mask_section(r))

    lines.extend([
        "## Quellen und Reverse-Pflege",
        "",
        "- `packages/frontend-web/src/app/navigation/domains/*.tsx` — Sidebar-Navigation.",
        "- `packages/frontend-web/src/app/routing/route-inventory.gen.json` — Routen-Inventar.",
        "- `docs/MASKEN.md` — Layout-Standard (Gewohnheits-Prinzip).",
        "",
        "Reverse-Pflege: Bei neuen Routen Generator `scripts/generate_benutzerhandbuch_full.py`",
        "ausführen; `mkdocs.yml`, `index.md` und `generate_inapp_help_map.py` mitziehen.",
        "",
    ])
    return "\n".join(lines)


def merge_preserve_intro(existing: str, generated: str) -> str:
    if PRESERVE_MARKER not in existing:
        return generated
    intro = existing.split(PRESERVE_MARKER)[0].rstrip()
    registry_part = generated.split(PRESERVE_MARKER, 1)[1]
    return intro + "\n\n" + PRESERVE_MARKER + registry_part


def collect_nav() -> list[NavItem]:
    items: list[NavItem] = []
    for f in sorted(NAV_DIR.glob("*.tsx")):
        items.extend(parse_nav_file(f))
    return items


def generate_mkdocs_nav_entries() -> list[str]:
    entries = []
    meta_files = {"index.md", "glossar.md", "release-notes.md", "in-app-hilfe.md", "sonstige-masken.md"}
    for filename, title, _, _ in CHAPTERS:
        entries.append(f"      - {title}: benutzerhandbuch/{filename}")
    entries.append("      - Release Notes: benutzerhandbuch/release-notes.md")
    entries.append("      - Glossar: benutzerhandbuch/glossar.md")
    entries.append("      - In-App-Hilfe: benutzerhandbuch/in-app-hilfe.md")
    return entries


def update_index_md(by_chapter: dict[str, list[RouteEntry]]) -> None:
    index_path = HANDBUCH / "index.md"
    text = index_path.read_text(encoding="utf-8")
    # Bereiche-Block ersetzen
    start = text.find("## Bereiche")
    end = text.find("## Screenshots")
    if start == -1 or end == -1:
        return
    bullets = [
        "- [**Einstieg**](einstieg.md) - Anmeldung, Mandantenwahl, Navigation.",
    ]
    for filename, title, _, desc in CHAPTERS:
        if filename == "einstieg.md":
            continue
        count = len(by_chapter.get(filename, []))
        bullets.append(f"- [**{title}**]({filename}) - {desc} ({count} Masken).")
    bullets.extend([
        "- [**Release Notes**](release-notes.md) - Anwenderrelevante Änderungen.",
        "- [**Glossar**](glossar.md) - Fachbegriffe Landhandel/Agrar.",
        "- [**In-App-Hilfe**](in-app-hilfe.md) - kontextsensitive Deep-Links.",
    ])
    new_block = "## Bereiche\n\n" + "\n".join(bullets) + "\n\n"
    new_text = text[:start] + new_block + text[end:]
    # version bump
    new_text = re.sub(r"version: 3\.\d+\.\d+", f"version: 3.2.0", new_text, count=1)
    new_text = re.sub(r"last_reviewed: \d{4}-\d{2}-\d{2}", f"last_reviewed: {TODAY}", new_text, count=1)
    index_path.write_text(new_text, encoding="utf-8")


def run_check(by_chapter: dict[str, list[RouteEntry]], routes: list[RouteEntry]) -> int:
    assigned = sum(len(v) for k, v in by_chapter.items())
    total = len([r for r in routes if not r.path.startswith(ADMIN_PREFIXES)])
    print(f"Routen gesamt (ohne Admin): {total}")
    print(f"Zugeordnet: {assigned}")
    for filename, title, _, _ in CHAPTERS:
        n = len(by_chapter.get(filename, []))
        if n:
            print(f"  {filename}: {n}")
    extra = by_chapter.get("sonstige-masken.md", [])
    if extra:
        print(f"  sonstige-masken.md: {len(extra)} (UNZUGEORDNET)")
        for r in extra[:20]:
            print(f"    - /{r.path}")
    return 0 if not extra and assigned >= total - 5 else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    nav_items = collect_nav()
    routes = load_routes()
    labels = build_label_map(nav_items, routes)
    by_chapter = assign_routes(routes, labels)

    if args.check:
        return run_check(by_chapter, routes)

    HANDBUCH.mkdir(parents=True, exist_ok=True)
    chapter_meta = {c[0]: c for c in CHAPTERS}

    for filename, title, _, description in CHAPTERS:
        chapter_routes = by_chapter.get(filename, [])
        out_path = HANDBUCH / filename
        generated = render_chapter(filename, title, description, chapter_routes, nav_items)
        if out_path.exists():
            existing = out_path.read_text(encoding="utf-8")
            if PRESERVE_MARKER not in existing and "img/" in existing:
                # Legacy-Kapitel mit Screenshots: Intro behalten, Register anhängen
                split_at = existing.find("## Quellen")
                if split_at == -1:
                    split_at = existing.find("## Häufige Fehler")
                if split_at != -1:
                    intro = existing[:split_at].rstrip()
                    generated = intro + "\n\n" + PRESERVE_MARKER + generated.split(PRESERVE_MARKER, 1)[1]
                else:
                    generated = merge_preserve_intro(existing, generated)
            else:
                generated = merge_preserve_intro(existing, generated)
        out_path.write_text(generated, encoding="utf-8")
        print(f"Wrote {out_path.name} ({len(chapter_routes)} routes)")

    if "sonstige-masken.md" in by_chapter and by_chapter["sonstige-masken.md"]:
        extra_routes = by_chapter["sonstige-masken.md"]
        content = render_chapter(
            "sonstige-masken.md",
            "Sonstige Masken",
            "Routen ohne dediziertes Fachkapitel — werden bei Bedarf in Fachkapitel überführt.",
            extra_routes,
            nav_items,
        )
        (HANDBUCH / "sonstige-masken.md").write_text(content, encoding="utf-8")
        print(f"Wrote sonstige-masken.md ({len(extra_routes)} routes)")

    update_index_md(by_chapter)
    print("Updated index.md")
    return run_check(by_chapter, routes)


if __name__ == "__main__":
    raise SystemExit(main())
