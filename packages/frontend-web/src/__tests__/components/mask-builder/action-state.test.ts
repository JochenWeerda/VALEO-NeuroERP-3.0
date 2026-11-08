import { describe, expect, it } from 'vitest'
import { actionIsEnabled } from '@/components/mask-builder/governance/screen-context'

describe('action state fails closed', () => {
  const conditional = { enabledWhen: 'aktion_buchen' }
  it.each([undefined, {}, { aktion_buchen: false }])('blocks absent or rejected server state: %j', root => {
    expect(actionIsEnabled(conditional, root)).toBe(false)
  })
  it('permits the positive server decision and preserves unconditional actions', () => {
    expect(actionIsEnabled(conditional, { aktion_buchen: true })).toBe(true)
    expect(actionIsEnabled({}, undefined)).toBe(true)
    expect(actionIsEnabled({ ...conditional, disabled: true }, { aktion_buchen: true })).toBe(false)
  })
})
