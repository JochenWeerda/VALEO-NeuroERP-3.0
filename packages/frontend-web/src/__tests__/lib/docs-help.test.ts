import { describe, expect, it } from 'vitest'
import { DOCS_BASE_URL, DOCS_USER_MANUAL_URL, resolveHelpUrl } from '@/lib/docs-help'

describe('docs-help', () => {
  it('liefert eine Basis-URL mit abschließendem Slash', () => {
    expect(DOCS_BASE_URL.endsWith('/')).toBe(true)
  })

  it('verweist auf das Benutzerhandbuch als Standard-Einstieg', () => {
    expect(DOCS_USER_MANUAL_URL).toBe(`${DOCS_BASE_URL}benutzerhandbuch/`)
  })

  it('mappt fachliche Routen kontextsensitiv auf Handbuch-Seiten', () => {
    expect(resolveHelpUrl('/verkauf/auftraege')).toBe(`${DOCS_BASE_URL}benutzerhandbuch/verkauf/`)
    expect(resolveHelpUrl('/einkauf')).toBe(`${DOCS_BASE_URL}benutzerhandbuch/einkauf/`)
    expect(resolveHelpUrl('/lager/wms/bestand')).toBe(`${DOCS_BASE_URL}benutzerhandbuch/lager/`)
    expect(resolveHelpUrl('/crm/kunden-stamm')).toBe(`${DOCS_BASE_URL}benutzerhandbuch/crm/`)
    expect(resolveHelpUrl('/fibu/buchungen')).toBe(`${DOCS_BASE_URL}benutzerhandbuch/finanzbuchhaltung/`)
  })

  it('bevorzugt das spezifischere Fragment (längster Prefix)', () => {
    expect(resolveHelpUrl('/agrar/annahme/erfassung')).toBe(`${DOCS_BASE_URL}benutzerhandbuch/annahme/`)
  })

  it('mappt Admin- und Schnittstellen-Routen auf ihre Doku-Sektionen', () => {
    expect(resolveHelpUrl('/admin/mandanten')).toBe(`${DOCS_BASE_URL}admin/`)
    expect(resolveHelpUrl('/schnittstellen/rest')).toBe(`${DOCS_BASE_URL}schnittstellen/`)
  })

  it('fällt ohne Zuordnung auf das Benutzerhandbuch zurück', () => {
    expect(resolveHelpUrl('/unbekannte-maske')).toBe(DOCS_USER_MANUAL_URL)
    expect(resolveHelpUrl('/')).toBe(DOCS_USER_MANUAL_URL)
    expect(resolveHelpUrl('')).toBe(DOCS_USER_MANUAL_URL)
  })
})
