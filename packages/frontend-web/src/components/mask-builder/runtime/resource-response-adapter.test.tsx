import { act, renderHook } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useActionRuntime } from './useActionRuntime'
import { checkResourceAction, prefillDeclaredInputs, resourceActionResult } from './resource-response-adapter'
import type { ScreenActionDefinition } from '../schema'
const request = vi.hoisted(() => vi.fn())
vi.mock('@/lib/api-client', () => ({ apiClient: { request } }))
const action: ScreenActionDefinition = { key: 'edit', label: 'Bearbeiten', permission: 'crm.campaign.update', method: 'PUT', commandEndpoint: '/api/v1/crm/campaigns/templates/{entity_id}', responseAdapter: 'resource.v1', forbiddenForAgents: true, inputPrefill: 'entity', inputFields: [{ key: 'name', label: 'Name', type: 'text' }] }
const opts = { screenId: 'crm/campaign-template', entityId: 'template-1', permissions: ['crm.campaign.update'] }
const req = { actionKey: 'edit', mode: 'execute' as const, payload: { name: 'Neu' } }
beforeEach(() => { vi.clearAllMocks(); request.mockResolvedValue({ data: { id: 'template-1' } }) })
describe('explicit human resource adapter', () => {
 it('projects only declared editable initial values, retaining false/null', () => {
  expect(prefillDeclaredInputs({ ...action, inputFields: [{ key: 'active', label: 'Aktiv', type: 'boolean' }, { key: 'description', label: 'Text', type: 'text' }] }, { active: false, description: null, tenant_id: 'other' }, {})).toEqual({ active: false, description: null })
 })
 it('normalizes a confirmed update receipt through the real action hook', async () => {
  const { result } = renderHook(() => useActionRuntime([action], opts))
  let receipt
  await act(async () => { receipt = await result.current.executeAction(req) })
  expect(receipt).toMatchObject({ success: true, resourceId: 'template-1' })
  expect(request).toHaveBeenCalledWith({ method: 'PUT', url: '/api/v1/crm/campaigns/templates/template-1', data: { name: 'Neu' } })
 })
 it.each(['dryRun', 'validate', 'propose'] as const)('blocks %s without an HTTP mutation', async mode => {
  const { result } = renderHook(() => useActionRuntime([action], opts))
  let receipt; await act(async () => { receipt = await result.current.executeAction({ ...req, mode }) })
  expect(receipt).toMatchObject({ success: false }); expect(request).not.toHaveBeenCalled()
 })
 it('blocks unauthorized and agent callers before transport', async () => {
  for (const caller of [{ ...opts, permissions: [] }, { ...opts, isAgentCaller: true }]) {
   const { result, unmount } = renderHook(() => useActionRuntime([action], caller))
   let receipt; await act(async () => { receipt = await result.current.executeAction(req) }); expect(receipt).toMatchObject({ success: false }); unmount()
  }
  expect(request).not.toHaveBeenCalled()
 })
 it('rejects resource receipts with missing, wrong or unsafe identities', () => {
  for (const id of [undefined, '', 'foreign-id', '../other', 'id?x=1']) expect(() => resourceActionResult(action, req, opts, { id })).toThrow()
 })
 it('requires a new identity for duplicate and rejects a different endpoint', () => {
  const duplicate = { ...action, method: 'POST' as const, commandEndpoint: action.commandEndpoint + '/duplicate' }
  expect(() => checkResourceAction(duplicate, req, opts)).not.toThrow()
  expect(resourceActionResult(duplicate, req, opts, { id: 'copy-2' }).resourceId).toBe('copy-2')
  expect(() => resourceActionResult(duplicate, req, opts, { id: opts.entityId })).toThrow()
  expect(() => checkResourceAction({ ...action, commandEndpoint: '/api/v1/finance/post' }, req, opts)).toThrow()
 })
 it('keeps transport errors unsuccessful', async () => {
  request.mockRejectedValue(new Error('synthetic failure'))
  const { result } = renderHook(() => useActionRuntime([action], opts)); let receipt
  await act(async () => { receipt = await result.current.executeAction(req) }); expect(receipt).toMatchObject({ success: false })
 })
})
