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

/**
 * Mapping: Routen-Pfad-Fragment → Doku-Seite (relativ zur Basis).
 * Aufgelöst per Längster-Prefix-Match, daher reicht das jeweils kürzeste
 * eindeutige Fragment. Erweiterung erfolgt gemeinsam mit neuen Masken.
 */
const ROUTE_DOC_MAP: Record<string, string> = {
  'agrar/annahme': 'benutzerhandbuch/annahme/',
  'agrar/ernte': 'benutzerhandbuch/annahme/',
  annahme: 'benutzerhandbuch/annahme/',
  waage: 'benutzerhandbuch/annahme/',
  verkauf: 'benutzerhandbuch/verkauf/',
  sales: 'benutzerhandbuch/verkauf/',
  einkauf: 'benutzerhandbuch/einkauf/',
  lager: 'benutzerhandbuch/lager/',
  crm: 'benutzerhandbuch/crm/',
  fibu: 'benutzerhandbuch/finanzbuchhaltung/',
  finanz: 'benutzerhandbuch/finanzbuchhaltung/',
  finanzen: 'benutzerhandbuch/finanzbuchhaltung/',
  finance: 'benutzerhandbuch/finanzbuchhaltung/',
  admin: 'admin/',
  schnittstellen: 'schnittstellen/',
  integrationen: 'schnittstellen/',
  agent: 'agent-docs/',
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
