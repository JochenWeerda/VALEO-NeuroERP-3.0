import { beforeEach, describe, expect, it, vi } from 'vitest'
import {
  callOrderStatusOpen,
  isSafeOrderRoutePath,
  pickSafeOrderRoutePath,
} from '@/lib/mcp-order-open'

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    post: vi.fn(),
  },
}))

import { apiClient } from '@/lib/api-client'

describe('mcp-order-open route guard', () => {
  it('accepts canonical relative order paths', () => {
    expect(isSafeOrderRoutePath('/sales/order-editor/ord-1')).toBe(true)
    expect(isSafeOrderRoutePath('/sales/order-editor/a1b2c3d4-e5f6-7890-abcd-ef1234567890')).toBe(true)
  })

  it('rejects open redirects and query fragments', () => {
    expect(isSafeOrderRoutePath('https://evil.example/sales/order-editor/x')).toBe(false)
    expect(isSafeOrderRoutePath('//evil.example/sales/order-editor/x')).toBe(false)
    expect(isSafeOrderRoutePath('/sales/order-editor/x?next=https://evil')).toBe(false)
    expect(isSafeOrderRoutePath('/sales/order-editor/x#tab')).toBe(false)
    expect(isSafeOrderRoutePath('/sales/auftraege-liste')).toBe(false)
    expect(pickSafeOrderRoutePath('/sales/order-editor/ok')).toBe('/sales/order-editor/ok')
    expect(pickSafeOrderRoutePath('/sales/order-editor/ok?x=1')).toBeNull()
  })
})

describe('callOrderStatusOpen', () => {
  beforeEach(() => {
    vi.mocked(apiClient.post).mockReset()
  })

  it('returns the safe route from MCP dryRun', async () => {
    vi.mocked(apiClient.post).mockResolvedValue({
      data: {
        order_id: 'ord-1',
        auftrag_nr: 'SO-100',
        status: 'confirmed',
        route_path: '/sales/order-editor/ord-1',
        screen_id: 'sales/sales-order',
      },
    } as never)

    const result = await callOrderStatusOpen('SO-100')
    expect(result.route_path).toBe('/sales/order-editor/ord-1')
    expect(apiClient.post).toHaveBeenCalledWith('/api/v1/mcp/tools/call', {
      tool_name: 'sales.order.status',
      parameters: { auftrag_nr: 'SO-100' },
      mode: 'dryRun',
    })
  })

  it('rejects unsafe MCP route_path', async () => {
    vi.mocked(apiClient.post).mockResolvedValue({
      data: {
        order_id: 'ord-1',
        auftrag_nr: 'SO-100',
        status: 'confirmed',
        route_path: 'https://evil.example/x',
        screen_id: 'sales/sales-order',
      },
    } as never)

    await expect(callOrderStatusOpen('SO-100')).rejects.toThrow(/unsafe or incomplete route/)
  })
})
