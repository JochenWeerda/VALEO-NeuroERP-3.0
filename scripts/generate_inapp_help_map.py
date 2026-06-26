"""Generiert route→Doku-Mapping für In-App-Hilfe (vollständige Fach-Routen).

DOC-USER-MANUAL-004: HELP_MAP wird aus scripts/generate_benutzerhandbuch_full.CHAPTERS
abgeleitet; Admin-/Entwickler-Routen bleiben manuell kuratiert.
"""
import importlib.util
import json
import sys
from pathlib import Path
from datetime import date

REPO = Path(__file__).parent.parent
DOCS_BASE = "https://jochenweerda.github.io/VALEO-NeuroERP-3.0"

# Handbuch-Kapitel laden (gemeinsame Zuordnungslogik)
_spec = importlib.util.spec_from_file_location(
    "benutzerhandbuch_full",
    REPO / "scripts" / "generate_benutzerhandbuch_full.py",
)
_bh = importlib.util.module_from_spec(_spec)
sys.modules["benutzerhandbuch_full"] = _bh
_spec.loader.exec_module(_bh)

ri = json.loads(
    (REPO / "packages/frontend-web/src/app/routing/route-inventory.gen.json").read_text(
        encoding="utf-8"
    )
)
routes = ri.get("routes", [])

# Admin / Entwickler (nicht Benutzerhandbuch)
ADMIN_HELP_MAP: list[tuple[str, str, str]] = [
    ("admin/mandanten", "admin/mandanten-administration", "Mandanten-Administration"),
    ("admin/benutzer", "admin/rbac-und-rollen", "Benutzer & Rollen"),
    ("admin/module", "admin/module-und-feature-flags", "Module & Feature-Flags"),
    ("admin/externe-gates", "admin/monitoring-und-slo", "Externe Gate-Dashboards"),
    ("admin/ai-approvals", "agent-docs/guardrails", "AI-Freigaben"),
    ("admin-suite", "admin/index", "Administration"),
    ("admin", "admin/index", "Administration"),
    ("compliance/gobd", "compliance/gobd-checklist", "GoBD-Prüfung"),
    ("compliance/datenschutz", "compliance/gdpr-checklist", "Datenschutz (DSGVO)"),
    ("api-docs", "schnittstellen/rest-api", "API-Dokumentation"),
]


def build_help_map() -> list[tuple[str, str, str]]:
    entries: list[tuple[str, str, str]] = []
    for filename, title, prefixes, _desc in _bh.CHAPTERS:
        doc_path = f"benutzerhandbuch/{filename.removesuffix('.md')}"
        for prefix in prefixes:
            entries.append((prefix.rstrip("/"), doc_path, title))
    entries.extend(ADMIN_HELP_MAP)
    # Längster Präfix zuerst
    entries.sort(key=lambda x: len(x[0]), reverse=True)
    return entries


HELP_MAP = build_help_map()


def find_doc(path: str) -> tuple[str, str] | None:
    if not path:
        ch = _bh.match_chapter("")
        if ch:
            return f"benutzerhandbuch/{ch[0].removesuffix('.md')}", ch[1]
        return "benutzerhandbuch/dashboard-workflows", "Dashboard und Workflows"
    for prefix, doc_path, label in HELP_MAP:
        if path == prefix or path.startswith(prefix + "/"):
            return doc_path, label
    ch = _bh.match_chapter(path)
    if ch:
        return f"benutzerhandbuch/{ch[0].removesuffix('.md')}", ch[1]
    return None


# Alle Routen mit Treffer (für Doku-Tabelle)
mapped_routes = []
for r in routes:
    path = (r.get("path") or "").strip().lstrip("/")
    match = find_doc(path)
    if match:
        mapped_routes.append(
            {
                "path": path or "(start)",
                "module": r.get("module", ""),
                "doc_path": match[0],
                "doc_label": match[1],
                "doc_url": f"{DOCS_BASE}/{match[0]}/",
            }
        )

seen: set[str] = set()
deduped = []
for r in mapped_routes:
    if r["path"] not in seen:
        seen.add(r["path"])
        deduped.append(r)

# ROUTE_HELP_MAP: ein Eintrag pro HELP_MAP-Präfix (längster zuerst in findHelpEntry)
prefix_entries: dict[str, dict] = {}
for prefix, doc_path, label in HELP_MAP:
    if prefix not in prefix_entries:
        prefix_entries[prefix] = {
            "docPath": doc_path,
            "label": label,
            "url": f"{DOCS_BASE}/{doc_path}/",
        }

sorted_prefixes = sorted(prefix_entries.keys(), key=len, reverse=True)
print(f"HELP_MAP-Präfixe: {len(sorted_prefixes)} · gemappte Routen: {len(deduped)}")

ts_entries = []
for prefix in sorted_prefixes:
    e = prefix_entries[prefix]
    ts_entries.append(
        f'  "{prefix}": {{ docPath: "{e["docPath"]}", label: "{e["label"]}", url: "{e["url"]}" }},'
    )

ts_content = f"""// DOC-INAPP-HELP-002 — Route → Dokumentation Mapping
// Generiert via scripts/generate_inapp_help_map.py
// Stand: {date.today().isoformat()}
// Nicht manuell bearbeiten — aus route-inventory.gen.json + HELP_MAP generiert.

export interface HelpEntry {{
  docPath: string;
  label: string;
  url: string;
}}

/** Vollständige Docs-Basis-URL */
export const DOCS_BASE_URL = "{DOCS_BASE}";

/**
 * Mapping von Route-Pfad-Präfix → Hilfe-Seite.
 * Wird von useInAppHelp() verwendet um die passende Doku zur aktuellen Route zu finden.
 */
export const ROUTE_HELP_MAP: Record<string, HelpEntry> = {{
{chr(10).join(ts_entries)}
}};

/**
 * Findet den passenden Hilfe-Eintrag für einen gegebenen Pfad.
 * Längster Präfix gewinnt.
 */
export function findHelpEntry(currentPath: string): HelpEntry | null {{
  const normalised = currentPath.replace(/^\\//, "").replace(/\\/$/, "");
  // Längsten Präfix zuerst prüfen
  const entries = Object.entries(ROUTE_HELP_MAP).sort(
    ([a], [b]) => b.length - a.length
  );
  for (const [prefix, entry] of entries) {{
    if (normalised === prefix || normalised.startsWith(prefix + "/")) {{
      return entry;
    }}
  }}
  return null;
}}

/** Route der eingebetteten Hilfeseite */
export const HELP_ROUTE = '/hilfe';

/** URL des Benutzerhandbuchs */
export const DOCS_USER_MANUAL_URL = `${{DOCS_BASE_URL}}/benutzerhandbuch/`;

/** Gibt die Hilfe-URL für einen gegebenen App-Pfad zurück. */
export function getEmbeddedHelpHref(currentPath: string): string {{
  const entry = findHelpEntry(currentPath);
  return entry ? `${{HELP_ROUTE}}?ctx=${{encodeURIComponent(entry.docPath)}}` : HELP_ROUTE;
}}

/** Löst einen doc-Pfad oder -Schlüssel zur vollständigen Hilfe-URL auf. */
export function resolveHelpUrl(docPath: string): string {{
  return docPath.startsWith('http') ? docPath : `${{DOCS_BASE_URL}}/${{docPath}}`;
}}

/** Öffnet eine Docs-URL im neuen Tab. */
export function openDocs(url: string): void {{
  window.open(url, '_blank', 'noopener,noreferrer');
}}
"""

ts_path = REPO / "packages/frontend-web/src/lib/docs-help.ts"
ts_path.write_text(ts_content, encoding="utf-8")
print(f"Geschrieben: {ts_path}")

# MkDocs-Seite: In-App-Hilfe (Top-50 Beispiele + Gesamtzahl)
top50 = deduped[:50]
md_lines = [
    "---",
    "title: In-App-Hilfe (Route → Dokumentation)",
    "description: Mapping von Frontend-Routen auf Dokumentationsseiten für die In-App-Hilfe.",
    "type: reference",
    "audience: [entwickler, endnutzer]",
    "owner: Cursor",
    "status: aktiv",
    f"last_reviewed: {date.today().isoformat()}",
    "version: 3.2.0",
    "---",
    "",
    "# In-App-Hilfe — Route → Dokumentation",
    "",
    "> Slice: **DOC-USER-MANUAL-004** / **DOC-INAPP-HELP-002**",
    "> Mapping: [`src/lib/docs-help.ts`](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/blob/main/packages/frontend-web/src/lib/docs-help.ts)",
    "",
    "## Konzept",
    "",
    "Der Hook `useInAppHelp()` liest die aktuelle Route, sucht den längsten Präfix-Treffer",
    "in `ROUTE_HELP_MAP` und öffnet die passende MkDocs-Seite im Benutzerhandbuch.",
    "",
    f"**Abdeckung:** {len(deduped)} App-Routen → {len(sorted_prefixes)} Präfix-Einträge.",
    "",
    "## Beispiel-Routen (Auszug)",
    "",
    "| Route-Präfix | Hilfe-Seite | Label |",
    "|---|---|---|",
]
for r in top50:
    md_lines.append(f"| `{r['path']}` | [{r['doc_label']}]({r['doc_url']}) | {r['doc_label']} |")

md_lines += [
    "",
    "## Erweiterung",
    "",
    "1. `scripts/generate_benutzerhandbuch_full.py` — Kapitel/Präfixe pflegen",
    "2. `python scripts/generate_inapp_help_map.py`",
    "3. `src/lib/docs-help.ts` committen",
    "",
    f"*Stand: {date.today().isoformat()} · {len(deduped)} Routen gemappt · Slice: DOC-USER-MANUAL-004*",
]

(REPO / "docs/benutzerhandbuch/in-app-hilfe.md").write_text("\n".join(md_lines), encoding="utf-8")
print(f"Geschrieben: docs/benutzerhandbuch/in-app-hilfe.md")
