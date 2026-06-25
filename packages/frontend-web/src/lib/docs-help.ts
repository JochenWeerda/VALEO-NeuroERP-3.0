/**
 * In-App-Hilfe: Verknüpfung der laufenden Anwendung mit der MkDocs-Dokumentation.
 *
 * Stufe 1: Hilfe-/Dokumentations-Einstieg (externe Doku-Site, neuer Tab).
 * Stufe 2: kontextsensitives Mapping `Routen-Pfad → Handbuch-Seite`
 *          (fachliche Referenz: `docs/benutzerhandbuch/in-app-hilfe.md`).
 *
 * Die Basis-URL ist über `VITE_DOCS_URL` konfigurierbar (siehe `.env.example`);
 * Fallback ist die veröffentlichte GitHub-Pages-Site (vgl. `mkdocs.yml#site_url`).
 */

const DEFAULT_DOCS_BASE = 'https://jochenweerda.github.io/VALEO-NeuroERP-3.0/'

/** Basis-URL der Doku-Site, garantiert mit abschließendem Slash. */
export const DOCS_BASE_URL: string = (
  (import.meta.env.VITE_DOCS_URL as string | undefined) || DEFAULT_DOCS_BASE
).replace(/\/?$/, '/')

/** Startseite des Benutzerhandbuchs. */
export const DOCS_USER_MANUAL_URL = `${DOCS_BASE_URL}benutzerhandbuch/`

/** In-App-Route der eingebetteten Hilfe (siehe `src/pages/hilfe.tsx`). */
export const HELP_ROUTE = '/hilfe'

/**
 * Mapping: Routen-Pfad-Fragment → Doku-Seite (relativ zur Basis).
 * Aufgelöst per Längster-Prefix-Match, daher reicht das jeweils kürzeste
 * eindeutige Fragment. Erweiterung erfolgt gemeinsam mit neuen Masken.
 *
 * Wichtig: Ziele müssen existierende Doku-Seiten sein (siehe `mkdocs.yml`),
 * sonst läuft der Deep-Link ins Leere.
 */
const ROUTE_DOC_MAP: Record<string, string> = {
  // --- Ernteannahme / Waage ---
  'agrar/annahme': 'benutzerhandbuch/annahme/',
  'agrar/ernte': 'benutzerhandbuch/annahme/',
  annahme: 'benutzerhandbuch/annahme/',
  waage: 'benutzerhandbuch/annahme/',
  weighing: 'benutzerhandbuch/annahme/',
  ernte: 'benutzerhandbuch/annahme/',
  // --- Verkauf / Vertrieb / POS ---
  verkauf: 'benutzerhandbuch/verkauf/',
  sales: 'benutzerhandbuch/verkauf/',
  vertrieb: 'benutzerhandbuch/verkauf/',
  auftrag: 'benutzerhandbuch/verkauf/',
  angebot: 'benutzerhandbuch/verkauf/',
  rechnung: 'benutzerhandbuch/verkauf/',
  lieferschein: 'benutzerhandbuch/verkauf/',
  pos: 'benutzerhandbuch/verkauf/',
  kasse: 'benutzerhandbuch/verkauf/',
  // --- Einkauf / Beschaffung ---
  einkauf: 'benutzerhandbuch/einkauf/',
  beschaffung: 'benutzerhandbuch/einkauf/',
  bestellung: 'benutzerhandbuch/einkauf/',
  lieferanten: 'benutzerhandbuch/einkauf/',
  // --- Lager / Bestand / Inventur ---
  lager: 'benutzerhandbuch/lager/',
  wms: 'benutzerhandbuch/lager/',
  bestand: 'benutzerhandbuch/lager/',
  inventur: 'benutzerhandbuch/lager/',
  inventory: 'benutzerhandbuch/lager/',
  'stock-management': 'benutzerhandbuch/lager/',
  silo: 'benutzerhandbuch/lager/',
  // --- CRM / Marketing ---
  crm: 'benutzerhandbuch/crm/',
  kontakte: 'benutzerhandbuch/crm/',
  leads: 'benutzerhandbuch/crm/',
  marketing: 'benutzerhandbuch/crm/',
  prospecting: 'benutzerhandbuch/crm/',
  // --- Finanzbuchhaltung ---
  fibu: 'benutzerhandbuch/finanzbuchhaltung/',
  finanz: 'benutzerhandbuch/finanzbuchhaltung/',
  finanzen: 'benutzerhandbuch/finanzbuchhaltung/',
  finance: 'benutzerhandbuch/finanzbuchhaltung/',
  finanzplanung: 'benutzerhandbuch/finanzbuchhaltung/',
  mahnwesen: 'benutzerhandbuch/finanzbuchhaltung/',
  banken: 'benutzerhandbuch/finanzbuchhaltung/',
  controlling: 'benutzerhandbuch/finanzbuchhaltung/',
  // --- Administration & Betrieb (spezifisch vor allgemein) ---
  'admin/mandanten': 'admin/mandanten-administration/',
  'admin/module': 'admin/module-und-feature-flags/',
  'admin/rbac': 'admin/rbac-und-rollen/',
  'admin/deployment': 'admin/deployment/',
  'admin/backup': 'admin/backup-restore/',
  'admin/datenbank': 'admin/datenbank-migrationen/',
  'admin/migrationen': 'admin/datenbank-migrationen/',
  'admin/monitoring': 'admin/monitoring-und-slo/',
  'admin/incident': 'admin/incident-response/',
  'admin/skalierung': 'admin/skalierung-performance/',
  admin: 'admin/',
  'admin-suite': 'admin/',
  // --- Schnittstellen / Integrationen ---
  schnittstellen: 'schnittstellen/',
  integrationen: 'schnittstellen/',
  // --- Agenten / KI-Automatisierung ---
  agent: 'agent-docs/',
  agenten: 'agent-docs/',
}

/**
 * Ermittelt die passende Handbuch-URL für einen App-Pfad.
 * Fällt ohne spezifische Zuordnung auf die Benutzerhandbuch-Startseite zurück.
 */
export function resolveHelpUrl(pathname: string): string {
  const clean = (pathname || '').replace(/^\/+/, '').toLowerCase()
  const keys = Object.keys(ROUTE_DOC_MAP).sort((a, b) => b.length - a.length)
  for (const key of keys) {
    if (clean === key || clean.startsWith(`${key}/`)) {
      return `${DOCS_BASE_URL}${ROUTE_DOC_MAP[key]}`
    }
  }
  return DOCS_USER_MANUAL_URL
}

/** Öffnet die kontextsensitive Hilfe in einem neuen Tab. */
export function openHelp(pathname?: string): void {
  if (typeof window === 'undefined') return
  const path = pathname ?? window.location.pathname
  window.open(resolveHelpUrl(path), '_blank', 'noopener,noreferrer')
}

/** Öffnet eine feste Doku-URL (z. B. Handbuch-Startseite) in einem neuen Tab. */
export function openDocs(url: string = DOCS_USER_MANUAL_URL): void {
  if (typeof window === 'undefined') return
  window.open(url, '_blank', 'noopener,noreferrer')
}

/**
 * Liefert den In-App-Link zur eingebetteten Hilfe (`/hilfe`).
 * Der ursprüngliche App-Pfad wird als `ctx` übergeben, damit die Hilfe-Seite
 * die passende Handbuch-Seite einbettet (Stufe 2).
 */
export function getEmbeddedHelpHref(pathname?: string): string {
  const ctx = (pathname ?? (typeof window !== 'undefined' ? window.location.pathname : '')) || ''
  return ctx ? `${HELP_ROUTE}?ctx=${encodeURIComponent(ctx)}` : HELP_ROUTE
}
