import { act, renderHook } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import contract from '@/components/mask-builder/runtime/harvest-control-contract.generated.json'
import { prepareHarvestControl } from '@/components/mask-builder/runtime/harvest-control-command-adapter'
import { useActionRuntime } from '@/components/mask-builder/runtime/useActionRuntime'
import type { ActionRequest, ActionRuntimeOptions } from '@/components/mask-builder/runtime/ActionRuntime'
import type { ScreenActionDefinition } from '@/components/mask-builder/schema'
import { apiClient } from '@/lib/api-client'

vi.mock('@/lib/api-client', () => ({ apiClient: { request: vi.fn() } }))
type Command = keyof typeof contract.paths
const action = (command: Command): ScreenActionDefinition => ({ key: command, label: command, method: 'POST',
  permission: command, commandEndpoint: contract.paths[command], forbiddenForAgents: true,
  requiresConfirmation: ['approve_rule', 'revoke_rule', 'approve_calculation', 'release'].includes(command),
  commandBinding: { adapter: 'harvest.control.v1', command, preview: false } })
const options: ActionRuntimeOptions = { screenId: 'agrar/harvest-controls', entityId: 'acceptance', permissions: ['calculate'],
  entityData: { control_context: { context_hash: 'a'.repeat(64), calculation_hash: 'b'.repeat(64),
    state: { acceptance: { id: 'acceptance' }, protocol: { id: 'protocol' } }, protocol_hash: 'c'.repeat(64) },
  selected_rule: { id: 'rule-version', content_hash: 'd'.repeat(64), definition: { rule_id: 'terms', rule_version: 2 } } } }
const request: ActionRequest = { actionKey: 'calculate', mode: 'execute', payload: { acceptance_id: 'acceptance' } }

beforeEach(() => vi.mocked(apiClient.request).mockReset())

describe('versioned harvest transport', () => {
  it('sends only the exact command body and binds the loaded input state', () => {
    const prepared = prepareHarvestControl(action('calculate'), { ...request, payload: {
      ...request.payload, tenant_id: 'foreign', actor: 'spoofed', impurities_free_pct: 2 } }, options, 'stable-key')
    expect(prepared.url).toBe('/api/v1/agrar/harvest-acceptance/acceptance/calculate')
    expect(prepared.body).toEqual({ idempotency_key: 'stable-key', expected_context_hash: 'a'.repeat(64) })
  })
  it.each(['dryRun', 'validate', 'propose'] as const)('never mutates through %s', mode => {
    expect(() => prepareHarvestControl(action('calculate'), { ...request, mode }, options, 'key')).toThrow('menschliche')
  })
  it('rejects agents, mismatched documents and modified endpoints', () => {
    expect(() => prepareHarvestControl(action('calculate'), request, { ...options, isAgentCaller: true }, 'key')).toThrow('menschliche')
    expect(() => prepareHarvestControl(action('calculate'), request, { ...options, entityId: 'other' }, 'key')).toThrow('Annahme')
    expect(() => prepareHarvestControl({ ...action('calculate'), commandEndpoint: '/evil' }, request, options, 'key')).toThrow('Endpunkt')
  })
  it('requires confirmation and the exact calculation hash for a financial command', () => {
    expect(() => prepareHarvestControl(action('release'), request, options, 'key')).toThrow('bestätigt')
    const prepared = prepareHarvestControl(action('release'), { ...request, payload: {
      acceptance_id: 'acceptance', confirm_execution: 'confirm' } }, options, 'key')
    expect(prepared.body).toEqual({ idempotency_key: 'key', expected_calculation_hash: 'b'.repeat(64) })
  })
  it('keeps the explicit zero allowance and excludes caller identities', () => {
    const prepared = prepareHarvestControl(action('create_rule'), { ...request, payload: {
      rule_id: 'terms', customer_id: 'customer', article_id: 'article', valid_from: '2026-01-01', valid_until: '2026-12-31',
      source_reference: 'synthetic agreement', measurement_method: 'lab', measurement_method_version: '1',
      impurities_free_pct: 0, quality_limit_pct: 2, actor: 'forged', tenant_id: 'foreign' } }, options, 'key')
    expect(prepared.body.expected_version).toBe(2)
    expect(prepared.body.terms).toMatchObject({ impurities_free_pct: '0', quality_limit_pct: 2, contract_id: null })
    expect(prepared.body).not.toHaveProperty('actor')
    expect(prepared.body).not.toHaveProperty('tenant_id')
  })
})

describe('central runtime retry safety', () => {
  it('reuses the idempotency key after an uncertain network outcome', async () => {
    vi.mocked(apiClient.request).mockRejectedValueOnce(new Error('uncertain network outcome'))
      .mockResolvedValueOnce({ data: { control_event_id: 'receipt', calculation_hash: 'hash' } })
    const { result } = renderHook(() => useActionRuntime([action('calculate')], options))
    await act(async () => { expect((await result.current.executeAction(request)).success).toBe(false) })
    await act(async () => { expect((await result.current.executeAction(request)).success).toBe(true) })
    const bodies = vi.mocked(apiClient.request).mock.calls.map(call => call[0]?.data as Record<string, unknown>)
    expect(bodies[0].idempotency_key).toBe(bodies[1].idempotency_key)
    expect(bodies[0]).toEqual(bodies[1])
  })
  it('does not reach transport without the existing permission projection', async () => {
    const { result } = renderHook(() => useActionRuntime([action('calculate')], { ...options, permissions: [] }))
    await act(async () => { expect((await result.current.executeAction(request)).success).toBe(false) })
    expect(apiClient.request).not.toHaveBeenCalled()
  })
})
