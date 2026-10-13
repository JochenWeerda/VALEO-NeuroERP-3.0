import { renderHook, act } from '@testing-library/react'
import { describe, expect, it, vi, beforeEach } from 'vitest'
import type { ScreenActionDefinition } from '@/components/mask-builder/schema'
import type { ActionRequest } from '@/components/mask-builder/runtime/ActionRuntime'
import { prepareDocflowCommand, docflowCommandResult, docflowErrorResult } from '@/components/mask-builder/runtime/docflow-command-adapter'
import { useActionRuntime } from '@/components/mask-builder/runtime/useActionRuntime'
import { apiClient } from '@/lib/api-client'
vi.mock('@/lib/api-client', () => ({ apiClient: { request: vi.fn() } }))

function action(command: NonNullable<ScreenActionDefinition['commandBinding']>['command']): ScreenActionDefinition {
  const suffix = command === 'approval_request' ? 'approvals' : command === 'approval_decide' ? 'approvals/{approval_id}/decision' : command
  return { key: command, label: command, permission: 'belege.buchen', enabledWhen: 'allowed', method: 'POST',
    commandEndpoint: `/api/v1/docflow/{entity_id}/${suffix}`, commandBinding: { adapter: 'docflow.v1', command, preview: command === 'convert',
      defaults: command === 'convert' ? { target_doc_type: 'purchase_invoice' } : command === 'approval_request' ? { action: 'post' } : { granted: true, action: 'post' } } }
}
const opts = (command: string) => ({ screenId: 'beleg/purchase-invoice', entityId: 'doc-1', permissions: ['belege.buchen'],
  entityData: { version: 7, allowed: true, aktionen: [{ key: command, erlaubt: true, approval_id: 'approval-1' }] } })
const request = (command: string): ActionRequest => ({ actionKey: command, mode: 'execute', expectedVersion: 7, approvalId: 'approval-1',
  ...(command === 'reverse' ? { auditReason: 'Fehlerkorrektur' } : {}) })
const key = 'stable-intent-key'
beforeEach(() => vi.mocked(apiClient.request).mockReset())

describe('versioned DocFlow transport', () => {
  it.each(['post', 'release', 'reverse', 'convert'] as const)('maps %s to canonical fields and result', command => {
    const prepared = prepareDocflowCommand(action(command), request(command), opts(command), key)
    expect(prepared.body).toMatchObject({ idempotency_key: key, expected_version: 7 })
    expect(prepared.body).not.toHaveProperty('_mode')
    expect(prepared.body).not.toHaveProperty('posted_by')
    if (command === 'reverse') expect(prepared.body.reason).toBe('Fehlerkorrektur')
    if (command === 'convert') expect(prepared.body).toMatchObject({ target_doc_type: 'purchase_invoice', dry_run: false })
    expect(docflowCommandResult(action(command), request(command), opts(command), { command, status: 'ok', source_doc_id: 'doc-1' }).success).toBe(true)
  })
  it('uses the actual convert dry-run endpoint and yields a visible proposal', () => {
    const req = { ...request('convert'), mode: 'dryRun' as const }
    expect(prepareDocflowCommand(action('convert'), req, opts('convert'), key).body.dry_run).toBe(true)
    const result = docflowCommandResult(action('convert'), req, opts('convert'), { command: 'convert', status: 'dry_run', source_doc_id: 'doc-1', payload: { item_count: 2, target_doc_type: 'purchase_invoice' } })
    expect(result.success).toBe(true)
    expect(result.proposedChanges?.[0].description).toContain('Positionen: 2')
  })
  it.each(['post', 'release', 'reverse', 'approval_request', 'approval_decide'] as const)('rejects fictitious %s previews', command => {
    expect(() => prepareDocflowCommand(action(command), { ...request(command), mode: 'dryRun' }, opts(command), key)).toThrow('schreibfreie Vorschau')
  })
  it.each([
    { payload: { posted_by: 'spoofed' } }, { payload: { idempotency_key: 'override' } },
    { payload: { target_doc_type: 'sales_invoice' } }, { expectedVersion: 6 }, { entityId: 'other-doc' },
  ])('rejects forged or stale inputs: %j', change => {
    expect(() => prepareDocflowCommand(action('post'), { ...request('post'), ...change }, opts('post'), key)).toThrow()
  })
  it('requires a verified server action and version', () => {
    expect(() => prepareDocflowCommand(action('post'), request('post'), { ...opts('post'), entityData: {} }, key)).toThrow('gesperrt')
    expect(() => prepareDocflowCommand(action('post'), { ...request('post'), expectedVersion: undefined }, { ...opts('post'), entityData: { ...opts('post').entityData, version: undefined } }, key)).toThrow('version fehlt')
  })
  it('rejects a mismatched endpoint or adapter version', () => {
    expect(() => prepareDocflowCommand({ ...action('post'), commandEndpoint: '/api/v1/pay' }, request('post'), opts('post'), key)).toThrow('Endpoint')
    expect(() => prepareDocflowCommand({ ...action('post'), commandBinding: undefined }, request('post'), opts('post'), key)).toThrow('Adapter')
  })
  it('rejects metadata changed after the user opened the action', () => {
    const original = action('convert')
    const changed = { ...original, commandBinding: { ...original.commandBinding!, defaults: { target_doc_type: 'sales_invoice' } } }
    expect(() => prepareDocflowCommand(changed, { ...request('convert'), bindingSnapshot: JSON.stringify(original.commandBinding) }, opts('convert'), key)).toThrow('Metadaten')
  })
  it('normalizes an actual declined approval response', () => {
    const declined = action('approval_decide')
    declined.commandBinding!.defaults = { granted: false, action: 'post' }
    expect(prepareDocflowCommand(declined, request('approval_decide'), opts('approval_decide'), key).body).toEqual({ granted: false })
    expect(docflowCommandResult(declined, request('approval_decide'), opts('approval_decide'), { id: 'approval-1', action: 'post', status: 'denied' }).success).toBe(true)
  })
  it('does not enable agent writes through metadata', () => {
    expect(() => prepareDocflowCommand(action('post'), request('post'), { ...opts('post'), isAgentCaller: true }, key)).toThrow('nicht freigeschaltet')
  })
  it('rejects unrelated or malformed success responses', () => {
    for (const response of [{ success: true }, { command: 'reverse', status: 'ok', source_doc_id: 'doc-1' }, { command: 'post', status: 'ok', source_doc_id: 'other' }]) {
      expect(docflowCommandResult(action('post'), request('post'), opts('post'), response).success).toBe(false)
    }
  })
  it('binds approvals to the server-provided ID and concrete decision', () => {
    const prepared = prepareDocflowCommand(action('approval_decide'), request('approval_decide'), opts('approval_decide'), key)
    expect(prepared).toEqual({ url: '/api/v1/docflow/doc-1/approvals/approval-1/decision', body: { granted: true } })
    expect(() => prepareDocflowCommand(action('approval_decide'), { ...request('approval_decide'), approvalId: 'other' }, opts('approval_decide'), key)).toThrow('Freigabebindung')
    const response = { id: 'approval-1', action: 'post', subject_version: 7, status: 'granted' }
    expect(docflowCommandResult(action('approval_decide'), request('approval_decide'), opts('approval_decide'), response).success).toBe(true)
    expect(docflowCommandResult(action('approval_decide'), request('approval_decide'), opts('approval_decide'), { ...response, id: 'other' }).success).toBe(false)
    expect(docflowCommandResult(action('approval_decide'), request('approval_decide'), opts('approval_decide'), { ...response, action: 'reverse' }).success).toBe(false)
  })
  it('requests exactly the declared approval action', () => {
    expect(prepareDocflowCommand(action('approval_request'), request('approval_request'), opts('approval_request'), key).body).toEqual({ action: 'post' })
    expect(() => prepareDocflowCommand(action('approval_request'), { ...request('approval_request'), payload: { action: 'reverse' } }, opts('approval_request'), key)).toThrow('Unzulaessige')
  })
  it('keeps HTTP rejection details without reflecting validation input values', () => {
    expect(docflowErrorResult(request('post'), { response: { data: { detail: 'Freigabe erforderlich' } } }).error).toBe('Freigabe erforderlich')
    const result = docflowErrorResult(request('post'), { response: { data: { detail: [{ loc: ['body', 'posting_date'], msg: 'Datum ungueltig', input: 'private-input' }] } } })
    expect(result.validationErrors?.[0].field).toBe('posting_date')
    expect(JSON.stringify(result)).not.toContain('private-input')
  })
  it('reuses the intent key after an uncertain result and changes it for a new version', async () => {
    vi.mocked(apiClient.request).mockRejectedValueOnce(new Error('Network Error')).mockResolvedValue({ data: { command: 'post', status: 'ok', source_doc_id: 'doc-1' } })
    const { result, rerender } = renderHook(({ version }) => useActionRuntime([action('post')], { ...opts('post'), entityData: { ...opts('post').entityData, version } }), { initialProps: { version: 7 } })
    await act(async () => { await result.current.executeAction(request('post')) })
    await act(async () => { await result.current.executeAction(request('post')) })
    const firstKey = vi.mocked(apiClient.request).mock.calls[0][0].data.idempotency_key
    expect(vi.mocked(apiClient.request).mock.calls[1][0].data.idempotency_key).toBe(firstKey)
    rerender({ version: 8 })
    await act(async () => { await result.current.executeAction({ ...request('post'), expectedVersion: 8 }) })
    expect(vi.mocked(apiClient.request).mock.calls[2][0].data.idempotency_key).not.toBe(firstKey)
  })
})
