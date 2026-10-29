import { beforeEach, describe, expect, it, vi } from 'vitest'

const apiClient = vi.hoisted(() => ({ post: vi.fn(), put: vi.fn(), delete: vi.fn(), get: vi.fn() }))
vi.mock('../api-client', () => ({ apiClient }))
import { crmService } from './crm-service'

const response = { data: { id: 'a', type: 'call', title: 'Title', version: 3, date: null, status: 'planned', main_topics: ['A'], orders_placed: [], follow_up_actions: [] } }

describe('activity aggregate commands', () => {
  beforeEach(() => { vi.clearAllMocks(); apiClient.post.mockResolvedValue(response); apiClient.put.mockResolvedValue(response); apiClient.delete.mockResolvedValue({ data: undefined }) })
  it('maps the aggregate once and excludes identity and read metadata', async () => {
    const result = await crmService.createActivity({ type: 'call', title: 'Title', contactPerson: 'Person', date: '', mainTopics: ['A'], ordersPlaced: ['B'], followUpActions: ['C'], ...({ tenantId: 'forged', createdBy: 'forged', version: 4 } as object) }, { idempotencyKey: 'intent' })
    expect(apiClient.post).toHaveBeenCalledTimes(1)
    expect(apiClient.post).toHaveBeenCalledWith('/api/v1/crm/activities', { type: 'call', title: 'Title', contact_person: 'Person', date: null, main_topics: ['A'], orders_placed: ['B'], follow_up_actions: ['C'], idempotency_key: 'intent' })
    expect(result.version).toBe(3)
    expect(result.date).toBe('')
  })
  it('sends version and stable key with update and delete', async () => {
    await crmService.updateActivity('a', { date: '2026-10-29', mainTopics: ['A'] }, { expectedVersion: 3, idempotencyKey: 'retry-key' })
    expect(apiClient.put).toHaveBeenCalledWith('/api/v1/crm/activities/a', { date: '2026-10-29T00:00:00Z', main_topics: ['A'], expected_version: 3, idempotency_key: 'retry-key' })
    await crmService.deleteActivity('a', { expectedVersion: 3, idempotencyKey: 'delete-key' })
    expect(apiClient.delete).toHaveBeenCalledWith('/api/v1/crm/activities/a', { headers: { 'If-Match': '"3"', 'Idempotency-Key': 'delete-key' } })
  })
  it('rejects a missing version before writing', async () => {
    await expect(crmService.updateActivity('a', {}, { expectedVersion: undefined as unknown as number, idempotencyKey: 'key' })).rejects.toThrow('Version')
    expect(apiClient.put).not.toHaveBeenCalled()
  })
})
