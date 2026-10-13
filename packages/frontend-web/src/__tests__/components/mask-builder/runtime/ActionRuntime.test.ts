import { describe, it, expect } from 'vitest'
import { buildActionPolicy, checkActionPolicy } from '@/components/mask-builder/runtime/ActionRuntime'

describe('buildActionPolicy', () => {
  it('defaults to safe/no confirmation', () => {
    const p = buildActionPolicy({ key: 'save' })
    expect(p.dangerLevel).toBe('safe')
    expect(p.requiresConfirmation).toBe(false)
    expect(p.requiresHumanApproval).toBe(false)
    expect(p.forbiddenForAgents).toBe(false)
  })

  it('preserves explicit values', () => {
    const p = buildActionPolicy({
      key: 'delete',
      dangerLevel: 'destructive',
      requiresConfirmation: true,
      humanApprovalRequired: true,
      auditReasonRequired: true,
    })
    expect(p.dangerLevel).toBe('destructive')
    expect(p.requiresConfirmation).toBe(true)
    expect(p.requiresHumanApproval).toBe(true)
    expect(p.auditReasonRequired).toBe(true)
  })
})

describe('checkActionPolicy', () => {
  const baseOpts = { screenId: 'test/screen', entityId: '1', permissions: [] }

  it('allows human caller even for dangerous action', () => {
    const p = buildActionPolicy({ key: 'delete', dangerLevel: 'destructive', requiresConfirmation: true })
    expect(checkActionPolicy(p, { ...baseOpts, isAgentCaller: false })).toBeUndefined()
  })

  it('blocks agent on forbiddenForAgents', () => {
    const p = buildActionPolicy({ key: 'admin', forbiddenForAgents: true })
    const result = checkActionPolicy(p, { ...baseOpts, isAgentCaller: true })
    expect(result).toMatch(/gesperrt/)
  })

  it('blocks agent when humanApprovalRequired', () => {
    const p = buildActionPolicy({ key: 'approve', humanApprovalRequired: true })
    const result = checkActionPolicy(p, { ...baseOpts, isAgentCaller: true })
    expect(result).toMatch(/menschliche Genehmigung/)
  })

  it('allows agent for safe action without restrictions', () => {
    const p = buildActionPolicy({ key: 'refresh', dangerLevel: 'safe' })
    expect(checkActionPolicy(p, { ...baseOpts, isAgentCaller: true })).toBeUndefined()
  })
})


describe('declared action rights are enforced on direct calls', () => {
  const policy = buildActionPolicy({ key: 'post', permission: 'belege.buchen' })
  it.each([false, true])('denies caller without declared right (agent=%s)', (isAgentCaller) => {
    expect(checkActionPolicy(policy, { screenId: 'beleg/purchase-invoice', permissions: [], isAgentCaller }))
      .toMatch(/Keine Berechtigung/)
  })
  it('allows the exact declared right, without wildcard expansion', () => {
    expect(checkActionPolicy(policy, { screenId: 'beleg/purchase-invoice', permissions: ['belege.buchen'] }))
      .toBeUndefined()
    expect(checkActionPolicy(policy, { screenId: 'beleg/purchase-invoice', permissions: ['belege:write'] }))
      .toMatch(/Keine Berechtigung/)
  })
})
