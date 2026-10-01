import { describe, expect, it } from 'vitest'
import { resolvePartyKind, resolvePartySectionKey } from '@/pages/crm/party-native'
import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'

describe('Party native entry', () => {
  it('resolves lead from query or path', () => {
    expect(resolvePartyKind('lead')).toBe('lead')
    expect(resolvePartyKind(null, '/crm/lead/abc')).toBe('lead')
    expect(resolvePartyKind(null, '/crm/kunden/abc')).toBe('customer')
  })

  it('maps KIM deep-link tabs onto ScreenDefinition sections', () => {
    expect(resolvePartySectionKey('chef')).toBe('masterdata')
    expect(resolvePartySectionKey('gifts')).toBe('praesente')
    expect(resolvePartySectionKey('präsente')).toBe('praesente')
    expect(resolvePartySectionKey('postfach')).toBe('postfach')
    expect(resolvePartySectionKey('geo')).toBe('address')
    expect(resolvePartySectionKey('belege')).toBe('auftraege')
    expect(resolvePartySectionKey('angebote')).toBe('angebote')
    expect(resolvePartySectionKey('quotes')).toBe('angebote')
    expect(resolvePartySectionKey('historie')).toBe('historie')
    expect(resolvePartySectionKey(null)).toBeUndefined()
  })

  it('turns KIM into a redirect instead of a second layout', () => {
    const source = readFileSync(resolve(__dirname, '../../../pages/crm/kim/index.tsx'), 'utf8')
    expect(source).toContain('verkauf/kunden-liste')
    expect(source).toContain('/crm/kunden/')
    expect(source).toContain('readQueryParam')
    expect(source).not.toContain('CustomerListSidebar')
    expect(source).not.toContain("type KimTab")
  })

  it('sends existing Stamm-IDs into the native Akte', () => {
    const stamm = readFileSync(resolve(__dirname, '../../../pages/verkauf/kunden-stamm.tsx'), 'utf8')
    expect(stamm).toContain('/crm/kunden/')
    expect(stamm).toContain("searchParams.get('pflege')")
    const popup = readFileSync(resolve(__dirname, '../../../components/telefonie/IncomingCallPopup.tsx'), 'utf8')
    expect(popup).toContain('/crm/kunden/')
    expect(popup).not.toContain('/crm/kunden-cockpit')
    const cockpit = readFileSync(resolve(__dirname, '../../../pages/crm/kunden-cockpit.tsx'), 'utf8')
    expect(cockpit).toContain('/crm/kunden/')
    expect(cockpit).toContain('readQueryParam')
  })
})
