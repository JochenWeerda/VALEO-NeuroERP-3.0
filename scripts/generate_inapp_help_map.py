"""Generiert route→Doku-Mapping für DOC-INAPP-HELP-002 (Top-50 Routen)."""
import json
from pathlib import Path
from datetime import date

REPO = Path(__file__).parent.parent
DOCS_BASE = "https://jochenweerda.github.io/VALEO-NeuroERP-3.0"

# Lade Route-Inventory
ri = json.loads((REPO / "packages/frontend-web/src/app/routing/route-inventory.gen.json").read_text(encoding="utf-8"))
routes = ri.get("routes", [])

# Mapping: path-prefix → docs-Ziel
# Reihenfolge: spezifischer zuerst
HELP_MAP = [
    # Agrar / Ernteannahme
    ("agrar/annahme",           "benutzerhandbuch/annahme",          "Ernteannahme"),
    ("agrar/partie",            "benutzerhandbuch/annahme",          "Partie-Verwaltung"),
    ("agrar/kontrakt",          "benutzerhandbuch/agrar-kontrakte",  "Agrar-Kontrakte"),
    ("agrar/kontrakte",         "benutzerhandbuch/agrar-kontrakte",  "Agrar-Kontrakte"),
    ("agrar/wetter",            "benutzerhandbuch/annahme",          "Wetter & Prognose"),
    ("agrar",                   "benutzerhandbuch/annahme",          "Agrar-Modul"),

    # NaWaRo
    ("nawaro",                  "benutzerhandbuch/nawaro",           "NaWaRo-Meldungen"),
    ("strecke/nawaro",          "benutzerhandbuch/nawaro",           "NaWaRo Streckengeschäft"),

    # Genossenschaft
    ("genossenschaft",          "benutzerhandbuch/genossenschaft",   "Genossenschaft"),

    # Verkauf / O2C
    ("verkauf/auftrag",         "benutzerhandbuch/verkauf",          "Verkaufsauftrag"),
    ("verkauf/lieferschein",    "benutzerhandbuch/verkauf",          "Lieferschein"),
    ("verkauf/rechnung",        "benutzerhandbuch/verkauf",          "Ausgangsrechnung"),
    ("verkauf/angebot",         "benutzerhandbuch/verkauf",          "Angebot"),
    ("verkauf",                 "benutzerhandbuch/verkauf",          "Verkauf"),

    # Einkauf / P2P
    ("einkauf/bestellung",      "benutzerhandbuch/einkauf",          "Bestellung"),
    ("einkauf/wareneingang",    "benutzerhandbuch/einkauf",          "Wareneingang"),
    ("einkauf/rechnung",        "benutzerhandbuch/einkauf",          "Eingangsrechnung"),
    ("einkauf",                 "benutzerhandbuch/einkauf",          "Einkauf"),

    # Lager / WMS
    ("lager/einlagerung",       "benutzerhandbuch/lager",            "Einlagerung"),
    ("lager/auslagerung",       "benutzerhandbuch/lager",            "Auslagerung"),
    ("lager/inventur",          "benutzerhandbuch/lager",            "Inventur"),
    ("lager/qs-leitstand",      "benutzerhandbuch/qualitaetssicherung","QS-Leitstand"),
    ("lager",                   "benutzerhandbuch/lager",            "Lager"),

    # Finanzbuchhaltung / Controlling
    ("fibu/buchungen",          "benutzerhandbuch/finanzbuchhaltung","Buchungsjournal"),
    ("fibu/offene-posten",      "benutzerhandbuch/finanzbuchhaltung","Offene Posten"),
    ("fibu/zahlungslaeufe",     "benutzerhandbuch/finanzbuchhaltung","Zahlungsläufe"),
    ("fibu/periodenabschluss",  "benutzerhandbuch/finanzbuchhaltung","Periodenabschluss"),
    ("fibu/datev",              "benutzerhandbuch/finanzbuchhaltung","DATEV-Export"),
    ("fibu",                    "benutzerhandbuch/finanzbuchhaltung","Finanzbuchhaltung"),
    ("controlling",             "benutzerhandbuch/controlling-kostenrechnung","Controlling"),

    # POS / Personal
    ("pos",                     "benutzerhandbuch/pos-kasse",        "POS und Kasse"),
    ("kasse",                   "benutzerhandbuch/pos-kasse",        "Kasse"),
    ("personal",                "benutzerhandbuch/personal-lohn",  "Personal und Lohn"),
    ("hr",                      "benutzerhandbuch/personal-lohn",  "Personal und Lohn"),

    # Produktion
    ("produktion",              "benutzerhandbuch/futtermittel-produktion","Futtermittel/Produktion"),
    ("mischfutter",             "benutzerhandbuch/futtermittel-produktion","Futtermittel/Produktion"),

    # CRM
    ("crm/kunden",              "benutzerhandbuch/crm",              "Kundenstamm"),
    ("crm/leads",               "benutzerhandbuch/crm",              "Leads"),
    ("crm/kampagnen",           "benutzerhandbuch/crm",              "Kampagnen"),
    ("crm/kim",                 "benutzerhandbuch/crm",              "KI-Kundencockpit (KIM)"),
    ("crm",                     "benutzerhandbuch/crm",              "CRM"),

    # Admin / Betrieb
    ("admin/mandanten",         "admin/mandanten-administration",    "Mandanten-Administration"),
    ("admin/benutzer",          "admin/rbac-und-rollen",             "Benutzer & Rollen"),
    ("admin/module",            "admin/module-und-feature-flags",    "Module & Feature-Flags"),
    ("admin/externe-gates",     "admin/monitoring-und-slo",          "Externe Gate-Dashboards"),
    ("admin/ai-approvals",      "agent-docs/guardrails",             "AI-Freigaben"),
    ("admin",                   "admin/index",                       "Administration"),

    # Compliance (Endnutzer-Meldewesen)
    ("compliance/meldewesen",   "benutzerhandbuch/compliance-meldewesen","Compliance/Meldewesen"),
    ("meldewesen",              "benutzerhandbuch/compliance-meldewesen","Meldewesen"),
    ("compliance/gobd",         "compliance/gobd-checklist",         "GoBD-Prüfung"),
    ("compliance/datenschutz",  "compliance/gdpr-checklist",         "Datenschutz (DSGVO)"),
    ("compliance",              "benutzerhandbuch/compliance-meldewesen","Compliance"),

    # Kontrakte (Navigation root)
    ("kontrakte/preisfixierung","benutzerhandbuch/agrar-kontrakte",  "Preisfixierung"),
    ("kontrakte",               "benutzerhandbuch/agrar-kontrakte",  "Kontrakte"),

    # Logistik
    ("logistik/disposition",    "benutzerhandbuch/logistik",         "Disposition"),
    ("logistik/touren",         "benutzerhandbuch/logistik",         "Tourenplanung"),
    ("logistik/frachtbriefe",   "benutzerhandbuch/logistik",         "Frachtbriefe"),
    ("logistik",                "benutzerhandbuch/logistik",         "Logistik"),

    # Dokumente / DMS
    ("dokumente",               "benutzerhandbuch/dokumente-belegarchiv","Dokumente"),
    ("fuhrpark/ausgehende",     "benutzerhandbuch/dokumente-belegarchiv","Ausgehende Belege"),
    ("strecke/dokumente",       "benutzerhandbuch/dokumente-belegarchiv","Strecken-Dokumente"),

    # Workflow / Betrieb
    ("workflow/leitstand",      "schnittstellen/events",             "Workflow-Leitstand"),
    ("workflow",                "schnittstellen/events",             "Workflow"),

    # Schnittstellen
    ("api-docs",                "schnittstellen/rest-api",           "API-Dokumentation"),
]

def find_doc(path: str) -> tuple[str, str] | None:
    for prefix, doc_path, label in HELP_MAP:
        if path == prefix or path.startswith(prefix + "/"):
            return doc_path, label
    return None

# Top-50 priorisierte Routen (auto + alias, keine generated-only)
priority_routes = []
for r in routes:
    path = r.get("path", "")
    if not path or path in ("", "/"):
        continue
    match = find_doc(path)
    if match:
        priority_routes.append({
            "path": path,
            "module": r.get("module", ""),
            "doc_path": match[0],
            "doc_label": match[1],
            "doc_url": f"{DOCS_BASE}/{match[0]}/",
        })

# Deduplizieren nach path
seen = set()
deduped = []
for r in priority_routes:
    if r["path"] not in seen:
        seen.add(r["path"])
        deduped.append(r)

top50 = deduped[:50]
print(f"Mapped: {len(top50)} Routen")

# ── TypeScript Mapping-Datei ───────────────────────────────────────────────────
ts_entries = []
for r in top50:
    ts_entries.append(
        f'  "{r["path"]}": {{ docPath: "{r["doc_path"]}", label: "{r["doc_label"]}", url: "{r["doc_url"]}" }},'
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

# ── MkDocs-Seite: In-App-Hilfe-Konzept ────────────────────────────────────────
md_lines = [
    "---",
    "title: In-App-Hilfe (Route → Dokumentation)",
    "description: Mapping von Frontend-Routen auf Dokumentationsseiten für die In-App-Hilfe.",
    "type: reference",
    "audience: [entwickler]",
    "owner: Claude Code",
    "status: aktiv",
    f"last_reviewed: {date.today().isoformat()}",
    "version: 3.0.0",
    "---",
    "",
    "# In-App-Hilfe — Route → Dokumentation",
    "",
    "> Slice: **DOC-INAPP-HELP-002**",
    "> Mapping: [`src/lib/docs-help.ts`](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/blob/main/packages/frontend-web/src/lib/docs-help.ts)",
    "",
    "## Konzept",
    "",
    "Der Hook `useInAppHelp()` liest die aktuelle Route, sucht den längsten Präfix-Treffer",
    "in `ROUTE_HELP_MAP` und öffnet die passende MkDocs-Seite.",
    "",
    "```ts",
    "import { findHelpEntry } from '@/lib/docs-help';",
    "",
    "// In einer Komponente:",
    "const entry = findHelpEntry('verkauf/auftrag/123');",
    "// → { label: 'Verkaufsauftrag', url: 'https://.../benutzerhandbuch/verkauf/' }",
    "```",
    "",
    "## Gemappte Routen",
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
    "1. `scripts/generate_inapp_help_map.py` — `HELP_MAP` erweitern",
    "2. Script neu ausführen: `python scripts/generate_inapp_help_map.py`",
    "3. `src/lib/docs-help.ts` committen",
    "",
    f"*Stand: {date.today().isoformat()} · {len(top50)} Routen gemappt · Slice: DOC-INAPP-HELP-002*",
]

(REPO / "docs/benutzerhandbuch/in-app-hilfe.md").write_text("\n".join(md_lines), encoding="utf-8")
print(f"Geschrieben: docs/benutzerhandbuch/in-app-hilfe.md ({len(top50)} Einträge)")
