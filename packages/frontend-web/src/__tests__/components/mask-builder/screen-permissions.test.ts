import { describe, expect, it } from 'vitest'
import { getScreenPermissions } from '@/components/mask-builder/runtime/screen-permissions'
import type { ScreenDefinition } from '@/components/mask-builder/schema'
import type { User } from '@/lib/auth'

const user = (scopes: string[] = [], roles: string[] = []): User => ({
  sub: 'test', name: 'Test', email: 'test@example.invalid', exp: 9999999999, scopes, roles,
})
const screen: ScreenDefinition = {
  schemaVersion: 1, id: 'logistik/test', domain: 'logistics', mode: 'list', title: 'Test',
  permissions: ['logistics:write'], // A schema cannot grant itself access.
  actions: [
    { key: 'read', label: 'Read', permission: 'logistics:read' },
    { key: 'write', label: 'Write', permission: 'logistics:write' },
  ],
}
describe('authenticated mask permission projection', () => {
  it('denies anonymous users and ignores schema grants', () => {
    expect(getScreenPermissions(screen, null)).toEqual([])
    expect(getScreenPermissions(screen, user())).toEqual([])
  })
  it('keeps read and write distinct', () => {
    expect(getScreenPermissions(screen, user(['logistics:read']))).toEqual(['logistics:read'])
    expect(getScreenPermissions(screen, user(['logistics:write']))).toEqual(['logistics:read', 'logistics:write'])
  })
  it('projects declared permissions for admin only', () => {
    expect(getScreenPermissions(screen, user(['admin:all']))).toEqual(['logistics:read', 'logistics:write'])
    expect(getScreenPermissions(screen, user([], ['admin']))).toEqual(['logistics:read', 'logistics:write'])
  })
  it('matches the canonical lead write roles including creation', () => {
    const lead: ScreenDefinition = { ...screen, id: 'crm/lead', domain: 'crm', actions: [],
      creation: { endpoint: '/api/v1/crm/leads', permission: 'crm.lead.create', detailRoute: '/crm/lead/{entity_id}' } }
    expect(getScreenPermissions(lead, user([], ['CRM_LESEN']))).toEqual([])
    expect(getScreenPermissions(lead, user([], ['CRM_BEARBEITEN']))).toEqual(['crm.lead.create'])
  })
})
