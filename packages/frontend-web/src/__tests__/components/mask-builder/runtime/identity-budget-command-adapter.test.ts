import { describe, expect, it } from 'vitest'
import { identityBudgetInput } from '@/components/mask-builder/runtime/identity-budget-command-adapter'

describe('strict native quota transport', () => {
  it('excludes session identity and allocation fields from a root command', () => {
    expect(identityBudgetInput('/api/v1/identity/budgets/actions/root', {
      tokens: 10000, max_children: 1, subject: 'untrusted', tenant_id: 'foreign',
      idle_seconds: 900, owner: 'foreign', _mode: 'execute',
    })).toEqual({ tokens: 10000, max_children: 1 })
  })
  it('retains explicit recipient and replay reference for allocation, including zero children', () => {
    expect(identityBudgetInput('/api/v1/identity/budgets/actions/allocate', {
      tokens: 10000, max_children: 0, owner: 'synthetic-user', kind: 'user',
      parent: 'bounded-parent', request_id: 'stable-intent', tenant_id: 'foreign',
    })).toEqual({ tokens: 10000, max_children: 0, owner: 'synthetic-user', kind: 'user',
      parent: 'bounded-parent', request_id: 'stable-intent' })
  })
  it('preserves unrelated commands without widening the exact endpoint match', () => {
    const input = { arbitrary: 'context' }
    expect(identityBudgetInput('/api/v1/other/actions/root', input)).toBe(input)
    expect(identityBudgetInput('/api/v1/identity/budgets/actions/root/other', input)).toBe(input)
  })
})
