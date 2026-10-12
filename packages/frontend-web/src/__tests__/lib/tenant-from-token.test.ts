import { describe, expect, it } from 'vitest'
import { tenantFromToken } from '@/lib/tenant-from-token'

const jwt = (claims: Record<string, unknown>): string => {
  const teil = (wert: unknown) =>
    btoa(unescape(encodeURIComponent(JSON.stringify(wert)))).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
  return `${teil({ alg: 'RS256' })}.${teil(claims)}.signatur`
}

// Seit 12.10.2026 lehnt das Backend ab, wenn X-Tenant-ID nicht der Mandant des Tokens ist.
describe('tenantFromToken', () => {
  it('liest den Mandanten der Anmeldung', () => {
    expect(tenantFromToken(jwt({ sub: 'a', tenant_id: 'haus-a' }))).toBe('haus-a')
    expect(tenantFromToken(jwt({ mandanten_id: 'haus-a' }))).toBe('haus-a')
    expect(tenantFromToken(jwt({ tenant_id: ['haus-a'] }))).toBe('haus-a')
    expect(tenantFromToken(jwt({ tenant_id: ' haus-a ' }))).toBe('haus-a')
  })

  it('kommt mit Umlauten im Token zurecht', () => {
    expect(tenantFromToken(jwt({ name: 'Jörg Müller', tenant_id: 'haus-a' }))).toBe('haus-a')
  })

  it('nennt keinen Mandanten, wenn das Token keinen oder mehrere nennt', () => {
    expect(tenantFromToken(jwt({ sub: 'a' }))).toBeNull()
    expect(tenantFromToken(jwt({ tenant_id: '' }))).toBeNull()
    expect(tenantFromToken(jwt({ tenant_id: 'haus-a', mandanten_id: 'haus-b' }))).toBeNull()
    expect(tenantFromToken(jwt({ tenant_id: ['haus-a', 'haus-b'] }))).toBeNull()
  })

  it('haelt den Dev-Token und Unlesbares nicht fuer ein JWT', () => {
    expect(tenantFromToken('dev-token')).toBeNull()
    expect(tenantFromToken('a.b.c')).toBeNull()
    expect(tenantFromToken(null)).toBeNull()
    expect(tenantFromToken(undefined)).toBeNull()
  })
})
