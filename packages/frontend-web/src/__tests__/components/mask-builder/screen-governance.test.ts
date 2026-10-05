import { describe, expect, it } from 'vitest'
import { evaluateCondition, readPath } from '@/components/mask-builder/governance/condition-engine'
import { primitiveForFieldType } from '@/components/mask-builder/governance/primitives'
import { actionIsEnabled, dispatchScreenAction } from '@/components/mask-builder/governance/screen-context'
import { assertSchemaVersion } from '@/components/mask-builder/governance/schema-version'
import { derivedScreenType, rejectedScreenTypeKeys } from '@/components/mask-builder/governance/screen-types'

describe('Screen-Governance', () => {
  it('behält Schema 1 und leitet den Typ aus dem Floorplan ab', () => {
    expect(assertSchemaVersion(1)).toBeNull()
    expect(assertSchemaVersion(2)).toContain('1')
    expect(derivedScreenType('cockpit', 'cockpit', 'single')).toBe('DASHBOARD')
    expect(derivedScreenType('worklist', 'list', 'single')).toBe('WORKLIST')
    expect(derivedScreenType('worklist', 'list', 'listDetail')).toBe('MASTER_DETAIL')
    expect(rejectedScreenTypeKeys({ screenType: 'LIST', id: 'x' })).toEqual(['screenType'])
  })

  it('wertet UI-Bedingungen und Domänen-Policies aus', () => {
    const root = { tour: { vehicleId: 'F-1', status: 'closed' }, 'tour.canCreate': false }
    expect(readPath(root, 'tour.vehicleId')).toBe('F-1')
    expect(evaluateCondition({
      all: [
        { path: 'tour.vehicleId', exists: true },
        { path: 'tour.status', notEquals: 'closed' },
      ],
    }, root)).toBe(false)
    expect(evaluateCondition('tour.canCreate', root)).toBe(false)
    expect(actionIsEnabled({ disabled: false, enabledWhen: 'tour.canCreate' }, { 'tour.canCreate': true })).toBe(true)
    expect(primitiveForFieldType('lookup')).toBe('EntityPicker')
    expect(primitiveForFieldType('badge')).toBeNull()
  })

  it('ruft den registrierten Befehl auf und lässt den Schlüssel als Rückfall', async () => {
    const calls: string[] = []
    await dispatchScreenAction(
      {
        data: {},
        permissions: { granted: [] },
        state: { values: {}, policies: {} },
        actions: { 'tour.create': () => { calls.push('command') } },
        navigation: { push: () => undefined },
      },
      { key: 'anlegen', command: 'tour.create' },
      {},
      () => { calls.push('fallback') },
    )
    await dispatchScreenAction(undefined, { key: 'neu' }, {}, () => { calls.push('fallback') })
    expect(calls).toEqual(['command', 'fallback'])
  })
})
