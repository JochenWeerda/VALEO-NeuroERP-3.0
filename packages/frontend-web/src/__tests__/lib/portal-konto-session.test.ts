import { afterEach, describe, expect, it, vi } from 'vitest'
import type { AxiosAdapter } from 'axios'
import { auth } from '@/lib/auth'
import { apiClient } from '@/lib/api-client'
import { aktivesKundenkonto, beginPortalInspection, endPortalInspection, isPortalInspection, portalSitzung, usePortalKonto } from '@/lib/portal-konto'

const token = (tenant: string) => `e30.${btoa(JSON.stringify({ tenant_id: tenant }))}.sig`
const konto = { customer_id: 'gleiche-id', customer_number: null, name: null, rolle: 'inhaber', rechte: [] }

describe('Portalkonto und Anmeldesitzung', () => {
  afterEach(() => {
    endPortalInspection()
    usePortalKonto.getState().waehle(null)
    vi.restoreAllMocks()
  })

  it('invalidates the selection for a new provider session without clearing drafts on token refresh', () => {
    let sid = 'session-one'
    vi.spyOn(auth, 'getUser').mockImplementation(() => ({ sub: 'person', email: '', name: '', roles: [], scopes: [], exp: 9999999999, iss: 'synthetic-provider', sid }))
    vi.spyOn(auth, 'getAccessToken').mockReturnValue(token('a'))
    usePortalKonto.getState().waehle(konto)
    expect(aktivesKundenkonto()).toBe('gleiche-id')
    const before = portalSitzung()
    expect(portalSitzung()).toBe(before)
    sid = 'session-two'
    expect(aktivesKundenkonto()).toBeNull()
    expect(isPortalInspection()).toBe(false)
  })

  it('sendet nach Mandantenwechsel keinen alten Kontokopf, auch bei gleicher Kunden-ID', async () => {
    let mandant = 'a'
    vi.spyOn(auth, 'getUser').mockImplementation(() => ({ sub: 'person', email: '', name: '', roles: [], scopes: [], exp: 9999999999 }))
    vi.spyOn(auth, 'getAccessToken').mockImplementation(() => token(mandant))
    vi.spyOn(auth, 'getFreshAccessToken').mockImplementation(async () => token(mandant))
    const headers: Array<string | undefined> = []
    const adapter: AxiosAdapter = async config => {
      headers.push(config.headers.get('X-Kundenkonto') as string | undefined)
      return { data: {}, status: 200, statusText: 'OK', headers: {}, config }
    }
    usePortalKonto.getState().waehle(konto)
    await apiClient.get('/api/v1/portal/rechnungen', { adapter })
    mandant = 'b'
    // Der Schutz im Request gilt auch vor einer UI-Aktualisierung.
    await apiClient.get('/api/v1/portal/rechnungen', { adapter })
    window.dispatchEvent(new Event('valeo-auth-changed'))
    expect(aktivesKundenkonto()).toBeNull()
    usePortalKonto.getState().waehle({ ...konto })
    await apiClient.get('/api/v1/portal/rechnungen', { adapter })
    expect(headers).toEqual(['gleiche-id', undefined, 'gleiche-id'])
  })

  it('verwirft die Wahl beim Logout und erneuter Anmeldung derselben Person', () => {
    let angemeldet = true
    vi.spyOn(auth, 'getUser').mockImplementation(() => angemeldet ? { sub: 'person', email: '', name: '', roles: [], scopes: [], exp: 9999999999 } : null)
    vi.spyOn(auth, 'getAccessToken').mockImplementation(() => angemeldet ? token('a') : null)
    usePortalKonto.getState().waehle(konto)
    const fingerprint = portalSitzung()
    expect(fingerprint).not.toContain(token('a'))
    angemeldet = false
    window.dispatchEvent(new Event('valeo-auth-changed'))
    angemeldet = true
    window.dispatchEvent(new Event('valeo-auth-changed'))
    expect(portalSitzung()).toBe(fingerprint)
    expect(aktivesKundenkonto()).toBeNull()
  })

  it('verwirft bei geaenderten Rollen oder Scopes die alte Auswahl sofort', async () => {
    let roles = ['SALES_LESEN']
    let scopes = ['portal:read']
    vi.spyOn(auth, 'getUser').mockImplementation(() => ({ sub: 'person', email: '', name: '', roles, scopes, exp: 9999999999 }))
    vi.spyOn(auth, 'getAccessToken').mockReturnValue(token('a'))
    vi.spyOn(auth, 'getFreshAccessToken').mockResolvedValue(token('a'))
    const headers: Array<string | undefined> = []
    const adapter: AxiosAdapter = async config => {
      headers.push(config.headers.get('X-Kundenkonto') as string | undefined)
      return { data: {}, status: 200, statusText: 'OK', headers: {}, config }
    }
    usePortalKonto.getState().waehle(konto)
    roles = []
    await apiClient.get('/api/v1/portal/rechnungen', { adapter })
    window.dispatchEvent(new Event('valeo-auth-changed'))
    expect(usePortalKonto.getState().aktiv).toBeNull()
    usePortalKonto.getState().waehle(konto)
    scopes = []
    await apiClient.get('/api/v1/portal/rechnungen', { adapter })
    expect(headers).toEqual([undefined, undefined])
  })

  it('haelt die Pruefansicht beim Kontowechsel und beendet sie bei Kontextwechsel oder Ende', () => {
    let tenant = 'a'
    let roles = ['SALES_LESEN']
    let signedIn = true
    vi.spyOn(auth, 'getUser').mockImplementation(() => signedIn ? { sub: 'person', email: '', name: '', roles, scopes: [], exp: 9999999999 } : null)
    vi.spyOn(auth, 'getAccessToken').mockImplementation(() => signedIn ? token(tenant) : null)
    usePortalKonto.getState().waehle(konto)
    expect(beginPortalInspection()).toBe(true)
    expect(aktivesKundenkonto()).toBeNull()
    usePortalKonto.getState().waehle(konto)
    expect(isPortalInspection()).toBe(true)
    tenant = 'b'
    expect(isPortalInspection()).toBe(false)
    window.dispatchEvent(new Event('valeo-auth-changed'))
    expect(usePortalKonto.getState().pruefansicht).toBe(false)
    expect(beginPortalInspection()).toBe(true)
    roles = []
    window.dispatchEvent(new Event('valeo-auth-changed'))
    expect(isPortalInspection()).toBe(false)
    expect(beginPortalInspection()).toBe(true)
    endPortalInspection()
    expect(isPortalInspection()).toBe(false)
    signedIn = false
    expect(beginPortalInspection()).toBe(false)
  })
})
