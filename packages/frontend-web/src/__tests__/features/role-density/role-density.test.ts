import { describe, expect, it } from 'vitest'
import { mergeToolbarActionsForDensity, resolveRoleDensityProfile } from '@/features/role-density'
import type { ToolbarAction } from '@/components/navigation/PageToolbar'

function createAction(id: string): ToolbarAction {
  return {
    id,
    label: id,
    onClick: () => undefined,
  }
}

describe('resolveRoleDensityProfile', () => {
  it('ordnet manager und admin in die verdichtete Dichte ein', () => {
    const profile = resolveRoleDensityProfile(['user', 'manager'])

    expect(profile.density).toBe('dense')
    expect(profile.maxPrimaryActions).toBe(4)
    expect(profile.processDetailLimit).toBe(Number.POSITIVE_INFINITY)
  })

  it('faellt fuer einfache operator/user Rollen auf focused oder standard zurueck', () => {
    expect(resolveRoleDensityProfile(['operator']).density).toBe('standard')
    expect(resolveRoleDensityProfile(['user']).density).toBe('focused')
  })

  it('zieht die Dichte fuer Finance-/Approval-Kontexte kontrolliert hoch', () => {
    const profile = resolveRoleDensityProfile(['user'], {
      pageDomain: 'finance-approval',
      availableActionIds: ['a1', 'a2', 'a3', 'a4', 'a5'],
      requiresApproval: true,
      processDetails: ['d1', 'd2', 'd3'],
    })

    expect(profile.density).toBe('dense')
  })

  it('zieht Agrar-Tenants ausserhalb des Dev-Defaults mindestens auf standard', () => {
    const profile = resolveRoleDensityProfile(['user'], {
      tenantId: 'tenant-raiffeisen-nord',
      pageDomain: 'agrar-saatgut',
    })

    expect(profile.density).toBe('standard')
  })

  it('respektiert backend-basierte Density-Hinweise als Mindestniveau', () => {
    const profile = resolveRoleDensityProfile(['user'], {
      pageDomain: 'crm',
      backendDensity: 'dense',
    })

    expect(profile.density).toBe('dense')
  })
})

describe('mergeToolbarActionsForDensity', () => {
  it('verschiebt ueberzaehlige Primary-Actions in das Overflow-Menue', () => {
    const profile = resolveRoleDensityProfile(['user'])

    const result = mergeToolbarActionsForDensity(
      [createAction('a1'), createAction('a2'), createAction('a3')],
      [createAction('o1')],
      profile,
    )

    expect(result.primaryActions.map((action) => action.id)).toEqual(['a1', 'a2'])
    expect(result.overflowActions.map((action) => action.id)).toEqual(['a3', 'o1'])
  })
})
