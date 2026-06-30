import { describe, expect, it } from 'vitest'
import {
  DOCS_BASE_URL,
  DOCS_USER_MANUAL_URL,
  findHelpEntry,
  getEmbeddedHelpHref,
  HELP_ROUTE,
  resolveHelpUrl,
} from '@/lib/docs-help'

describe('docs-help', () => {
  it('liefert eine Basis-URL ohne abschließenden Slash', () => {
    expect(DOCS_BASE_URL.endsWith('/')).toBe(false)
    expect(DOCS_BASE_URL).toContain('jochenweerda.github.io')
  })

  it('verweist auf das Benutzerhandbuch als Standard-Einstieg', () => {
    expect(DOCS_USER_MANUAL_URL).toBe(`${DOCS_BASE_URL}/benutzerhandbuch/`)
  })

  it('mappt fachliche Routen kontextsensitiv auf Handbuch-Seiten', () => {
    expect(findHelpEntry('/verkauf/auftraege')?.url).toBe(`${DOCS_BASE_URL}/benutzerhandbuch/verkauf/`)
    expect(findHelpEntry('/einkauf')?.url).toBe(`${DOCS_BASE_URL}/benutzerhandbuch/einkauf/`)
    expect(findHelpEntry('/lager/wms/bestand')?.url).toBe(`${DOCS_BASE_URL}/benutzerhandbuch/lager/`)
    expect(findHelpEntry('/crm/kunden-stamm')?.url).toBe(`${DOCS_BASE_URL}/benutzerhandbuch/crm/`)
    expect(findHelpEntry('/fibu/buchungen')?.url).toBe(`${DOCS_BASE_URL}/benutzerhandbuch/finanzbuchhaltung/`)
  })

  it('bevorzugt das spezifischere Fragment (längster Prefix)', () => {
    expect(findHelpEntry('/agrar/annahme/erfassung')?.url).toBe(`${DOCS_BASE_URL}/benutzerhandbuch/annahme/`)
  })

  it('mappt erweiterte Fachrouten (POS, WMS, Mahnwesen) korrekt', () => {
    expect(findHelpEntry('/pos/terminal')?.url).toBe(`${DOCS_BASE_URL}/benutzerhandbuch/pos-kasse/`)
    expect(findHelpEntry('/lager/wms')?.url).toBe(`${DOCS_BASE_URL}/benutzerhandbuch/lager/`)
    expect(findHelpEntry('/mahnwesen/laeufe')?.url).toBe(`${DOCS_BASE_URL}/benutzerhandbuch/finanzbuchhaltung/`)
  })

  it('löst spezifische Admin-Deep-Links vor der Admin-Sektion auf', () => {
    expect(findHelpEntry('/admin/mandanten')?.url).toBe(`${DOCS_BASE_URL}/admin/mandanten-administration/`)
    expect(findHelpEntry('/admin/benutzer')?.url).toBe(`${DOCS_BASE_URL}/admin/rbac-und-rollen/`)
  })

  it('fällt ohne Zuordnung auf null zurück', () => {
    expect(findHelpEntry('/unbekannte-maske')).toBeNull()
    expect(findHelpEntry('/')).toBeNull()
    expect(findHelpEntry('')).toBeNull()
  })

  it('resolveHelpUrl baut vollständige URL aus docPath', () => {
    expect(resolveHelpUrl('benutzerhandbuch/verkauf')).toBe(`${DOCS_BASE_URL}/benutzerhandbuch/verkauf`)
    expect(resolveHelpUrl('https://extern.example.com/page')).toBe('https://extern.example.com/page')
  })

  it('baut den eingebetteten Hilfe-Link mit ctx-Parameter aus docPath', () => {
    const entry = findHelpEntry('/verkauf/auftraege')
    expect(entry).not.toBeNull()
    expect(getEmbeddedHelpHref('/verkauf/auftraege')).toBe(
      `${HELP_ROUTE}?ctx=${encodeURIComponent(entry!.docPath)}`,
    )
    expect(getEmbeddedHelpHref('')).toBe(HELP_ROUTE)
  })
})
