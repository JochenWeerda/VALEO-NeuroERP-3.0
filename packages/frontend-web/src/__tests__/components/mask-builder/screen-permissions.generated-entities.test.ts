import { describe, expect, it } from 'vitest'
import { getScreenPermissions } from '@/components/mask-builder/runtime/screen-permissions'
import type { ScreenDefinition } from '@/components/mask-builder/schema'
import type { User } from '@/lib/auth'

const user = (roles: string[], scopes: string[] = []): User => ({ sub: 'synthetic', name: 'Synthetic',
  email: 'synthetic@example.invalid', exp: 9999999999, roles, scopes })
const screen = (domain: string): ScreenDefinition => ({ schemaVersion: 1, id: 'tenant/studio_probe',
  domain, mode: 'list', title: 'Synthetic', actions: [{ key: 'create', label: 'Anlegen',
    permission: `studio.entity.${domain}.write` }] })

describe('generated entity permissions from existing backend authorizers', () => {
  it('keeps readers, unrelated writers and retired manager outside CRM writes', () => {
    for (const roles of [[], ['CRM_LESEN'], ['FINANCE_BEARBEITEN'], ['manager']]) {
      expect(getScreenPermissions(screen('crm'), user(roles))).toEqual([])
    }
  })
  it('projects the existing CRM and sales writer roles and admin', () => {
    for (const role of ['CRM_BEARBEITEN', 'CRM_ADMIN', 'SALES_BEARBEITEN', 'admin']) {
      expect(getScreenPermissions(screen('crm'), user([role]))).toEqual(['studio.entity.crm.write'])
    }
  })
  it('does not replace domain roles with a claimed scope or admin scope', () => {
    expect(getScreenPermissions(screen('crm'), user([], ['studio.entity.crm.write', 'admin:all']))).toEqual([])
  })
  it('keeps warehouse and agrar roles separate and unknown namespaces denied', () => {
    expect(getScreenPermissions(screen('inventory'), user(['LAGER_BEARBEITEN']))).toEqual(['studio.entity.inventory.write'])
    expect(getScreenPermissions(screen('inventory'), user(['CRM_BEARBEITEN']))).toEqual([])
    expect(getScreenPermissions(screen('agrar'), user(['AGRAR_BEARBEITEN']))).toEqual(['studio.entity.agrar.write'])
    expect(getScreenPermissions(screen('finance'), user(['admin']))).toEqual([])
  })
})
